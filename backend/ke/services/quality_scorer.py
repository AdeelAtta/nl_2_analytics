from __future__ import annotations

import json
import re
import time
from typing import Any

from ke.models.planning import QueryIntent
from ke.models.quality import (
    QualityDimension,
    QualityDimensionScore,
    QualityScore,
)

try:
    from ke.services.inference import InferenceFactory, ModelClient
except ImportError:
    ModelClient = Any  # type: ignore[misc,assignment]
    InferenceFactory = None  # type: ignore[assignment]


QUALITY_JUDGE_TEMPLATE = """You are a SQL quality judge. Evaluate the following SQL query for the given user request.

User Request: {query}

Generated SQL:
{sql}

Schema:
{schema_ddl}

Rate each dimension from 0.0 (worst) to 1.0 (best):

1. correctness: Does the SQL correctly answer the user's question? Check table/column names match the schema.
2. efficiency: Is the SQL well-optimized? Avoid SELECT * unless needed, proper JOINs, WHERE filters.
3. safety: Does the SQL avoid dangerous patterns? No injection, proper scoping, read-only safe.
4. readability: Is the SQL well-formatted? Proper indentation, meaningful aliases, no unnecessary complexity.
5. schema_alignment: Does the SQL reference only tables/columns that exist in the schema?

Return ONLY valid JSON with this structure:
{{"dimensions": {{"correctness": 0.9, "efficiency": 0.7, "safety": 1.0, "readability": 0.8, "schema_alignment": 1.0}}, "issues": ["issue 1"], "suggestion": "optional fix"}}"""


class QueryQualityScorer:
    def __init__(
        self,
        llm_client: ModelClient | None = None,
        enable_llm: bool = True,
    ) -> None:
        self._llm_client = llm_client
        self._enable_llm = enable_llm

    async def score(
        self,
        sql: str,
        query: str,
        intent: QueryIntent | None = None,
        context: dict[str, Any] | None = None,
    ) -> QualityScore:
        start = time.perf_counter()
        llm_scores: dict[str, float] | None = None
        issues: list[str] = []
        suggestion = ""

        llm_was_used = False
        if self._enable_llm:
            try:
                parsed = await self._llm_judge(sql, query, context or {})
                if parsed[0] is not None:
                    llm_scores, issues, suggestion = parsed
                    llm_was_used = True
            except Exception:
                pass

        rule_scores = self._rule_scorer(sql, query, intent, context or {})

        dimensions: list[QualityDimensionScore] = []
        dim_names = [d.value for d in QualityDimension]
        for dim_name in dim_names:
            llm_val = (llm_scores or {}).get(dim_name)
            rule_val = rule_scores.get(dim_name, 0.0)
            if llm_val is not None:
                combined = round(llm_val * 0.6 + rule_val * 0.4, 4)
            else:
                combined = rule_val
            dim = QualityDimension(dim_name)
            reason_parts = []
            if llm_val is not None:
                reason_parts.append(f"LLM: {llm_val:.2f}")
            reason_parts.append(f"rules: {rule_val:.2f}")
            dimensions.append(QualityDimensionScore(
                dimension=dim,
                score=combined,
                reason=" | ".join(reason_parts),
                issues=[i for i in issues if dim_name in i.lower()] if issues else [],
            ))

        if llm_was_used and llm_scores and llm_scores.get("overall") is not None:
            overall = round(llm_scores["overall"] * 0.6 + self._rule_overall(sql, query, intent, context or {}) * 0.4, 4)
        else:
            overall = round(self._rule_overall(sql, query, intent, context or {}), 4)

        elapsed = (time.perf_counter() - start) * 1000
        return QualityScore(
            overall=overall,
            dimensions=dimensions,
            issues=issues,
            suggestion=suggestion,
            model="llm+rule" if llm_was_used else "rule_based",
            latency_ms=elapsed,
        )

    async def _llm_judge(
        self,
        sql: str,
        query: str,
        context: dict[str, Any],
    ) -> tuple[dict[str, float] | None, list[str], str]:
        schema_ddl = self._build_schema_ddl(context)
        prompt = QUALITY_JUDGE_TEMPLATE.format(
            query=query, sql=sql, schema_ddl=schema_ddl or "No schema available",
        )

        client = self._llm_client or InferenceFactory.create("mock", "quality-judge", 0.0)
        raw = await client.generate(prompt)

        parsed = self._parse_llm_response(raw)
        dims = parsed.get("dimensions", {})
        issues = parsed.get("issues", [])
        suggestion = parsed.get("suggestion", "")

        if isinstance(dims, dict) and dims:
            correct = float(dims.get("correctness", 0.5))
            efficient = float(dims.get("efficiency", 0.5))
            safe = float(dims.get("safety", 0.5))
            readable = float(dims.get("readability", 0.5))
            aligned = float(dims.get("schema_alignment", 0.5))
            overall = (correct * 0.35 + efficient * 0.20 + safe * 0.20 + readable * 0.10 + aligned * 0.15)
            return {
                "correctness": correct,
                "efficiency": efficient,
                "safety": safe,
                "readability": readable,
                "schema_alignment": aligned,
                "overall": round(overall, 4),
            }, issues, suggestion

        return None, [], ""

    @staticmethod
    def _parse_llm_response(raw: str) -> dict[str, Any]:
        json_match = re.search(r"\{.*\}", raw, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        return {}

    def _rule_scorer(
        self,
        sql: str,
        query: str,
        intent: QueryIntent | None,
        context: dict[str, Any],
    ) -> dict[str, float]:
        if not sql or not sql.strip():
            return {d.value: 0.0 for d in QualityDimension}

        correctness = self._score_correctness(sql, query, context)
        efficiency = self._score_efficiency(sql, context)
        safety = self._score_safety(sql)
        readability = self._score_readability(sql)
        alignment = self._score_schema_alignment(sql, context)

        return {
            "correctness": correctness,
            "efficiency": efficiency,
            "safety": safety,
            "readability": readability,
            "schema_alignment": alignment,
        }

    def _rule_overall(
        self,
        sql: str,
        query: str,
        intent: QueryIntent | None,
        context: dict[str, Any],
    ) -> float:
        dims = self._rule_scorer(sql, query, intent, context)
        return round(
            dims["correctness"] * 0.35
            + dims["efficiency"] * 0.20
            + dims["safety"] * 0.20
            + dims["readability"] * 0.10
            + dims["schema_alignment"] * 0.15,
            4,
        )

    @staticmethod
    def _score_correctness(sql: str, query: str, context: dict[str, Any]) -> float:
        score = 0.5
        sql_lower = sql.lower()
        keywords = _extract_keywords(query)
        if keywords:
            matches = sum(1 for kw in keywords if kw in sql_lower)
            score += (matches / len(keywords)) * 0.3

        table_names = [t.get("name", "") for t in (context.get("tables") or [])]
        if table_names:
            table_hits = sum(1 for t in table_names if t.lower() in sql_lower)
            if table_hits > 0:
                score += 0.2 * (table_hits / len(table_names))

        column_names = [c.get("name", "") for c in (context.get("columns") or [])]
        if column_names:
            col_hits = sum(1 for c in column_names if c.lower() in sql_lower)
            if col_hits > 0:
                score += 0.1 * min(col_hits / max(len(column_names), 1), 1.0)

        safe_commands = ("select", "with", "explain", "show")
        if not sql_lower.strip().startswith(safe_commands):
            score -= 0.3

        return max(0.0, min(1.0, score))

    @staticmethod
    def _score_efficiency(sql: str, context: dict[str, Any]) -> float:
        score = 0.7
        sql_lower = sql.lower()

        if "select *" in sql_lower and "exists" not in sql_lower:
            score -= 0.2

        if "where" not in sql_lower and "join" not in sql_lower:
            score -= 0.1

        if "like '%" in sql_lower or "like '%" in sql_lower:
            score -= 0.1

        if "limit" in sql_lower:
            score += 0.1

        if "join" in sql_lower and "on" not in sql_lower:
            score -= 0.2

        if "order by" in sql_lower and "limit" not in sql_lower:
            score -= 0.1

        return max(0.0, min(1.0, score))

    @staticmethod
    def _score_safety(sql: str) -> float:
        score = 1.0
        sql_lower = sql.lower()

        dangerous = ["drop ", "truncate ", "delete ", "insert ", "update ", "alter ", "create ", "exec ", "execute ", "shutdown", "kill ", "pg_sleep", "waitfor delay"]
        for keyword in dangerous:
            if keyword in sql_lower:
                score -= 0.3

        inject_patterns = [r"or\s+1\s*=\s*1", r"or\s+'\w+'\s*=\s*'\w+'", r"--", r"/\*", r"union\s+select"]
        for pattern in inject_patterns:
            if re.search(pattern, sql_lower):
                score -= 0.2

        return max(0.0, min(1.0, score))

    @staticmethod
    def _score_readability(sql: str) -> float:
        score = 0.5

        if sql.strip().endswith(";"):
            score += 0.1

        keywords = ["select", "from", "where", "join", "on", "group by", "order by", "having", "limit"]
        for kw in keywords:
            if kw in sql.lower():
                score += 0.05

        if "\n" in sql:
            score += 0.15

        if re.search(r"\b\w+\s+as\s+\w+\b", sql, re.I):
            score += 0.1

        lines = sql.strip().split("\n")
        if len(lines) > 1:
            indented = sum(1 for l in lines[1:] if l.startswith("  ") or l.startswith("\t"))
            if indented > 0:
                score += 0.1

        return min(1.0, score)

    @staticmethod
    def _score_schema_alignment(sql: str, context: dict[str, Any]) -> float:
        score = 1.0
        table_names = [t.get("name", "").lower() for t in (context.get("tables") or [])]
        if not table_names:
            return score

        sql_lower = sql.lower()
        refs = re.findall(r"\bfrom\s+(\w+)", sql_lower) + re.findall(r"\bjoin\s+(\w+)", sql_lower)
        for ref in refs:
            if ref not in table_names:
                score -= 0.3

        return max(0.0, min(1.0, score))

    @staticmethod
    def _build_schema_ddl(context: dict[str, Any]) -> str:
        from ke.services.prompts import format_schema_ddl
        return format_schema_ddl(
            context.get("tables", []),
            context.get("columns", []),
            context.get("relationships", []),
        )


def _extract_keywords(query: str) -> list[str]:
    words = re.findall(r"\b[a-z]{3,}\b", query.lower())
    stopwords = {"the", "and", "for", "all", "from", "with", "that", "this", "show", "list", "get", "find", "display", "give", "me", "each", "per", "how", "many", "what", "which", "where", "have", "has", "who"}
    return [w for w in words if w not in stopwords]
