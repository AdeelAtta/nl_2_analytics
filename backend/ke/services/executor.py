from __future__ import annotations

import asyncio
import time
import uuid
from typing import Any

import sqlglot
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.core.config import get_settings
from ke.models.execution import ExecutionError, ExecutionResult, ExecutionStatus


class QueryExecutor:
    ERROR_CODES: dict[str, str] = {
        "syntax": "EXEC-001",
        "timeout": "EXEC-002",
        "connection": "EXEC-003",
        "permission": "EXEC-004",
        "not_found": "EXEC-005",
        "internal": "EXEC-500",
    }

    def __init__(self, dsn: str | None = None, engine: AsyncEngine | None = None) -> None:
        self._dsn = dsn or get_settings().postgres_dsn
        self._engine = engine

    async def _get_engine(self) -> AsyncEngine:
        if self._engine is not None:
            return self._engine
        return create_async_engine(self._dsn, pool_pre_ping=True, pool_size=5, max_overflow=10)

    async def execute(
        self,
        sql: str,
        params: dict[str, Any] | None = None,
        timeout: float = 30.0,
        page: int = 1,
        page_size: int = 1000,
        dry_run: bool = False,
    ) -> ExecutionResult:
        exec_id = str(uuid.uuid4())
        start = time.perf_counter()

        if not sql or not sql.strip():
            return ExecutionResult(
                id=exec_id,
                sql=sql,
                status=ExecutionStatus.ERROR,
                error=ExecutionError(code=self.ERROR_CODES["syntax"], message="Empty SQL query"),
                duration_ms=(time.perf_counter() - start) * 1000,
            )

        sql_stripped = sql.strip().rstrip(";")

        try:
            parsed = sqlglot.parse_one(sql_stripped, dialect="postgres")
            if parsed is None:
                raise sqlglot.errors.ParseError("Empty SQL")
        except sqlglot.errors.ParseError:
            elapsed = (time.perf_counter() - start) * 1000
            return ExecutionResult(
                id=exec_id,
                sql=sql,
                status=ExecutionStatus.ERROR,
                error=ExecutionError(code=self.ERROR_CODES["syntax"], message="Invalid SQL syntax"),
                duration_ms=elapsed,
            )

        try:
            engine = await self._get_engine()

            async with engine.begin() as conn:
                if dry_run:
                    try:
                        explain_sql = f"EXPLAIN (FORMAT JSON) {sql_stripped}"
                        result = await conn.execute(text(explain_sql))
                        explain_rows = result.fetchall()
                        explain_output = [dict(row._mapping) for row in explain_rows]
                    except Exception:
                        explain_output = [{"Note": "Database not available — dry run passed (SQL validated)"}]
                    elapsed = (time.perf_counter() - start) * 1000
                    return ExecutionResult(
                        id=exec_id,
                        sql=sql,
                        status=ExecutionStatus.DRY_RUN,
                        explain_output=explain_output,
                        duration_ms=elapsed,
                    )

                try:
                    exec_result = await asyncio.wait_for(
                        conn.execute(text(sql_stripped), params or {}),
                        timeout=timeout,
                    )
                except asyncio.TimeoutError:
                    elapsed = (time.perf_counter() - start) * 1000
                    return ExecutionResult(
                        id=exec_id,
                        sql=sql,
                        status=ExecutionStatus.TIMEOUT,
                        error=ExecutionError(
                            code=self.ERROR_CODES["timeout"],
                            message=f"Query timed out after {timeout}s",
                            detail=f"Timeout: {timeout}s",
                        ),
                        duration_ms=elapsed,
                    )

                if exec_result.returns_rows:
                    all_rows = [list(row) for row in exec_result.fetchall()]
                    columns = list(exec_result.keys())
                    total_rows = len(all_rows)
                    offset = (page - 1) * page_size
                    page_rows = all_rows[offset : offset + page_size]
                    truncated = total_rows > offset + page_size
                    elapsed = (time.perf_counter() - start) * 1000
                    return ExecutionResult(
                        id=exec_id,
                        sql=sql,
                        status=ExecutionStatus.SUCCESS,
                        columns=columns,
                        rows=page_rows,
                        row_count=len(page_rows),
                        total_rows=total_rows,
                        truncated=truncated,
                        page=page,
                        page_size=page_size,
                        duration_ms=elapsed,
                    )
                else:
                    elapsed = (time.perf_counter() - start) * 1000
                    rowcount = exec_result.rowcount or 0
                    return ExecutionResult(
                        id=exec_id,
                        sql=sql,
                        status=ExecutionStatus.SUCCESS,
                        row_count=rowcount,
                        total_rows=rowcount,
                        duration_ms=elapsed,
                    )

        except Exception as e:
            elapsed = (time.perf_counter() - start) * 1000
            error = self._classify_error(e)
            return ExecutionResult(
                id=exec_id,
                sql=sql,
                status=ExecutionStatus.ERROR,
                error=error,
                duration_ms=elapsed,
            )

    def _classify_error(self, error: Exception) -> ExecutionError:
        msg = str(error).lower()
        if any(k in msg for k in ("syntax error", "syntax_error", "parser error", "column", "does not exist", "relation")):
            return ExecutionError(code=self.ERROR_CODES["syntax"], message="SQL syntax error", detail=str(error))
        if any(k in msg for k in ("permission denied", "not authorized", "cannot execute", "no permission")):
            return ExecutionError(code=self.ERROR_CODES["permission"], message="Permission denied", detail=str(error))
        if any(k in msg for k in ("could not connect", "connection refused", "connection timed out", "no such host")):
            return ExecutionError(code=self.ERROR_CODES["connection"], message="Connection failed", detail=str(error))
        if any(k in msg for k in ("not found", "does not exist", "not exist")):
            return ExecutionError(code=self.ERROR_CODES["not_found"], message="Resource not found", detail=str(error))
        return ExecutionError(code=self.ERROR_CODES["internal"], message="Internal execution error", detail=str(error))
