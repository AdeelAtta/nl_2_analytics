from __future__ import annotations

from prometheus_client import REGISTRY
from prometheus_client.openmetrics import exposition as openmetrics
from prometheus_client.parser import text_string_to_metric_families

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from ke.api.schemas import KEResponse, success_response

router = APIRouter(tags=["metrics"])


@router.get("/metrics", response_class=PlainTextResponse)
async def get_prometheus_metrics() -> str:
    return PlainTextResponse(
        content=openmetrics.generate_latest(REGISTRY),
        media_type="text/plain; version=0.0.4",
    )


@router.get("/metrics/summary", response_model=KEResponse[list[dict]])
async def get_metrics_summary() -> KEResponse[list[dict]]:
    families = []
    for metric in REGISTRY.collect():
        samples = []
        for sample in metric.samples:
            samples.append({
                "name": sample.name,
                "labels": sample.labels,
                "value": sample.value,
            })
        families.append({
            "name": metric.name,
            "documentation": metric.documentation,
            "type": metric.type,
            "samples": samples,
        })
    return success_response(families)
