from __future__ import annotations

from datetime import datetime
from typing import Any

from shared.models.base import BaseSchema


class PolicyLayerResult(BaseSchema):
    model_config = {"frozen": False}

    layer_name: str = ""
    layer_number: int = 0
    passed: bool = True
    reason: str = ""
    blocked: bool = False
    metadata: dict[str, Any] = {}
    duration_ms: float = 0.0


class PolicyChainResult(BaseSchema):
    model_config = {"frozen": False}

    passed: bool = True
    sql: str = ""
    sanitized_sql: str = ""
    layers: list[PolicyLayerResult] = []
    stopped_at: str | None = None
    total_duration_ms: float = 0.0
    timestamp: datetime = datetime.now()
