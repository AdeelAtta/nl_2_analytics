from __future__ import annotations

from typing import Any

_schemas: dict[str, dict[str, Any]] = {}


def store_schema(tenant_id: str, tables: list[dict[str, Any]], columns: list[dict[str, Any]]) -> None:
    _schemas[tenant_id] = {"tables": tables, "columns": columns}


def get_schema(tenant_id: str) -> dict[str, Any] | None:
    return _schemas.get(tenant_id)


def has_schema(tenant_id: str) -> bool:
    return tenant_id in _schemas


def clear_schema(tenant_id: str) -> None:
    _schemas.pop(tenant_id, None)


def build_ddl(tables: list[dict[str, Any]], columns: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for tbl in tables:
        tbl_name = tbl["name"]
        tbl_cols = [c for c in columns if c.get("table_name", "").lower() == tbl_name.lower()]
        lines.append(f"CREATE TABLE {tbl_name} (")
        for col in tbl_cols:
            parts = [f"  {col['name']} {col['data_type']}"]
            if col.get("is_primary_key"):
                parts.append("PRIMARY KEY")
            if not col.get("is_nullable", True):
                parts.append("NOT NULL")
            lines.append(" ".join(parts))
        lines.append(");")
    return "\n".join(lines)
