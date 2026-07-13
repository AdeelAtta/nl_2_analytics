from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import get_current_user
from app.services.store import FileStore, get_users_by_tenant

router = APIRouter(prefix="/api/v1/tenants/members", tags=["tenants"])
_invites_store = FileStore("invites.json")


@router.get("")
async def list_members(
    current_user: dict[str, str] = Depends(get_current_user),
) -> dict[str, Any]:
    if current_user.get("sub") == "anonymous":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    tenant_id = current_user.get("tenant_id", "demo")
    members = await get_users_by_tenant(tenant_id)
    return {
        "success": True,
        "data": [
            {
                "id": u["id"], "email": u["email"], "name": u.get("name", ""),
                "role": u.get("role", "user"),
            }
            for u in members
        ],
    }


@router.post("/invite")
async def invite_member(
    body: dict[str, str],
    current_user: dict[str, str] = Depends(get_current_user),
) -> dict[str, Any]:
    if current_user.get("sub") == "anonymous":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    email = (body.get("email") or "").strip()
    if not email:
        raise HTTPException(status_code=422, detail="Email is required")
    tenant_id = current_user.get("tenant_id", "demo")
    _invites_store.insert({
        "id": str(uuid.uuid4()),
        "email": email,
        "tenant_id": tenant_id,
        "invited_by": current_user.get("sub", ""),
        "status": "pending",
        "created_at": str(datetime.now(UTC)),
    })
    return {"success": True, "data": {"email": email, "status": "invited"}}
