from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from shared.models.base import BaseSchema


class QualityDimension(str, Enum):
    CORRECTNESS = "correctness"
    EFFICIENCY = "efficiency"
    SAFETY = "safety"
    READABILITY = "readability"
    SCHEMA_ALIGNMENT = "schema_alignment"


class QualityDimensionScore(BaseSchema):
    model_config = {"frozen": False}

    dimension: QualityDimension
    score: float = 0.0
    reason: str = ""
    issues: list[str] = []


class QualityScore(BaseSchema):
    model_config = {"frozen": False}

    overall: float = 0.0
    dimensions: list[QualityDimensionScore] = []
    issues: list[str] = []
    suggestion: str = ""
    model: str = "rule_based"
    latency_ms: float = 0.0
    created_at: datetime = datetime.now()

    def dimension_score(self, dim: QualityDimension) -> float:
        for d in self.dimensions:
            if d.dimension == dim:
                return d.score
        return 0.0

    def passed(self, threshold: float = 0.5) -> bool:
        return self.overall >= threshold
