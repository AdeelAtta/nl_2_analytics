from __future__ import annotations

from prometheus_client import Counter, Histogram
from prometheus_client.registry import REGISTRY

pipeline_runs_total = Counter(
    "pipeline_runs_total",
    "Total number of pipeline executions",
    ["status"],
    registry=REGISTRY,
)

pipeline_duration_seconds = Histogram(
    "pipeline_duration_seconds",
    "Pipeline execution duration in seconds",
    ["status"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0),
    registry=REGISTRY,
)

stage_runs_total = Counter(
    "pipeline_stage_runs_total",
    "Total number of pipeline stage executions",
    ["stage", "status"],
    registry=REGISTRY,
)

stage_duration_seconds = Histogram(
    "pipeline_stage_duration_seconds",
    "Pipeline stage execution duration in seconds",
    ["stage", "status"],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
    registry=REGISTRY,
)

query_type_runs_total = Counter(
    "pipeline_query_type_runs_total",
    "Total pipeline runs by query type",
    ["query_type", "status"],
    registry=REGISTRY,
)

guard_blocked_total = Counter(
    "pipeline_guard_blocked_total",
    "Total queries blocked by guardrails",
    ["layer"],
    registry=REGISTRY,
)


def record_pipeline_result(status: str, duration_ms: float) -> None:
    pipeline_runs_total.labels(status=status).inc()
    pipeline_duration_seconds.labels(status=status).observe(duration_ms / 1000.0)


def record_stage_result(stage: str, status: str, duration_ms: float) -> None:
    stage_runs_total.labels(stage=stage, status=status).inc()
    stage_duration_seconds.labels(stage=stage, status=status).observe(duration_ms / 1000.0)


def record_query_type(query_type: str, status: str) -> None:
    query_type_runs_total.labels(query_type=query_type, status=status).inc()


def record_guard_blocked(layer: str) -> None:
    guard_blocked_total.labels(layer=layer).inc()
