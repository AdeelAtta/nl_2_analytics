from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import text

from ke.models.feedback import QueryFeedback, QueryHistory
from ke.stores.query.repository import (
    QueryFeedbackRepository,
    QueryHistoryRepository,
)
from shared.models.pagination import PaginationParams


class QueryHistoryService:
    def __init__(
        self,
        history_repo: QueryHistoryRepository,
        feedback_repo: QueryFeedbackRepository,
    ) -> None:
        self._history_repo = history_repo
        self._feedback_repo = feedback_repo

    async def save(
        self,
        tenant_id: str,
        query: str,
        sql: str,
        status: str,
        duration_ms: float = 0.0,
        model_tier: str = "none",
        model_name: str = "",
        guard_passed: bool = True,
        guard_stopped_at: str | None = None,
        stage_data: list[dict[str, Any]] | None = None,
        user_id: str | None = None,
        session_id: str | None = None,
        database: str = "",
    ) -> dict[str, Any]:
        record_id = str(uuid.uuid4())
        from ke.stores.query.repository import QueryHistoryOrm
        orm = QueryHistoryOrm(
            id=record_id,
            tenant_id=tenant_id,
            database=database,
            user_id=user_id,
            session_id=session_id,
            query=query,
            sql=sql,
            status=status,
            duration_ms=duration_ms,
            model_tier=model_tier,
            model_name=model_name,
            guard_passed=1 if guard_passed else 0,
            guard_stopped_at=guard_stopped_at,
            stage_data=stage_data or [],
        )
        self._history_repo._session.add(orm)
        await self._history_repo._session.flush()
        return {"id": record_id}

    async def list_history(
        self,
        tenant_id: str,
        page: int = 1,
        page_size: int = 50,
        user_id: str | None = None,
        status: str | None = None,
    ) -> tuple[list[QueryHistory], int]:
        pagination = PaginationParams(page=page, page_size=page_size, sort_by="created_at")
        items, total = await self._history_repo.list_by_tenant(
            tenant_id=tenant_id,
            pagination=pagination,
            user_id=user_id,
            status_filter=status,
        )
        return items, total

    async def get_history(self, history_id: str) -> QueryHistory | None:
        return await self._history_repo.get(history_id)

    async def submit_feedback(
        self,
        query_id: str,
        user_id: str | None = None,
        rating: int | None = None,
        flag: str | None = None,
        comment: str = "",
    ) -> QueryFeedback:
        feedback = QueryFeedback(
            id=str(uuid.uuid4()),
            query_id=query_id,
            user_id=user_id,
            rating=rating,
            flag=flag,
            comment=comment,
        )
        result = await self._feedback_repo.create(feedback)
        await self._history_repo.mark_feedback(query_id)
        return result
