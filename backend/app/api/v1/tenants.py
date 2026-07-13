from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.auth.dependencies import get_current_user
from app.services.store import create_tenant, get_tenant, get_tenants_by_user

router = APIRouter(prefix="/api/v1/tenants", tags=["tenants"])


@router.get("")
async def list_tenants(
    current_user: dict[str, str] = Depends(get_current_user),
) -> dict[str, Any]:
    if current_user.get("sub") == "anonymous":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    tenants = await get_tenants_by_user(current_user.get("sub", ""))
    return {
        "success": True,
        "data": [
            {"id": t["id"], "name": t["name"], "slug": t["slug"],
             "status": t["status"], "created_at": t["created_at"]}
            for t in tenants
        ],
    }


@router.post("")
async def create_tenant_endpoint(
    body: dict[str, str],
    current_user: dict[str, str] = Depends(get_current_user),
) -> dict[str, Any]:
    if current_user.get("sub") == "anonymous":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    name = (body.get("name") or "").strip()
    if not name:
        raise HTTPException(status_code=422, detail="Tenant name is required")
    tenant = await create_tenant(name, current_user.get("sub", "unknown"))
    return {
        "success": True,
        "data": {"id": tenant["id"], "name": tenant["name"], "slug": tenant["slug"]},
    }


@router.get("/current")
async def current_tenant(
    request: Request,
    current_user: dict[str, str] = Depends(get_current_user),
) -> dict[str, Any]:
    if current_user.get("sub") == "anonymous":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    tenant_id = current_user.get("tenant_id", "demo")
    tenant = await get_tenant(tenant_id)
    if not tenant:
        tenant = {"id": tenant_id, "name": tenant_id, "slug": tenant_id, "status": "active"}
    return {
        "success": True,
        "data": {
            "id": tenant["id"], "name": tenant["name"], "slug": tenant.get("slug", ""),
            "status": tenant.get("status", "active"),
        },
    }
