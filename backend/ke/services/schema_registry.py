from __future__ import annotations

import json
from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.core.config import get_settings

_settings = get_settings()
_engine = create_engine(_settings.postgres_dsn_sync, pool_pre_ping=True)

# Auto-create schema_cache table on module load (no migration needed)
try:
    with _engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS public.schema_cache (
                tenant_id VARCHAR(100) NOT NULL,
                db_name VARCHAR(255) NOT NULL DEFAULT '',
                data JSONB NOT NULL DEFAULT '{}',
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW(),
                PRIMARY KEY (tenant_id, db_name)
            )
        """))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_schema_cache_tenant ON public.schema_cache (tenant_id)"))
        conn.commit()
except Exception:
    import logging
    logging.getLogger(__name__).warning("Could not create schema_cache table — DB not available yet")


def _get_session() -> Session:
    return Session(_engine)


def _db_name(conn_info_or_name: dict[str, Any] | str) -> str:
    if isinstance(conn_info_or_name, dict):
        return conn_info_or_name.get("database", "") or conn_info_or_name.get("name", "")
    return conn_info_or_name


def store_schema(tenant_id: str, tables: list[dict[str, Any]], columns: list[dict[str, Any]],
                 relationships: list[dict[str, Any]] | None = None,
                 db_name: str = "") -> None:
    with _get_session() as session:
        row = session.execute(
            text("SELECT data FROM public.schema_cache WHERE tenant_id = :tid AND db_name = :db"),
            {"tid": tenant_id, "db": db_name},
        ).fetchone()
        data = dict(row[0]) if row else {}

        data["tables"] = tables
        data["columns"] = columns
        if relationships:
            data["relationships"] = relationships

        session.execute(
            text("""
                INSERT INTO public.schema_cache (tenant_id, db_name, data, updated_at)
                VALUES (:tid, :db, :data, NOW())
                ON CONFLICT (tenant_id, db_name)
                DO UPDATE SET data = :data, updated_at = NOW()
            """),
            {"tid": tenant_id, "db": db_name, "data": json.dumps(data)},
        )
        session.commit()


def get_sample_rows(tenant_id: str, table_name: str, db_name: str = "") -> list[dict[str, Any]]:
    with _get_session() as session:
        row = session.execute(
            text("SELECT data FROM public.schema_cache WHERE tenant_id = :tid AND db_name = :db"),
            {"tid": tenant_id, "db": db_name},
        ).fetchone()
        if not row:
            return []
        data = row[0]
        for t in data.get("tables", []):
            if t.get("name", "").lower() == table_name.lower():
                return t.get("sample_rows", [])
    return []


def store_connection(tenant_id: str, conn_info: dict[str, Any]) -> None:
    db_name = _db_name(conn_info)
    with _get_session() as session:
        row = session.execute(
            text("SELECT data FROM public.schema_cache WHERE tenant_id = :tid AND db_name = :db"),
            {"tid": tenant_id, "db": db_name},
        ).fetchone()
        data = dict(row[0]) if row else {}
        data["connection"] = conn_info

        session.execute(
            text("""
                INSERT INTO public.schema_cache (tenant_id, db_name, data, updated_at)
                VALUES (:tid, :db, :data, NOW())
                ON CONFLICT (tenant_id, db_name)
                DO UPDATE SET data = :data, updated_at = NOW()
            """),
            {"tid": tenant_id, "db": db_name, "data": json.dumps(data)},
        )
        session.commit()


def get_connection(tenant_id: str, db_name: str = "") -> dict[str, Any] | None:
    with _get_session() as session:
        row = session.execute(
            text("SELECT data FROM public.schema_cache WHERE tenant_id = :tid AND db_name = :db"),
            {"tid": tenant_id, "db": db_name},
        ).fetchone()
        if row and "connection" in row[0]:
            return dict(row[0]["connection"])
    return None


def get_schema(tenant_id: str, db_name: str = "") -> dict[str, Any] | None:
    with _get_session() as session:
        row = session.execute(
            text("SELECT data FROM public.schema_cache WHERE tenant_id = :tid AND db_name = :db"),
            {"tid": tenant_id, "db": db_name},
        ).fetchone()
        if row:
            return dict(row[0])
    return None


def has_schema(tenant_id: str, db_name: str = "") -> bool:
    with _get_session() as session:
        row = session.execute(
            text("SELECT 1 FROM public.schema_cache WHERE tenant_id = :tid AND db_name = :db"),
            {"tid": tenant_id, "db": db_name},
        ).fetchone()
        return row is not None


def list_databases(tenant_id: str) -> list[dict[str, Any]]:
    with _get_session() as session:
        rows = session.execute(
            text("SELECT db_name, data FROM public.schema_cache WHERE tenant_id = :tid ORDER BY updated_at DESC"),
            {"tid": tenant_id},
        ).fetchall()

        results: list[dict[str, Any]] = []
        for row in rows:
            db_name = row[0]
            data = row[1]
            conn = data.get("connection", {})
            tables = data.get("tables", [])
            results.append({
                "name": conn.get("name", db_name or "default"),
                "database": conn.get("database", db_name or "default"),
                "db_type": conn.get("db_type", "postgresql"),
                "host": conn.get("host", ""),
                "table_count": len(tables),
                "synced_at": str(conn.get("synced_at", "")),
            })
    return results


def clear_schema(tenant_id: str, db_name: str = "") -> None:
    with _get_session() as session:
        session.execute(
            text("DELETE FROM public.schema_cache WHERE tenant_id = :tid AND db_name = :db"),
            {"tid": tenant_id, "db": db_name},
        )
        session.commit()


def build_ddl(tables: list[dict[str, Any]], columns: list[dict[str, Any]],
              relationships: list[dict[str, Any]] | None = None) -> str:
    lines: list[str] = []
    for tbl in tables:
        tbl_name = tbl["name"]
        tbl_desc = tbl.get("description", "")
        tbl_cols = [c for c in columns if c.get("table_name", "").lower() == tbl_name.lower()]
        desc = f" -- {tbl_desc}" if tbl_desc else ""
        lines.append(f"CREATE TABLE {tbl_name}{desc} (")
        for col in tbl_cols:
            parts = [f"  {col['name']} {col['data_type']}"]
            if col.get("is_primary_key"):
                parts.append("PRIMARY KEY")
            if not col.get("is_nullable", True):
                parts.append("NOT NULL")
            col_desc = col.get("description", "")
            if col_desc:
                parts[-1] += f" -- {col_desc}"
            lines.append(" ".join(parts))
        lines.append(");")
        if relationships:
            for rel in relationships:
                if rel.get("source_table", "").lower() == tbl_name.lower():
                    lines.append(f"-- {rel['source_table']}.{rel['source_column']} -> "
                                 f"{rel['target_table']}.{rel['target_column']}")
    return "\n".join(lines)
