"""Integration tests for database connections.

These tests require running PostgreSQL, Redis, and Qdrant instances.
They are skipped by default unless INTEGRATION_TEST=1 is set.
"""

import os

import pytest
from sqlalchemy import text

from app.core.config import get_settings
from app.core.database import engine, get_qdrant, get_redis

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.skipif(
        os.environ.get("INTEGRATION_TEST") != "1",
        reason="Set INTEGRATION_TEST=1 to run integration tests",
    ),
]

settings = get_settings()


async def test_postgres_connection() -> None:
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1 AS val"))
        row = result.fetchone()
        assert row is not None
        assert row._mapping["val"] == 1


async def test_redis_connection() -> None:
    redis_conn = await get_redis()
    pong = await redis_conn.ping()
    assert pong is True


async def test_qdrant_connection() -> None:
    qdrant = await get_qdrant()
    result = await qdrant.get_collections()
    assert result is not None
