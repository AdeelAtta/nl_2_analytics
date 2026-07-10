from __future__ import annotations

from typing import Any, TypeVar

from pydantic import Field

from shared.models.base import BaseSchema
from shared.models.pagination import Page

T = TypeVar("T")


class MetaInfo(BaseSchema):
    request_id: str = ""
    took_ms: float = 0.0
    api_version: str = "1.0.0"
    pagination: Page | None = None


class ErrorDetail(BaseSchema):
    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)
    request_id: str = ""
    docs_url: str = ""


class ErrorResponse(BaseSchema):
    status: str = "error"
    error: ErrorDetail


class APIResponse[T](BaseSchema):
    status: str = "ok"
    data: T
    meta: MetaInfo = Field(default_factory=MetaInfo)
