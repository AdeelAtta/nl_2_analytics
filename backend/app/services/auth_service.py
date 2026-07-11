from __future__ import annotations

import hashlib
import uuid
from datetime import UTC, datetime
from typing import Any


class UserStore:
    def __init__(self) -> None:
        self._users: dict[str, dict[str, Any]] = {}

    def create_user(self, email: str, password: str, name: str = "") -> dict[str, Any]:
        if email in self._users:
            raise ValueError("Email already registered")
        salt = uuid.uuid4().hex
        pwd_hash = hashlib.sha256(f"{salt}:{password}".encode()).hexdigest()
        user = {
            "id": str(uuid.uuid4()),
            "email": email,
            "name": name or email.split("@")[0],
            "password_hash": pwd_hash,
            "salt": salt,
            "role": "user",
            "tenant_id": "demo",
            "created_at": datetime.now(UTC),
        }
        self._users[email] = user
        return user

    def authenticate(self, email: str, password: str) -> dict[str, Any] | None:
        user = self._users.get(email)
        if not user:
            return None
        pwd_hash = hashlib.sha256(f"{user['salt']}:{password}".encode()).hexdigest()
        if pwd_hash != user["password_hash"]:
            return None
        return user

    def get_by_email(self, email: str) -> dict[str, Any] | None:
        return self._users.get(email)


_user_store = UserStore()


def get_user_store() -> UserStore:
    return _user_store
