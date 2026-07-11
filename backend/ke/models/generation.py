from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from shared.models.base import BaseSchema


class GenerationStatus(str, Enum):
    PENDING = "pending"
    GENERATING = "generating"
    REFLECTING = "reflecting"
    COMPLETED = "completed"
    FAILED = "failed"


class CandidateResult(BaseSchema):
    model_config = {"frozen": False}

    sql: str
    model_tier: str
    model_name: str
    score: float = 0.0
    latency_ms: float = 0.0
    cost: float = 0.0


class ReflectionResult(BaseSchema):
    model_config = {"frozen": False}

    is_valid: bool
    issues: list[str] = []
    suggestion: str = ""


class GenerationResult(BaseSchema):
    model_config = {"frozen": False}

    id: str
    query: str
    sql: str
    status: GenerationStatus
    model_tier: str
    model_name: str
    intent: dict[str, Any] | None = None
    candidates: list[CandidateResult] = []
    reflection: ReflectionResult | None = None
    latency_ms: float = 0.0
    cost: float = 0.0
    error: str | None = None
    created_at: datetime = datetime.now()
