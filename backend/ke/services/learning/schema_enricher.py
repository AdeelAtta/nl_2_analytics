from __future__ import annotations

import re
from typing import Any

from ke.stores.schema.repository import ColumnRepository, TableRepository


class SchemaEnricher:
    def __init__(
        self,
        table_repo: TableRepository,
        column_repo: ColumnRepository,
    ) -> None:
        self._table_repo = table_repo
        self._column_repo = column_repo

    async def enrich_from_feedback(
        self,
        feedback_items: list[dict[str, Any]],
    ) -> int:
        enriched_count = 0
        for item in feedback_items:
            comment = (item.get("comment") or "").strip()
            if not comment:
                continue
            table_name = self._extract_table(comment, item.get("sql", ""))
            column_desc = self._extract_column_description(comment)
            if table_name and column_desc:
                updated = await self._update_table_description(
                    item.get("tenant_id", "default"), table_name, column_desc,
                )
                if updated:
                    enriched_count += 1
        return enriched_count

    def _extract_table(self, comment: str, sql: str) -> str | None:
        m = re.search(r"\b(from|join|table)\s+(\w+)", sql, re.I)
        if m:
            return m.group(2)
        m2 = re.search(r"(?:table|about)\s+['\"]?(\w+)['\"]?", comment, re.I)
        if m2:
            return m2.group(1)
        return None

    def _extract_column_description(self, comment: str) -> str | None:
        patterns = [
            r"(?:means|is|contains|shows|represents)\s+(.+?)(?:\.|$)",
            r"description[:\s]+(.+?)(?:\.|$)",
        ]
        for pat in patterns:
            m = re.search(pat, comment, re.I)
            if m:
                return m.group(1).strip()
        return None if len(comment) > 100 else comment

    async def _update_table_description(
        self, tenant_id: str, table_name: str, description: str,
    ) -> bool:
        items, _ = await self._table_repo.list(
            filters={"name": table_name, "is_active": True},
        )
        if not items:
            return False
        tbl = items[0]
        if tbl.description:
            return False
        tbl.description = description
        await self._table_repo.update(tbl.id, tbl)
        return True
