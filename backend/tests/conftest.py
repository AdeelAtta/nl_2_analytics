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
def _clear_stores() -> None:
    from app.services.store import get_tenant_store, get_user_store_file
    get_tenant_store().clear()
    get_user_store_file().clear()


@pytest.fixture
def test_settings() -> Settings:
    return get_settings()


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
