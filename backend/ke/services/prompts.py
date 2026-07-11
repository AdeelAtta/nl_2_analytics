from __future__ import annotations

from typing import Any

SQL_GENERATION_TEMPLATE = """You are a SQL expert. Generate a {dialect} SQL query based on the user's request.

Database Schema:
{schema_ddl}

{conversation_history}
User Request: {query}

Query Intent: {intent_description}
Tables: {tables}
Filters: {filters}
Aggregations: {aggregations}
Joins: {joins}

Generate only the SQL query, no explanation. Use proper {dialect} syntax."""

SIMPLE_SQL_TEMPLATE = """Generate a {dialect} SQL query for: {query}

Schema:
{schema_ddl}
{conversation_history}
Return only the SQL query, no explanation."""

REFLECTION_TEMPLATE = """Review this {dialect} SQL query for correctness:

SQL: {sql}

Original Request: {query}

Schema:
{schema_ddl}

Check for:
1. Correct table and column names (match schema exactly)
2. Proper JOIN conditions
3. Correct aggregate functions with GROUP BY
4. Proper WHERE clause syntax
5. No ambiguous column references (use table aliases)

List any issues found. If the SQL is correct, respond with "VALID".
If issues exist, list them and provide the corrected SQL."""

TEMPLATES: dict[str, str] = {
    "simple": SIMPLE_SQL_TEMPLATE,
    "standard": SQL_GENERATION_TEMPLATE,
    "reflection": REFLECTION_TEMPLATE,
}


def format_schema_ddl(tables: list[dict[str, Any]], columns: list[dict[str, Any]], relationships: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for tbl in tables:
        tbl_name = tbl.get("name", "")
        tbl_cols = [c for c in columns if c.get("table_name", "") == tbl_name or c.get("table", "") == tbl_name]
        col_lines = []
        for col in tbl_cols:
            col_name = col.get("name", col.get("column", ""))
            col_type = col.get("data_type", col.get("type", "unknown"))
            nullable = col.get("nullable", True)
            pk = col.get("is_primary_key", col.get("primary_key", False))
            parts = [f"  {col_name} {col_type}"]
            if pk:
                parts.append("PK")
            if not nullable:
                parts.append("NOT NULL")
            col_lines.append(" ".join(parts))
        lines.append(f"CREATE TABLE {tbl_name} (")
        lines.extend(col_lines)
        lines.append(");")
        for rel in relationships:
            src = rel.get("source_table", "")
            tgt = rel.get("target_table", "")
            if src == tbl_name or tgt == tbl_name:
                src_col = rel.get("source_column", "id")
                tgt_col = rel.get("target_column", "id")
                lines.append(f"-- {src}.{src_col} -> {tgt}.{tgt_col}")
    return "\n".join(lines)


def format_intent_description(intent: dict[str, Any]) -> str:
    qtype = intent.get("query_type", "UNKNOWN")
    complexity = intent.get("complexity", "simple")
    return f"{qtype} query ({complexity} complexity)"
