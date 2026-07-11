from __future__ import annotations

from typing import Any

from sqlalchemy import Column as SAColumn
from sqlalchemy import DateTime, Float, Integer, String, Text, func, select
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from ke.models.feedback import QueryFeedback, QueryHistory
from ke.stores.schema.repository import BaseRepository
from shared.models.pagination import PaginationParams


class QueryBase(DeclarativeBase):
    pass


class QueryHistoryOrm(QueryBase):
    __tablename__ = "query_history"
    __table_args__ = {"schema": "query_store"}

    id = SAColumn(PG_UUID(), primary_key=True)
    tenant_id = SAColumn(String(64), nullable=False)
    user_id = SAColumn(String(64), nullable=True)
    session_id = SAColumn(String(64), nullable=True)
    query = SAColumn(Text(), nullable=False)
    sql = SAColumn(Text(), nullable=False, server_default="")
    status = SAColumn(String(16), nullable=False)
    duration_ms = SAColumn(Float(), nullable=False, server_default="0")
    model_tier = SAColumn(String(32), nullable=False, server_default="none")
    model_name = SAColumn(String(128), nullable=False, server_default="")
    guard_passed = SAColumn(Integer(), nullable=False, server_default="1")
    guard_stopped_at = SAColumn(String(64), nullable=True)
    stage_data = SAColumn(JSONB(), nullable=False, server_default="'[]'::jsonb")
    has_feedback = SAColumn(Integer(), nullable=False, server_default="0")
    created_at = SAColumn(DateTime(timezone=True), nullable=False, server_default=func.now())


class QueryFeedbackOrm(QueryBase):
    __tablename__ = "query_feedback"
    __table_args__ = {"schema": "query_store"}

    id = SAColumn(PG_UUID(), primary_key=True)
    query_id = SAColumn(PG_UUID(), nullable=False)
    user_id = SAColumn(String(64), nullable=True)
    rating = SAColumn(Integer(), nullable=True)
    flag = SAColumn(String(32), nullable=True)
    comment = SAColumn(Text(), nullable=False, server_default="")
    created_at = SAColumn(DateTime(timezone=True), nullable=False, server_default=func.now())


class QueryHistoryRepository(BaseRepository[QueryHistory]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, QueryHistoryOrm, QueryHistory)

    async def list_by_tenant(
        self,
        tenant_id: str,
        pagination: PaginationParams | None = None,
        user_id: str | None = None,
        status_filter: str | None = None,
    ) -> tuple[list[QueryHistory], int]:
        filters: dict[str, Any] = {"tenant_id": tenant_id}
        if user_id:
            filters["user_id"] = user_id
        if status_filter:
            filters["status"] = status_filter
        return await self.list(filters=filters, pagination=pagination)

    async def mark_feedback(self, query_id: str) -> None:
        stmt = (
            select(QueryHistoryOrm)
            .where(QueryHistoryOrm.id == query_id)
        )
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        if orm:
            orm.has_feedback = 1
            await self._session.flush()


class QueryFeedbackRepository(BaseRepository[QueryFeedback]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, QueryFeedbackOrm, QueryFeedback)
