from __future__ import annotations

import datetime

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        validate_default=True,
        str_strip_whitespace=True,
        populate_by_name=True,
    )


class TimestampMixin(BaseModel):
    created_at: datetime.datetime = datetime.datetime.now(datetime.UTC)
    updated_at: datetime.datetime = datetime.datetime.now(datetime.UTC)


class TenantScopedModel(BaseSchema):
    tenant_id: str
