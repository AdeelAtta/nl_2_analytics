from __future__ import annotations

import os
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.core.config import Settings, get_settings
from app.main import create_app

os.environ.setdefault("KE_API_TOKEN", "ke_dev_token_2026")


@pytest.fixture(autouse=True)
async def _clear_stores() -> None:
    from app.core.database import async_session_factory
    from sqlalchemy import text
    async with async_session_factory() as session:
        await session.execute(text("DELETE FROM auth.users"))
        await session.execute(text("DELETE FROM auth.tenants"))
        await session.commit()


@pytest.fixture
def test_settings() -> Settings:
    return get_settings()


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
