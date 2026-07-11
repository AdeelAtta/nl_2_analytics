from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from typing import Any

from ke.services.session import SessionTurn


class RedisSessionService:
    def __init__(self, redis_client: Any | None = None) -> None:
        self._redis = redis_client
        self._max_turns: int = 20
        self._prefix: str = "session:"

    async def _get_turns(self, session_key: str) -> list[SessionTurn]:
        if self._redis is None:
            return []
        try:
            raw = await self._redis.get(session_key)
            if not raw:
                return []
            data = json.loads(raw)
            return [SessionTurn(**t) for t in data]
        except Exception:
            return []

    async def _set_turns(self, session_key: str, turns: list[SessionTurn]) -> None:
        if self._redis is None:
            return
        try:
            data = [t.to_dict() for t in turns]
            await self._redis.set(session_key, json.dumps(data))
            await self._redis.expire(session_key, 86400)
        except Exception:
            pass

    async def get_or_create(self, session_id: str | None, tenant_id: str = "default") -> tuple[str, list[SessionTurn]]:
        if session_id:
            key = f"{self._prefix}{session_id}"
            turns = await self._get_turns(key)
            if turns:
                return session_id, turns
        new_id = session_id or str(uuid.uuid4())
        key = f"{self._prefix}{new_id}"
        existing = await self._get_turns(key)
        return new_id, existing

    async def add_turn(
        self,
        session_id: str,
        query: str,
        sql: str = "",
        result_summary: str = "",
        intent_type: str = "",
        model_tier: str = "none",
        model_name: str = "",
    ) -> SessionTurn:
        key = f"{self._prefix}{session_id}"
        turns = await self._get_turns(key)
        turn = SessionTurn(
            query=query, sql=sql, result_summary=result_summary,
            intent_type=intent_type, model_tier=model_tier, model_name=model_name,
        )
        turns.append(turn)
        if len(turns) > self._max_turns:
            turns = turns[-self._max_turns:]
        await self._set_turns(key, turns)
        return turn

    def format_history(self, turns: list[SessionTurn], max_turns: int = 3) -> str:
        recent = turns[-max_turns:] if turns else []
        if not recent:
            return ""
        lines: list[str] = ["Previous conversation:"]
        for t in recent:
            lines.append(f"  User: {t.query}")
            if t.sql:
                lines.append(f"  SQL: {t.sql}")
            if t.result_summary:
                lines.append(f"  Result: {t.result_summary}")
        return "\n".join(lines)


async def create_session_service() -> RedisSessionService | None:
    try:
        from app.core.database import get_redis
        redis = await get_redis()
        await redis.ping()
        return RedisSessionService(redis)
    except Exception:
        return None
