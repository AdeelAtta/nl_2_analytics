from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
import redis.asyncio as aioredis

from app.core.database import get_redis
from ke.api.schemas import (
    KEErrorCode,
    KEListResponse,
    KEResponse,
    error_response,
    success_response,
)
from ke.services.cache import CacheService

router = APIRouter(tags=["cache"])

CACHE_KEY_PATTERN_HEADER = "X-Cache-Pattern"


async def _get_cache() -> CacheService:
    redis: aioredis.Redis = await get_redis()
    return CacheService(redis)


@router.get("/cache/{key}", response_model=KEResponse[Any])
async def cache_get(
    key: str,
    cache: CacheService = Depends(_get_cache),
) -> KEResponse[Any]:
    value = await cache.get(key)
    if value is None:
        raise HTTPException(status_code=404, detail=error_response(
            KEErrorCode.ENTITY_NOT_FOUND,
            {"key": key},
        ).model_dump())
    return success_response(value)


@router.put("/cache/{key}", response_model=KEResponse[dict[str, Any]])
async def cache_set(
    key: str,
    body: dict[str, Any],
    cache: CacheService = Depends(_get_cache),
) -> KEResponse[dict[str, Any]]:
    value = body.get("value")
    ttl = body.get("ttl", 300)
    if not isinstance(ttl, int) or ttl < 0:
        raise HTTPException(status_code=422, detail=error_response(
            KEErrorCode.VALIDATION_ERROR,
            {"ttl": "Must be a non-negative integer"},
        ).model_dump())
    await cache.set(key, value, ttl=ttl if ttl > 0 else None)
    return success_response({"key": key, "ttl": ttl})


@router.delete("/cache/{key}", response_model=KEResponse[dict[str, bool]])
async def cache_delete(
    key: str,
    cache: CacheService = Depends(_get_cache),
) -> KEResponse[dict[str, bool]]:
    deleted = await cache.delete(key)
    if not deleted:
        raise HTTPException(status_code=404, detail=error_response(
            KEErrorCode.ENTITY_NOT_FOUND,
            {"key": key},
        ).model_dump())
    return success_response({"deleted": True})


@router.post("/cache/invalidate", response_model=KEResponse[dict[str, int]])
async def cache_invalidate(
    body: dict[str, str],
    cache: CacheService = Depends(_get_cache),
) -> KEResponse[dict[str, int]]:
    pattern = body.get("pattern", "")
    if not pattern:
        raise HTTPException(status_code=422, detail=error_response(
            KEErrorCode.VALIDATION_ERROR,
            {"pattern": "Pattern is required"},
        ).model_dump())
    count = await cache.invalidate_pattern(pattern)
    return success_response({"invalidated": count})
