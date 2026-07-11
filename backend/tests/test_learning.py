from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from ke.models.feedback import QueryFeedback
from ke.services.learning.batch import LearningBatchProcessor
from ke.services.learning.collector import FeedbackCollectorService
from ke.services.learning.pattern_miner import PatternMiner
from ke.services.learning.qa_builder import QAPairBuilder
from ke.services.learning.schema_enricher import SchemaEnricher
from ke.services.learning.validator import FeedbackValidator


class TestFeedbackValidator:
    def test_valid_feedback_passes(self) -> None:
        v = FeedbackValidator()
        fb = QueryFeedback(id="1", query_id="q1", rating=4, flag=None, comment="good job")
        assert v.is_valid(fb)

    def test_rating_out_of_range_fails(self) -> None:
        v = FeedbackValidator()
        assert not v.is_valid(QueryFeedback(id="1", query_id="q1", rating=0))
        assert not v.is_valid(QueryFeedback(id="1", query_id="q1", rating=6))

    def test_spam_comment_fails(self) -> None:
        v = FeedbackValidator()
        fb = QueryFeedback(id="1", query_id="q1", comment="buy now http://spam.com")
        assert not v.is_valid(fb)

    def test_comment_too_long_fails(self) -> None:
        v = FeedbackValidator()
        fb = QueryFeedback(id="1", query_id="q1", comment="x" * 2500)
        assert not v.is_valid(fb)

    def test_deduplicate_removes_duplicates(self) -> None:
        v = FeedbackValidator()
        items = [
            {"query_id": "q1", "user_id": "u1"},
            {"query_id": "q1", "user_id": "u1"},
            {"query_id": "q2", "user_id": "u1"},
        ]
        result = v.deduplicate(items)
        assert len(result) == 2

    def test_invalid_flag_fails(self) -> None:
        v = FeedbackValidator()
        fb = QueryFeedback(id="1", query_id="q1", flag="nonsense")
        assert not v.is_valid(fb)

    def test_valid_flags_pass(self) -> None:
        v = FeedbackValidator()
        for flag in ("spam", "incorrect", "offensive", "other"):
            fb = QueryFeedback(id="1", query_id="q1", flag=flag, rating=3)
            assert v.is_valid(fb)


class TestQAPairBuilder:
    def test_build_from_good_feedback(self) -> None:
        b = QAPairBuilder()
        items = [
            {"query": "show users", "sql": "SELECT * FROM users", "rating": 5, "tenant_id": "t1", "query_id": "q1"},
        ]
        pairs = b.build(items)
        assert len(pairs) == 1
        assert pairs[0].question == "show users"
        assert pairs[0].answer == "SELECT * FROM users"

    def test_skips_low_rated(self) -> None:
        b = QAPairBuilder()
        items = [{"query": "x", "sql": "SELECT 1", "rating": 1, "tenant_id": "t1", "query_id": "q1"}]
        assert b.build(items) == []

    def test_skips_empty_query(self) -> None:
        b = QAPairBuilder()
        items = [{"query": "", "sql": "SELECT 1", "rating": 5, "tenant_id": "t1", "query_id": "q1"}]
        assert b.build(items) == []


class TestPatternMiner:
    def test_mine_joins(self) -> None:
        m = PatternMiner()
        items = [
            {"sql": "SELECT * FROM users JOIN orders ON users.id = orders.user_id"},
            {"sql": "SELECT * FROM users JOIN orders ON users.id = orders.user_id"},
            {"sql": "SELECT * FROM products JOIN categories ON products.cat_id = categories.id"},
        ]
        patterns = m.mine_join_patterns(items, top_n=5)
        assert len(patterns) == 2
        join_tables = {p["tables"][0] + "|" + p["tables"][1] for p in patterns}
        assert "orders|users" in join_tables
        assert "categories|products" in join_tables

    def test_mine_table_frequencies(self) -> None:
        m = PatternMiner()
        items = [
            {"sql": "SELECT * FROM users JOIN orders ON ..."},
            {"sql": "SELECT * FROM users WHERE id = 1"},
        ]
        freq = m.mine_table_frequencies(items, top_n=10)
        table_names = {f["table"] for f in freq}
        assert "users" in table_names

    def test_empty_sql(self) -> None:
        m = PatternMiner()
        assert m.mine_join_patterns([]) == []
        assert m.mine_table_frequencies([]) == []


class TestSchemaEnricher:
    @pytest.mark.asyncio
    async def test_enrich_with_table_comment(self) -> None:
        table_repo = MagicMock()
        table_repo.list = AsyncMock(return_value=([MagicMock(id="t1", description="")], 1))
        table_repo.update = AsyncMock(return_value=None)

        enricher = SchemaEnricher(table_repo=MagicMock(), column_repo=MagicMock())
        enricher._table_repo = table_repo

        items = [
            {"comment": "This table stores customer orders", "sql": "SELECT * FROM orders", "tenant_id": "t1"},
        ]
        count = await enricher.enrich_from_feedback(items)
        assert count == 1

    def test_extract_table_from_sql(self) -> None:
        enricher = SchemaEnricher(MagicMock(), MagicMock())
        assert enricher._extract_table("", "SELECT * FROM users") == "users"
        assert enricher._extract_table("about orders", "") == "orders"
        assert enricher._extract_table("", "") is None

    def test_extract_column_description(self) -> None:
        enricher = SchemaEnricher(MagicMock(), MagicMock())
        desc = enricher._extract_column_description("This column means the user email address.")
        assert desc is not None
        assert "user email" in desc


class TestFeedbackCollector:
    @pytest.mark.asyncio
    async def test_collect_unprocessed(self) -> None:
        history = MagicMock()
        history.has_feedback = True
        history.id = "h1"
        history.query = "test"
        history.sql = "SELECT 1"
        history.user_id = "u1"
        history.status = "success"

        feedback = QueryFeedback(id="f1", query_id="h1", rating=4)

        history_repo = MagicMock()
        history_repo.list_by_tenant = AsyncMock(return_value=([history], 1))
        feedback_repo = MagicMock()
        feedback_repo.list = AsyncMock(return_value=([feedback], 1))

        collector = FeedbackCollectorService(
            history_repo=history_repo,
            feedback_repo=feedback_repo,
        )
        result = await collector.collect_unprocessed("tenant1")
        assert len(result) == 1
        assert result[0]["query_id"] == "h1"


class TestLearningBatchProcessor:
    @pytest.mark.asyncio
    async def test_process_with_feedback(self) -> None:
        collector = MagicMock()
        collector.collect_unprocessed = AsyncMock(return_value=[
            {"query_id": "q1", "user_id": "u1", "query": "show users", "sql": "SELECT * FROM users",
             "rating": 5, "flag": None, "comment": "", "tenant_id": "t1"},
        ])
        enricher = MagicMock()
        enricher.enrich_from_feedback = AsyncMock(return_value=1)
        result = await LearningBatchProcessor(
            collector=collector,
            validator=FeedbackValidator(),
            qa_builder=QAPairBuilder(),
            enricher=enricher,
            miner=PatternMiner(),
        ).process("t1")
        assert result["status"] == "completed"
        assert result["feedback_processed"] == 1
        assert result["qa_pairs"] == 1

    @pytest.mark.asyncio
    async def test_process_no_feedback_skips(self) -> None:
        collector = MagicMock()
        collector.collect_unprocessed = AsyncMock(return_value=[])
        result = await LearningBatchProcessor(
            collector=collector,
            validator=FeedbackValidator(),
            qa_builder=QAPairBuilder(),
            enricher=MagicMock(),
            miner=PatternMiner(),
        ).process("t1")
        assert result["status"] == "skipped"
