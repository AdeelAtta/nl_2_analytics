from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    checks: dict[str, Any] | None = None


class VersionInfo(BaseModel):
    version: str
    build: str = "development"
    environment: str


class ProblemDetail(BaseModel):
    type: str = Field(default="about:blank", alias="type")
    title: str
    status: int
    detail: str
    instance: str
