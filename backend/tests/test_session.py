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
from ke.models.policy import PolicyChainResult
from ke.services.pipeline import PipelineOrchestrator
from ke.services.session import InMemorySessionService


class TestInMemorySessionService:
    @pytest.mark.asyncio
    async def test_get_or_create_new_session(self) -> None:
        svc = InMemorySessionService()
        sid, turns = await svc.get_or_create(None)
        assert sid is not None
        assert turns == []

    @pytest.mark.asyncio
    async def test_get_or_create_existing_session(self) -> None:
        svc = InMemorySessionService()
        sid1, _ = await svc.get_or_create(None)
        sid2, turns = await svc.get_or_create(sid1)
        assert sid1 == sid2

    @pytest.mark.asyncio
    async def test_get_or_create_custom_id(self) -> None:
        svc = InMemorySessionService()
        sid, turns = await svc.get_or_create("my-session")
        assert sid == "my-session"
        assert turns == []

    @pytest.mark.asyncio
    async def test_get_or_create_returns_existing_turns(self) -> None:
        svc = InMemorySessionService()
        sid, _ = await svc.get_or_create("test")
        await svc.add_turn("test", "show users", sql="SELECT * FROM users")
        _, turns = await svc.get_or_create("test")
        assert len(turns) == 1

    @pytest.mark.asyncio
    async def test_add_turn_stores_data(self) -> None:
        svc = InMemorySessionService()
        await svc.add_turn("s1", "show users", sql="SELECT * FROM users", result_summary="10 rows", intent_type="SIMPLE_SELECT")
        key = svc._key("s1", "default")
        assert len(svc._sessions[key]) == 1
        t = svc._sessions[key][0]
        assert t.query == "show users"

    @pytest.mark.asyncio
    async def test_add_turn_auto_creates_session(self) -> None:
        svc = InMemorySessionService()
        await svc.add_turn("new-session", "hello")
        key = svc._key("new-session", "default")
        assert key in svc._sessions

    @pytest.mark.asyncio
    async def test_max_turns_enforced(self) -> None:
        svc = InMemorySessionService()
        svc._max_turns = 3
        for i in range(5):
            await svc.add_turn("s1", f"query {i}")
        key = svc._key("s1", "default")
        assert len(svc._sessions[key]) == 3
        assert svc._sessions[key][-1].query == "query 4"

    def test_format_history_empty(self) -> None:
        svc = InMemorySessionService()
        assert svc.format_history([]) == ""

    @pytest.mark.asyncio
    async def test_format_history_single_turn(self) -> None:
        svc = InMemorySessionService()
        await svc.add_turn("s1", "show users", sql="SELECT * FROM users", result_summary="10 rows returned")
        key = svc._key("s1", "default")
        result = svc.format_history(svc._sessions[key])
        assert "show users" in result
        assert "SELECT * FROM users" in result
        assert "10 rows returned" in result

    @pytest.mark.asyncio
    async def test_format_history_max_turns(self) -> None:
        svc = InMemorySessionService()
        for i in range(5):
            await svc.add_turn("s1", f"query {i}")
        key = svc._key("s1", "default")
        result = svc.format_history(svc._sessions[key], max_turns=2)
        assert "query 3" in result
        assert "query 4" in result
        assert "query 0" not in result


class TestPipelineSessionIntegration:
    @pytest.fixture
    def session_svc(self) -> InMemorySessionService:
        return InMemorySessionService()

    def _make_mocks(self):
        intent_agent = MagicMock()
        planner = AsyncMock()
        generator = AsyncMock()
        policy_chain = AsyncMock()
        executor = AsyncMock()
        return intent_agent, planner, generator, policy_chain, executor

    def _setup_success_mocks(self, mocks, sql="SELECT * FROM users", row_count=10):
        intent_agent, planner, generator, policy_chain, executor = mocks
        intent = QueryIntent(query_type=QueryType.SIMPLE_SELECT, tables=[TableRef(id="", name="users")])
        intent_agent.classify.return_value = intent

        planner.plan.return_value = QueryPlan(
            id="plan_1", intent=intent,
            steps=[PlanStep(id="s1", step_number=1, operation=PlanOperation.SCAN)],
            validation=ValidationResult(valid=True),
            cost_estimate=CostEstimate(estimated_rows=100, estimated_cost=1.0),
        )

        gen_result = GenerationResult(
            id="gen_1", query="test", sql=sql,
            status=GenerationStatus.COMPLETED,
            model_tier="standard", model_name="mock", intent=intent.model_dump(),
        )
        generator.generate.return_value = gen_result

        policy_chain.enforce.return_value = PolicyChainResult(
            passed=True, sql=sql, sanitized_sql=sql, layers=[],
        )

        executor.execute.return_value = ExecutionResult(
            id="exec_1", sql=sql,
            status=ExecutionStatus.SUCCESS,
            columns=["id", "name"], rows=[[1, "alice"]],
            row_count=row_count, total_rows=row_count,
        )

    @pytest.mark.asyncio
    async def test_pipeline_injects_session_history(self, session_svc) -> None:
        await session_svc.add_turn("s1", "show users", sql="SELECT * FROM users", result_summary="10 rows returned")
        mocks = self._make_mocks()
        self._setup_success_mocks(mocks)
        intent_agent, planner, generator, policy_chain, executor = mocks

        orch = PipelineOrchestrator(
            intent_agent=intent_agent,
            planner=planner,
            generator=generator,
            policy_chain=policy_chain,
            executor=executor,
        )

        result = await orch.execute(
            "show active users",
            session_service=session_svc,
            session_id="s1",
        )

        assert result.session_id == "s1"
        assert result.status == PipelineStatus.SUCCESS

    @pytest.mark.asyncio
    async def test_pipeline_saves_turn_after_execution(self, session_svc) -> None:
        await session_svc.add_turn("s2", "prior query", sql="SELECT 1")
        mocks = self._make_mocks()
        self._setup_success_mocks(mocks)
        intent_agent, planner, generator, policy_chain, executor = mocks

        orch = PipelineOrchestrator(
            intent_agent=intent_agent,
            planner=planner,
            generator=generator,
            policy_chain=policy_chain,
            executor=executor,
        )

        await orch.execute(
            "show users",
            session_service=session_svc,
            session_id="s2",
        )

        turns = session_svc._sessions[session_svc._key("s2", "default")]
        assert len(turns) == 2
        assert turns[-1].query == "show users"
        assert turns[-1].sql == "SELECT * FROM users"

    @pytest.mark.asyncio
    async def test_pipeline_new_session_if_not_provided(self) -> None:
        session_svc = InMemorySessionService()
        mocks = self._make_mocks()
        self._setup_success_mocks(mocks, sql="SELECT 1", row_count=1)
        intent_agent, planner, generator, policy_chain, executor = mocks

        orch = PipelineOrchestrator(
            intent_agent=intent_agent,
            planner=planner,
            generator=generator,
            policy_chain=policy_chain,
            executor=executor,
        )

        result = await orch.execute("test", session_service=session_svc)

        assert result.session_id != ""
        assert result.status == PipelineStatus.SUCCESS

    @pytest.mark.asyncio
    async def test_pipeline_conversation_history_in_context(self) -> None:
        session_svc = InMemorySessionService()
        await session_svc.add_turn("s3", "show users", sql="SELECT * FROM users", result_summary="10 rows returned")

        mocks = self._make_mocks()
        self._setup_success_mocks(mocks, sql="SELECT * FROM users WHERE active = true", row_count=5)
        intent_agent, planner, generator, policy_chain, executor = mocks

        orch = PipelineOrchestrator(
            intent_agent=intent_agent,
            planner=planner,
            generator=generator,
            policy_chain=policy_chain,
            executor=executor,
        )

        await orch.execute(
            "now only active ones",
            session_service=session_svc,
            session_id="s3",
        )

        call_kwargs = generator.generate.call_args[1]
        context = call_kwargs.get("context", {})
        assert "conversation_history" in context
        assert "show users" in context["conversation_history"]
