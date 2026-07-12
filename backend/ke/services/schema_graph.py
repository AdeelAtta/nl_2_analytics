from __future__ import annotations

from typing import Any


class SchemaGraph:
    def __init__(self, tables: list[dict[str, Any]], columns: list[dict[str, Any]],
                 relationships: list[dict[str, Any]] | None = None) -> None:
        self._tables = {t["name"].lower(): t for t in tables}
        self._columns: dict[str, list[dict[str, Any]]] = {}
        for col in columns:
            t = col.get("table_name", "").lower()
            if t not in self._columns:
                self._columns[t] = []
            self._columns[t].append(col)
        self._relationships = relationships or []

    def find_join_path(self, table_a: str, table_b: str) -> list[dict[str, Any]]:
        a, b = table_a.lower(), table_b.lower()
        if a not in self._tables or b not in self._tables:
            return []

        visited: set[str] = set()
        paths: list[list[str]] = [[a]]

        for path in paths:
            current = path[-1]
            if current == b:
                return self._path_to_edges(path)
            if current in visited:
                continue
            visited.add(current)
            neighbors = self._get_neighbors(current)
            for n in neighbors:
                if n not in visited:
                    paths.append(path + [n])

        return []

    def _get_neighbors(self, table: str) -> list[str]:
        neighbors: set[str] = set()
        for rel in self._relationships:
            s = rel.get("source_table", "").lower()
            t = rel.get("target_table", "").lower()
            if s == table and t in self._tables:
                neighbors.add(t)
            if t == table and s in self._tables:
                neighbors.add(s)
        for col in self._columns.get(table, []):
            cname = col.get("name", "").lower()
            if cname.endswith("_id") and cname != "id":
                ref = cname[:-3]
                if ref in self._tables and ref != table:
                    neighbors.add(ref)
        return list(neighbors)

    def _path_to_edges(self, path: list[str]) -> list[dict[str, Any]]:
        edges: list[dict[str, Any]] = []
        for i in range(len(path) - 1):
            src, tgt = path[i], path[i + 1]
            edges.append({
                "source": src, "target": tgt,
                "source_column": self._find_join_column(src, tgt),
                "target_column": self._find_join_column(tgt, src, reverse=True),
            })
        return edges

    def _find_join_column(self, from_table: str, to_table: str, reverse: bool = False) -> str:
        for col in self._columns.get(from_table, []):
            cname = col.get("name", "").lower()
            if cname.endswith("_id") and cname[:-3] == to_table:
                return col.get("name", cname)
        if reverse:
            return "id"
        for col in self._columns.get(from_table, []):
            if col.get("is_primary_key"):
                return col.get("name", "id")
        return "id"

    def render_for_prompt(self) -> str:
        lines: list[str] = []
        for tbl_name, tbl in sorted(self._tables.items()):
            tbl_desc = tbl.get("description", "")
            desc_tag = f" -- {tbl_desc}" if tbl_desc else ""
            lines.append(f"TABLE {tbl['name']}{desc_tag}")
            lines.append(f"(")
            for col in self._columns.get(tbl_name, []):
                col_desc = col.get("description", "")
                desc = f" -- {col_desc}" if col_desc else ""
                pk = " PK" if col.get("is_primary_key") else ""
                nn = " NOT NULL" if not col.get("is_nullable", True) else ""
                lines.append(f"  {col['name']} {col['data_type']}{pk}{nn}{desc}")
            lines.append(f")")
            lines.append("")

        if self._relationships:
            lines.append("--- RELATIONSHIPS ---")
            for rel in self._relationships:
                lines.append(
                    f"  {rel['source_table']}.{rel['source_column']} "
                    f"-> {rel['target_table']}.{rel['target_column']}"
                )
        return "\n".join(lines)


def build_graph_from_registry(tenant_id: str) -> SchemaGraph | None:
    from ke.services.schema_registry import get_schema
    schema = get_schema(tenant_id)
    if not schema:
        return None
    return SchemaGraph(
        tables=schema.get("tables", []),
        columns=schema.get("columns", []),
        relationships=schema.get("relationships", []),
    )
