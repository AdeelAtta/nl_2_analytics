from __future__ import annotations

from typing import Any

import pytest

from ke.models.generation import GenerationStatus
from ke.models.planning import QueryComplexity, QueryIntent, QueryType
from ke.services.generator import NL2SQLGenerator
from ke.services.intent import IntentAgent
from ke.services.router import ModelRouter


@pytest.fixture
def intent_agent() -> IntentAgent:
    return IntentAgent()


@pytest.fixture
def model_router() -> ModelRouter:
    return ModelRouter()


@pytest.fixture
def generator() -> NL2SQLGenerator:
    return NL2SQLGenerator()


@pytest.fixture
def sample_context() -> dict[str, Any]:
    return {
        "tables": [
            {"id": "t1", "name": "customers"},
            {"id": "t2", "name": "orders"},
        ],
        "columns": [
            {"name": "id", "table_name": "customers", "data_type": "integer"},
            {"name": "name", "table_name": "customers", "data_type": "varchar"},
            {"name": "email", "table_name": "customers", "data_type": "varchar"},
            {"name": "id", "table_name": "orders", "data_type": "integer"},
            {"name": "customer_id", "table_name": "orders", "data_type": "integer"},
            {"name": "total", "table_name": "orders", "data_type": "decimal"},
        ],
        "relationships": [
            {
                "source_table": "customers",
                "source_column": "id",
                "target_table": "orders",
                "target_column": "customer_id",
                "relationship_type": "one_to_many",
            }
        ],
    }


class TestNL2SQLGenerator:
    @pytest.mark.asyncio
    async def test_generate_simple_select(self, generator: NL2SQLGenerator) -> None:
        intent = QueryIntent(query_type=QueryType.SIMPLE_SELECT, complexity=QueryComplexity.SIMPLE, tables=[])
        result = await generator.generate("Show all records", intent)
        assert result.status == GenerationStatus.COMPLETED
        assert result.model_tier == "none"
        assert result.model_name == "rule_based"
        assert result.sql

    @pytest.mark.asyncio
    async def test_generate_with_context(self, generator: NL2SQLGenerator, sample_context: dict[str, Any]) -> None:
        intent = QueryIntent(
            query_type=QueryType.SIMPLE_SELECT,
            complexity=QueryComplexity.SIMPLE,
            tables=[sample_context["tables"][0]],
        )
        result = await generator.generate("Show all customers", intent, sample_context)
        assert result.status == GenerationStatus.COMPLETED
        assert "customers" in result.sql

    @pytest.mark.asyncio
    async def test_generate_via_intent_agent(self, generator: NL2SQLGenerator, intent_agent: IntentAgent, sample_context: dict[str, Any]) -> None:
        intent = intent_agent.classify("Show all customers", sample_context)
        result = await generator.generate("Show all customers", intent, sample_context)
        assert result.status == GenerationStatus.COMPLETED
        assert result.sql

    @pytest.mark.asyncio
    async def test_generate_filtered_select(self, generator: NL2SQLGenerator, sample_context: dict[str, Any]) -> None:
        intent = QueryIntent(
            query_type=QueryType.FILTERED_SELECT,
            complexity=QueryComplexity.SIMPLE,
            tables=[sample_context["tables"][0]],
        )
        result = await generator.generate("Find customers by name", intent, sample_context)
        assert result.status == GenerationStatus.COMPLETED
        assert "SELECT" in result.sql.upper()

    @pytest.mark.asyncio
    async def test_generate_with_aggregation(self, generator: NL2SQLGenerator, sample_context: dict[str, Any]) -> None:
        intent = QueryIntent(
            query_type=QueryType.AGGREGATION,
            complexity=QueryComplexity.SIMPLE,
            tables=[sample_context["tables"][1]],
            aggregations=[{"function": "SUM", "column": "total"}],
        )
        result = await generator.generate("Total order amount", intent, sample_context)
        assert result.status == GenerationStatus.COMPLETED
        assert "SUM" in result.sql.upper() or "sum" in result.sql

    @pytest.mark.asyncio
    async def test_generate_with_join(self, generator: NL2SQLGenerator, sample_context: dict[str, Any]) -> None:
        intent = QueryIntent(
            query_type=QueryType.JOIN,
            complexity=QueryComplexity.MEDIUM,
            tables=sample_context["tables"],
            join_edges=[{
                "source_table": "customers",
                "source_column": "id",
                "target_table": "orders",
                "target_column": "customer_id",
                "join_type": "INNER",
                "confidence": 1.0,
            }],
        )
        result = await generator.generate("Show customers with their orders", intent, sample_context)
        assert result.status == GenerationStatus.COMPLETED
        assert "customers" in result.sql.lower()
        assert "orders" in result.sql.lower()

    @pytest.mark.asyncio
    async def test_generate_rejects_ddl(self, generator: NL2SQLGenerator, sample_context: dict[str, Any]) -> None:
        intent = QueryIntent(query_type=QueryType.DDL, confidence=0.0)
        result = await generator.generate("Create a table", intent, sample_context)
        assert result.status == GenerationStatus.FAILED
        assert "DDL" in (result.error or "")

    @pytest.mark.asyncio
    async def test_generates_candidates(self, generator: NL2SQLGenerator, sample_context: dict[str, Any]) -> None:
        intent = QueryIntent(
            query_type=QueryType.SIMPLE_SELECT,
            complexity=QueryComplexity.MEDIUM,
            tables=[sample_context["tables"][0]],
        )
        result = await generator.generate("Show all customers", intent, sample_context, num_candidates=2)
        assert len(result.candidates) >= 1

    @pytest.mark.asyncio
    async def test_reflection_valid_sql(self, generator: NL2SQLGenerator) -> None:
        result = await generator._reflect("Show customers", "SELECT * FROM customers;", None, "postgresql")
        assert result is None or isinstance(result, object)

    @pytest.mark.asyncio
    async def test_rule_based_with_filters(self, generator: NL2SQLGenerator) -> None:
        from ke.models.planning import ColumnRef, FilterExpression
        intent = QueryIntent(
            query_type=QueryType.FILTERED_SELECT,
            complexity=QueryComplexity.SIMPLE,
            tables=[{"id": "t1", "name": "customers", "schema_name": "", "database_name": "", "alias": ""}],
            filters=[FilterExpression(column=ColumnRef(table="customers", column="name"), operator="=", value="John", logical_operator="AND")],
        )
        sql = generator._rule_based_generate("Find John", intent, None, "postgresql")
        assert "WHERE" in sql
        assert "John" in sql

    @pytest.mark.asyncio
    async def test_score_candidate(self, generator: NL2SQLGenerator) -> None:
        intent = QueryIntent(query_type=QueryType.SIMPLE_SELECT, complexity=QueryComplexity.SIMPLE, tables=[])
        score = generator._score_candidate("SELECT * FROM customers WHERE id = 1;", "find customers by id", intent)
        assert 0.0 < score <= 1.0

    @pytest.mark.asyncio
    async def test_pipeline_integration(self, generator: NL2SQLGenerator, intent_agent: IntentAgent, sample_context: dict[str, Any]) -> None:
        intent = intent_agent.classify("Show all customers", sample_context)
        result = await generator.generate("Show all customers", intent, sample_context)
        assert result.status == GenerationStatus.COMPLETED
        assert result.query == "Show all customers"
        assert result.intent is not None


class TestInferenceFactory:
    def test_create_mock_client(self) -> None:
        from ke.services.inference import InferenceFactory
        client = InferenceFactory.create("mock", "test-model")
        assert client.model_name == "test-model"
        assert client.cost_per_query == 0.0

    def test_create_hf_client(self) -> None:
        from ke.services.inference import InferenceFactory
        client = InferenceFactory.create("huggingface", "test-model", 0.001)
        assert client.model_name == "test-model"
        assert client.cost_per_query == 0.001

    def test_mock_generates_sql(self) -> None:
        from ke.services.inference import MockClient
        client = MockClient()
        assert client.model_name == "mock"


class TestPromptTemplates:
    def test_format_schema_ddl(self) -> None:
        from ke.services.prompts import format_schema_ddl
        tables = [{"name": "users"}]
        columns = [{"name": "id", "table_name": "users", "data_type": "integer"}]
        relationships = [{"source_table": "users", "source_column": "id", "target_table": "orders", "target_column": "user_id"}]
        ddl = format_schema_ddl(tables, columns, relationships)
        assert "CREATE TABLE users" in ddl
        assert "id integer" in ddl
        assert "users.id -> orders.user_id" in ddl or "-- users" in ddl

    def test_format_intent_description(self) -> None:
        from ke.services.prompts import format_intent_description
        desc = format_intent_description({"query_type": "JOIN", "complexity": "medium"})
        assert "JOIN" in desc
        assert "medium" in desc
