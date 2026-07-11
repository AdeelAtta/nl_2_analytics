from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
import redis.asyncio as aioredis

from app.core.database import get_redis
from ke.api.schemas import (
    KEErrorCode,
    error_response,
    success_response,
)
from ke.stores.config.repository import ConfigRepository

router = APIRouter(tags=["config"])


async def _get_config_repo(request: Request) -> ConfigRepository:
    redis: aioredis.Redis = await get_redis()
    return ConfigRepository(redis)


@router.get("/config")
async def list_config(
    request: Request,
    repo: ConfigRepository = Depends(_get_config_repo),
):
    tenant_id = getattr(request.state, "tenant_id", None)
    entries = await repo.list_all(tenant_id=tenant_id)
    return {"success": True, "data": [e.model_dump() for e in entries]}


@router.get("/config/{key}")
async def get_config(
    key: str,
    request: Request,
    repo: ConfigRepository = Depends(_get_config_repo),
):
    tenant_id = getattr(request.state, "tenant_id", None)
    entry = await repo.get(key, tenant_id=tenant_id)
    if entry is None:
        raise HTTPException(status_code=404, detail=error_response(
            KEErrorCode.ENTITY_NOT_FOUND,
            {"key": key},
        ).model_dump())
    return success_response(entry.model_dump())


@router.put("/config/{key}")
async def set_config(
    key: str,
    body: dict[str, Any],
    request: Request,
    repo: ConfigRepository = Depends(_get_config_repo),
):
    tenant_id = getattr(request.state, "tenant_id", None)
    value = body.get("value")
    description = body.get("description", "")
    entry = await repo.set(key, value, tenant_id=tenant_id, description=description)
    return success_response(entry.model_dump())


@router.delete("/config/{key}")
async def delete_config(
    key: str,
    request: Request,
    repo: ConfigRepository = Depends(_get_config_repo),
):
    tenant_id = getattr(request.state, "tenant_id", None)
    deleted = await repo.delete(key, tenant_id=tenant_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=error_response(
            KEErrorCode.ENTITY_NOT_FOUND,
            {"key": key},
        ).model_dump())
    return success_response({"deleted": True})
