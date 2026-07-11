from __future__ import annotations

import hashlib
import re
from typing import Any

from ke.models.policy import PolicyLayerResult
from ke.services.policy.base import PolicyLayerBase


class L1IntentClassificationLayer(PolicyLayerBase):
    layer_number = 1
    layer_name = "intent_classification"

    async def check(self, sql: str, context: dict[str, Any] | None = None) -> PolicyLayerResult:
        sql_upper = sql.strip().upper()
        if not sql_upper:
            return PolicyLayerResult(passed=False, reason="Empty SQL")
        if sql_upper.startswith("SELECT"):
            return PolicyLayerResult(passed=True, reason="SELECT query allowed")
        if any(sql_upper.startswith(kw) for kw in ("INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "TRUNCATE", "MERGE", "CALL", "EXEC")):
            return PolicyLayerResult(passed=False, blocked=True, reason=f"Non-SELECT query type blocked: {sql_upper.split()[0]}")
        return PolicyLayerResult(passed=True, reason="Query passed intent check")


class L2SQLSanitizationLayer(PolicyLayerBase):
    layer_number = 2
    layer_name = "sql_sanitization"

    async def check(self, sql: str, context: dict[str, Any] | None = None) -> PolicyLayerResult:
        sanitized = sql
        sanitized = sanitized.replace("\x00", "")
        sanitized = re.sub(r"[\x01-\x08\x0B\x0C\x0E-\x1F]", "", sanitized)
        sanitized = re.sub(r"--.*", "", sanitized)
        sanitized = re.sub(r"#.*", "", sanitized)
        sanitized = re.sub(r"/\*.*?\*/", "", sanitized, flags=re.DOTALL)
        sanitized = sanitized.strip()
        sql_upper = sanitized.upper()

        injection_patterns = [
            r"\bOR\s+1\s*=\s*1\b",
            r"\bOR\s+['\"]\w+['\"]\s*=\s*['\"]\w+['\"]",
            r"\bUNION\s+(ALL\s+)?SELECT\b",
            r"\bINTO\s+(OUTFILE|DUMPFILE|LOAD\s+DATA)\b",
            r"\b(SLEEP|WAITFOR|BENCHMARK|PG_SLEEP)\s*\(",
            r"\bEXEC\s*\(",
            r"\bEXECUTE\s+",
            r"\bINFORMATION_SCHEMA\.",
            r"'\s*OR\s*'",
            r"\bLOAD_FILE\s*\(",
            r"\bINTO\s+@",
        ]
        for pattern in injection_patterns:
            if re.search(pattern, sql_upper, re.I):
                return PolicyLayerResult(
                    passed=False,
                    blocked=True,
                    reason="SQL injection pattern detected",
                    metadata={"sanitized_sql": sanitized, "original_sql": sql},
                )

        return PolicyLayerResult(
            passed=True,
            reason="SQL sanitized successfully",
            metadata={"sanitized_sql": sanitized, "original_sql": sql},
        )


class L3RBACSchemaScopingLayer(PolicyLayerBase):
    layer_number = 3
    layer_name = "rbac_schema_scoping"

    async def check(self, sql: str, context: dict[str, Any] | None = None) -> PolicyLayerResult:
        if not context:
            return PolicyLayerResult(passed=True, reason="No RBAC context available — skip")

        authorized_tables = context.get("authorized_tables", [])
        if not authorized_tables:
            return PolicyLayerResult(passed=True, reason="No authorized tables configured — skip")

        sql_lower = sql.lower()
        table_refs = re.findall(r"\b(from|join|into|update|table)\s+(\w+)", sql_lower, re.I)
        mentioned_tables = set()
        for keyword, tbl in table_refs:
            mentioned_tables.add(tbl.lower())

        allowed = {t.lower() for t in authorized_tables}
        unauthorized = mentioned_tables - allowed
        if unauthorized:
            return PolicyLayerResult(
                passed=False,
                blocked=True,
                reason=f"Unauthorized table(s) referenced: {', '.join(sorted(unauthorized))}",
                metadata={"unauthorized_tables": list(unauthorized), "authorized_tables": allowed},
            )

        return PolicyLayerResult(passed=True, reason="All table references are authorized")


class L4CostCeilingLayer(PolicyLayerBase):
    layer_number = 4
    layer_name = "cost_ceiling"

    MAX_ESTIMATED_ROWS = 10_000_000

    async def check(self, sql: str, context: dict[str, Any] | None = None) -> PolicyLayerResult:
        if not context:
            return PolicyLayerResult(passed=True, reason="No cost context — skip")

        estimated_rows = context.get("estimated_rows", 0)
        if estimated_rows > self.MAX_ESTIMATED_ROWS:
            return PolicyLayerResult(
                passed=False,
                blocked=True,
                reason=f"Estimated rows ({estimated_rows:,}) exceeds ceiling ({self.MAX_ESTIMATED_ROWS:,})",
                metadata={"estimated_rows": estimated_rows, "max_rows": self.MAX_ESTIMATED_ROWS},
            )

        return PolicyLayerResult(passed=True, reason=f"Estimated rows ({estimated_rows:,}) within ceiling")


class L5SQLValidationLayer(PolicyLayerBase):
    layer_number = 5
    layer_name = "sql_validation"

    async def check(self, sql: str, context: dict[str, Any] | None = None) -> PolicyLayerResult:
        try:
            import sqlglot

            parsed = sqlglot.parse_one(sql)
            if parsed is None:
                return PolicyLayerResult(passed=False, reason="SQL parsing returned None")
            return PolicyLayerResult(
                passed=True,
                reason="SQL parsed successfully",
                metadata={"ast_type": type(parsed).__name__},
            )
        except Exception as e:
            return PolicyLayerResult(
                passed=False,
                reason=f"SQL parse error: {e}",
                metadata={"error": str(e)},
            )


class L6ReadOnlyEnforcementLayer(PolicyLayerBase):
    layer_number = 6
    layer_name = "read_only_enforcement"

    DML_PATTERNS = [
        r"^\s*INSERT\s+INTO",
        r"^\s*UPDATE\s+",
        r"^\s*DELETE\s+FROM",
        r"^\s*MERGE\s+INTO",
        r"^\s*REPLACE\s+INTO",
        r"^\s*TRUNCATE\s+",
    ]

    DDL_PATTERNS = [
        r"^\s*CREATE\s+(TABLE|INDEX|VIEW|SCHEMA|DATABASE|FUNCTION|PROCEDURE|TRIGGER|EVENT)",
        r"^\s*ALTER\s+(TABLE|INDEX|VIEW|SCHEMA|DATABASE|FUNCTION|PROCEDURE|TRIGGER)",
        r"^\s*DROP\s+(TABLE|INDEX|VIEW|SCHEMA|DATABASE|FUNCTION|PROCEDURE|TRIGGER)",
    ]

    DCL_PATTERNS = [
        r"^\s*GRANT\s+",
        r"^\s*REVOKE\s+",
        r"^\s*DENY\s+",
    ]

    async def check(self, sql: str, context: dict[str, Any] | None = None) -> PolicyLayerResult:
        sql_trimmed = sql.strip()
        sql_upper = sql_trimmed.upper()

        all_blocked = self.DML_PATTERNS + self.DDL_PATTERNS + self.DCL_PATTERNS
        for pattern in all_blocked:
            if re.search(pattern, sql_trimmed, re.I):
                kw = sql_upper.split()[0]
                return PolicyLayerResult(
                    passed=False,
                    blocked=True,
                    reason=f"Read-only violation: {kw} statements are not allowed",
                    metadata={"statement_type": kw},
                )

        return PolicyLayerResult(passed=True, reason="Query is read-only (SELECT)")


class L7AuditLoggingLayer(PolicyLayerBase):
    layer_number = 7
    layer_name = "audit_logging"

    async def check(self, sql: str, context: dict[str, Any] | None = None) -> PolicyLayerResult:
        tenant_id = (context or {}).get("tenant_id", "unknown")
        user_id = (context or {}).get("user_id", "unknown")
        query_hash = hashlib.sha256(sql.encode()).hexdigest()[:16]
        decision = "pass"

        log_entry = {
            "tenant_id": tenant_id,
            "user_id": user_id,
            "query_hash": query_hash,
            "sql_preview": sql[:200],
            "decision": decision,
            "timestamp": str(__import__("datetime").datetime.now()),
        }

        return PolicyLayerResult(
            passed=True,
            reason="Query logged",
            metadata={"log_entry": log_entry},
        )


class L8DataClassificationLayer(PolicyLayerBase):
    layer_number = 8
    layer_name = "data_classification"

    PII_COLUMN_PATTERNS = {
        "email": r"\bemail\b",
        "phone": r"\b(phone|telephone|mobile|cell|contact_number)\b",
        "ssn": r"\b(ssn|social_security)\b",
        "credit_card": r"\b(credit_card|cc_number|card_number|pan)\b",
        "password": r"\b(password|passwd|pwd)\b",
        "date_of_birth": r"\b(dob|date_of_birth|birth_date|birthday)\b",
        "address": r"\b(address|street|city|state|zip|postal_code)\b",
        "name": r"\b(full_name|first_name|last_name|middle_name|customer_name)\b",
        "bank_account": r"\b(bank_account|account_number|routing_number)\b",
        "ip_address": r"\b(ip_address|client_ip|remote_addr)\b",
        "health": r"\b(health|medical|diagnosis|condition|treatment)\b",
        "financial": r"\b(salary|income|credit_score|fico)\b",
    }

    async def check(self, sql: str, context: dict[str, Any] | None = None) -> PolicyLayerResult:
        if not context:
            return PolicyLayerResult(passed=True, reason="No schema context — skip")

        columns = context.get("columns", [])
        if not columns:
            return PolicyLayerResult(passed=True, reason="No columns to classify")

        pii_columns_found = []
        for col in columns:
            col_name = col.get("name", "") if isinstance(col, dict) else getattr(col, "name", "")
            col_lower = col_name.lower()
            for category, pattern in self.PII_COLUMN_PATTERNS.items():
                if re.search(pattern, col_lower):
                    sql_lower = sql.lower()
                    if col_lower in sql_lower:
                        pii_columns_found.append({"column": col_name, "category": category})
                    break

        if pii_columns_found:
            return PolicyLayerResult(
                passed=True,
                reason=f"PII columns detected in query: {len(pii_columns_found)} field(s)",
                metadata={"pii_columns": pii_columns_found, "pii_count": len(pii_columns_found)},
            )

        return PolicyLayerResult(passed=True, reason="No PII columns referenced")


class L9AdvancedValidationLayer(PolicyLayerBase):
    layer_number = 9
    layer_name = "advanced_validation"

    DANGEROUS_FUNCTIONS = [
        r"\b(LOAD_FILE|UNION|INTO\s+OUTFILE|INTO\s+DUMPFILE|PG_SLEEP|SLEEP|WAITFOR|BENCHMARK|EXEC|EXECUTE|SP_EXECUTESQL|XP_CMDSHELL)\b",
    ]

    SQL_ALLOWLIST: list[str] = []

    SQL_DENYLIST: list[str] = [
        r"\bEXEC\b",
        r"\bEXECUTE\b",
        r"\bEXEC\s*\(",
        r"\bSP_EXECUTESQL\b",
        r"\bXP_CMDSHELL\b",
    ]

    async def check(self, sql: str, context: dict[str, Any] | None = None) -> PolicyLayerResult:
        sql_upper = sql.upper()

        for pattern in self.DANGEROUS_FUNCTIONS:
            if re.search(pattern, sql_upper):
                return PolicyLayerResult(
                    passed=False,
                    blocked=True,
                    reason="Dangerous function detected",
                    metadata={"pattern": pattern},
                )

        allowlist = (context or {}).get("sql_allowlist", self.SQL_ALLOWLIST)
        if allowlist:
            sql_normalized = re.sub(r"\s+", " ", sql.strip()).lower()
            allowed = False
            for entry in allowlist:
                if entry.lower() in sql_normalized:
                    allowed = True
                    break
            if not allowed:
                return PolicyLayerResult(
                    passed=False,
                    blocked=True,
                    reason="SQL does not match any allowlist entry",
                    metadata={"allowlist": allowlist},
                )

        return PolicyLayerResult(passed=True, reason="Advanced validation passed")


class L10AnomalyDetectionLayer(PolicyLayerBase):
    layer_number = 10
    layer_name = "anomaly_detection"

    async def check(self, sql: str, context: dict[str, Any] | None = None) -> PolicyLayerResult:
        if not context:
            return PolicyLayerResult(passed=True, reason="No historical data — skip")

        recent_queries = context.get("recent_queries", [])
        if not recent_queries:
            return PolicyLayerResult(passed=True, reason="No baseline queries yet — skip")

        current_length = len(sql)
        lengths = [len(q) for q in recent_queries[-100:]]
        if not lengths:
            return PolicyLayerResult(passed=True, reason="No length baseline — skip")

        mean = sum(lengths) / len(lengths)
        variance = sum((x - mean) ** 2 for x in lengths) / len(lengths)
        std_dev = variance ** 0.5

        if std_dev > 0 and abs(current_length - mean) > 2 * std_dev:
            return PolicyLayerResult(
                passed=False,
                reason=f"Query length anomaly: {current_length} chars vs baseline mean {mean:.0f} ± {std_dev:.0f}",
                metadata={"current_length": current_length, "mean": mean, "std_dev": std_dev, "z_score": (current_length - mean) / std_dev if std_dev > 0 else 0},
            )

        return PolicyLayerResult(
            passed=True,
            reason="No anomaly detected",
            metadata={"current_length": current_length, "baseline_mean": mean},
        )
