from __future__ import annotations

import pytest

from ke.models.planning import (
    PlanOperation,
    QueryComplexity,
    QueryIntent,
    QueryType,
)
from ke.services.intent import IntentAgent
from ke.services.planner import QueryPlanner


@pytest.fixture
def planner() -> QueryPlanner:
    return QueryPlanner(intent_agent=IntentAgent())


class TestQueryPlanner:
    async def test_create_simple_plan(self, planner: QueryPlanner) -> None:
        intent = QueryIntent(
            query_type=QueryType.SIMPLE_SELECT,
            complexity=QueryComplexity.SIMPLE,
            tables=[{"id": "t1", "name": "customers"}],
        )
        plan = await planner.create_plan("Show all customers", intent)
        assert plan.id
        assert len(plan.steps) >= 1
        assert plan.steps[0].operation == PlanOperation.SCAN

    async def test_plan_with_tables(self, planner: QueryPlanner) -> None:
        intent = QueryIntent(
            query_type=QueryType.SIMPLE_SELECT,
            complexity=QueryComplexity.SIMPLE,
            tables=[
                {"id": "t1", "name": "customers"},
            ],
            filters=[],
            join_edges=[],
            aggregations=[],
        )
        plan = await planner.create_plan("Show customers", intent)
        assert len(plan.steps) == 1
        assert plan.steps[0].tables[0].name == "customers"

    async def test_plan_with_join(self, planner: QueryPlanner) -> None:
        intent = QueryIntent(
            query_type=QueryType.JOIN,
            complexity=QueryComplexity.MEDIUM,
            tables=[
                {"id": "t1", "name": "orders"},
                {"id": "t2", "name": "customers"},
            ],
            join_edges=[
                {
                    "source_table": "orders",
                    "source_column": "customer_id",
                    "target_table": "customers",
                    "target_column": "id",
                },
            ],
            filters=[],
            aggregations=[],
        )
        plan = await planner.create_plan("Show orders with customers", intent)
        operations = [s.operation for s in plan.steps]
        assert PlanOperation.JOIN in operations

    async def test_plan_with_aggregation(self, planner: QueryPlanner) -> None:
        intent = QueryIntent(
            query_type=QueryType.AGGREGATION,
            complexity=QueryComplexity.SIMPLE,
            tables=[{"id": "t1", "name": "sales"}],
            aggregations=[
                {"function": "SUM", "column": "amount"},
                {"function": "COUNT", "column": "id"},
            ],
            filters=[],
            join_edges=[],
        )
        plan = await planner.create_plan("Total sales", intent)
        operations = [s.operation for s in plan.steps]
        assert PlanOperation.AGGREGATE in operations
        agg_step = next(s for s in plan.steps if s.operation == PlanOperation.AGGREGATE)
        assert len(agg_step.aggregations) == 2

    async def test_plan_with_filters(self, planner: QueryPlanner) -> None:
        intent = QueryIntent(
            query_type=QueryType.FILTERED_SELECT,
            complexity=QueryComplexity.SIMPLE,
            tables=[{"id": "t1", "name": "orders"}],
            filters=[
                {
                    "column": {"table": "orders", "column": "created_at"},
                    "operator": ">",
                    "value": "2024-01-01",
                },
            ],
            join_edges=[],
            aggregations=[],
        )
        plan = await planner.create_plan("Orders from 2024", intent)
        operations = [s.operation for s in plan.steps]
        assert PlanOperation.FILTER in operations

    async def test_plan_validates_successfully(self, planner: QueryPlanner) -> None:
        intent = IntentAgent().classify("Show all customers")
        plan = await planner.create_plan("Show all customers", intent)
        assert plan.validation.valid is True

    async def test_plan_detects_ddl_error(self, planner: QueryPlanner) -> None:
        intent = IntentAgent().classify("Create a table")
        plan = await planner.create_plan("Create a table", intent)
        assert plan.validation.valid is False
        assert any("DDL" in e.message for e in plan.validation.errors)

    async def test_plan_detects_unknown_error(self, planner: QueryPlanner) -> None:
        intent = IntentAgent().classify("")
        plan = await planner.create_plan("", intent)
        assert plan.validation.valid is False

    async def test_cost_estimate(self, planner: QueryPlanner) -> None:
        intent = QueryIntent(
            query_type=QueryType.JOIN,
            complexity=QueryComplexity.MEDIUM,
            tables=[
                {"id": "t1", "name": "orders"},
                {"id": "t2", "name": "customers"},
            ],
            join_edges=[
                {
                    "source_table": "orders",
                    "source_column": "customer_id",
                    "target_table": "customers",
                    "target_column": "id",
                },
            ],
            filters=[],
            aggregations=[],
        )
        plan = await planner.create_plan("Join", intent)
        assert plan.cost_estimate.estimated_cost > 0
        assert plan.cost_estimate.estimated_rows > 0

    async def test_plan_metadata(self, planner: QueryPlanner) -> None:
        intent = IntentAgent().classify("Total sales by region")
        plan = await planner.create_plan("Total sales by region", intent)
        assert "query" in plan.metadata
        assert "table_count" in plan.metadata
        assert "step_count" in plan.metadata
