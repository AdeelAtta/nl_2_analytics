from __future__ import annotations

import json
import os
import uuid
from datetime import UTC, datetime
from typing import Any

import bcrypt as _bcrypt
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.core.database import async_session_factory

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")


class FileStore:
    """File-based JSON store for non-critical data (API keys)."""

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


async def create_tenant(name: str, owner_email: str) -> dict[str, Any]:
    async with async_session_factory() as session:
        tid = str(uuid.uuid4())
        slug = name.lower().replace(" ", "-").replace("'", "").replace('"', "")[:50]
        try:
            await session.execute(
                text("""
                    INSERT INTO auth.tenants (id, name, slug, owner_email, status, created_at)
                    VALUES (:id, :name, :slug, :email, 'active', :now)
                """),
                {"id": tid, "name": name, "slug": slug, "email": owner_email, "now": datetime.now(UTC)},
            )
        except IntegrityError:
            await session.rollback()
            slug = slug[:45] + "-" + uuid.uuid4().hex[:4]
            await session.execute(
                text("""
                    INSERT INTO auth.tenants (id, name, slug, owner_email, status, created_at)
                    VALUES (:id, :name, :slug, :email, 'active', :now)
                """),
                {"id": tid, "name": name, "slug": slug, "email": owner_email, "now": datetime.now(UTC)},
            )
        await session.commit()
        return {
            "id": tid,
            "name": name,
            "slug": slug,
            "owner_email": owner_email,
            "created_at": str(datetime.now(UTC)),
            "status": "active",
        }


async def create_user(email: str, password: str, tenant_id: str, name: str = "") -> dict[str, Any]:
    async with async_session_factory() as session:
        result = await session.execute(
            text("SELECT id FROM auth.users WHERE email = :email"),
            {"email": email},
        )
        if result.scalar_one_or_none():
            raise ValueError("Email already registered")

        uid = str(uuid.uuid4())
        pwd_hash = _bcrypt.hashpw(password.encode(), _bcrypt.gensalt()).decode()
        await session.execute(
            text("""
                INSERT INTO auth.users (id, email, password_hash, name, role, tenant_id, created_at)
                VALUES (:id, :email, :pwd, :name, 'admin', :tid, :now)
            """),
            {
                "id": uid, "email": email, "pwd": pwd_hash,
                "name": name or email.split("@")[0],
                "tid": tenant_id, "now": datetime.now(UTC),
            },
        )
        await session.commit()
        return {
            "id": uid,
            "email": email,
            "name": name or email.split("@")[0],
            "password_hash": pwd_hash,
            "role": "admin",
            "tenant_id": tenant_id,
            "created_at": str(datetime.now(UTC)),
        }


async def authenticate_user(email: str, password: str) -> dict[str, Any] | None:
    async with async_session_factory() as session:
        result = await session.execute(
            text("""
                SELECT id, email, password_hash, name, role, tenant_id, created_at
                FROM auth.users WHERE email = :email
            """),
            {"email": email},
        )
        row = result.fetchone()
        if row is None:
            return None
        if not _bcrypt.checkpw(password.encode(), row[2].encode()):
            return None
        return {
            "id": str(row[0]),
            "email": row[1],
            "name": row[3],
            "role": row[4],
            "tenant_id": str(row[5]),
            "created_at": str(row[6]),
        }


async def get_tenant(tenant_id: str) -> dict[str, Any] | None:
    async with async_session_factory() as session:
        result = await session.execute(
            text("SELECT id, name, slug, owner_email, status FROM auth.tenants WHERE id = :id"),
            {"id": tenant_id},
        )
        row = result.fetchone()
        if row is None:
            return None
        return {"id": str(row[0]), "name": row[1], "slug": row[2],
                "owner_email": row[3], "status": row[4]}


async def get_tenants_by_user(user_id: str) -> list[dict[str, Any]]:
    async with async_session_factory() as session:
        result = await session.execute(
            text("SELECT id, name, slug, owner_email, status FROM auth.tenants"),
        )
        return [
            {"id": str(r[0]), "name": r[1], "slug": r[2],
             "owner_email": r[3], "status": r[4]}
            for r in result.fetchall()
        ]


async def get_users_by_tenant(tenant_id: str) -> list[dict[str, Any]]:
    async with async_session_factory() as session:
        result = await session.execute(
            text("""
                SELECT id, email, name, role, tenant_id, created_at
                FROM auth.users WHERE tenant_id = :tid
            """),
            {"tid": tenant_id},
        )
        return [
            {            "id": str(r[0]), "email": r[1], "name": r[2],
             "role": r[3], "tenant_id": str(r[4])}
            for r in result.fetchall()
        ]


async def get_user_by_id(user_id: str) -> dict[str, Any] | None:
    async with async_session_factory() as session:
        result = await session.execute(
            text("""
                SELECT id, email, name, role, tenant_id
                FROM auth.users WHERE id = :id
            """),
            {"id": user_id},
        )
        row = result.fetchone()
        if row is None:
            return None
        return {"id": str(row[0]), "email": row[1], "name": row[2],
                "role": row[3], "tenant_id": str(row[4])}
