from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Any

from ke.models.policy import PolicyLayerResult


class PolicyLayerBase(ABC):
    layer_number: int = 0
    layer_name: str = ""

    @abstractmethod
    async def check(self, sql: str, context: dict[str, Any] | None = None) -> PolicyLayerResult:
        ...

    async def run(self, sql: str, context: dict[str, Any] | None = None) -> PolicyLayerResult:
        start = time.perf_counter()
        result = await self.check(sql, context)
        result.layer_name = self.layer_name
        result.layer_number = self.layer_number
        result.duration_ms = (time.perf_counter() - start) * 1000
        return result
