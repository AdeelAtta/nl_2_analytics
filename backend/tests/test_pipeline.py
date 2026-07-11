from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from ke.models.execution import ExecutionResult, ExecutionStatus
from ke.models.generation import GenerationResult, GenerationStatus
from ke.models.pipeline import PipelineStatus
from ke.models.planning import (
    CostEstimate,
    PlanStep,
    PlanOperation,
    QueryIntent,
    QueryPlan,
    QueryType,
    TableRef,
    ValidationResult,
)
from ke.models.policy import PolicyChainResult, PolicyLayerResult
from ke.services.pipeline import PipelineOrchestrator
from ke.services.schema_resolver import SchemaResolver


@pytest.fixture
def mock_intent() -> QueryIntent:
    return QueryIntent(query_type=QueryType.SIMPLE_SELECT, description="test query")


@pytest.fixture
def mock_plan(mock_intent: QueryIntent) -> QueryPlan:
    return QueryPlan(
        id="plan_1",
        intent=mock_intent,
        steps=[PlanStep(id="s1", step_number=1, operation=PlanOperation.SCAN)],
        validation=ValidationResult(valid=True),
        cost_estimate=CostEstimate(estimated_rows=100, estimated_cost=1.0),
    )


@pytest.fixture
def mock_generation() -> GenerationResult:
    return GenerationResult(
        id="gen_1",
        query="test query",
        sql="SELECT * FROM users",
        status=GenerationStatus.COMPLETED,
        model_tier="standard",
        model_name="mock",
    )


@pytest.fixture
def mock_guard() -> PolicyChainResult:
    return PolicyChainResult(
        passed=True,
        sql="SELECT * FROM users",
        sanitized_sql="SELECT * FROM users",
        layers=[],
    )


@pytest.fixture
def mock_execution() -> ExecutionResult:
    return ExecutionResult(
        id="exec_1",
        sql="SELECT * FROM users",
        status=ExecutionStatus.SUCCESS,
        columns=["id", "name"],
        rows=[[1, "alice"]],
        row_count=1,
        total_rows=1,
    )


@pytest.fixture
def components(
    mock_intent: QueryIntent,
    mock_plan: QueryPlan,
    mock_generation: GenerationResult,
    mock_guard: PolicyChainResult,
    mock_execution: ExecutionResult,
):
    intent_agent = MagicMock()
    intent_agent.classify.return_value = mock_intent

    planner = AsyncMock()
    planner.plan.return_value = mock_plan

    generator = AsyncMock()
    generator.generate.return_value = mock_generation

    policy_chain = AsyncMock()
    policy_chain.enforce.return_value = mock_guard

    executor = AsyncMock()
    executor.execute.return_value = mock_execution

    return intent_agent, planner, generator, policy_chain, executor


@pytest.fixture
def orchestrator(components):
    intent_agent, planner, generator, policy_chain, executor = components
    return PipelineOrchestrator(
        intent_agent=intent_agent,
        planner=planner,
        generator=generator,
        policy_chain=policy_chain,
        executor=executor,
    )


class TestPipelineOrchestrator:
    @pytest.mark.asyncio
    async def test_full_success(self, orchestrator: PipelineOrchestrator) -> None:
        result = await orchestrator.execute("show me users")

        assert result.status == PipelineStatus.SUCCESS
        assert len(result.stages) == 5
        assert result.stages[0].name == "classify"
        assert result.stages[1].name == "plan"
        assert result.stages[2].name == "generate"
        assert result.stages[3].name == "guard"
        assert result.stages[4].name == "execute"
        assert all(s.status == "success" for s in result.stages)
        assert result.total_duration_ms > 0

    @pytest.mark.asyncio
    async def test_ddl_query_fails_early(self, components) -> None:
        intent_agent, planner, generator, policy_chain, executor = components
        intent_agent.classify.return_value = QueryIntent(query_type=QueryType.DDL)
        orch = PipelineOrchestrator(
            intent_agent=intent_agent,
            planner=planner,
            generator=generator,
            policy_chain=policy_chain,
            executor=executor,
        )

        result = await orch.execute("DROP TABLE users")

        assert result.status == PipelineStatus.FAILED
        assert "DDL" in result.error
        classify_stage = next(s for s in result.stages if s.name == "classify")
        assert classify_stage.status == "success"

    @pytest.mark.asyncio
    async def test_unknown_query_fails_early(self, components) -> None:
        intent_agent, planner, generator, policy_chain, executor = components
        intent_agent.classify.return_value = QueryIntent(query_type=QueryType.UNKNOWN)
        orch = PipelineOrchestrator(
            intent_agent=intent_agent,
            planner=planner,
            generator=generator,
            policy_chain=policy_chain,
            executor=executor,
        )

        result = await orch.execute("foo bar baz")

        assert result.status == PipelineStatus.FAILED
        assert "intent" in result.error.lower()

    @pytest.mark.asyncio
    async def test_classify_failure(self, components) -> None:
        intent_agent, planner, generator, policy_chain, executor = components
        intent_agent.classify.side_effect = ValueError("classification failed")
        orch = PipelineOrchestrator(
            intent_agent=intent_agent,
            planner=planner,
            generator=generator,
            policy_chain=policy_chain,
            executor=executor,
        )

        result = await orch.execute("some query")

        assert result.status == PipelineStatus.FAILED
        assert result.error == "classification failed"
        assert result.stages[0].status == "failed"
        assert len(result.stages) == 1

    @pytest.mark.asyncio
    async def test_plan_failure(self, components, mock_intent) -> None:
        intent_agent, planner, generator, policy_chain, executor = components
        planner.plan.side_effect = RuntimeError("plan failed")
        orch = PipelineOrchestrator(
            intent_agent=intent_agent,
            planner=planner,
            generator=generator,
            policy_chain=policy_chain,
            executor=executor,
        )

        result = await orch.execute("some query")

        assert result.status == PipelineStatus.FAILED
        assert "plan" in result.stages[1].error

    @pytest.mark.asyncio
    async def test_plan_validation_fatal_fails(self, components, mock_intent) -> None:
        intent_agent, planner, generator, policy_chain, executor = components
        from ke.models.planning import ValidationError, ValidationSeverity

        planner.plan.return_value = QueryPlan(
            id="bad_plan",
            intent=mock_intent,
            validation=ValidationResult(
                valid=False,
                errors=[ValidationError(code="PLAN-000", severity=ValidationSeverity.FATAL, message="Bad plan")],
            ),
        )
        orch = PipelineOrchestrator(
            intent_agent=intent_agent,
            planner=planner,
            generator=generator,
            policy_chain=policy_chain,
            executor=executor,
        )

        result = await orch.execute("some query")

        assert result.status == PipelineStatus.FAILED
        assert "Bad plan" in result.error

    @pytest.mark.asyncio
    async def test_generation_failure(self, components) -> None:
        intent_agent, planner, generator, policy_chain, executor = components
        generator.generate.return_value = GenerationResult(
            id="failed",
            query="test",
            sql="",
            status=GenerationStatus.FAILED,
            model_tier="none",
            model_name="",
            error="LLM unavailable",
        )
        orch = PipelineOrchestrator(
            intent_agent=intent_agent,
            planner=planner,
            generator=generator,
            policy_chain=policy_chain,
            executor=executor,
        )

        result = await orch.execute("some query")

        assert result.status == PipelineStatus.FAILED
        assert "LLM unavailable" in result.error

    @pytest.mark.asyncio
    async def test_generation_exception(self, components) -> None:
        intent_agent, planner, generator, policy_chain, executor = components
        generator.generate.side_effect = RuntimeError("model crash")
        orch = PipelineOrchestrator(
            intent_agent=intent_agent,
            planner=planner,
            generator=generator,
            policy_chain=policy_chain,
            executor=executor,
        )

        result = await orch.execute("some query")

        assert result.status == PipelineStatus.FAILED
        assert "model crash" in result.error

    @pytest.mark.asyncio
    async def test_guardrail_blocks_query(self, components) -> None:
        intent_agent, planner, generator, policy_chain, executor = components
        policy_chain.enforce.return_value = PolicyChainResult(
            passed=False,
            sql="SELECT * FROM users",
            sanitized_sql="",
            layers=[PolicyLayerResult(layer_name="L1IntentClassification", layer_number=1, passed=False, blocked=True)],
            stopped_at="L1IntentClassification",
        )
        orch = PipelineOrchestrator(
            intent_agent=intent_agent,
            planner=planner,
            generator=generator,
            policy_chain=policy_chain,
            executor=executor,
        )

        result = await orch.execute("some query")

        assert result.status == PipelineStatus.BLOCKED
        assert "guardrail" in result.error.lower()
        guard_stage = next(s for s in result.stages if s.name == "guard")
        assert guard_stage.status == "blocked"

    @pytest.mark.asyncio
    async def test_execution_failure(self, components) -> None:
        intent_agent, planner, generator, policy_chain, executor = components
        executor.execute.return_value = ExecutionResult(
            id="exec_fail",
            sql="SELECT * FROM users",
            status=ExecutionStatus.ERROR,
        )
        orch = PipelineOrchestrator(
            intent_agent=intent_agent,
            planner=planner,
            generator=generator,
            policy_chain=policy_chain,
            executor=executor,
        )

        result = await orch.execute("some query")

        assert result.status == PipelineStatus.FAILED
        exec_stage = next(s for s in result.stages if s.name == "execute")
        assert exec_stage.status == "error"

    @pytest.mark.asyncio
    async def test_execution_exception(self, components) -> None:
        intent_agent, planner, generator, policy_chain, executor = components
        executor.execute.side_effect = RuntimeError("executor crash")
        orch = PipelineOrchestrator(
            intent_agent=intent_agent,
            planner=planner,
            generator=generator,
            policy_chain=policy_chain,
            executor=executor,
        )

        result = await orch.execute("some query")

        assert result.status == PipelineStatus.FAILED
        exec_stage = next(s for s in result.stages if s.name == "execute")
        assert exec_stage.status == "failed"

    @pytest.mark.asyncio
    async def test_dry_run_mode(self, components, mock_execution) -> None:
        intent_agent, planner, generator, policy_chain, executor = components
        mock_execution.status = ExecutionStatus.DRY_RUN
        mock_execution.explain_output = [{"QUERY PLAN": "Seq Scan on users"}]
        executor.execute.return_value = mock_execution
        orch = PipelineOrchestrator(
            intent_agent=intent_agent,
            planner=planner,
            generator=generator,
            policy_chain=policy_chain,
            executor=executor,
        )

        result = await orch.execute("show me users", dry_run=True)

        assert result.status == PipelineStatus.SUCCESS
        exec_stage = next(s for s in result.stages if s.name == "execute")
        assert exec_stage.status == "dry_run"

    @pytest.mark.asyncio
    async def test_schema_resolver_adds_context(self, orchestrator, components) -> None:
        intent_agent, planner, generator, policy_chain, executor = components
        schema_resolver = AsyncMock(spec=SchemaResolver)
        schema_resolver.resolve.return_value = {
            "tables": [{"id": "t1", "name": "users"}],
            "columns": [{"table_name": "t1", "name": "id", "data_type": "integer", "is_nullable": False, "is_primary_key": True}],
            "relationships": [],
            "ddl_context": "CREATE TABLE users (id integer PK NOT NULL);",
        }
        orch = PipelineOrchestrator(
            intent_agent=intent_agent,
            planner=planner,
            generator=generator,
            policy_chain=policy_chain,
            executor=executor,
        )

        result = await orch.execute("show users", schema_resolver=schema_resolver)

        assert result.status == PipelineStatus.SUCCESS
        assert any(s.name == "resolve_schema" for s in result.stages)
        schema_stage = next(s for s in result.stages if s.name == "resolve_schema")
        assert schema_stage.status == "success"

    @pytest.mark.asyncio
    async def test_schema_resolver_populates_merged_context(self, components, mock_intent) -> None:
        intent_agent, planner, generator, policy_chain, executor = components
        intent_agent.classify.return_value = QueryIntent(
            query_type=QueryType.SIMPLE_SELECT,
            tables=[TableRef(id="", name="users")],
        )
        schema_resolver = AsyncMock(spec=SchemaResolver)
        schema_resolver.resolve.return_value = {
            "tables": [{"id": "t1", "name": "users"}],
            "columns": [{"table_name": "t1", "name": "id", "data_type": "integer"}],
            "relationships": [],
            "ddl_context": "CREATE TABLE users (id integer);",
        }
        orch = PipelineOrchestrator(
            intent_agent=intent_agent,
            planner=planner,
            generator=generator,
            policy_chain=policy_chain,
            executor=executor,
        )

        await orch.execute("show users", schema_resolver=schema_resolver)

        schema_resolver.resolve.assert_called_once()

    @pytest.mark.asyncio
    async def test_schema_resolver_failure_does_not_block_pipeline(self, orchestrator) -> None:
        schema_resolver = AsyncMock(spec=SchemaResolver)
        schema_resolver.resolve.side_effect = RuntimeError("schema resolve failed")

        result = await orchestrator.execute("show users", schema_resolver=schema_resolver)

        assert result.status == PipelineStatus.SUCCESS
        schema_stage = next(s for s in result.stages if s.name == "resolve_schema")
        assert schema_stage.status == "failed"

    @pytest.mark.asyncio
    async def test_schema_resolver_not_called_when_not_provided(self, orchestrator) -> None:
        result = await orchestrator.execute("show users")

        assert result.status == PipelineStatus.SUCCESS
        assert not any(s.name == "resolve_schema" for s in result.stages)
