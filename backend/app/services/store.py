from __future__ import annotations

import hashlib
import json
import os
import uuid
from datetime import UTC, datetime
from typing import Any

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")


class FileStore:
    def __init__(self, filename: str) -> None:
        self._path = os.path.join(DATA_DIR, filename)
        os.makedirs(DATA_DIR, exist_ok=True)
        self._data = self._load()

    def _load(self) -> list[dict[str, Any]]:
        if os.path.exists(self._path):
            try:
                with open(self._path) as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                return []
        return []

    def _save(self) -> None:
        with open(self._path, "w") as f:
            json.dump(self._data, f, indent=2, default=str)

    def all(self) -> list[dict[str, Any]]:
        return list(self._data)

    def find(self, key: str, value: Any) -> dict[str, Any] | None:
        for item in self._data:
            if item.get(key) == value:
                return item
        return None

    def insert(self, item: dict[str, Any]) -> dict[str, Any]:
        self._data.append(item)
        self._save()
        return item

    def update(self, key: str, value: Any, updates: dict[str, Any]) -> dict[str, Any] | None:
        for item in self._data:
            if item.get(key) == value:
                item.update(updates)
                self._save()
                return item
        return None

    def delete(self, key: str, value: Any) -> bool:
        before = len(self._data)
        self._data = [item for item in self._data if item.get(key) != value]
        if len(self._data) < before:
            self._save()
            return True
        return False

    def clear(self) -> None:
        self._data = []
        self._save()


_tenant_store = FileStore("tenants.json")
_user_store = FileStore("users.json")


def get_tenant_store() -> FileStore:
    return _tenant_store


def get_user_store_file() -> FileStore:
    return _user_store


def create_tenant(name: str, owner_email: str) -> dict[str, Any]:
    store = get_tenant_store()
    tenant = {
        "id": str(uuid.uuid4()),
        "name": name,
        "slug": name.lower().replace(" ", "-")[:50],
        "owner_email": owner_email,
        "created_at": str(datetime.now(UTC)),
        "status": "active",
    }
    store.insert(tenant)
    return tenant


def create_user(email: str, password: str, tenant_id: str, name: str = "") -> dict[str, Any]:
    import bcrypt as _bcrypt
    store = get_user_store_file()
    if store.find("email", email):
        raise ValueError("Email already registered")
    pwd_hash = _bcrypt.hashpw(password.encode(), _bcrypt.gensalt()).decode()
    user = {
        "id": str(uuid.uuid4()),
        "email": email,
        "name": name or email.split("@")[0],
        "password_hash": pwd_hash,
        "role": "admin",
        "tenant_id": tenant_id,
        "created_at": str(datetime.now(UTC)),
    }
    store.insert(user)
    return user


def authenticate_user(email: str, password: str) -> dict[str, Any] | None:
    import bcrypt as _bcrypt
    store = get_user_store_file()
    user = store.find("email", email)
    if not user:
        return None
    if not _bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        return None
    return user
