from __future__ import annotations

import uuid
from typing import Any

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from unittest.mock import AsyncMock

from app.core.config import get_settings
from ke.models.execution import ExecutionResult, ExecutionStatus
from ke.models.generation import GenerationResult, GenerationStatus
from ke.models.pipeline import PipelineStatus
from ke.models.planning import QueryIntent, QueryType, TableRef
from ke.services.executor import QueryExecutor
from ke.services.pipeline import PipelineOrchestrator
from ke.services.session import InMemorySessionService

TEST_USERS = [
    {"name": "Alice", "email": "alice@example.com"},
    {"name": "Bob", "email": "bob@example.com"},
    {"name": "Charlie", "email": "charlie@example.com"},
]

TEST_ORDERS = [
    {"user_id": 1, "product": "Widget A", "amount": 100.00},
    {"user_id": 1, "product": "Widget B", "amount": 50.00},
    {"user_id": 2, "product": "Gadget X", "amount": 200.00},
    {"user_id": 3, "product": "Widget A", "amount": 75.00},
]


@pytest_asyncio.fixture
async def e2e_setup() -> (
    tuple[AsyncEngine, str, str, dict[str, Any]]
):
    suffix = uuid.uuid4().hex[:8]
    users_table = f"e2e_users_{suffix}"
    orders_table = f"e2e_orders_{suffix}"

    settings = get_settings()
    engine = create_async_engine(settings.postgres_dsn, pool_pre_ping=True)

    async with engine.begin() as conn:
        await conn.execute(text(f"""
            CREATE TABLE {users_table} (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(200)
            )
        """))
        await conn.execute(text(f"""
            CREATE TABLE {orders_table} (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES {users_table}(id),
                product VARCHAR(200) NOT NULL,
                amount DECIMAL(10,2)
            )
        """))
        for row in TEST_USERS:
            await conn.execute(
                text(f"INSERT INTO {users_table} (name, email) VALUES (:name, :email)"),
                row,
            )
        for row in TEST_ORDERS:
            await conn.execute(
                text(f"INSERT INTO {orders_table} (user_id, product, amount) VALUES (:user_id, :product, :amount)"),
                row,
            )

    context: dict[str, Any] = {
        "tables": [
            {"id": "t1", "name": users_table},
            {"id": "t2", "name": orders_table},
        ],
        "columns": [
            {"name": "id", "table_name": users_table, "data_type": "integer"},
            {"name": "name", "table_name": users_table, "data_type": "varchar"},
            {"name": "email", "table_name": users_table, "data_type": "varchar"},
            {"name": "id", "table_name": orders_table, "data_type": "integer"},
            {"name": "user_id", "table_name": orders_table, "data_type": "integer"},
            {"name": "product", "table_name": orders_table, "data_type": "varchar"},
            {"name": "amount", "table_name": orders_table, "data_type": "decimal"},
        ],
        "relationships": [
            {
                "source_table": users_table,
                "source_column": "id",
                "target_table": orders_table,
                "target_column": "user_id",
                "relationship_type": "one_to_many",
            }
        ],
    }

    yield engine, users_table, orders_table, context

    async with engine.begin() as conn:
        await conn.execute(text(f"DROP TABLE IF EXISTS {orders_table} CASCADE"))
        await conn.execute(text(f"DROP TABLE IF EXISTS {users_table} CASCADE"))
    await engine.dispose()


class TestE2EPipeline:
    @pytest.mark.asyncio
    async def test_pipeline_executes_sql_against_real_db(
        self,
        e2e_setup: tuple[AsyncEngine, str, str, dict[str, Any]],
    ) -> None:
        _engine, users_table, _orders_table, context = e2e_setup
        orch = PipelineOrchestrator()

        result = await orch.execute(
            f"show me all {users_table}",
            context=context,
        )

        assert result.status == PipelineStatus.SUCCESS
        assert users_table in result.sql

        exec_stage = next(s for s in result.stages if s.name == "execute")
        assert exec_stage.status == "success"
        assert exec_stage.data["row_count"] == 3
        assert exec_stage.data["total_rows"] == 3

        classify_stage = next(s for s in result.stages if s.name == "classify")
        assert classify_stage.status == "success"

        plan_stage = next(s for s in result.stages if s.name == "plan")
        assert plan_stage.status == "success"

        gen_stage = next(s for s in result.stages if s.name == "generate")
        assert gen_stage.status == "success"
        assert gen_stage.data["sql"]

        guard_stage = next(s for s in result.stages if s.name == "guard")
        assert guard_stage.status == "success"
        assert guard_stage.data["passed"] is True

    @pytest.mark.asyncio
    async def test_dry_run(
        self,
        e2e_setup: tuple[AsyncEngine, str, str, dict[str, Any]],
    ) -> None:
        _engine, users_table, _orders_table, context = e2e_setup
        orch = PipelineOrchestrator()

        result = await orch.execute(
            f"show me all {users_table}",
            context=context,
            dry_run=True,
        )

        assert result.status == PipelineStatus.SUCCESS
        exec_stage = next(s for s in result.stages if s.name == "execute")
        assert exec_stage.status == "dry_run"

    @pytest.mark.asyncio
    async def test_ddl_is_blocked(
        self,
        e2e_setup: tuple[AsyncEngine, str, str, dict[str, Any]],
    ) -> None:
        _engine, users_table, _orders_table, _context = e2e_setup
        orch = PipelineOrchestrator()

        result = await orch.execute(f"DROP TABLE {users_table}")

        assert result.status == PipelineStatus.FAILED
        assert "DDL" in (result.error or "")

    @pytest.mark.asyncio
    async def test_pagination(
        self,
        e2e_setup: tuple[AsyncEngine, str, str, dict[str, Any]],
    ) -> None:
        _engine, users_table, _orders_table, context = e2e_setup
        orch = PipelineOrchestrator()

        result = await orch.execute(
            f"show me all {users_table}",
            context=context,
            page=1,
            page_size=2,
        )

        assert result.status == PipelineStatus.SUCCESS
        exec_stage = next(s for s in result.stages if s.name == "execute")
        assert exec_stage.status == "success"
        assert exec_stage.data["row_count"] <= 2
        assert exec_stage.data["total_rows"] == 3

    @pytest.mark.asyncio
    async def test_session_and_history(
        self,
        e2e_setup: tuple[AsyncEngine, str, str, dict[str, Any]],
    ) -> None:
        _engine, users_table, _orders_table, context = e2e_setup
        session_svc = InMemorySessionService()
        orch = PipelineOrchestrator()

        result1 = await orch.execute(
            f"show me all {users_table}",
            context=context,
            session_service=session_svc,
            session_id="e2e-test",
        )
        assert result1.status == PipelineStatus.SUCCESS
        assert result1.session_id == "e2e-test"

        result2 = await orch.execute(
            f"show me all {users_table}",
            context=context,
            session_service=session_svc,
            session_id="e2e-test",
        )

        assert result2.status == PipelineStatus.SUCCESS
        turns = session_svc._sessions.get("e2e-test", [])
        assert len(turns) == 2

    @pytest.mark.asyncio
    async def test_filtered_select(
        self,
        e2e_setup: tuple[AsyncEngine, str, str, dict[str, Any]],
    ) -> None:
        _engine, users_table, _orders_table, context = e2e_setup
        orch = PipelineOrchestrator()

        result = await orch.execute(
            f"find {users_table}",
            context=context,
        )

        assert result.status == PipelineStatus.SUCCESS
        assert users_table in result.sql
        exec_stage = next(s for s in result.stages if s.name == "execute")
        assert exec_stage.status == "success"

    @pytest.mark.asyncio
    async def test_syntax_error_from_db(
        self,
        e2e_setup: tuple[AsyncEngine, str, str, dict[str, Any]],
    ) -> None:
        _engine, _users_table, _orders_table, context = e2e_setup

        fake_gen = AsyncMock()
        fake_gen.generate.return_value = GenerationResult(
            id="fake", query="fake", sql="SELECT invalid SQL that will break",
            status=GenerationStatus.COMPLETED,
            model_tier="standard", model_name="mock",
            intent=QueryIntent(query_type=QueryType.SIMPLE_SELECT).model_dump(),
        )

        orch = PipelineOrchestrator()
        orch._generator = fake_gen

        result = await orch.execute("show users", context=context)

        assert result.status == PipelineStatus.FAILED
        exec_stage = next(s for s in result.stages if s.name == "execute")
        assert exec_stage.status == "error"

    @pytest.mark.asyncio
    async def test_timeout_from_db(
        self,
        e2e_setup: tuple[AsyncEngine, str, str, dict[str, Any]],
    ) -> None:
        _engine, users_table, _orders_table, context = e2e_setup

        fake_executor = AsyncMock(spec=QueryExecutor)
        fake_executor.execute.return_value = ExecutionResult(
            id="timeout", sql="SELECT 1",
            status=ExecutionStatus.TIMEOUT,
        )

        orch = PipelineOrchestrator()
        orch._executor = fake_executor

        result = await orch.execute(
            f"show me {users_table}",
            context=context,
            timeout=0.001,
        )

        assert result.status == PipelineStatus.FAILED
        exec_stage = next(s for s in result.stages if s.name == "execute")
        assert exec_stage.status == "timeout"
