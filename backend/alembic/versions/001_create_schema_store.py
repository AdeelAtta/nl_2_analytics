"""Create schema_store schema and all 6 entity tables.

Revision ID: 001
Revises: None
Create Date: 2026-07-10

"""
# ruff: noqa: E501
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS schema_store")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    op.create_table(
        "tenants",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("tier", sa.String(50), nullable=False, server_default="starter"),
        sa.Column("status", sa.String(50), nullable=False, server_default="active"),
        sa.Column("settings", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb")),
        sa.Column("features", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("tier IN ('free', 'starter', 'pro', 'enterprise')", name="ck_tenants_tier"),
        sa.CheckConstraint("status IN ('active', 'suspended', 'deleting', 'deleted')", name="ck_tenants_status"),
        sa.CheckConstraint(
            "slug ~* '^[a-z0-9]([a-z0-9-]*[a-z0-9])?$'",
            name="ck_tenants_slug_format",
        ),
        schema="public",
    )
    op.create_index("uq_tenants_slug", "tenants", ["slug"], unique=True,
                    postgresql_where=sa.text("deleted_at IS NULL"), schema="public")
    op.create_index("idx_tenants_tier", "tenants", ["tier"],
                    postgresql_where=sa.text("deleted_at IS NULL"), schema="public")
    op.create_index("idx_tenants_status", "tenants", ["status"], schema="public")

    op.create_table(
        "databases",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("db_type", sa.String(50), nullable=False),
        sa.Column("connection_hash", sa.String(64), nullable=False),
        sa.Column("host", sa.String(255), nullable=True),
        sa.Column("port", sa.Integer(), nullable=True),
        sa.Column("database_name", sa.String(255), nullable=True),
        sa.Column("username", sa.String(255), nullable=True),
        sa.Column("schema_filter", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("ssl_enabled", sa.Boolean(), nullable=False, server_default=sa.text("TRUE")),
        sa.Column("connection_options", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb")),
        sa.Column("sync_status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("sync_error_message", sa.Text(), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("table_count", sa.Integer(), server_default=sa.text("0")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("TRUE")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["public.tenants.id"], ondelete="CASCADE"),
        sa.CheckConstraint(
            "db_type IN ('postgresql', 'mysql', 'snowflake', 'bigquery', 'duckdb')",
            name="ck_databases_type",
        ),
        sa.CheckConstraint(
            "sync_status IN ('pending', 'syncing', 'synced', 'error')",
            name="ck_databases_sync_status",
        ),
        schema="schema_store",
    )
    op.create_index("idx_databases_tenant", "databases", ["tenant_id"],
                    postgresql_where=sa.text("deleted_at IS NULL"), schema="schema_store")
    op.create_index("idx_databases_type", "databases", ["db_type"],
                    postgresql_where=sa.text("deleted_at IS NULL"), schema="schema_store")
    op.create_index("idx_databases_status", "databases", ["sync_status"], schema="schema_store")
    op.create_index("idx_databases_conn_hash", "databases", ["connection_hash"], schema="schema_store")
    op.create_index("uq_databases_tenant_name", "databases", ["tenant_id", "name"], unique=True,
                    postgresql_where=sa.text("deleted_at IS NULL"), schema="schema_store")

    op.create_table(
        "schema_infos",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("database_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("raw_ddl", sa.Text(), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("table_count", sa.Integer(), server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["database_id"], ["schema_store.databases.id"], ondelete="CASCADE"),
        schema="schema_store",
    )
    op.create_index("idx_schema_infos_database", "schema_infos", ["database_id"], schema="schema_store")
    op.create_index("uq_schema_infos_db_name", "schema_infos", ["database_id", "name"], unique=True,
                    schema="schema_store")

    op.create_table(
        "tables",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("schema_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("ddl", sa.Text(), nullable=True),
        sa.Column("row_estimate", sa.BigInteger(), server_default=sa.text("0")),
        sa.Column("version", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("TRUE")),
        sa.Column("last_introspected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["schema_id"], ["schema_store.schema_infos.id"], ondelete="CASCADE"),
        schema="schema_store",
    )
    op.create_index("idx_tables_schema", "tables", ["schema_id"], schema="schema_store")
    op.create_index("idx_tables_active", "tables", ["is_active"],
                    postgresql_where=sa.text("is_active = TRUE"), schema="schema_store")
    op.create_index("idx_tables_updated", "tables", ["updated_at"], schema="schema_store")
    op.create_index("idx_tables_name_search", "tables", ["name"],
                    postgresql_using="gin", postgresql_ops={"name": "gin_trgm_ops"},
                    schema="schema_store")
    op.create_index("uq_tables_schema_name", "tables", ["schema_id", "name"], unique=True,
                    schema="schema_store")

    op.create_table(
        "columns",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("table_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("ordinal_position", sa.Integer(), nullable=False),
        sa.Column("data_type", sa.String(100), nullable=False),
        sa.Column("is_nullable", sa.Boolean(), nullable=False, server_default=sa.text("TRUE")),
        sa.Column("is_primary_key", sa.Boolean(), nullable=False, server_default=sa.text("FALSE")),
        sa.Column("is_unique", sa.Boolean(), nullable=False, server_default=sa.text("FALSE")),
        sa.Column("default_value", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("foreign_key_table", sa.String(255), nullable=True),
        sa.Column("foreign_key_column", sa.String(255), nullable=True),
        sa.Column("character_maximum_length", sa.Integer(), nullable=True),
        sa.Column("numeric_precision", sa.Integer(), nullable=True),
        sa.Column("numeric_scale", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["table_id"], ["schema_store.tables.id"], ondelete="CASCADE"),
        schema="schema_store",
    )
    op.create_index("idx_columns_table", "columns", ["table_id"], schema="schema_store")
    op.create_index("idx_columns_pk", "columns", ["table_id"],
                    postgresql_where=sa.text("is_primary_key = TRUE"), schema="schema_store")
    op.create_index("idx_columns_fk", "columns", ["foreign_key_table", "foreign_key_column"],
                    postgresql_where=sa.text("foreign_key_table IS NOT NULL"), schema="schema_store")
    op.create_index("idx_columns_name_search", "columns", ["name"],
                    postgresql_using="gin", postgresql_ops={"name": "gin_trgm_ops"},
                    schema="schema_store")
    op.create_index("idx_columns_data_type", "columns", ["data_type"], schema="schema_store")
    op.create_index("uq_columns_table_name", "columns", ["table_id", "name"], unique=True,
                    schema="schema_store")

    op.create_table(
        "relationships",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("source_table_id", sa.Uuid(), nullable=False),
        sa.Column("source_column", sa.String(255), nullable=False),
        sa.Column("target_table_id", sa.Uuid(), nullable=False),
        sa.Column("target_column", sa.String(255), nullable=False),
        sa.Column("relationship_type", sa.String(50), nullable=False, server_default="foreign_key"),
        sa.Column("confidence", sa.Float(), nullable=False, server_default=sa.text("1.0")),
        sa.Column("discovered_by", sa.String(100), nullable=False, server_default="connector"),
        sa.Column("properties", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["tenant_id"], ["public.tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_table_id"], ["schema_store.tables.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["target_table_id"], ["schema_store.tables.id"], ondelete="CASCADE"),
        sa.CheckConstraint(
            "relationship_type IN ('foreign_key', 'inferred', 'semantic')",
            name="ck_relationships_type",
        ),
        sa.CheckConstraint(
            "confidence >= 0.0 AND confidence <= 1.0",
            name="ck_relationships_confidence",
        ),
        schema="schema_store",
    )
    op.create_index("idx_relationships_tenant", "relationships", ["tenant_id"], schema="schema_store")
    op.create_index("idx_relationships_source", "relationships", ["source_table_id"], schema="schema_store")
    op.create_index("idx_relationships_target", "relationships", ["target_table_id"], schema="schema_store")
    op.create_index("idx_relationships_type", "relationships", ["relationship_type"], schema="schema_store")
    op.create_index("uq_relationships_columns", "relationships",
                    ["source_table_id", "source_column", "target_table_id", "target_column"],
                    unique=True, schema="schema_store")

    op.execute("""
        ALTER TABLE schema_store.databases ENABLE ROW LEVEL SECURITY;
        CREATE POLICY tenant_isolation ON schema_store.databases
            AS PERMISSIVE FOR ALL TO public
            USING (tenant_id = current_setting('app.tenant_id')::UUID);
    """)
    op.execute("""
        ALTER TABLE schema_store.schema_infos ENABLE ROW LEVEL SECURITY;
        CREATE POLICY tenant_isolation_inherited ON schema_store.schema_infos
            AS PERMISSIVE FOR ALL TO public
            USING (
                EXISTS (
                    SELECT 1 FROM schema_store.databases
                    WHERE databases.id = schema_infos.database_id
                      AND databases.tenant_id = current_setting('app.tenant_id')::UUID
                )
            );
    """)
    op.execute("""
        ALTER TABLE schema_store.tables ENABLE ROW LEVEL SECURITY;
        CREATE POLICY tenant_isolation_inherited ON schema_store.tables
            AS PERMISSIVE FOR ALL TO public
            USING (
                EXISTS (
                    SELECT 1 FROM schema_store.schema_infos
                    JOIN schema_store.databases ON databases.id = schema_infos.database_id
                    WHERE schema_infos.id = tables.schema_id
                      AND databases.tenant_id = current_setting('app.tenant_id')::UUID
                )
            );
    """)
    op.execute("""
        ALTER TABLE schema_store.columns ENABLE ROW LEVEL SECURITY;
        CREATE POLICY tenant_isolation_inherited ON schema_store.columns
            AS PERMISSIVE FOR ALL TO public
            USING (
                EXISTS (
                    SELECT 1 FROM schema_store.tables
                    JOIN schema_store.schema_infos ON schema_infos.id = tables.schema_id
                    JOIN schema_store.databases ON databases.id = schema_infos.database_id
                    WHERE tables.id = columns.table_id
                      AND databases.tenant_id = current_setting('app.tenant_id')::UUID
                )
            );
    """)
    op.execute("""
        ALTER TABLE schema_store.relationships ENABLE ROW LEVEL SECURITY;
        CREATE POLICY tenant_isolation ON schema_store.relationships
            AS PERMISSIVE FOR ALL TO public
            USING (tenant_id = current_setting('app.tenant_id')::UUID);
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS schema_store.relationships CASCADE")
    op.execute("DROP TABLE IF EXISTS schema_store.columns CASCADE")
    op.execute("DROP TABLE IF EXISTS schema_store.tables CASCADE")
    op.execute("DROP TABLE IF EXISTS schema_store.schema_infos CASCADE")
    op.execute("DROP TABLE IF EXISTS schema_store.databases CASCADE")
    op.execute("DROP TABLE IF EXISTS public.tenants CASCADE")
    op.execute("DROP SCHEMA IF EXISTS schema_store")
