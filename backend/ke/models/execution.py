from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from shared.models.base import BaseSchema


class ExecutionStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    DRY_RUN = "dry_run"


class ExecutionError(BaseSchema):
    model_config = {"frozen": False}

    code: str
    message: str
    detail: str = ""


class ExecutionResult(BaseSchema):
    model_config = {"frozen": False}

    id: str
    sql: str
    status: ExecutionStatus
    columns: list[str] = []
    rows: list[list[Any]] = []
    row_count: int = 0
    total_rows: int = 0
    truncated: bool = False
    page: int = 1
    page_size: int = 1000
    duration_ms: float = 0.0
    error: ExecutionError | None = None
    explain_output: list[dict[str, Any]] | None = None
    timestamp: datetime = datetime.now()
