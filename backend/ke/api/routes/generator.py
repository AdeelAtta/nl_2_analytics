from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from ke.api.schemas import error_response, success_response
from ke.models.planning import QueryIntent
from ke.services.generator import NL2SQLGenerator
from ke.services.intent import IntentAgent
from ke.services.planner import QueryPlanner
from ke.services.policy.chain import PolicyChain

router = APIRouter(tags=["generator"])

_intent_agent = IntentAgent()
_planner = QueryPlanner(intent_agent=_intent_agent)
_generator = NL2SQLGenerator()
_policy_chain = PolicyChain()


def get_intent_agent() -> IntentAgent:
    return _intent_agent


def get_planner() -> QueryPlanner:
    return _planner


def get_generator() -> NL2SQLGenerator:
    return _generator


def get_policy_chain() -> PolicyChain:
    return _policy_chain


@router.post("/v1/ke/generate")
async def generate_sql(
    body: dict[str, Any],
    generator: NL2SQLGenerator = Depends(get_generator),
) -> dict[str, Any]:
    query = body.get("query", "").strip()
    if not query:
        return error_response("QUERY_REQUIRED", "Query text is required")
    context = body.get("context")
    tenant_tier = body.get("tenant_tier", "pro")
    num_candidates = body.get("num_candidates", 1)
    reflect = body.get("reflect", True)
    dialect = body.get("dialect", "postgresql")

    intent = _intent_agent.classify(query, context)
    result = await generator.generate(query, intent, context, tenant_tier, num_candidates, reflect, dialect)
    return success_response(result.model_dump())


@router.post("/v1/ke/generate/from-plan")
async def generate_from_plan(
    body: dict[str, Any],
    generator: NL2SQLGenerator = Depends(get_generator),
) -> dict[str, Any]:
    query = body.get("query", "").strip()
    if not query:
        return error_response("QUERY_REQUIRED", "Query text is required")
    intent_data = body.get("intent")
    if not intent_data:
        return error_response("INTENT_REQUIRED", "Query intent is required")
    context = body.get("context")
    tenant_tier = body.get("tenant_tier", "pro")
    num_candidates = body.get("num_candidates", 1)
    reflect = body.get("reflect", True)
    dialect = body.get("dialect", "postgresql")

    intent = QueryIntent(**intent_data)
    result = await generator.generate(query, intent, context, tenant_tier, num_candidates, reflect, dialect)
    return success_response(result.model_dump())


@router.post("/v1/ke/generate/guard")
async def guard_sql(
    body: dict[str, Any],
    chain: PolicyChain = Depends(get_policy_chain),
) -> dict[str, Any]:
    sql = body.get("sql", "").strip()
    if not sql:
        return error_response("SQL_REQUIRED", "SQL query is required")
    context = body.get("context")
    result = await chain.enforce(sql, context)
    return success_response(result.model_dump())
