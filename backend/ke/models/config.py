from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from shared.models.base import BaseSchema


class ConfigEntry(BaseSchema):
    id: str
    tenant_id: str | None = None
    key: str
    value: Any
    description: str = ""
    created_at: datetime = datetime.now(UTC)
    updated_at: datetime = datetime.now(UTC)
