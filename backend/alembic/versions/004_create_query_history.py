"""Create query_store schema with query_history and query_feedback tables.

Revision ID: 004
Revises: 003
Create Date: 2026-07-11
"""
# ruff: noqa: E501
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "004"
down_revision: str | None = "003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS query_store")

    op.create_table(
        "query_history",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column("user_id", sa.String(64), nullable=True),
        sa.Column("session_id", sa.String(64), nullable=True),
        sa.Column("query", sa.Text(), nullable=False),
        sa.Column("sql", sa.Text(), nullable=False, server_default=""),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("duration_ms", sa.Float(), nullable=False, server_default="0"),
        sa.Column("model_tier", sa.String(32), nullable=False, server_default="none"),
        sa.Column("model_name", sa.String(128), nullable=False, server_default=""),
        sa.Column("guard_passed", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("guard_stopped_at", sa.String(64), nullable=True),
        sa.Column("stage_data", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("has_feedback", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        schema="query_store",
    )
    op.create_index("idx_history_tenant", "query_history", ["tenant_id"], schema="query_store")
    op.create_index("idx_history_tenant_created", "query_history", ["tenant_id", "created_at"], schema="query_store")
    op.create_index("idx_history_status", "query_history", ["status"], schema="query_store")

    op.create_table(
        "query_feedback",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("query_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.String(64), nullable=True),
        sa.Column("rating", sa.Integer(), nullable=True),
        sa.Column("flag", sa.String(32), nullable=True),
        sa.Column("comment", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["query_id"], ["query_store.query_history.id"], ondelete="CASCADE"),
        schema="query_store",
    )
    op.create_index("idx_feedback_query", "query_feedback", ["query_id"], schema="query_store")

    op.execute("""
        ALTER TABLE query_store.query_history ENABLE ROW LEVEL SECURITY;
        CREATE POLICY tenant_isolation_query_history ON query_store.query_history
            AS PERMISSIVE FOR ALL TO public
            USING (tenant_id = current_setting('app.tenant_id'));
    """)
    op.execute("""
        ALTER TABLE query_store.query_feedback ENABLE ROW LEVEL SECURITY;
        CREATE POLICY tenant_isolation_query_feedback ON query_store.query_feedback
            AS PERMISSIVE FOR ALL TO public
            USING (
                EXISTS (
                    SELECT 1 FROM query_store.query_history
                    WHERE query_history.id = query_feedback.query_id
                      AND query_history.tenant_id = current_setting('app.tenant_id')
                )
            );
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS query_store.query_feedback CASCADE")
    op.execute("DROP TABLE IF EXISTS query_store.query_history CASCADE")
    op.execute("DROP SCHEMA IF EXISTS query_store CASCADE")
