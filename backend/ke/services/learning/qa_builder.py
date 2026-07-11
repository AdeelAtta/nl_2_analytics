from __future__ import annotations

from typing import Any


class QAPair:
    def __init__(self, question: str, answer: str, tenant_id: str, source_query_id: str) -> None:
        self.question = question
        self.answer = answer
        self.tenant_id = tenant_id
        self.source_query_id = source_query_id


class QAPairBuilder:
    def build(self, feedback_items: list[dict[str, Any]]) -> list[QAPair]:
        pairs: list[QAPair] = []
        for item in feedback_items:
            query = (item.get("query") or "").strip()
            sql = (item.get("sql") or "").strip()
            rating = item.get("rating")
            if not query or not sql:
                continue
            if rating is not None and rating < 3:
                continue
            pairs.append(QAPair(
                question=query,
                answer=sql,
                tenant_id=item.get("tenant_id", "default"),
                source_query_id=item.get("query_id", ""),
            ))
        return pairs
