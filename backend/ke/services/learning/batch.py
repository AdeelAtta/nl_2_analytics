from __future__ import annotations

import logging
from collections.abc import Callable

from ke.services.learning.collector import FeedbackCollectorService
from ke.services.learning.pattern_miner import PatternMiner
from ke.services.learning.qa_builder import QAPairBuilder
from ke.services.learning.schema_enricher import SchemaEnricher
from ke.services.learning.validator import FeedbackValidator

logger = logging.getLogger(__name__)


class LearningBatchProcessor:
    def __init__(
        self,
        collector: FeedbackCollectorService,
        validator: FeedbackValidator,
        qa_builder: QAPairBuilder,
        enricher: SchemaEnricher,
        miner: PatternMiner,
        on_qa_pairs: Callable | None = None,
        on_patterns: Callable | None = None,
    ) -> None:
        self._collector = collector
        self._validator = validator
        self._qa_builder = qa_builder
        self._enricher = enricher
        self._miner = miner
        self._on_qa_pairs = on_qa_pairs
        self._on_patterns = on_patterns

    async def process(self, tenant_id: str = "default") -> dict:
        raw = await self._collector.collect_unprocessed(tenant_id)
        if not raw:
            return {"status": "skipped", "reason": "no feedback", "count": 0}

        deduped = self._validator.deduplicate(raw)
        qa_pairs = self._qa_builder.build(deduped)
        enriched = await self._enricher.enrich_from_feedback(deduped)
        patterns = self._miner.mine_join_patterns(deduped)
        freq = self._miner.mine_table_frequencies(deduped)

        if self._on_qa_pairs and qa_pairs:
            await self._on_qa_pairs(qa_pairs)
        if self._on_patterns and patterns:
            await self._on_patterns(patterns)

        logger.info(
            "Batch processed: %d items, %d QA pairs, %d enriched, %d patterns",
            len(deduped), len(qa_pairs), enriched, len(patterns),
        )
        return {
            "status": "completed",
            "feedback_processed": len(deduped),
            "qa_pairs": len(qa_pairs),
            "schema_enriched": enriched,
            "join_patterns": len(patterns),
            "frequent_tables": len(freq),
        }
