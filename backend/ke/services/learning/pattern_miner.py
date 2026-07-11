from __future__ import annotations

import re
from collections import Counter
from typing import Any


class PatternMiner:
    def mine_join_patterns(
        self,
        feedback_items: list[dict[str, Any]],
        top_n: int = 10,
    ) -> list[dict[str, Any]]:
        joins: Counter = Counter()
        for item in feedback_items:
            sql = (item.get("sql") or "").lower()
            join_pairs = self._extract_joins(sql)
            for pair in join_pairs:
                joins[pair] += 1
        return [
            {"tables": pair.split("|"), "count": count}
            for pair, count in joins.most_common(top_n)
        ]

    def _extract_joins(self, sql: str) -> list[str]:
        pattern = re.compile(
            r"(?:join|inner\s+join|left\s+join|right\s+join|full\s+join)\s+(\w+)\s+"
            r"(?:\w+\s+)?on\s+(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)",
            re.I,
        )
        pairs: list[str] = []
        for m in pattern.finditer(sql):
            t1, t2 = sorted([m.group(2).lower(), m.group(4).lower()])
            pairs.append(f"{t1}|{t2}")
        return pairs

    def mine_table_frequencies(
        self,
        feedback_items: list[dict[str, Any]],
        top_n: int = 20,
    ) -> list[dict[str, Any]]:
        tables: Counter = Counter()
        for item in feedback_items:
            sql = (item.get("sql") or "").lower()
            found = set(re.findall(r"\b(?:from|join)\s+(\w+)", sql))
            for t in found:
                tables[t] += 1
        return [
            {"table": t, "count": c}
            for t, c in tables.most_common(top_n)
        ]
