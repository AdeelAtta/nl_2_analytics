from __future__ import annotations

import pytest

from ke.models.planning import (
    QueryComplexity,
    QueryType,
)
from ke.services.intent import IntentAgent


@pytest.fixture
def agent() -> IntentAgent:
    return IntentAgent()


class TestIntentAgent:
    def test_classify_simple_select(self, agent: IntentAgent) -> None:
        intent = agent.classify("Show all customers")
        assert intent.query_type == QueryType.SIMPLE_SELECT
        assert intent.complexity == QueryComplexity.SIMPLE

    def test_classify_filtered_select(self, agent: IntentAgent) -> None:
        intent = agent.classify("Find customers from New York")
        assert intent.query_type == QueryType.FILTERED_SELECT
        assert intent.complexity == QueryComplexity.SIMPLE

    def test_classify_aggregation(self, agent: IntentAgent) -> None:
        intent = agent.classify("Total sales by region")
        assert intent.query_type == QueryType.AGGREGATION
        assert intent.complexity == QueryComplexity.SIMPLE

    def test_classify_aggregation_avg(self, agent: IntentAgent) -> None:
        intent = agent.classify("Average order value per customer")
        assert intent.query_type == QueryType.AGGREGATION

    def test_classify_aggregation_count(self, agent: IntentAgent) -> None:
        intent = agent.classify("Count of orders by status")
        assert intent.query_type == QueryType.AGGREGATION

    def test_classify_join(self, agent: IntentAgent) -> None:
        intent = agent.classify("join orders and customers")
        assert intent.query_type == QueryType.JOIN

    def test_classify_window_rank(self, agent: IntentAgent) -> None:
        intent = agent.classify("Rank employees by salary")
        assert intent.query_type == QueryType.WINDOW

    def test_classify_window_top_n(self, agent: IntentAgent) -> None:
        intent = agent.classify("Top 10 products by revenue")
        assert intent.query_type == QueryType.WINDOW

    def test_classify_ddl_rejected(self, agent: IntentAgent) -> None:
        intent = agent.classify("Create a table named users")
        assert intent.query_type == QueryType.DDL
        assert intent.confidence == 0.0

    def test_classify_compound(self, agent: IntentAgent) -> None:
        intent = agent.classify("Compare Q1 sales vs Q2 sales")
        assert intent.query_type == QueryType.COMPOUND

    def test_classify_subquery(self, agent: IntentAgent) -> None:
        intent = agent.classify("Customers who have placed more than 5 orders")
        assert intent.query_type == QueryType.SUBQUERY

    def test_complexity_with_context(self, agent: IntentAgent) -> None:
        intent = agent.classify("Show all data", None)
        assert intent.query_type == QueryType.SIMPLE_SELECT

    def test_complexity_increases_with_tables(self, agent: IntentAgent) -> None:
        context = {
            "tables": [
                {"id": "t1", "name": "users"},
                {"id": "t2", "name": "orders"},
                {"id": "t3", "name": "products"},
                {"id": "t4", "name": "categories"},
                {"id": "t5", "name": "reviews"},
            ],
            "columns": [],
            "relationships": [],
        }
        intent = agent.classify("Show users orders products categories reviews", context)
        assert intent.query_type == QueryType.JOIN
        assert intent.complexity == QueryComplexity.COMPLEX

    def test_model_tier_simple(self, agent: IntentAgent) -> None:
        intent = agent.classify("Show all customers")
        assert intent.model_tier == "lightweight"

    def test_model_tier_medium(self, agent: IntentAgent) -> None:
        intent = agent.classify("Show me customers who made orders")
        assert intent.model_tier == "lightweight"

    def test_model_tier_complex(self, agent: IntentAgent) -> None:
        context = {
            "tables": [
                {"id": "t1", "name": "orders"},
                {"id": "t2", "name": "customers"},
                {"id": "t3", "name": "products"},
                {"id": "t4", "name": "categories"},
                {"id": "t5", "name": "reviews"},
            ],
        }
        intent = agent.classify("Rank products by sales within each category compared to last year", context)
        assert intent.model_tier in ("standard", "premium")

    def test_unknown_query(self, agent: IntentAgent) -> None:
        intent = agent.classify("")
        assert intent.query_type == QueryType.UNKNOWN
        assert intent.confidence == 0.0

    def test_extract_aggregations(self, agent: IntentAgent) -> None:
        intent = agent.classify("Total sales and average price by region")
        assert len(intent.aggregations) >= 1
        funcs = {a["function"] for a in intent.aggregations}
        assert "SUM" in funcs or "AVG" in funcs

    def test_analytical_detected(self, agent: IntentAgent) -> None:
        intent = agent.classify("Show sales growth trend by quarter")
        assert intent.query_type == QueryType.ANALYTICAL
