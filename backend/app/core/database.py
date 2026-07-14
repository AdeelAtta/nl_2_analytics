from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings

settings = get_settings()

_dsn = settings.postgres_dsn
if "+" not in _dsn.split("://")[0]:
    _dsn = _dsn.replace("postgresql://", "postgresql+asyncpg://", 1)

# Auto-add database column to query_history if not exists
try:
    _sync_engine = create_engine(settings.postgres_dsn_sync)
    with _sync_engine.connect() as conn:
        conn.execute(text("""
            ALTER TABLE query_store.query_history
            ADD COLUMN IF NOT EXISTS database VARCHAR(255) NOT NULL DEFAULT ''
        """))
        conn.commit()
    _sync_engine.dispose()
except Exception:
    import logging
    logging.getLogger(__name__).warning("Could not add database column to query_history")

engine = create_async_engine(
    _dsn,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    echo=settings.debug,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def check_db_health() -> bool:
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False

