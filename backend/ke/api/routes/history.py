from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from ke.api.schemas import error_response, success_response
from ke.models.feedback import QueryFeedback, QueryHistory
from ke.services.history import QueryHistoryService
from ke.stores.query.repository import (
    QueryFeedbackRepository,
    QueryHistoryRepository,
)

router = APIRouter(tags=["history"])


async def _get_history_service(session: AsyncSession = Depends(get_session)) -> QueryHistoryService:
    return QueryHistoryService(
        history_repo=QueryHistoryRepository(session),
        feedback_repo=QueryFeedbackRepository(session),
    )


class FeedbackRequest(BaseModel):
    query_id: str
    rating: int | None = None
    flag: str | None = None
    comment: str = ""


@router.get("/history")
async def list_history(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=500),
    user_id: str | None = None,
    status: str | None = None,
    service: QueryHistoryService = Depends(_get_history_service),
):
    tenant_id = getattr(request.state, "tenant_id", "default")
    try:
        items, total = await service.list_history(
            tenant_id=tenant_id,
            page=page,
            page_size=page_size,
            user_id=user_id,
            status=status,
        )
        return success_response({"items": [i.model_dump() for i in items], "total": total, "page": page, "page_size": page_size})
    except Exception as e:
        return error_response("HISTORY_001", {"error": str(e)})


@router.get("/history/{history_id}")
async def get_history(
    history_id: str,
    service: QueryHistoryService = Depends(_get_history_service),
):
    try:
        item = await service.get_history(history_id)
        if item is None:
            return error_response("HISTORY_002", {"id": history_id})
        return success_response(item.model_dump())
    except Exception as e:
        return error_response("HISTORY_003", {"error": str(e)})


@router.post("/history/feedback")
async def submit_feedback(
    request: Request,
    payload: FeedbackRequest,
    service: QueryHistoryService = Depends(_get_history_service),
):
    try:
        result = await service.submit_feedback(
            query_id=payload.query_id,
            user_id=getattr(request.state, "user_id", None),
            rating=payload.rating,
            flag=payload.flag,
            comment=payload.comment,
        )
        return success_response(result.model_dump())
    except Exception as e:
        return error_response("HISTORY_004", {"error": str(e)})
