"""Create auth schema with users and tenants tables for persistent auth.

Revision ID: 007
Revises: 006
Create Date: 2026-07-13

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "007"
down_revision: str | None = "006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS auth")

    op.create_table(
        "tenants",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False, unique=True),
        sa.Column("owner_email", sa.String(255), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="auth",
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("name", sa.String(255), nullable=False, server_default=""),
        sa.Column("role", sa.String(50), nullable=False, server_default="user"),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["tenant_id"], ["auth.tenants.id"], ondelete="CASCADE"),
        schema="auth",
    )

    op.create_index("ix_users_email", "users", ["email"], schema="auth")


def downgrade() -> None:
    op.drop_table("users", schema="auth")
    op.drop_table("tenants", schema="auth")
    op.execute("DROP SCHEMA IF EXISTS auth")
