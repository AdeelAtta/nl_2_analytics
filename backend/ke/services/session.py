from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any


class SessionTurn:
    def __init__(
        self,
        query: str,
        sql: str = "",
        result_summary: str = "",
        intent_type: str = "",
        model_tier: str = "none",
        model_name: str = "",
        created_at: datetime | None = None,
    ) -> None:
        self.query = query
        self.sql = sql
        self.result_summary = result_summary
        self.intent_type = intent_type
        self.model_tier = model_tier
        self.model_name = model_name
        self.created_at = created_at or datetime.now()

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "sql": self.sql,
            "result_summary": self.result_summary,
            "intent_type": self.intent_type,
            "model_tier": self.model_tier,
            "model_name": self.model_name,
            "created_at": self.created_at.isoformat(),
        }


class InMemorySessionService:
    def __init__(self) -> None:
        self._sessions: dict[str, list[SessionTurn]] = {}
        self._max_turns: int = 20

    def _key(self, session_id: str, tenant_id: str) -> str:
        return f"{tenant_id}:{session_id}"

    async def get_or_create(self, session_id: str | None, tenant_id: str = "default") -> tuple[str, list[SessionTurn]]:
        if session_id:
            k = self._key(session_id, tenant_id)
            if k in self._sessions:
                return session_id, self._sessions[k]
        new_id = session_id or str(uuid.uuid4())
        k = self._key(new_id, tenant_id)
        if k not in self._sessions:
            self._sessions[k] = []
        return new_id, self._sessions[k]

    async def add_turn(
        self,
        session_id: str,
        query: str,
        sql: str = "",
        result_summary: str = "",
        intent_type: str = "",
        model_tier: str = "none",
        model_name: str = "",
        tenant_id: str = "default",
    ) -> SessionTurn:
        k = self._key(session_id, tenant_id)
        if k not in self._sessions:
            self._sessions[k] = []
        turn = SessionTurn(
            query=query,
            sql=sql,
            result_summary=result_summary,
            intent_type=intent_type,
            model_tier=model_tier,
            model_name=model_name,
        )
        self._sessions[k].append(turn)
        if len(self._sessions[k]) > self._max_turns:
            self._sessions[k] = self._sessions[k][-self._max_turns:]
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
