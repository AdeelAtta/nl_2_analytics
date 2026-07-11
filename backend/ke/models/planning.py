from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal

from shared.models.base import BaseSchema


class QueryType(str, Enum):
    SIMPLE_SELECT = "SIMPLE_SELECT"
    FILTERED_SELECT = "FILTERED_SELECT"
    JOIN = "JOIN"
    AGGREGATION = "AGGREGATION"
    COMPOUND = "COMPOUND"
    WINDOW = "WINDOW"
    SUBQUERY = "SUBQUERY"
    CROSS_DB = "CROSS_DB"
    ANALYTICAL = "ANALYTICAL"
    DDL = "DDL"
    UNKNOWN = "UNKNOWN"


class QueryComplexity(str, Enum):
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"


class ModelTier(str, Enum):
    NONE = "none"
    LIGHTWEIGHT = "lightweight"
    STANDARD = "standard"
    PREMIUM = "premium"


class PlanOperation(str, Enum):
    SCAN = "SCAN"
    FILTER = "FILTER"
    JOIN = "JOIN"
    AGGREGATE = "AGGREGATE"
    WINDOW = "WINDOW"
    SORT = "SORT"
    LIMIT = "LIMIT"
    SUBQUERY_EXEC = "SUBQUERY_EXEC"
    UNION = "UNION"
    PROJECT = "PROJECT"
    DISTINCT = "DISTINCT"
    CTE = "CTE"


class ValidationSeverity(str, Enum):
    FATAL = "FATAL"
    WARNING = "WARNING"


class TableRef(BaseSchema):
    model_config = {"frozen": False}

    id: str
    name: str
    schema_name: str = ""
    database_name: str = ""
    alias: str = ""


class ColumnRef(BaseSchema):
    model_config = {"frozen": False}

    table: str
    column: str
    alias: str = ""
    data_type: str = ""


class JoinEdge(BaseSchema):
    model_config = {"frozen": False}

    source_table: str
    source_column: str
    target_table: str
    target_column: str
    join_type: Literal["INNER", "LEFT", "RIGHT", "FULL", "CROSS"] = "INNER"
    confidence: float = 1.0


class FilterExpression(BaseSchema):
    model_config = {"frozen": False}

    column: ColumnRef
    operator: str
    value: str
    logical_operator: str = "AND"


class AggregationSpec(BaseSchema):
    model_config = {"frozen": False}

    function: str
    column: ColumnRef
    alias: str = ""


class GroupingSpec(BaseSchema):
    model_config = {"frozen": False}

    columns: list[ColumnRef] = []


class WindowSpec(BaseSchema):
    model_config = {"frozen": False}

    function: str
    column: ColumnRef
    partition_by: list[ColumnRef] = []
    order_by: list[ColumnRef] = []
    alias: str = ""


class CostEstimate(BaseSchema):
    model_config = {"frozen": False}

    estimated_rows: int = 0
    estimated_cost: float = 0.0
    estimated_duration_ms: float = 0.0


class PlanStep(BaseSchema):
    model_config = {"frozen": False}

    id: str
    step_number: int
    operation: PlanOperation
    tables: list[TableRef] = []
    columns: list[ColumnRef] = []
    filters: list[FilterExpression] = []
    joins: list[JoinEdge] = []
    grouping: GroupingSpec | None = None
    aggregations: list[AggregationSpec] = []
    windows: list[WindowSpec] = []
    ordering: list[ColumnRef] = []
    limit: int | None = None
    estimated_cost: float = 0.0
    estimated_rows: int = 0
    dependencies: list[str] = []


class ValidationError(BaseSchema):
    model_config = {"frozen": False}

    step_id: str = ""
    code: str = ""
    severity: ValidationSeverity = ValidationSeverity.FATAL
    message: str = ""
    suggestion: str = ""


class ValidationResult(BaseSchema):
    model_config = {"frozen": False}

    valid: bool = True
    errors: list[ValidationError] = []
    warnings: list[ValidationError] = []


class SubQuery(BaseSchema):
    model_config = {"frozen": False}

    id: str
    goal: str
    query_type: QueryType = QueryType.SIMPLE_SELECT
    tables: list[TableRef] = []
    dependencies: list[str] = []
    execution_mode: Literal["sequential", "parallel"] = "sequential"


class QueryIntent(BaseSchema):
    model_config = {"frozen": False}

    query_type: QueryType
    complexity: QueryComplexity = QueryComplexity.SIMPLE
    confidence: float = 1.0
    tables: list[TableRef] = []
    columns: list[ColumnRef] = []
    filters: list[FilterExpression] = []
    aggregations: list[dict] = []
    join_edges: list[dict] = []
    sub_queries: list[SubQuery] = []
    description: str = ""
    model_tier: ModelTier = ModelTier.NONE


class QueryPlan(BaseSchema):
    model_config = {"frozen": False}

    id: str
    intent: QueryIntent
    steps: list[PlanStep] = []
    validation: ValidationResult = ValidationResult()
    cost_estimate: CostEstimate = CostEstimate()
    created_at: datetime = datetime.now()
    metadata: dict[str, Any] = {}
