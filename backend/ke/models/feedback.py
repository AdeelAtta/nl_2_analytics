from __future__ import annotations

from datetime import datetime
from typing import Any

from shared.models.base import BaseSchema


class QueryHistory(BaseSchema):
    model_config = {"from_attributes": True, "frozen": False}

    id: Any = ""
    tenant_id: str
    database: str = ""
    user_id: str | None = None
    session_id: str | None = None
    query: str
    sql: str = ""
    status: str = ""
    duration_ms: float = 0.0
    model_tier: str = "none"
    model_name: str = ""
    guard_passed: bool = True
    guard_stopped_at: str | None = None
    stage_data: list[dict[str, Any]] = []
    has_feedback: bool = False
    created_at: datetime = datetime.now()


class QueryFeedback(BaseSchema):
    model_config = {"from_attributes": True, "frozen": False}

    id: str
    query_id: str
    user_id: str | None = None
    rating: int | None = None
    flag: str | None = None
    comment: str = ""
    created_at: datetime = datetime.now()
