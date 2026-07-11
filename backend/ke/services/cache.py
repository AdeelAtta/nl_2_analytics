from __future__ import annotations

import json
from typing import Any

import redis.asyncio as aioredis


class CacheService:
    def __init__(self, redis_client: aioredis.Redis, prefix: str = "ke:cache:") -> None:
        self._redis = redis_client
        self._prefix = prefix

    def _key(self, suffix: str) -> str:
        return f"{self._prefix}{suffix}"

    async def get(self, key: str) -> Any | None:
        data = await self._redis.get(self._key(key))
        if data is None:
            return None
        try:
            return json.loads(data)
        except (json.JSONDecodeError, TypeError):
            return data

    async def set(self, key: str, value: Any, ttl: int | None = 300) -> None:
        serialized = json.dumps(value, default=str)
        if ttl is not None:
            await self._redis.setex(self._key(key), ttl, serialized)
        else:
            await self._redis.set(self._key(key), serialized)

    async def delete(self, key: str) -> bool:
        deleted = await self._redis.delete(self._key(key))
        return deleted > 0

    async def invalidate_pattern(self, pattern: str) -> int:
        keys = await self._redis.keys(f"{self._prefix}{pattern}")
        if not keys:
            return 0
        return await self._redis.delete(*keys)

    async def exists(self, key: str) -> bool:
        return await self._redis.exists(self._key(key)) > 0

    async def get_or_set(
        self,
        key: str,
        factory: callable,
        ttl: int = 300,
    ) -> Any:
        cached = await self.get(key)
        if cached is not None:
            return cached
        value = await factory()
        await self.set(key, value, ttl=ttl)
        return value

    @property
    def client(self) -> aioredis.Redis:
        return self._redis
