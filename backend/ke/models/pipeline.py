from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from shared.models.base import BaseSchema

from ke.models.quality import QualityScore


class PipelineStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    BLOCKED = "blocked"


class PipelineStageResult(BaseSchema):
    model_config = {"frozen": False}

    name: str
    status: str = "success"
    data: dict[str, Any] | None = None
    error: str | None = None
    duration_ms: float = 0.0


class PipelineResult(BaseSchema):
    model_config = {"frozen": False}

    id: str
    query: str
    status: PipelineStatus
    stages: list[PipelineStageResult] = []
    total_duration_ms: float = 0.0
    sql: str = ""
    model_tier: str = "none"
    model_name: str = ""
    guard_passed: bool = True
    guard_stopped_at: str | None = None
    session_id: str = ""
    error: str | None = None
    quality_score: QualityScore | None = None
    created_at: datetime = datetime.now()
