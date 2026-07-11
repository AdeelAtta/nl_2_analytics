from __future__ import annotations

from httpx import AsyncClient


class TestAuthEndpoints:
    async def test_demo_login_returns_token(self, async_client: AsyncClient) -> None:
        response = await async_client.post(
            "/api/v1/auth/demo-login",
            json={"tenant_id": "test-tenant", "user_id": "test-user"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["tenant_id"] == "test-tenant"
        assert data["user_id"] == "test-user"

    async def test_demo_login_defaults(self, async_client: AsyncClient) -> None:
        response = await async_client.post("/api/v1/auth/demo-login", json={})
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["tenant_id"] == "demo"
        assert data["user_id"] == "demo-user"

    async def test_demo_login_token_decodes(self, async_client: AsyncClient) -> None:
        from app.auth.jwt import decode_token

        response = await async_client.post("/api/v1/auth/demo-login", json={})
        token = response.json()["access_token"]
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "demo-user"
        assert payload["tenant_id"] == "demo"
        assert payload["role"] == "user"


class TestQueryEndpoint:
    async def test_requires_auth(self, async_client: AsyncClient) -> None:
        response = await async_client.post("/api/v1/query", json={"query": "test"})
        assert response.status_code == 401

    async def test_requires_query_field(self, async_client: AsyncClient) -> None:
        token_resp = await async_client.post("/api/v1/auth/demo-login", json={})
        token = token_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.post("/api/v1/query", json={}, headers=headers)
        assert response.status_code == 422

    async def test_empty_query_rejected(self, async_client: AsyncClient) -> None:
        token_resp = await async_client.post("/api/v1/auth/demo-login", json={})
        token = token_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.post(
            "/api/v1/query", json={"query": "   "}, headers=headers
        )
        assert response.status_code == 422

    async def test_query_with_valid_auth_returns_pipeline_result(
        self, async_client: AsyncClient,
    ) -> None:
        token_resp = await async_client.post("/api/v1/auth/demo-login", json={})
        token = token_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.post(
            "/api/v1/query",
            json={"query": "show me users", "session_id": "test-session"},
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "query" in data
        assert "sql" in data
        assert "stages" in data
        assert data["query"] == "show me users"


class TestSchemaEndpoints:
    async def test_list_tables_requires_auth(self, async_client: AsyncClient) -> None:
        r = await async_client.get("/api/v1/schema/tables")
        assert r.status_code == 401

    async def test_list_tables_with_auth(self, async_client: AsyncClient) -> None:
        token = (await async_client.post("/api/v1/auth/demo-login", json={})).json()["access_token"]
        r = await async_client.get("/api/v1/schema/tables", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        data = r.json()
        assert "data" in data

    async def test_schema_search(self, async_client: AsyncClient) -> None:
        token = (await async_client.post("/api/v1/auth/demo-login", json={})).json()["access_token"]
        r = await async_client.get("/api/v1/schema/search?q=user", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200

    async def test_list_databases(self, async_client: AsyncClient) -> None:
        token = (await async_client.post("/api/v1/auth/demo-login", json={})).json()["access_token"]
        r = await async_client.get("/api/v1/schema/databases", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200


class TestHistoryEndpoints:
    async def test_history_requires_auth(self, async_client: AsyncClient) -> None:
        r = await async_client.get("/api/v1/history")
        assert r.status_code == 401

    async def test_list_history(self, async_client: AsyncClient) -> None:
        token = (await async_client.post("/api/v1/auth/demo-login", json={})).json()["access_token"]
        r = await async_client.get("/api/v1/history", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200


class TestFeedbackEndpoints:
    async def test_submit_feedback_requires_auth(self, async_client: AsyncClient) -> None:
        r = await async_client.post("/api/v1/feedback", json={"query_id": "x"})
        assert r.status_code == 401

    async def test_submit_feedback_invalid_rating(self, async_client: AsyncClient) -> None:
        token = (await async_client.post("/api/v1/auth/demo-login", json={})).json()["access_token"]
        r = await async_client.post("/api/v1/feedback", json={"query_id": "x", "rating": 99},
                                     headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 422


class TestAuthRegisterLogin:
    async def test_register_creates_user(self, async_client: AsyncClient) -> None:
        r = await async_client.post("/api/v1/auth/register", json={
            "email": "new@test.com", "password": "pass123", "name": "Test User",
        })
        assert r.status_code == 200
        data = r.json()
        assert "access_token" in data
        assert data["email"] == "new@test.com"
        assert data["name"] == "Test User"

    async def test_register_duplicate_email(self, async_client: AsyncClient) -> None:
        await async_client.post("/api/v1/auth/register", json={
            "email": "dup@test.com", "password": "pass123",
        })
        r = await async_client.post("/api/v1/auth/register", json={
            "email": "dup@test.com", "password": "pass456",
        })
        assert r.status_code == 409

    async def test_login_with_valid_credentials(self, async_client: AsyncClient) -> None:
        await async_client.post("/api/v1/auth/register", json={
            "email": "login@test.com", "password": "pass123", "name": "Login Test",
        })
        r = await async_client.post("/api/v1/auth/login", json={
            "email": "login@test.com", "password": "pass123",
        })
        assert r.status_code == 200
        data = r.json()
        assert "access_token" in data
        assert data["email"] == "login@test.com"

    async def test_login_with_wrong_password(self, async_client: AsyncClient) -> None:
        await async_client.post("/api/v1/auth/register", json={
            "email": "wrong@test.com", "password": "correct",
        })
        r = await async_client.post("/api/v1/auth/login", json={
            "email": "wrong@test.com", "password": "wrong",
        })
        assert r.status_code == 401

    async def test_login_nonexistent_user(self, async_client: AsyncClient) -> None:
        r = await async_client.post("/api/v1/auth/login", json={
            "email": "nobody@test.com", "password": "pass",
        })
        assert r.status_code == 401


class TestApiKeyAuth:
    async def test_valid_api_key_authenticates(self, async_client: AsyncClient) -> None:
        from app.core.config import get_settings
        settings = get_settings()
        settings.api_keys = ["test-key-123"]
        r = await async_client.post("/api/v1/query", json={"query": "test"},
                                     headers={"x-api-key": "test-key-123"})
        assert r.status_code in (200, 422)

    async def test_invalid_api_key_rejected(self, async_client: AsyncClient) -> None:
        from app.core.config import get_settings
        settings = get_settings()
        settings.api_keys = ["valid-key"]
        r = await async_client.post("/api/v1/query", json={"query": "test"},
                                     headers={"x-api-key": "wrong-key"})
        assert r.status_code == 401

    async def test_api_key_takes_precedence_over_bearer(self, async_client: AsyncClient) -> None:
        from app.core.config import get_settings
        settings = get_settings()
        settings.api_keys = ["key-1"]
        r = await async_client.post("/api/v1/query", json={"query": "test"},
                                     headers={"x-api-key": "key-1", "Authorization": "Bearer invalid"})
        assert r.status_code in (200, 422)


class TestAdminEndpoints:
    async def test_admin_dashboard_requires_admin(self, async_client: AsyncClient) -> None:
        r = await async_client.get("/api/v1/admin/dashboard")
        assert r.status_code in (401, 403)

    async def test_admin_dashboard_returns_forbidden_for_user(self, async_client: AsyncClient) -> None:
        token = (await async_client.post("/api/v1/auth/demo-login", json={})).json()["access_token"]
        r = await async_client.get("/api/v1/admin/dashboard", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 403
