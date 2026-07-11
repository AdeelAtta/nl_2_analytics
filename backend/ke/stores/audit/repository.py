from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import Column as SAColumn
from sqlalchemy import DateTime, Integer, String, Text, and_, func, select
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from ke.models.audit import AuditEntry
from ke.stores.schema.repository import BaseRepository
from shared.models.pagination import PaginationParams


class AuditBase(DeclarativeBase):
    pass


class AuditEntryOrm(AuditBase):
    __tablename__ = "audit_log"
    __table_args__ = {"schema": "audit_store"}

    id = SAColumn(PG_UUID(), primary_key=True)
    tenant_id = SAColumn(String(64), nullable=False)
    actor_id = SAColumn(String(128), nullable=True)
    action = SAColumn(String(64), nullable=False)
    resource_type = SAColumn(String(64), nullable=False, server_default="")
    resource_id = SAColumn(String(128), nullable=False, server_default="")
    details = SAColumn(JSONB(), nullable=False, server_default="'{}'::jsonb")
    ip_address = SAColumn(String(45), nullable=False, server_default="")
    user_agent = SAColumn(Text(), nullable=False, server_default="")
    outcome = SAColumn(String(16), nullable=False, server_default="success")
    created_at = SAColumn(DateTime(timezone=True), nullable=False, server_default=func.now())


class AuditRepository(BaseRepository[AuditEntry]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, AuditEntryOrm, AuditEntry)

    async def create_entry(
        self,
        tenant_id: str,
        action: str,
        actor_id: str | None = None,
        resource_type: str = "",
        resource_id: str = "",
        details: dict[str, Any] | None = None,
        ip_address: str = "",
        user_agent: str = "",
        outcome: str = "success",
    ) -> AuditEntry:
        entry = AuditEntry(
            id=str(uuid4()),
            tenant_id=tenant_id,
            actor_id=actor_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent,
            outcome=outcome,
            created_at=datetime.now(UTC),
        )
        return await self.create(entry)

    async def list_by_tenant(
        self,
        tenant_id: str,
        pagination: PaginationParams | None = None,
        action_filter: str | None = None,
        actor_id: str | None = None,
        resource_type: str | None = None,
        outcome_filter: str | None = None,
    ) -> tuple[list[AuditEntry], int]:
        filters: dict[str, Any] = {"tenant_id": tenant_id}
        if action_filter:
            filters["action"] = action_filter
        if actor_id:
            filters["actor_id"] = actor_id
        if resource_type:
            filters["resource_type"] = resource_type
        if outcome_filter:
            filters["outcome"] = outcome_filter
        return await self.list(filters=filters, pagination=pagination)

    async def list_recent(
        self,
        tenant_id: str,
        limit: int = 50,
    ) -> list[AuditEntry]:
        pagination = PaginationParams(page=1, page_size=limit)
        entries, _ = await self.list(filters={"tenant_id": tenant_id}, pagination=pagination)
        return entries
