from __future__ import annotations

import pytest

from ke.models.planning import (
    ModelTier,
    QueryComplexity,
    QueryIntent,
    QueryType,
)
from ke.services.router import ModelRouter


@pytest.fixture
def router() -> ModelRouter:
    return ModelRouter()


@pytest.fixture
def simple_intent() -> QueryIntent:
    return QueryIntent(
        query_type=QueryType.SIMPLE_SELECT,
        complexity=QueryComplexity.SIMPLE,
        model_tier=ModelTier.NONE,
    )


@pytest.fixture
def medium_intent() -> QueryIntent:
    return QueryIntent(
        query_type=QueryType.JOIN,
        complexity=QueryComplexity.MEDIUM,
        model_tier=ModelTier.LIGHTWEIGHT,
    )


@pytest.fixture
def complex_intent() -> QueryIntent:
    return QueryIntent(
        query_type=QueryType.COMPOUND,
        complexity=QueryComplexity.COMPLEX,
        model_tier=ModelTier.STANDARD,
    )


class TestModelRouter:
    def test_route_simple(self, router: ModelRouter, simple_intent: QueryIntent) -> None:
        result = router.route(simple_intent)
        assert result["selected_tier"] == "none"
        assert result["config"]["provider"] == "rule_based"

    def test_route_medium(self, router: ModelRouter, medium_intent: QueryIntent) -> None:
        result = router.route(medium_intent)
        assert result["selected_tier"] == "lightweight"
        assert result["config"]["model"] == "meta-llama/Llama-3.1-8B-Instruct"

    def test_route_complex(self, router: ModelRouter, complex_intent: QueryIntent) -> None:
        result = router.route(complex_intent)
        assert result["selected_tier"] == "standard"
        assert result["config"]["model"] == "meta-llama/Llama-3.1-8B-Instruct"

    def test_route_tenant_free_caps_to_lightweight(
        self, router: ModelRouter, complex_intent: QueryIntent
    ) -> None:
        result = router.route(complex_intent, tenant_tier="free")
        assert result["selected_tier"] == "lightweight"

    def test_route_tenant_starter_caps_to_lightweight(
        self, router: ModelRouter, complex_intent: QueryIntent
    ) -> None:
        result = router.route(complex_intent, tenant_tier="starter")
        assert result["selected_tier"] == "lightweight"

    def test_route_tenant_pro_allows_standard(
        self, router: ModelRouter, complex_intent: QueryIntent
    ) -> None:
        result = router.route(complex_intent, tenant_tier="pro")
        assert result["selected_tier"] == "standard"

    def test_route_tenant_enterprise_allows_premium(self, router: ModelRouter) -> None:
        intent = QueryIntent(
            query_type=QueryType.CROSS_DB,
            complexity=QueryComplexity.VERY_COMPLEX,
            model_tier=ModelTier.PREMIUM,
        )
        result = router.route(intent, tenant_tier="enterprise")
        assert result["selected_tier"] == "premium"

    def test_fallback_chain(self, router: ModelRouter, complex_intent: QueryIntent) -> None:
        result = router.route(complex_intent)
        assert "none" in result["fallback_chain"]
        assert "lightweight" in result["fallback_chain"]
        assert "standard" in result["fallback_chain"]

    def test_estimate_cost_simple(self, router: ModelRouter, simple_intent: QueryIntent) -> None:
        cost = router.estimate_cost(simple_intent)
        assert cost == 0.0

    def test_estimate_cost_complex(self, router: ModelRouter, complex_intent: QueryIntent) -> None:
        cost = router.estimate_cost(complex_intent)
        assert cost > 0.0

    def test_tier_configs_have_all_keys(self, router: ModelRouter) -> None:
        for tier, config in router.TIER_CONFIGS.items():
            assert "provider" in config
            assert "cost_per_query" in config
            assert "description" in config
