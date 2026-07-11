from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)


class LearningBatchScheduler:
    def __init__(
        self,
        batch_process_fn: Callable[[], Any],
        interval_seconds: int = 300,
    ) -> None:
        self._fn = batch_process_fn
        self._interval = interval_seconds
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        logger.info("Learning batch scheduler started (interval=%ss)", self._interval)
        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            self._task = None
            logger.info("Learning batch scheduler stopped")

    async def _run(self) -> None:
        while True:
            try:
                await asyncio.sleep(self._interval)
                await self._fn()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.exception("Batch processing failed: %s", e)
