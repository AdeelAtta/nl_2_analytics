#!/usr/bin/env python3
"""Async seed script for initial data population."""

import asyncio

import structlog
from sqlalchemy import text

from app.core.config import get_settings
from app.core.database import async_session_factory, engine

logger = structlog.get_logger()
settings = get_settings()


async def seed() -> None:
    logger.info("seed_started", dsn=settings.postgres_dsn)
    async with async_session_factory() as session:
        result = await session.execute(text("SELECT 1"))
        logger.info("seed_connection_ok", result=result.scalar())
    logger.info("seed_completed")


async def main() -> None:
    try:
        await seed()
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
