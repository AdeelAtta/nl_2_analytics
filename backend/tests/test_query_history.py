from __future__ import annotations

from unittest.mock import ANY, AsyncMock, MagicMock

import pytest

from ke.models.feedback import QueryFeedback, QueryHistory
from ke.services.history import QueryHistoryService
from ke.stores.query.repository import (
    QueryFeedbackRepository,
    QueryHistoryRepository,
)
from shared.models.pagination import PaginationParams


@pytest.fixture
def mock_history_repo() -> MagicMock:
    repo = MagicMock(spec=QueryHistoryRepository)
    repo.create = AsyncMock()
    repo.get = AsyncMock()
    repo.list_by_tenant = AsyncMock()
    repo.mark_feedback = AsyncMock()
    return repo


@pytest.fixture
def mock_feedback_repo() -> MagicMock:
    repo = MagicMock(spec=QueryFeedbackRepository)
    repo.create = AsyncMock()
    return repo


@pytest.fixture
def service(mock_history_repo, mock_feedback_repo) -> QueryHistoryService:
    return QueryHistoryService(
        history_repo=mock_history_repo,
        feedback_repo=mock_feedback_repo,
    )


class TestQueryHistoryService:
    @pytest.mark.asyncio
    async def test_save_creates_record(self, service: QueryHistoryService, mock_history_repo: MagicMock) -> None:
        mock_history_repo.create.return_value = QueryHistory(id="h1", tenant_id="t1", query="show users", status="success")

        result = await service.save(
            tenant_id="t1",
            query="show users",
            sql="SELECT * FROM users",
            status="success",
            duration_ms=150.0,
            model_tier="standard",
            model_name="gpt-4o",
            guard_passed=True,
        )

        assert result.id == "h1"
        assert result.tenant_id == "t1"
        mock_history_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_history_calls_repo(self, service: QueryHistoryService, mock_history_repo: MagicMock) -> None:
        mock_history_repo.list_by_tenant.return_value = (
            [QueryHistory(id="h1", tenant_id="t1", query="test", status="success")],
            1,
        )

        items, total = await service.list_history(tenant_id="t1", page=1, page_size=10)

        assert total == 1
        assert len(items) == 1
        mock_history_repo.list_by_tenant.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_history_filters_by_user(self, service: QueryHistoryService, mock_history_repo: MagicMock) -> None:
        mock_history_repo.list_by_tenant.return_value = ([], 0)

        await service.list_history(tenant_id="t1", user_id="u1", status="success")

        mock_history_repo.list_by_tenant.assert_called_with(
            tenant_id="t1",
            pagination=ANY,
            user_id="u1",
            status_filter="success",
        )

    @pytest.mark.asyncio
    async def test_get_history_returns_record(self, service: QueryHistoryService, mock_history_repo: MagicMock) -> None:
        mock_history_repo.get.return_value = QueryHistory(id="h1", tenant_id="t1", query="test", status="success")

        result = await service.get_history("h1")

        assert result is not None
        assert result.id == "h1"

    @pytest.mark.asyncio
    async def test_get_history_missing_returns_none(self, service: QueryHistoryService, mock_history_repo: MagicMock) -> None:
        mock_history_repo.get.return_value = None

        result = await service.get_history("nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_submit_feedback_creates_and_marks(self, service: QueryHistoryService, mock_history_repo: MagicMock, mock_feedback_repo: MagicMock) -> None:
        mock_feedback_repo.create.return_value = QueryFeedback(
            id="f1", query_id="h1", rating=5, flag=None, comment="great",
        )

        result = await service.submit_feedback(
            query_id="h1",
            rating=5,
            comment="great",
        )

        assert result.id == "f1"
        assert result.rating == 5
        mock_feedback_repo.create.assert_called_once()
        mock_history_repo.mark_feedback.assert_called_once_with("h1")

    @pytest.mark.asyncio
    async def test_save_with_full_stage_data(self, service: QueryHistoryService, mock_history_repo: MagicMock) -> None:
        mock_history_repo.create.return_value = QueryHistory(id="h2", tenant_id="t1", query="test", status="success")

        result = await service.save(
            tenant_id="t1",
            query="show users",
            sql="SELECT * FROM users",
            status="success",
            duration_ms=200.0,
            model_tier="lightweight",
            model_name="sqlcoder",
            guard_passed=False,
            guard_stopped_at="L3RBACSchemaScoping",
            stage_data=[{"name": "classify", "status": "success"}],
            user_id="u1",
            session_id="s1",
        )

        assert result.id == "h2"
        mock_history_repo.create.assert_called_once()
        created = mock_history_repo.create.call_args[0][0]
        assert created.user_id == "u1"
        assert created.session_id == "s1"
        assert created.guard_passed is False
        assert created.guard_stopped_at == "L3RBACSchemaScoping"


class TestQueryHistoryModel:
    def test_query_history_defaults(self) -> None:
        h = QueryHistory(id="h1", tenant_id="t1", query="test", status="success")
        assert h.sql == ""
        assert h.model_tier == "none"
        assert h.guard_passed is True
        assert h.has_feedback is False
        assert h.stage_data == []

    def test_query_feedback_defaults(self) -> None:
        f = QueryFeedback(id="f1", query_id="h1")
        assert f.rating is None
        assert f.flag is None
        assert f.comment == ""
