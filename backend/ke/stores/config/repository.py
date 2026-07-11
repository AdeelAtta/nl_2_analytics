from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import redis.asyncio as aioredis

from ke.models.config import ConfigEntry


class ConfigRepository:
    def __init__(self, redis_client: aioredis.Redis) -> None:
        self._redis = redis_client
        self._prefix = "ke:config:"

    def _key(self, tenant_id: str | None, config_key: str) -> str:
        if tenant_id:
            return f"{self._prefix}{tenant_id}:{config_key}"
        return f"{self._prefix}global:{config_key}"

    def _pattern(self, tenant_id: str | None = None) -> str:
        if tenant_id:
            return f"{self._prefix}{tenant_id}:*"
        return f"{self._prefix}global:*"

    async def get(self, key: str, tenant_id: str | None = None) -> ConfigEntry | None:
        data = await self._redis.get(self._key(tenant_id, key))
        if data is None:
            return None
        raw = json.loads(data)
        return ConfigEntry(**raw)

    async def set(self, key: str, value: Any, tenant_id: str | None = None, description: str = "") -> ConfigEntry:
        now = datetime.now(UTC)
        entry_id = str(uuid4())
        entry = ConfigEntry(
            id=entry_id,
            tenant_id=tenant_id,
            key=key,
            value=value,
            description=description,
            created_at=now,
            updated_at=now,
        )
        await self._redis.set(
            self._key(tenant_id, key),
            entry.model_dump_json(),
        )
        return entry

    async def delete(self, key: str, tenant_id: str | None = None) -> bool:
        deleted = await self._redis.delete(self._key(tenant_id, key))
        return deleted > 0

    async def list_all(self, tenant_id: str | None = None) -> list[ConfigEntry]:
        keys = await self._redis.keys(self._pattern(tenant_id))
        if not keys:
            return []
        values = await self._redis.mget(*keys)
        results: list[ConfigEntry] = []
        for v in values:
            if v:
                results.append(ConfigEntry(**json.loads(v)))
        results.sort(key=lambda e: e.key)
        return results
