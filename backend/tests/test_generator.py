from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from ke.models.generation import GenerationResult, GenerationStatus
from ke.models.planning import ModelTier, QueryComplexity, QueryIntent, QueryType
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
            {"source_table": "orders", "source_column": "customer_id",
             "target_table": "customers", "target_column": "id"},
        ],
    }


class TestNL2SQLGenerator:
    @pytest.mark.asyncio
    async def test_generate_simple_select(self, generator: NL2SQLGenerator) -> None:
        intent = QueryIntent(query_type=QueryType.SIMPLE_SELECT, complexity=QueryComplexity.SIMPLE, tables=[], model_tier=ModelTier.LIGHTWEIGHT)
        with patch("ke.services.generator.InferenceFactory.create") as mock_create:
            mock_client = AsyncMock()
            mock_client.generate.return_value = "SELECT * FROM customers;"
            mock_client.model_name = "mock"
            mock_client.cost_per_query = 0.0
            mock_create.return_value = mock_client

            result = await generator.generate("Show all records", intent)
            assert result.status == GenerationStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_generate_with_context(self, generator: NL2SQLGenerator, sample_context: dict[str, Any]) -> None:
        intent = QueryIntent(
            query_type=QueryType.SIMPLE_SELECT,
            complexity=QueryComplexity.SIMPLE,
            tables=[sample_context["tables"][0]],
            model_tier=ModelTier.LIGHTWEIGHT,
        )
        with patch("ke.services.generator.InferenceFactory.create") as mock_create:
            mock_client = AsyncMock()
            mock_client.generate.return_value = "SELECT * FROM customers;"
            mock_client.model_name = "mock"
            mock_client.cost_per_query = 0.0
            mock_create.return_value = mock_client

            result = await generator.generate("Show all customers", intent, sample_context)
            assert result.status == GenerationStatus.COMPLETED
            assert "customers" in result.sql

    @pytest.mark.asyncio
    async def test_generate_via_intent_agent(self, generator: NL2SQLGenerator, intent_agent: IntentAgent, sample_context: dict[str, Any]) -> None:
        intent = intent_agent.classify("Show all customers", sample_context)
        with patch("ke.services.generator.InferenceFactory.create") as mock_create:
            mock_client = AsyncMock()
            mock_client.generate.return_value = "SELECT * FROM customers;"
            mock_client.model_name = "mock"
            mock_client.cost_per_query = 0.0
            mock_create.return_value = mock_client

            result = await generator.generate("Show all customers", intent, sample_context)
            assert result.status == GenerationStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_generate_fails_without_llm(self, generator: NL2SQLGenerator) -> None:
        intent = QueryIntent(query_type=QueryType.SIMPLE_SELECT, complexity=QueryComplexity.SIMPLE, tables=[], model_tier=ModelTier.LIGHTWEIGHT)
        with patch("ke.services.generator.InferenceFactory.create") as mock_create:
            mock_create.side_effect = RuntimeError("No LLM configured")

            result = await generator.generate("Show all records", intent)
            assert result.status == GenerationStatus.FAILED

    @pytest.mark.asyncio
    async def test_generate_with_filters(self, generator: NL2SQLGenerator, sample_context: dict[str, Any]) -> None:
        from ke.models.planning import ColumnRef, FilterExpression

        intent = QueryIntent(
            query_type=QueryType.FILTERED_SELECT,
            complexity=QueryComplexity.SIMPLE,
            tables=[sample_context["tables"][0]],
            model_tier=ModelTier.LIGHTWEIGHT,
            filters=[FilterExpression(column=ColumnRef(table="customers", column="email"), operator="=", value="test@test.com")],
        )
        with patch("ke.services.generator.InferenceFactory.create") as mock_create:
            mock_client = AsyncMock()
            mock_client.generate.return_value = "SELECT * FROM customers WHERE email = 'test@test.com';"
            mock_client.model_name = "mock"
            mock_client.cost_per_query = 0.0
            mock_create.return_value = mock_client

            result = await generator.generate("Find by email", intent, sample_context)
            assert result.status == GenerationStatus.COMPLETED
