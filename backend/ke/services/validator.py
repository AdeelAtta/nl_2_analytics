from __future__ import annotations

import re
from typing import Any


def validate_sql_against_schema(sql: str, context: dict[str, Any] | None) -> list[str]:
    errors: list[str] = []
    if not sql or not context:
        return errors

    tables_in_schema = {t.get("name", "").lower() for t in context.get("tables", [])}
    columns_in_schema: dict[str, set[str]] = {}
    for col in context.get("columns", []):
        t = col.get("table_name", "").lower() if isinstance(col, dict) else ""
        c = col.get("name", "").lower() if isinstance(col, dict) else ""
        if t not in columns_in_schema:
            columns_in_schema[t] = set()
        columns_in_schema[t].add(c)

    sql_lower = sql.lower()

    # Extract referenced tables
    ref_tables = set()
    for m in re.finditer(r"\b(?:from|join|update|into)\s+(\w+)", sql_lower):
        t = m.group(1)
        if t not in ("select", "where", "set", "values", "on", "inner", "left", "right", "full", "cross", "outer", "join"):
            ref_tables.add(t)

    unknown_tables = ref_tables - tables_in_schema
    for t in sorted(unknown_tables):
        errors.append(f"Table '{t}' does not exist in the schema")

    # Extract qualified column references (table.column or table alias.column)
    for m in re.finditer(r"(\w+)\.(\w+)", sql_lower):
        tbl = m.group(1)
        col = m.group(2)
        if tbl in tables_in_schema:
            if col not in columns_in_schema.get(tbl, set()):
                errors.append(f"Column '{col}' does not exist in table '{tbl}'")

    # Check unqualified column names in SELECT (except functions like COUNT(*))
    select_match = re.search(r"select\s+(.*?)\s+from", sql_lower, re.DOTALL)
    if select_match:
        select_clause = select_match.group(1)
        for part in select_clause.split(","):
            part = part.strip()
            col = part.split(" as ")[0].strip()
            if "(" in col or col == "*":
                continue
            if "." not in col:
                exists = any(col in cols for cols in columns_in_schema.values())
                if not exists:
                    errors.append(f"Column '{col}' does not exist in the schema")

    return errors
