from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from ke.models.planning import QueryComplexity, QueryIntent, QueryType, TableRef, ColumnRef
from ke.models.quality import QualityDimension, QualityScore
from ke.services.quality_scorer import QueryQualityScorer


def _sample_context() -> dict:
    return {
        "tables": [{"id": "t1", "name": "users"}],
        "columns": [
            {"name": "id", "table_name": "users", "data_type": "integer"},
            {"name": "name", "table_name": "users", "data_type": "varchar"},
            {"name": "email", "table_name": "users", "data_type": "varchar"},
        ],
    }


def _sample_intent() -> QueryIntent:
    return QueryIntent(
        query_type=QueryType.SIMPLE_SELECT,
        complexity=QueryComplexity.SIMPLE,
        tables=[TableRef(id="t1", name="users")],
        columns=[ColumnRef(table="users", column="name")],
    )


class TestQueryQualityScorer:
    @pytest.mark.asyncio
    async def test_score_valid_sql(self) -> None:
        scorer = QueryQualityScorer(enable_llm=False)
        score = await scorer.score(
            sql="SELECT * FROM users WHERE id = 1;",
            query="show me users where id is 1",
            context=_sample_context(),
        )

        assert isinstance(score, QualityScore)
        assert score.overall > 0.0
        assert len(score.dimensions) == len(QualityDimension)
        for d in score.dimensions:
            assert 0.0 <= d.score <= 1.0
        assert score.model == "rule_based"

    @pytest.mark.asyncio
    async def test_score_empty_sql(self) -> None:
        scorer = QueryQualityScorer(enable_llm=False)
        score = await scorer.score(
            sql="",
            query="something",
            context=_sample_context(),
        )

        assert score.overall == 0.0
        for d in score.dimensions:
            assert d.score == 0.0

    @pytest.mark.asyncio
    async def test_score_dangerous_sql_low_safety(self) -> None:
        scorer = QueryQualityScorer(enable_llm=False)
        score = await scorer.score(
            sql="DROP TABLE users; DELETE FROM users;",
            query="drop users",
            context=_sample_context(),
        )

        safety = next(d for d in score.dimensions if d.dimension == QualityDimension.SAFETY)
        assert safety.score < 0.5

    @pytest.mark.asyncio
    async def test_score_schema_alignment_hit(self) -> None:
        scorer = QueryQualityScorer(enable_llm=False)
        score = await scorer.score(
            sql="SELECT * FROM users WHERE name = 'Alice';",
            query="show alice",
            context=_sample_context(),
        )

        alignment = next(d for d in score.dimensions if d.dimension == QualityDimension.SCHEMA_ALIGNMENT)
        assert alignment.score > 0.5

    @pytest.mark.asyncio
    async def test_score_schema_alignment_miss(self) -> None:
        scorer = QueryQualityScorer(enable_llm=False)
        score = await scorer.score(
            sql="SELECT * FROM nonexistent_table;",
            query="show stuff",
            context=_sample_context(),
        )

        alignment = next(d for d in score.dimensions if d.dimension == QualityDimension.SCHEMA_ALIGNMENT)
        assert alignment.score < 1.0

    @pytest.mark.asyncio
    async def test_score_readability_well_formatted(self) -> None:
        scorer = QueryQualityScorer(enable_llm=False)
        score = await scorer.score(
            sql="SELECT u.id, u.name\n  FROM users u\n  WHERE u.email IS NOT NULL\n  ORDER BY u.name;",
            query="list users with email",
            context=_sample_context(),
        )

        readability = next(d for d in score.dimensions if d.dimension == QualityDimension.READABILITY)
        assert readability.score > 0.5

    @pytest.mark.asyncio
    async def test_score_readability_poor(self) -> None:
        scorer = QueryQualityScorer(enable_llm=False)
        score = await scorer.score(
            sql="select*from users",
            query="show users",
            context=_sample_context(),
        )

        readability = next(d for d in score.dimensions if d.dimension == QualityDimension.READABILITY)
        assert readability.score < 0.7

    @pytest.mark.asyncio
    async def test_score_efficiency_select_star_penalty(self) -> None:
        scorer = QueryQualityScorer(enable_llm=False)
        score = await scorer.score(
            sql="SELECT * FROM users",
            query="show users",
            context=_sample_context(),
        )

        efficiency = next(d for d in score.dimensions if d.dimension == QualityDimension.EFFICIENCY)
        assert efficiency.score < 1.0

    @pytest.mark.asyncio
    async def test_score_correctness_table_in_sql(self) -> None:
        scorer = QueryQualityScorer(enable_llm=False)
        score = await scorer.score(
            sql="SELECT name, email FROM users WHERE active = true;",
            query="list active users",
            context=_sample_context(),
        )

        correctness = next(d for d in score.dimensions if d.dimension == QualityDimension.CORRECTNESS)
        assert correctness.score > 0.5

    @pytest.mark.asyncio
    async def test_score_with_intent(self) -> None:
        scorer = QueryQualityScorer(enable_llm=False)
        score = await scorer.score(
            sql="SELECT * FROM users;",
            query="show users",
            intent=_sample_intent(),
            context=_sample_context(),
        )

        assert score.overall > 0.0

    @pytest.mark.asyncio
    async def test_score_with_llm_enabled_and_mock_client(self) -> None:
        mock_client = AsyncMock()
        mock_client.generate.return_value = (
            '{"dimensions": {"correctness": 0.9, "efficiency": 0.7, "safety": 1.0, '
            '"readability": 0.8, "schema_alignment": 0.9}, '
            '"issues": ["missing limit clause"], "suggestion": "add limit 100"}'
        )
        mock_client.model_name = "mock-judge"
        mock_client.cost_per_query = 0.0

        scorer = QueryQualityScorer(llm_client=mock_client, enable_llm=True)
        score = await scorer.score(
            sql="SELECT * FROM users WHERE id = 1;",
            query="show users where id is 1",
            context=_sample_context(),
        )

        assert score.model == "llm+rule"
        assert score.overall > 0.0
        assert len(score.issues) > 0
        assert score.suggestion != ""

    @pytest.mark.asyncio
    async def test_score_with_llm_parse_handles_bad_json(self) -> None:
        mock_client = AsyncMock()
        mock_client.generate.return_value = "not json at all"
        mock_client.model_name = "mock-judge"
        mock_client.cost_per_query = 0.0

        scorer = QueryQualityScorer(llm_client=mock_client, enable_llm=True)
        score = await scorer.score(
            sql="SELECT * FROM users;",
            query="show users",
            context=_sample_context(),
        )

        assert score.model == "rule_based"
        assert score.overall > 0.0

    @pytest.mark.asyncio
    async def test_score_with_llm_handles_exception(self) -> None:
        mock_client = AsyncMock()
        mock_client.generate.side_effect = RuntimeError("LLM unavailable")
        mock_client.model_name = "mock-judge"
        mock_client.cost_per_query = 0.0

        scorer = QueryQualityScorer(llm_client=mock_client, enable_llm=True)
        score = await scorer.score(
            sql="SELECT * FROM users;",
            query="show users",
            context=_sample_context(),
        )

        assert score.model == "rule_based"
        assert score.overall > 0.0

    @pytest.mark.asyncio
    async def test_score_passed_threshold(self) -> None:
        scorer = QueryQualityScorer(enable_llm=False)
        score = await scorer.score(
            sql="SELECT * FROM users WHERE id = 1;",
            query="show users where id is 1",
            context=_sample_context(),
        )

        assert score.passed() is True
        assert score.passed(threshold=0.0) is True

    @pytest.mark.asyncio
    async def test_dimension_score_helper(self) -> None:
        scorer = QueryQualityScorer(enable_llm=False)
        score = await scorer.score(
            sql="SELECT * FROM users;",
            query="show users",
            context=_sample_context(),
        )

        assert score.dimension_score(QualityDimension.CORRECTNESS) > 0.0
        assert score.dimension_score(QualityDimension.SAFETY) >= 0.0
        assert score.dimension_score(QualityDimension.EFFICIENCY) >= 0.0


class TestQualityScorerIntegrationWithPipeline:
    @pytest.mark.asyncio
    async def test_orchestrator_with_quality_enabled(self) -> None:
        from unittest.mock import MagicMock, AsyncMock

        from ke.services.pipeline import PipelineOrchestrator
        from ke.models.planning import QueryType, QueryIntent, TableRef, QueryPlan, PlanStep, PlanOperation, ValidationResult, CostEstimate
        from ke.models.generation import GenerationResult, GenerationStatus
        from ke.models.policy import PolicyChainResult
        from ke.models.execution import ExecutionResult, ExecutionStatus
        from ke.models.quality import QualityScore
        from ke.services.quality_scorer import QueryQualityScorer

        intent = QueryIntent(query_type=QueryType.SIMPLE_SELECT, tables=[TableRef(id="", name="users")])
        intent_agent = MagicMock()
        intent_agent.classify.return_value = intent

        planner = AsyncMock()
        planner.plan.return_value = QueryPlan(
            id="p1", intent=intent,
            steps=[PlanStep(id="s1", step_number=1, operation=PlanOperation.SCAN)],
            validation=ValidationResult(valid=True),
            cost_estimate=CostEstimate(estimated_rows=10, estimated_cost=1.0),
        )

        generator = AsyncMock()
        generator.generate.return_value = GenerationResult(
            id="g1", query="test", sql="SELECT * FROM users",
            status=GenerationStatus.COMPLETED,
            model_tier="standard", model_name="mock",
            intent=intent.model_dump(),
        )

        policy_chain = AsyncMock()
        policy_chain.enforce.return_value = PolicyChainResult(
            passed=True, sql="SELECT * FROM users", sanitized_sql="SELECT * FROM users", layers=[],
        )

        executor = AsyncMock()
        executor.execute.return_value = ExecutionResult(
            id="e1", sql="SELECT * FROM users", status=ExecutionStatus.SUCCESS,
            columns=["id", "name"], rows=[[1, "alice"]], row_count=1, total_rows=1,
        )

        quality_scorer = AsyncMock(spec=QueryQualityScorer)
        quality_scorer.score.return_value = QualityScore(
            overall=0.85,
            model="rule_based",
            latency_ms=5.0,
        )

        orch = PipelineOrchestrator(
            intent_agent=intent_agent,
            planner=planner,
            generator=generator,
            policy_chain=policy_chain,
            executor=executor,
            quality_scorer=quality_scorer,
        )

        result = await orch.execute("show users", context={"tables": [{"name": "users"}], "columns": []})

        assert result.status.value == "success"
        assert quality_scorer.score.called
        assert result.quality_score is not None
        assert result.quality_score.overall == 0.85
        stage_names = [s.name for s in result.stages]
        assert "quality" in stage_names
        quality_stage = next(s for s in result.stages if s.name == "quality")
        assert quality_stage.status == "success"
        assert quality_stage.data["overall"] == 0.85

    @pytest.mark.asyncio
    async def test_orchestrator_without_quality_scorer_skips_stage(self) -> None:
        from unittest.mock import MagicMock, AsyncMock

        from ke.services.pipeline import PipelineOrchestrator
        from ke.models.planning import QueryType, QueryIntent, TableRef, QueryPlan, PlanStep, PlanOperation, ValidationResult, CostEstimate
        from ke.models.generation import GenerationResult, GenerationStatus
        from ke.models.policy import PolicyChainResult
        from ke.models.execution import ExecutionResult, ExecutionStatus

        intent = QueryIntent(query_type=QueryType.SIMPLE_SELECT, tables=[TableRef(id="", name="users")])
        intent_agent = MagicMock()
        intent_agent.classify.return_value = intent

        planner = AsyncMock()
        planner.plan.return_value = QueryPlan(
            id="p1", intent=intent,
            steps=[PlanStep(id="s1", step_number=1, operation=PlanOperation.SCAN)],
            validation=ValidationResult(valid=True),
            cost_estimate=CostEstimate(estimated_rows=10, estimated_cost=1.0),
        )

        generator = AsyncMock()
        generator.generate.return_value = GenerationResult(
            id="g1", query="test", sql="SELECT * FROM users",
            status=GenerationStatus.COMPLETED,
            model_tier="standard", model_name="mock",
            intent=intent.model_dump(),
        )

        policy_chain = AsyncMock()
        policy_chain.enforce.return_value = PolicyChainResult(
            passed=True, sql="SELECT * FROM users", sanitized_sql="SELECT * FROM users", layers=[],
        )

        executor = AsyncMock()
        executor.execute.return_value = ExecutionResult(
            id="e1", sql="SELECT * FROM users", status=ExecutionStatus.SUCCESS,
            columns=["id", "name"], rows=[[1, "alice"]], row_count=1, total_rows=1,
        )

        orch = PipelineOrchestrator(
            intent_agent=intent_agent,
            planner=planner,
            generator=generator,
            policy_chain=policy_chain,
            executor=executor,
        )

        result = await orch.execute("show users", context={"tables": [{"name": "users"}], "columns": []})

        assert result.status.value == "success"
        assert result.quality_score is None
        stage_names = [s.name for s in result.stages]
        assert "quality" not in stage_names
