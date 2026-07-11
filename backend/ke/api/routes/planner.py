from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from ke.api.schemas import error_response, success_response
from ke.models.planning import QueryIntent
from ke.services.intent import IntentAgent
from ke.services.planner import QueryPlanner
from ke.services.router import ModelRouter

router = APIRouter(tags=["planner"])

_intent_agent = IntentAgent()
_planner = QueryPlanner(intent_agent=_intent_agent)
_model_router = ModelRouter()


def get_intent_agent() -> IntentAgent:
    return _intent_agent


def get_planner() -> QueryPlanner:
    return _planner


def get_model_router() -> ModelRouter:
    return _model_router


@router.post("/v1/ke/planner/classify")
async def classify_query(
    body: dict[str, Any],
    agent: IntentAgent = Depends(get_intent_agent),
) -> dict[str, Any]:
    query = body.get("query", "").strip()
    if not query:
        return error_response("QUERY_REQUIRED", "Query text is required")
    context = body.get("context")
    intent = agent.classify(query, context)
    return success_response(intent.model_dump())


@router.post("/v1/ke/planner/plan")
async def plan_query(
    body: dict[str, Any],
    planner: QueryPlanner = Depends(get_planner),
) -> dict[str, Any]:
    query = body.get("query", "").strip()
    if not query:
        return error_response("QUERY_REQUIRED", "Query text is required")
    context = body.get("context")
    intent_data = body.get("intent")
    intent = QueryIntent(**intent_data) if intent_data else None
    plan = await planner.plan(query, context, intent=intent)
    return success_response(plan.model_dump())


@router.post("/v1/ke/planner/route")
async def route_query(
    body: dict[str, Any],
    router_service: ModelRouter = Depends(get_model_router),
) -> dict[str, Any]:
    intent_data = body.get("intent")
    if not intent_data:
        return error_response("INTENT_REQUIRED", "Query intent is required")
    intent = QueryIntent(**intent_data)
    tenant_tier = body.get("tenant_tier", "pro")
    result = router_service.route(intent, tenant_tier)
    return success_response(result)


@router.post("/v1/ke/planner/pipeline")
async def full_pipeline(
    body: dict[str, Any],
    agent: IntentAgent = Depends(get_intent_agent),
    planner: QueryPlanner = Depends(get_planner),
    router_service: ModelRouter = Depends(get_model_router),
) -> dict[str, Any]:
    query = body.get("query", "").strip()
    if not query:
        return error_response("QUERY_REQUIRED", "Query text is required")
    context = body.get("context")
    tenant_tier = body.get("tenant_tier", "pro")

    intent = agent.classify(query, context)
    plan = await planner.create_plan(query, intent, context)
    route = router_service.route(intent, tenant_tier)

    return success_response({
        "intent": intent.model_dump(),
        "plan": plan.model_dump(),
        "route": route,
    })
