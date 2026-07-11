from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from ke.api.schemas import (
    KEErrorCode,
    error_response,
    success_response,
)
from ke.stores.audit.repository import AuditRepository
from shared.models.pagination import PaginationParams

router = APIRouter(tags=["audit"])


async def _get_audit_repo(session: AsyncSession = Depends(get_session)) -> AuditRepository:
    return AuditRepository(session)


@router.get("/audit")
async def list_audit(
    request: Request,
    repo: AuditRepository = Depends(_get_audit_repo),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    action: str | None = None,
    actor: str | None = None,
    resource_type: str | None = None,
    outcome: str | None = None,
):
    tenant_id = getattr(request.state, "tenant_id", None)
    if not tenant_id:
        raise HTTPException(status_code=400, detail=error_response(
            KEErrorCode.TENANT_REQUIRED,
        ).model_dump())
    pagination = PaginationParams(page=page, page_size=page_size)
    entries, total = await repo.list_by_tenant(
        tenant_id=tenant_id,
        pagination=pagination,
        action_filter=action,
        actor_id=actor,
        resource_type=resource_type,
        outcome_filter=outcome,
    )
    total_pages = (total + page_size - 1) // page_size
    return {
        "success": True,
        "data": [e.model_dump() for e in entries],
        "meta": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
        },
    }


@router.get("/audit/{entry_id}")
async def get_audit_entry(
    entry_id: str,
    repo: AuditRepository = Depends(_get_audit_repo),
):
    entry = await repo.get(entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail=error_response(
            KEErrorCode.ENTITY_NOT_FOUND,
            {"entry_id": entry_id},
        ).model_dump())
    return success_response(entry.model_dump())
