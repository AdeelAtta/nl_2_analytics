from __future__ import annotations

import time
from typing import Any

from ke.models.policy import PolicyChainResult, PolicyLayerResult
from ke.services.policy.base import PolicyLayerBase
from ke.services.policy.layers import (
    L1IntentClassificationLayer,
    L2SQLSanitizationLayer,
    L3RBACSchemaScopingLayer,
    L4CostCeilingLayer,
    L5SQLValidationLayer,
    L6ReadOnlyEnforcementLayer,
    L7AuditLoggingLayer,
    L8DataClassificationLayer,
    L9AdvancedValidationLayer,
    L10AnomalyDetectionLayer,
)


class PolicyChain:
    def __init__(self, layers: list[PolicyLayerBase] | None = None) -> None:
        self._layers = layers or self._default_layers()

    @staticmethod
    def _default_layers() -> list[PolicyLayerBase]:
        return [
            L1IntentClassificationLayer(),
            L2SQLSanitizationLayer(),
            L3RBACSchemaScopingLayer(),
            L4CostCeilingLayer(),
            L5SQLValidationLayer(),
            L6ReadOnlyEnforcementLayer(),
            L7AuditLoggingLayer(),
            L8DataClassificationLayer(),
            L9AdvancedValidationLayer(),
            L10AnomalyDetectionLayer(),
        ]

    async def enforce(self, sql: str, context: dict[str, Any] | None = None) -> PolicyChainResult:
        start = time.perf_counter()
        all_results: list[PolicyLayerResult] = []
        current_sql = sql
        stopped_at: str | None = None

        for layer in self._layers:
            result = await layer.run(current_sql, context)

            if result.metadata and "sanitized_sql" in result.metadata:
                current_sql = result.metadata["sanitized_sql"]

            all_results.append(result)

            if not result.passed and result.blocked:
                stopped_at = layer.layer_name
                break

        total_ms = (time.perf_counter() - start) * 1000
        passed = stopped_at is None

        return PolicyChainResult(
            passed=passed,
            sql=sql,
            sanitized_sql=current_sql,
            layers=all_results,
            stopped_at=stopped_at,
            total_duration_ms=total_ms,
        )
