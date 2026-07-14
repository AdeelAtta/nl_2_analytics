from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from app.auth.dependencies import get_current_user
from app.core.database import async_session_factory, get_session
from ke.stores.query.repository import QueryHistoryRepository

router = APIRouter(prefix="/api/v1/history", tags=["history"])


async def _run(fn):
    try:
        async with get_session() as session:
            return await fn(session)
    except Exception:
        return None


@router.get("")
async def list_history(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    database: str = Query(""),
    current_user: dict[str, str] = Depends(get_current_user),
) -> dict[str, Any]:
    if current_user.get("sub") == "anonymous":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    tenant_id = getattr(request.state, "tenant_id", current_user.get("tenant_id", "demo"))

    async def _list(session):
        repo = QueryHistoryRepository(session)
        from shared.models.pagination import PaginationParams
        pagination = PaginationParams(page=page, page_size=page_size, sort_by="created_at", sort_order="desc")
        items, total = await repo.list_by_tenant(tenant_id=tenant_id, pagination=pagination, database=database or None)
        return [
            {
                "id": h.id, "query": h.query, "sql": h.sql, "status": h.status,
                "duration_ms": h.duration_ms, "model_tier": h.model_tier,
                "has_feedback": bool(h.has_feedback),
                "created_at": h.created_at.isoformat(),
            }
            for h in items
        ], total

    result = await _run(_list)
    if result is None:
        return {"success": True, "data": [], "meta": {"page": page, "page_size": page_size, "total": 0}}
    items, total = result
    return {"success": True, "data": items, "meta": {"page": page, "page_size": page_size, "total": total}}


@router.get("/{history_id}")
async def get_history(
    history_id: str,
    current_user: dict[str, str] = Depends(get_current_user),
) -> dict[str, Any]:
    if current_user.get("sub") == "anonymous":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    async def _get(session):
        repo = QueryHistoryRepository(session)
        return await repo.get(history_id)

    item = await _run(_get)
    if item is None:
        raise HTTPException(status_code=404, detail="History entry not found")
    return {
        "success": True,
        "data": {
            "id": item.id, "query": item.query, "sql": item.sql, "status": item.status,
            "duration_ms": item.duration_ms, "model_tier": item.model_tier,
            "model_name": item.model_name, "guard_passed": bool(item.guard_passed),
            "has_feedback": bool(item.has_feedback), "stage_data": item.stage_data,
            "created_at": item.created_at.isoformat(),
        },
    }


@router.delete("/{history_id}")
async def delete_history(
    history_id: str,
    current_user: dict[str, str] = Depends(get_current_user),
) -> dict[str, Any]:
    if current_user.get("sub") == "anonymous":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    async with get_session() as session:
        repo = QueryHistoryRepository(session)
        entry = await repo.get(history_id)
        if entry is None:
            raise HTTPException(status_code=404, detail="History not found")
        if entry.tenant_id != current_user.get("tenant_id", "demo"):
            raise HTTPException(status_code=403, detail="Not allowed to delete this history entry")
        await repo.delete(history_id, hard=True)
    return {"success": True}
