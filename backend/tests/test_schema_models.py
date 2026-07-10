from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, cast

import pytest
from pydantic import ValidationError

from ke.models.schema import (
    Column,
    DatabaseConfig,
    Relationship,
    SchemaInfo,
    Table,
    Tenant,
)


def _dt() -> datetime:
    return datetime.now(UTC)


class TestTenant:
    def test_valid_tenant(self) -> None:
        tenant = Tenant(
            id="abc-123",
            name="Acme Corp",
            slug="acme-corp",
            created_at=_dt(),
            updated_at=_dt(),
        )
        assert tenant.name == "Acme Corp"
        assert tenant.slug == "acme-corp"
        assert tenant.tier == "starter"
        assert tenant.status == "active"

    def test_slug_validation(self) -> None:
        with pytest.raises(ValidationError):
            Tenant(id="x", name="X", slug="INVALID SLUG!", created_at=_dt(), updated_at=_dt())

    def test_slug_with_trailing_hyphen(self) -> None:
        with pytest.raises(ValidationError):
            Tenant(id="x", name="X", slug="acme-", created_at=_dt(), updated_at=_dt())

    def test_valid_slug_patterns(self) -> None:
        for slug in ["a", "abc", "a-b", "abc123", "a1b2c3"]:
            tenant = Tenant(id="x", name="X", slug=slug, created_at=_dt(), updated_at=_dt())
            assert tenant.slug == slug

    def test_invalid_tier(self) -> None:
        with pytest.raises(ValidationError):
            Tenant(
                id="x",
                name="X",
                slug="acme",
                tier=cast(Any, "invalid"),
                created_at=_dt(),
                updated_at=_dt(),
            )

    def test_invalid_status(self) -> None:
        with pytest.raises(ValidationError):
            Tenant(
                id="x",
                name="X",
                slug="acme",
                status=cast(Any, "invalid"),
                created_at=_dt(),
                updated_at=_dt(),
            )

    def test_default_tier_and_status(self) -> None:
        tenant = Tenant(id="x", name="X", slug="acme", created_at=_dt(), updated_at=_dt())
        assert tenant.tier == "starter"
        assert tenant.status == "active"

    def test_settings_and_features_defaults(self) -> None:
        tenant = Tenant(id="x", name="X", slug="acme", created_at=_dt(), updated_at=_dt())
        assert tenant.settings == {}
        assert tenant.features == {}

    def test_deleted_at_nullable(self) -> None:
        tenant = Tenant(id="x", name="X", slug="acme", created_at=_dt(), updated_at=_dt())
        assert tenant.deleted_at is None

    def test_from_attributes(self) -> None:
        data = {
            "id": "x",
            "name": "X",
            "slug": "acme",
            "tier": "enterprise",
            "status": "active",
            "settings": {},
            "features": {},
            "created_at": _dt(),
            "updated_at": _dt(),
        }
        tenant = Tenant.model_validate(data, from_attributes=True)
        assert tenant.name == "X"

    def test_serialization_round_trip(self) -> None:
        tenant = Tenant(id="x", name="X", slug="acme", created_at=_dt(), updated_at=_dt())
        data = tenant.model_dump()
        restored = Tenant.model_validate(data)
        assert restored.name == "X"
        assert restored.slug == "acme"


class TestDatabaseConfig:
    def test_valid_config(self) -> None:
        cfg = DatabaseConfig(
            id="db-1",
            tenant_id="tnt-1",
            name="My DB",
            db_type="postgresql",
            connection_hash="abc123",
            created_at=_dt(),
            updated_at=_dt(),
        )
        assert cfg.name == "My DB"
        assert cfg.db_type == "postgresql"
        assert cfg.is_active is True
        assert cfg.sync_status == "pending"

    def test_invalid_db_type(self) -> None:
        with pytest.raises(ValidationError):
            DatabaseConfig(
                id="x",
                tenant_id="t",
                name="X",
                db_type=cast(Any, "oracle"),
                connection_hash="x",
                created_at=_dt(),
                updated_at=_dt(),
            )

    def test_invalid_sync_status(self) -> None:
        with pytest.raises(ValidationError):
            DatabaseConfig(
                id="x",
                tenant_id="t",
                name="X",
                db_type="postgresql",
                connection_hash="x",
                sync_status=cast(Any, "invalid"),
                created_at=_dt(),
                updated_at=_dt(),
            )

    def test_schema_filter_optional(self) -> None:
        cfg = DatabaseConfig(
            id="x",
            tenant_id="t",
            name="X",
            db_type="mysql",
            connection_hash="x",
            schema_filter=["public", "sales"],
            created_at=_dt(),
            updated_at=_dt(),
        )
        assert cfg.schema_filter == ["public", "sales"]

    def test_ssl_default_true(self) -> None:
        cfg = DatabaseConfig(
            id="x",
            tenant_id="t",
            name="X",
            db_type="postgresql",
            connection_hash="x",
            created_at=_dt(),
            updated_at=_dt(),
        )
        assert cfg.ssl_enabled is True

    def test_nullable_host_port(self) -> None:
        cfg = DatabaseConfig(
            id="x",
            tenant_id="t",
            name="X",
            db_type="postgresql",
            connection_hash="x",
            host="localhost",
            port=5432,
            created_at=_dt(),
            updated_at=_dt(),
        )
        assert cfg.host == "localhost"
        assert cfg.port == 5432

    def test_last_synced_at_nullable(self) -> None:
        cfg = DatabaseConfig(
            id="x",
            tenant_id="t",
            name="X",
            db_type="postgresql",
            connection_hash="x",
            created_at=_dt(),
            updated_at=_dt(),
        )
        assert cfg.last_synced_at is None

    def test_connection_options_default(self) -> None:
        cfg = DatabaseConfig(
            id="x",
            tenant_id="t",
            name="X",
            db_type="postgresql",
            connection_hash="x",
            created_at=_dt(),
            updated_at=_dt(),
        )
        assert cfg.connection_options == {}

    def test_table_count_default(self) -> None:
        cfg = DatabaseConfig(
            id="x",
            tenant_id="t",
            name="X",
            db_type="postgresql",
            connection_hash="x",
            created_at=_dt(),
            updated_at=_dt(),
        )
        assert cfg.table_count == 0

    def test_serialization_round_trip(self) -> None:
        cfg = DatabaseConfig(
            id="x",
            tenant_id="t",
            name="X",
            db_type="postgresql",
            connection_hash="x",
            created_at=_dt(),
            updated_at=_dt(),
        )
        data = cfg.model_dump()
        restored = DatabaseConfig.model_validate(data)
        assert restored.db_type == "postgresql"


class TestSchemaInfo:
    def test_valid_schema_info(self) -> None:
        info = SchemaInfo(
            id="si-1",
            database_id="db-1",
            name="public",
            created_at=_dt(),
            updated_at=_dt(),
        )
        assert info.name == "public"
        assert info.version == 1
        assert info.table_count == 0

    def test_raw_ddl_optional(self) -> None:
        info = SchemaInfo(
            id="x",
            database_id="d",
            name="public",
            raw_ddl="CREATE SCHEMA public;",
            created_at=_dt(),
            updated_at=_dt(),
        )
        assert info.raw_ddl == "CREATE SCHEMA public;"

    def test_version_increment(self) -> None:
        info = SchemaInfo(
            id="x",
            database_id="d",
            name="public",
            version=3,
            created_at=_dt(),
            updated_at=_dt(),
        )
        assert info.version == 3

    def test_serialization_round_trip(self) -> None:
        info = SchemaInfo(
            id="x",
            database_id="d",
            name="public",
            created_at=_dt(),
            updated_at=_dt(),
        )
        data = info.model_dump()
        restored = SchemaInfo.model_validate(data)
        assert restored.name == "public"


class TestTable:
    def test_valid_table(self) -> None:
        table = Table(
            id="tbl-1",
            schema_id="si-1",
            name="users",
            created_at=_dt(),
            updated_at=_dt(),
        )
        assert table.name == "users"
        assert table.version == 1
        assert table.is_active is True
        assert table.row_estimate == 0

    def test_description_optional(self) -> None:
        table = Table(
            id="x",
            schema_id="s",
            name="users",
            description="User accounts",
            created_at=_dt(),
            updated_at=_dt(),
        )
        assert table.description == "User accounts"

    def test_ddl_optional(self) -> None:
        table = Table(
            id="x",
            schema_id="s",
            name="users",
            ddl="CREATE TABLE users (...)",
            created_at=_dt(),
            updated_at=_dt(),
        )
        assert table.ddl is not None

    def test_is_active_false(self) -> None:
        table = Table(
            id="x",
            schema_id="s",
            name="deprecated",
            is_active=False,
            created_at=_dt(),
            updated_at=_dt(),
        )
        assert table.is_active is False

    def test_last_introspected_at_nullable(self) -> None:
        table = Table(
            id="x",
            schema_id="s",
            name="users",
            created_at=_dt(),
            updated_at=_dt(),
        )
        assert table.last_introspected_at is None

    def test_serialization_round_trip(self) -> None:
        table = Table(
            id="x",
            schema_id="s",
            name="users",
            created_at=_dt(),
            updated_at=_dt(),
        )
        data = table.model_dump()
        restored = Table.model_validate(data)
        assert restored.name == "users"
        assert restored.is_active is True


class TestColumn:
    def test_valid_column(self) -> None:
        col = Column(
            id="col-1",
            table_id="tbl-1",
            name="email",
            ordinal_position=1,
            data_type="varchar(255)",
            created_at=_dt(),
            updated_at=_dt(),
        )
        assert col.name == "email"
        assert col.ordinal_position == 1
        assert col.is_nullable is True
        assert col.is_primary_key is False

    def test_primary_key(self) -> None:
        col = Column(
            id="x",
            table_id="t",
            name="id",
            ordinal_position=1,
            data_type="uuid",
            is_primary_key=True,
            is_nullable=False,
            created_at=_dt(),
            updated_at=_dt(),
        )
        assert col.is_primary_key is True
        assert col.is_nullable is False

    def test_unique_constraint(self) -> None:
        col = Column(
            id="x",
            table_id="t",
            name="email",
            ordinal_position=2,
            data_type="varchar(255)",
            is_unique=True,
            created_at=_dt(),
            updated_at=_dt(),
        )
        assert col.is_unique is True

    def test_foreign_key(self) -> None:
        col = Column(
            id="x",
            table_id="t",
            name="user_id",
            ordinal_position=3,
            data_type="uuid",
            foreign_key_table="users",
            foreign_key_column="id",
            created_at=_dt(),
            updated_at=_dt(),
        )
        assert col.foreign_key_table == "users"
        assert col.foreign_key_column == "id"

    def test_numeric_types(self) -> None:
        col = Column(
            id="x",
            table_id="t",
            name="price",
            ordinal_position=4,
            data_type="decimal(10,2)",
            numeric_precision=10,
            numeric_scale=2,
            created_at=_dt(),
            updated_at=_dt(),
        )
        assert col.numeric_precision == 10
        assert col.numeric_scale == 2

    def test_character_max_length(self) -> None:
        col = Column(
            id="x",
            table_id="t",
            name="name",
            ordinal_position=5,
            data_type="varchar(100)",
            character_maximum_length=100,
            created_at=_dt(),
            updated_at=_dt(),
        )
        assert col.character_maximum_length == 100

    def test_default_value(self) -> None:
        col = Column(
            id="x",
            table_id="t",
            name="created_at",
            ordinal_position=6,
            data_type="timestamptz",
            default_value="NOW()",
            created_at=_dt(),
            updated_at=_dt(),
        )
        assert col.default_value == "NOW()"

    def test_serialization_round_trip(self) -> None:
        col = Column(
            id="x",
            table_id="t",
            name="email",
            ordinal_position=1,
            data_type="varchar(255)",
            created_at=_dt(),
            updated_at=_dt(),
        )
        data = col.model_dump()
        restored = Column.model_validate(data)
        assert restored.name == "email"
        assert restored.ordinal_position == 1


class TestRelationship:
    def test_valid_relationship(self) -> None:
        rel = Relationship(
            id="rel-1",
            tenant_id="tnt-1",
            source_table_id="src-1",
            source_column="user_id",
            target_table_id="tgt-1",
            target_column="id",
            created_at=_dt(),
        )
        assert rel.relationship_type == "foreign_key"
        assert rel.confidence == 1.0
        assert rel.discovered_by == "connector"

    def test_inferred_relationship(self) -> None:
        rel = Relationship(
            id="x",
            tenant_id="t",
            source_table_id="s",
            source_column="c",
            target_table_id="t",
            target_column="id",
            relationship_type="inferred",
            confidence=0.75,
            discovered_by="inferer",
            created_at=_dt(),
        )
        assert rel.relationship_type == "inferred"
        assert rel.confidence == 0.75
        assert rel.discovered_by == "inferer"

    def test_semantic_relationship(self) -> None:
        rel = Relationship(
            id="x",
            tenant_id="t",
            source_table_id="s",
            source_column="c",
            target_table_id="t",
            target_column="id",
            relationship_type="semantic",
            discovered_by="manual",
            created_at=_dt(),
        )
        assert rel.relationship_type == "semantic"
        assert rel.discovered_by == "manual"

    def test_invalid_relationship_type(self) -> None:
        with pytest.raises(ValidationError):
            Relationship(
                id="x",
                tenant_id="t",
                source_table_id="s",
                source_column="c",
                target_table_id="t",
                target_column="id",
                relationship_type=cast(Any, "invalid"),
                created_at=_dt(),
            )

    def test_confidence_out_of_range(self) -> None:
        with pytest.raises(ValidationError):
            Relationship(
                id="x",
                tenant_id="t",
                source_table_id="s",
                source_column="c",
                target_table_id="t",
                target_column="id",
                confidence=1.5,
                created_at=_dt(),
            )

    def test_confidence_zero(self) -> None:
        rel = Relationship(
            id="x",
            tenant_id="t",
            source_table_id="s",
            source_column="c",
            target_table_id="t",
            target_column="id",
            confidence=0.0,
            created_at=_dt(),
        )
        assert rel.confidence == 0.0

    def test_invalid_discovered_by(self) -> None:
        with pytest.raises(ValidationError):
            Relationship(
                id="x",
                tenant_id="t",
                source_table_id="s",
                source_column="c",
                target_table_id="t",
                target_column="id",
                discovered_by=cast(Any, "ai"),
                created_at=_dt(),
            )

    def test_properties_default(self) -> None:
        rel = Relationship(
            id="x",
            tenant_id="t",
            source_table_id="s",
            source_column="c",
            target_table_id="t",
            target_column="id",
            created_at=_dt(),
        )
        assert rel.properties == {}

    def test_properties_custom(self) -> None:
        rel = Relationship(
            id="x",
            tenant_id="t",
            source_table_id="s",
            source_column="c",
            target_table_id="t",
            target_column="id",
            properties={"cardinality": "many-to-one"},
            created_at=_dt(),
        )
        assert rel.properties["cardinality"] == "many-to-one"

    def test_no_updated_at_deleted_at(self) -> None:
        rel = Relationship(
            id="x",
            tenant_id="t",
            source_table_id="s",
            source_column="c",
            target_table_id="t",
            target_column="id",
            created_at=_dt(),
        )
        assert not hasattr(rel, "updated_at")
        assert not hasattr(rel, "deleted_at")

    def test_serialization_round_trip(self) -> None:
        rel = Relationship(
            id="x",
            tenant_id="t",
            source_table_id="s",
            source_column="c",
            target_table_id="t",
            target_column="id",
            created_at=_dt(),
        )
        data = rel.model_dump()
        restored = Relationship.model_validate(data)
        assert restored.source_column == "c"
        assert restored.target_table_id == "t"
        assert restored.confidence == 1.0
