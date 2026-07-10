from __future__ import annotations

import enum
import math

from pydantic import Field

from shared.models.base import BaseSchema


class SortOrder(enum.StrEnum):
    ASC = "asc"
    DESC = "desc"


class PaginationParams(BaseSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=500)
    sort_by: str | None = None
    sort_order: SortOrder = SortOrder.ASC

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


class Page(BaseSchema):
    items: list[object]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=500)

    @property
    def total_pages(self) -> int:
        return max(1, math.ceil(self.total / self.page_size)) if self.total > 0 else 1

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @property
    def has_prev(self) -> bool:
        return self.page > 1
