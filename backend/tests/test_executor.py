from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from ke.models.execution import ExecutionStatus
from ke.services.executor import QueryExecutor


class TestQueryExecutor:
    @pytest.mark.asyncio
    async def test_empty_sql_returns_error(self) -> None:
        executor = QueryExecutor(dsn="postgresql+asyncpg://mock:mock@localhost:5432/mock")
        result = await executor.execute("")
        assert result.status == ExecutionStatus.ERROR
        assert result.error is not None
        assert result.error.code == "EXEC-001"

    @pytest.mark.asyncio
    async def test_whitespace_sql_returns_error(self) -> None:
        executor = QueryExecutor(dsn="postgresql+asyncpg://mock:mock@localhost:5432/mock")
        result = await executor.execute("   ")
        assert result.status == ExecutionStatus.ERROR

    def test_error_classification_syntax(self) -> None:
        executor = QueryExecutor()
        error = executor._classify_error(Exception("syntax error at or near"))
        assert error.code == "EXEC-001"

    def test_error_classification_permission(self) -> None:
        executor = QueryExecutor()
        error = executor._classify_error(Exception("permission denied for table"))
        assert error.code == "EXEC-004"

    def test_error_classification_connection(self) -> None:
        executor = QueryExecutor()
        error = executor._classify_error(Exception("could not connect to server"))
        assert error.code == "EXEC-003"

    def test_error_classification_not_found(self) -> None:
        executor = QueryExecutor()
        error = executor._classify_error(Exception("relation does not exist"))
        assert error.code == "EXEC-001"

    def test_error_classification_internal(self) -> None:
        executor = QueryExecutor()
        error = executor._classify_error(Exception("unknown error occurred"))
        assert error.code == "EXEC-500"

    def _make_engine(self, conn: AsyncMock) -> MagicMock:
        cm = AsyncMock()
        cm.__aenter__.return_value = conn
        cm.__aexit__.return_value = None
        engine = MagicMock()
        engine.begin.return_value = cm
        return engine

    @pytest.mark.asyncio
    async def test_injected_engine_with_results(self) -> None:
        mock_result = MagicMock()
        mock_result.returns_rows = True
        mock_result.keys.return_value = ["id", "name"]
        mock_result.fetchall.return_value = [(1, "alice"), (2, "bob")]

        async def mock_execute(*args, **kwargs):
            return mock_result

        mock_conn = AsyncMock()
        mock_conn.execute = mock_execute

        executor = QueryExecutor(engine=self._make_engine(mock_conn))
        result = await executor.execute("SELECT * FROM users")

        assert result.status == ExecutionStatus.SUCCESS
        assert result.columns == ["id", "name"]
        assert len(result.rows) == 2

    @pytest.mark.asyncio
    async def test_injected_engine_pagination(self) -> None:
        mock_result = MagicMock()
        mock_result.returns_rows = True
        mock_result.keys.return_value = ["id"]
        mock_result.fetchall.return_value = [(i,) for i in range(50)]

        async def mock_execute(*args, **kwargs):
            return mock_result

        mock_conn = AsyncMock()
        mock_conn.execute = mock_execute

        executor = QueryExecutor(engine=self._make_engine(mock_conn))
        result = await executor.execute("SELECT id FROM big_table", page=1, page_size=10)

        assert result.status == ExecutionStatus.SUCCESS
        assert len(result.rows) == 10
        assert result.total_rows == 50
        assert result.truncated is True

    @pytest.mark.asyncio
    async def test_injected_engine_dry_run(self) -> None:
        mock_row = MagicMock()
        mock_row._mapping = {"QUERY PLAN": "Seq Scan on users"}

        async def mock_execute(*args, **kwargs):
            mock_result = MagicMock()
            mock_result.fetchall.return_value = [mock_row]
            return mock_result

        mock_conn = AsyncMock()
        mock_conn.execute = mock_execute

        executor = QueryExecutor(engine=self._make_engine(mock_conn))
        result = await executor.execute("SELECT * FROM users", dry_run=True)

        assert result.status == ExecutionStatus.DRY_RUN
        assert result.explain_output is not None

    @pytest.mark.asyncio
    async def test_injected_engine_timeout(self) -> None:
        async def slow_execute(*args, **kwargs):
            import asyncio
            await asyncio.sleep(100)

        mock_conn = AsyncMock()
        mock_conn.execute = slow_execute

        executor = QueryExecutor(engine=self._make_engine(mock_conn))
        result = await executor.execute("SELECT 1", timeout=0.01)

        assert result.status == ExecutionStatus.TIMEOUT
        assert result.error is not None
        assert result.error.code == "EXEC-002"

    @pytest.mark.asyncio
    async def test_injected_engine_non_select(self) -> None:
        async def mock_execute(*args, **kwargs):
            mock_result = MagicMock()
            mock_result.returns_rows = False
            mock_result.rowcount = 1
            return mock_result

        mock_conn = AsyncMock()
        mock_conn.execute = mock_execute

        executor = QueryExecutor(engine=self._make_engine(mock_conn))
        result = await executor.execute("UPDATE users SET name = 'test' WHERE id = 1")

        assert result.status == ExecutionStatus.SUCCESS
        assert result.row_count == 1

    @pytest.mark.asyncio
    async def test_injected_engine_error(self) -> None:
        mock_conn = AsyncMock()
        mock_conn.execute.side_effect = Exception("syntax error at or near")

        executor = QueryExecutor(engine=self._make_engine(mock_conn))
        result = await executor.execute("SELECT invalid SQL")

        assert result.status == ExecutionStatus.ERROR
        assert result.error is not None
        assert result.error.code == "EXEC-001"
