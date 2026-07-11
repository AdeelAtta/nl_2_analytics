from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import get_current_user
from app.services.store import FileStore

router = APIRouter(prefix="/api/v1/auth/api-keys", tags=["auth"])
_key_store = FileStore("api_keys.json")


@router.get("")
async def list_api_keys(
    current_user: dict[str, str] = Depends(get_current_user),
) -> dict[str, Any]:
    if current_user.get("sub") == "anonymous":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    user_id = current_user["sub"]
    keys = [k for k in _key_store.all() if k.get("user_id") == user_id and not k.get("revoked")]
    return {
        "success": True,
        "data": [
            {"id": k["id"], "name": k["name"], "prefix": k["key"][:8] + "...",
             "created_at": k["created_at"]}
            for k in keys
        ],
    }


@router.post("")
async def create_api_key(
    body: dict[str, str],
    current_user: dict[str, str] = Depends(get_current_user),
) -> dict[str, Any]:
    if current_user.get("sub") == "anonymous":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    name = (body.get("name") or "").strip()
    if not name:
        raise HTTPException(status_code=422, detail="Key name is required")
    key_id = str(uuid.uuid4())
    key_value = f"oq_{uuid.uuid4().hex}{uuid.uuid4().hex}"
    _key_store.insert({
        "id": key_id,
        "user_id": current_user["sub"],
        "name": name,
        "key": key_value,
        "created_at": str(datetime.now(UTC)),
        "revoked": False,
    })
    from app.core.config import get_settings
    settings = get_settings()
    if key_value not in settings.api_keys:
        settings.api_keys.append(key_value)
    return {"success": True, "data": {"id": key_id, "name": name, "key": key_value}}


@router.delete("/{key_id}")
async def revoke_api_key(
    key_id: str,
    current_user: dict[str, str] = Depends(get_current_user),
) -> dict[str, Any]:
    if current_user.get("sub") == "anonymous":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    key = _key_store.find("id", key_id)
    if not key or key.get("user_id") != current_user["sub"]:
        raise HTTPException(status_code=404, detail="Key not found")
    _key_store.update("id", key_id, {"revoked": True})
    return {"success": True}
