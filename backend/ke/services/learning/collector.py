from __future__ import annotations

from typing import Any

from ke.services.learning.validator import FeedbackValidator
from ke.stores.query.repository import (
    QueryFeedbackRepository,
    QueryHistoryRepository,
)


class FeedbackCollectorService:
    def __init__(
        self,
        history_repo: QueryHistoryRepository,
        feedback_repo: QueryFeedbackRepository,
        validator: FeedbackValidator | None = None,
    ) -> None:
        self._history_repo = history_repo
        self._feedback_repo = feedback_repo
        self._validator = validator or FeedbackValidator()

    async def collect_unprocessed(
        self,
        tenant_id: str,
        limit: int = 500,
    ) -> list[dict[str, Any]]:
        items, _ = await self._history_repo.list_by_tenant(
            tenant_id=tenant_id,
        )
        collected: list[dict[str, Any]] = []
        for entry in items:
            if not entry.has_feedback:
                continue
            feedbacks, _ = await self._feedback_repo.list(
                filters={"query_id": entry.id},
            )
            for fb in feedbacks:
                if not self._validator.is_valid(fb):
                    continue
                collected.append({
                    "feedback_id": fb.id,
                    "query_id": entry.id,
                    "user_id": fb.user_id or entry.user_id,
                    "query": entry.query,
                    "sql": entry.sql,
                    "rating": fb.rating,
                    "flag": fb.flag,
                    "comment": fb.comment,
                    "status": entry.status,
                    "tenant_id": tenant_id,
                    "created_at": fb.created_at,
                })
        return collected[:limit]
