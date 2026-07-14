from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from app.auth.dependencies import get_current_user
from app.core.database import get_session
from ke.models.feedback import QueryFeedback
from ke.stores.query.repository import QueryFeedbackRepository, QueryHistoryRepository

router = APIRouter(prefix="/api/v1/feedback", tags=["feedback"])


class SubmitFeedbackRequest(BaseModel):
    query_id: str
    rating: int | None = None
    flag: str | None = None
    comment: str = ""


@router.post("")
async def submit_feedback(
    request: Request,
    body: SubmitFeedbackRequest,
    current_user: dict[str, str] = Depends(get_current_user),
) -> dict[str, Any]:
    if current_user.get("sub") == "anonymous":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    if body.rating is not None and (body.rating < 1 or body.rating > 5):
        raise HTTPException(status_code=422, detail="Rating must be between 1 and 5")
    if body.flag and body.flag not in ("spam", "incorrect", "offensive", "other"):
        raise HTTPException(status_code=422, detail="Invalid flag value")

    async with get_session() as session:
        feedback_repo = QueryFeedbackRepository(session)
        history_repo = QueryHistoryRepository(session)
        existing = await history_repo.get(body.query_id)
        if existing is None:
            raise HTTPException(status_code=404, detail="Query not found")

        import uuid
        feedback = QueryFeedback(
            id=str(uuid.uuid4()),
            query_id=body.query_id,
            user_id=current_user.get("sub"),
            rating=body.rating,
            flag=body.flag,
            comment=body.comment,
        )
        result = await feedback_repo.create(feedback)
        await history_repo.mark_feedback(body.query_id)

    return {"success": True, "data": {"id": result.id, "query_id": result.query_id, "rating": result.rating}}


@router.get("")
async def list_feedback(
    request: Request,
    page: int = 1,
    page_size: int = 50,
    current_user: dict[str, str] = Depends(get_current_user),
) -> dict[str, Any]:
    if current_user.get("sub") == "anonymous":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    async with get_session() as session:
        repo = QueryFeedbackRepository(session)
        from shared.models.pagination import PaginationParams
        pagination = PaginationParams(page=page, page_size=page_size, sort_by="created_at")
        items, total = await repo.list(filters={"user_id": current_user.get("sub")}, pagination=pagination)
    return {
        "success": True,
        "data": [
            {"id": f.id, "query_id": f.query_id, "rating": f.rating, "flag": f.flag, "comment": f.comment}
            for f in items
        ],
        "meta": {"page": page, "page_size": page_size, "total": total},
    }
