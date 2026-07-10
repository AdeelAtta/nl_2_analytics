from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, TypeVar

from pydantic import BaseModel
from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    and_,
    func,
    select,
    text,
)
from sqlalchemy import (
    Column as SAColumn,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from ke.models.schema import (
    Column as ColumnModel,
)
from ke.models.schema import (
    DatabaseConfig as DatabaseConfigModel,
)
from ke.models.schema import (
    Relationship as RelationshipModel,
)
from ke.models.schema import (
    SchemaInfo as SchemaInfoModel,
)
from ke.models.schema import (
    Table as TableModel,
)
from ke.models.schema import (
    Tenant as TenantModel,
)
from shared.models.pagination import PaginationParams

T = TypeVar("T", bound=BaseModel)


class ORMBase(DeclarativeBase):
    pass


class TenantOrm(ORMBase):
    __tablename__ = "tenants"
    __table_args__ = {"schema": "public"}

    id = SAColumn(PG_UUID(), primary_key=True, server_default=text("gen_random_uuid()"))
    name = SAColumn(String(255), nullable=False)
    slug = SAColumn(String(100), nullable=False)
    tier = SAColumn(String(50), nullable=False, server_default="starter")
    status = SAColumn(String(50), nullable=False, server_default="active")
    settings = SAColumn(JSONB, server_default=text("'{}'::jsonb"))
    features = SAColumn(JSONB, server_default=text("'{}'::jsonb"))
    created_at = SAColumn(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))
    updated_at = SAColumn(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))
    deleted_at = SAColumn(DateTime(timezone=True), nullable=True)


class DatabaseOrm(ORMBase):
    __tablename__ = "databases"
    __table_args__ = {"schema": "schema_store"}

    id = SAColumn(PG_UUID(), primary_key=True, server_default=text("gen_random_uuid()"))
    tenant_id = SAColumn(PG_UUID(), nullable=False)
    name = SAColumn(String(255), nullable=False)
    db_type = SAColumn(String(50), nullable=False)
    connection_hash = SAColumn(String(64), nullable=False)
    host = SAColumn(String(255), nullable=True)
    port = SAColumn(Integer(), nullable=True)
    database_name = SAColumn(String(255), nullable=True)
    username = SAColumn(String(255), nullable=True)
    schema_filter = SAColumn(ARRAY(Text), nullable=True)
    ssl_enabled = SAColumn(Boolean(), nullable=False, server_default=text("TRUE"))
    connection_options = SAColumn(JSONB, server_default=text("'{}'::jsonb"))
    sync_status = SAColumn(String(50), nullable=False, server_default="pending")
    sync_error_message = SAColumn(Text, nullable=True)
    last_synced_at = SAColumn(DateTime(timezone=True), nullable=True)
    table_count = SAColumn(Integer(), server_default=text("0"))
    is_active = SAColumn(Boolean(), nullable=False, server_default=text("TRUE"))
    created_at = SAColumn(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))
    updated_at = SAColumn(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))
    deleted_at = SAColumn(DateTime(timezone=True), nullable=True)


class SchemaInfoOrm(ORMBase):
    __tablename__ = "schema_infos"
    __table_args__ = {"schema": "schema_store"}

    id = SAColumn(PG_UUID(), primary_key=True, server_default=text("gen_random_uuid()"))
    database_id = SAColumn(PG_UUID(), nullable=False)
    name = SAColumn(String(255), nullable=False)
    raw_ddl = SAColumn(Text, nullable=True)
    version = SAColumn(Integer(), nullable=False, server_default=text("1"))
    table_count = SAColumn(Integer(), server_default=text("0"))
    created_at = SAColumn(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))
    updated_at = SAColumn(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))


class TableOrm(ORMBase):
    __tablename__ = "tables"
    __table_args__ = {"schema": "schema_store"}

    id = SAColumn(PG_UUID(), primary_key=True, server_default=text("gen_random_uuid()"))
    schema_id = SAColumn(PG_UUID(), nullable=False)
    name = SAColumn(String(255), nullable=False)
    description = SAColumn(Text, nullable=True)
    ddl = SAColumn(Text, nullable=True)
    row_estimate = SAColumn(BigInteger(), server_default=text("0"))
    version = SAColumn(Integer(), nullable=False, server_default=text("1"))
    is_active = SAColumn(Boolean(), nullable=False, server_default=text("TRUE"))
    last_introspected_at = SAColumn(DateTime(timezone=True), nullable=True)
    created_at = SAColumn(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))
    updated_at = SAColumn(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))


class ColumnOrm(ORMBase):
    __tablename__ = "columns"
    __table_args__ = {"schema": "schema_store"}

    id = SAColumn(PG_UUID(), primary_key=True, server_default=text("gen_random_uuid()"))
    table_id = SAColumn(PG_UUID(), nullable=False)
    name = SAColumn(String(255), nullable=False)
    ordinal_position = SAColumn(Integer(), nullable=False)
    data_type = SAColumn(String(100), nullable=False)
    is_nullable = SAColumn(Boolean(), nullable=False, server_default=text("TRUE"))
    is_primary_key = SAColumn(Boolean(), nullable=False, server_default=text("FALSE"))
    is_unique = SAColumn(Boolean(), nullable=False, server_default=text("FALSE"))
    default_value = SAColumn(Text, nullable=True)
    description = SAColumn(Text, nullable=True)
    foreign_key_table = SAColumn(String(255), nullable=True)
    foreign_key_column = SAColumn(String(255), nullable=True)
    character_maximum_length = SAColumn(Integer(), nullable=True)
    numeric_precision = SAColumn(Integer(), nullable=True)
    numeric_scale = SAColumn(Integer(), nullable=True)
    created_at = SAColumn(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))
    updated_at = SAColumn(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))


class RelationshipOrm(ORMBase):
    __tablename__ = "relationships"
    __table_args__ = {"schema": "schema_store"}

    id = SAColumn(PG_UUID(), primary_key=True, server_default=text("gen_random_uuid()"))
    tenant_id = SAColumn(PG_UUID(), nullable=False)
    source_table_id = SAColumn(PG_UUID(), nullable=False)
    source_column = SAColumn(String(255), nullable=False)
    target_table_id = SAColumn(PG_UUID(), nullable=False)
    target_column = SAColumn(String(255), nullable=False)
    relationship_type = SAColumn(String(50), nullable=False, server_default="foreign_key")
    confidence = SAColumn(Float(), nullable=False, server_default=text("1.0"))
    discovered_by = SAColumn(String(100), nullable=False, server_default="connector")
    properties = SAColumn(JSONB, server_default=text("'{}'::jsonb"))
    created_at = SAColumn(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))


class BaseRepository[T]:
    def __init__(
        self, session: AsyncSession, orm_class: type[ORMBase], pydantic_class: type[T]
    ) -> None:
        self._session = session
        self._orm_class = orm_class
        self._pydantic_class = pydantic_class

    async def create(self, data: T) -> T:
        values = data.model_dump()
        instance = self._orm_class(**values)
        self._session.add(instance)
        await self._session.flush()
        await self._session.refresh(instance)
        return self._pydantic_class.model_validate(instance, from_attributes=True)

    async def get(self, id: str) -> T | None:
        stmt = select(self._orm_class).where(self._orm_class.id == id)
        result = await self._session.execute(stmt)
        instance = result.scalar_one_or_none()
        if instance is None:
            return None
        return self._pydantic_class.model_validate(instance, from_attributes=True)

    async def update(self, id: str, data: dict[str, Any]) -> T | None:
        stmt = select(self._orm_class).where(self._orm_class.id == id)
        result = await self._session.execute(stmt)
        instance = result.scalar_one_or_none()
        if instance is None:
            return None
        data.pop("id", None)
        data.pop("created_at", None)
        data["updated_at"] = datetime.now(UTC)
        for key, value in data.items():
            setattr(instance, key, value)
        await self._session.flush()
        await self._session.refresh(instance)
        return self._pydantic_class.model_validate(instance, from_attributes=True)

    async def delete(self, id: str, hard: bool = False) -> bool:
        stmt = select(self._orm_class).where(self._orm_class.id == id)
        result = await self._session.execute(stmt)
        instance = result.scalar_one_or_none()
        if instance is None:
            return False
        if hard:
            await self._session.delete(instance)
        else:
            instance.deleted_at = datetime.now(UTC)
        await self._session.flush()
        return True

    async def list(
        self,
        filters: dict[str, Any] | None = None,
        pagination: PaginationParams | None = None,
        tenant_id: str | None = None,
    ) -> tuple[list[T], int]:
        conditions = []
        if filters:
            for key, value in filters.items():
                column = getattr(self._orm_class, key, None)
                if column is not None:
                    conditions.append(column == value)
        if hasattr(self._orm_class, "deleted_at"):
            conditions.append(self._orm_class.deleted_at.is_(None))
        if tenant_id is not None and hasattr(self._orm_class, "tenant_id"):
            conditions.append(self._orm_class.tenant_id == tenant_id)

        query = select(self._orm_class)
        if conditions:
            query = query.where(and_(*conditions))

        count_query = select(func.count()).select_from(self._orm_class)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        total_result = await self._session.execute(count_query)
        total = total_result.scalar() or 0

        if pagination:
            offset = (pagination.page - 1) * pagination.page_size
            query = query.offset(offset).limit(pagination.page_size)
            if pagination.sort_by and hasattr(self._orm_class, pagination.sort_by):
                sort_col = getattr(self._orm_class, pagination.sort_by)
                if pagination.sort_order == "desc":
                    sort_col = sort_col.desc()
                query = query.order_by(sort_col)

        result = await self._session.execute(query)
        instances = result.scalars().all()
        items = [
            self._pydantic_class.model_validate(inst, from_attributes=True)
            for inst in instances
        ]
        return items, int(total)


class TenantRepository(BaseRepository[TenantModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, TenantOrm, TenantModel)

    async def get_by_slug(self, slug: str) -> TenantModel | None:
        stmt = select(TenantOrm).where(
            TenantOrm.slug == slug,
            TenantOrm.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        instance = result.scalar_one_or_none()
        if instance is None:
            return None
        return TenantModel.model_validate(instance, from_attributes=True)


class DatabaseConfigRepository(BaseRepository[DatabaseConfigModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, DatabaseOrm, DatabaseConfigModel)

    async def list_by_tenant(self, tenant_id: str) -> list[DatabaseConfigModel]:
        items, _ = await self.list(filters={"tenant_id": tenant_id})
        return items


class SchemaInfoRepository(BaseRepository[SchemaInfoModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, SchemaInfoOrm, SchemaInfoModel)

    async def list_by_database(self, database_id: str) -> list[SchemaInfoModel]:
        items, _ = await self.list(filters={"database_id": database_id})
        return items


class TableRepository(BaseRepository[TableModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, TableOrm, TableModel)

    async def list_by_schema(self, schema_id: str) -> list[TableModel]:
        items, _ = await self.list(filters={"schema_id": schema_id})
        return items

    async def list_active(self) -> list[TableModel]:
        items, _ = await self.list(filters={"is_active": True})
        return items


class ColumnRepository(BaseRepository[ColumnModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ColumnOrm, ColumnModel)

    async def list_by_table(self, table_id: str) -> list[ColumnModel]:
        items, _ = await self.list(
            filters={"table_id": table_id}, pagination=PaginationParams(page_size=500)
        )
        return items

    async def list_primary_keys(self, table_id: str) -> list[ColumnModel]:
        items, _ = await self.list(filters={"table_id": table_id, "is_primary_key": True})
        return items


class RelationshipRepository(BaseRepository[RelationshipModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, RelationshipOrm, RelationshipModel)

    async def list_by_tenant(self, tenant_id: str) -> list[RelationshipModel]:
        items, _ = await self.list(tenant_id=tenant_id)
        return items

    async def list_by_source_table(self, source_table_id: str) -> list[RelationshipModel]:
        items, _ = await self.list(filters={"source_table_id": source_table_id})
        return items

    async def list_by_target_table(self, target_table_id: str) -> list[RelationshipModel]:
        items, _ = await self.list(filters={"target_table_id": target_table_id})
        return items
