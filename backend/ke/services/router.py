from __future__ import annotations

from ke.models.planning import (
    ModelTier,
    QueryComplexity,
    QueryIntent,
)


class ModelRouter:
    TIER_CONFIGS: dict[ModelTier, dict] = {
        ModelTier.NONE: {
            "provider": "rule_based",
            "model": None,
            "cost_per_query": 0.0,
            "description": "No LLM needed — rule-based processing",
        },
        ModelTier.LIGHTWEIGHT: {
            "provider": "huggingface",
            "model": "meta-llama/Llama-3.1-8B-Instruct",
            "cost_per_query": 0.0001,
            "description": "General-purpose model for SQL queries",
        },
        ModelTier.STANDARD: {
            "provider": "huggingface",
            "model": "meta-llama/Llama-3.1-8B-Instruct",
            "cost_per_query": 0.001,
            "description": "Larger instruct model for complex queries",
        },
        ModelTier.PREMIUM: {
            "provider": "openai",
            "model": "gpt-4o",
            "cost_per_query": 0.01,
            "description": "Premium model for very complex queries",
        },
    }

    ROUTE_RULES: list[tuple[QueryComplexity, ModelTier]] = [
        (QueryComplexity.SIMPLE, ModelTier.LIGHTWEIGHT),
        (QueryComplexity.MEDIUM, ModelTier.LIGHTWEIGHT),
        (QueryComplexity.COMPLEX, ModelTier.STANDARD),
        (QueryComplexity.VERY_COMPLEX, ModelTier.PREMIUM),
    ]

    def route(self, intent: QueryIntent, tenant_tier: str = "pro") -> dict:
        base_tier = intent.model_tier
        if not isinstance(base_tier, ModelTier):
            base_tier = ModelTier(base_tier) if isinstance(base_tier, str) else ModelTier.NONE

        tier = self._apply_tenant_overrides(base_tier, tenant_tier)
        config = self.TIER_CONFIGS.get(tier, self.TIER_CONFIGS[ModelTier.NONE])

        fallback_chain = self._build_fallback_chain(tier)

        return {
            "selected_tier": tier.value,
            "config": config,
            "fallback_chain": [t.value for t in fallback_chain],
            "tenant_tier": tenant_tier,
        }

    def _apply_tenant_overrides(self, base_tier: ModelTier, tenant_tier: str) -> ModelTier:
        max_tiers = {
            "free": ModelTier.LIGHTWEIGHT,
            "starter": ModelTier.LIGHTWEIGHT,
            "pro": ModelTier.STANDARD,
            "enterprise": ModelTier.PREMIUM,
        }
        max_tier = max_tiers.get(tenant_tier, ModelTier.STANDARD)
        tier_values = list(ModelTier)
        if tier_values.index(base_tier) > tier_values.index(max_tier):
            return max_tier
        return base_tier

    def _build_fallback_chain(self, tier: ModelTier) -> list[ModelTier]:
        tiers = list(ModelTier)
        idx = tiers.index(tier)
        return tiers[: idx + 1]

    def estimate_cost(self, intent: QueryIntent, tenant_tier: str = "pro") -> float:
        route = self.route(intent, tenant_tier)
        return route["config"]["cost_per_query"]
