from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from qdrant_client import AsyncQdrantClient

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_qdrant, get_session
from ke.api.routes.schema import _get_column_repo, _get_table_repo
from ke.api.schemas import (
    KEErrorCode,
    KEResponse,
    error_response,
    success_response,
)
from ke.models.pipeline import PipelineResult
from ke.services.history import QueryHistoryService
from ke.services.pipeline import PipelineOrchestrator
from ke.services.query import QueryService
from ke.services.schema_resolver import SchemaResolver
from ke.services.session import InMemorySessionService
from ke.stores.query.repository import QueryFeedbackRepository, QueryHistoryRepository
from ke.stores.schema.repository import ColumnRepository, RelationshipRepository, TableRepository
from ke.stores.vector.embedding import EmbeddingService
from ke.stores.vector.repository import VectorRepository

router = APIRouter(tags=["query"])
_pipeline = PipelineOrchestrator()
_session_service: InMemorySessionService = InMemorySessionService()


async def _get_or_init_session_service() -> InMemorySessionService:
    global _session_service
    if isinstance(_session_service, InMemorySessionService):
        from ke.services.session_redis import create_session_service
        try:
            redis_svc = await create_session_service()
            if redis_svc is not None:
                _session_service = redis_svc
        except Exception:
            pass
    return _session_service


class ContextQuery(BaseModel):
    question: str
    limit: int = 10
    score_threshold: float | None = None


class DDLRenderRequest(BaseModel):
    table_ids: list[str]


async def _get_query_service(
    qdrant: AsyncQdrantClient = Depends(get_qdrant),
    table_repo: TableRepository = Depends(_get_table_repo),
    column_repo: ColumnRepository = Depends(_get_column_repo),
) -> QueryService:
    vector_repo = VectorRepository(qdrant)
    return QueryService(
        vector_repo=vector_repo,
        embedding_service=EmbeddingService(),
        table_repo=table_repo,
        column_repo=column_repo,
    )


@router.post("/context", response_model=KEResponse[dict])
async def search_context(
    request: Request,
    payload: ContextQuery,
    service: QueryService = Depends(_get_query_service),
):
    tenant_id = getattr(request.state, "tenant_id", "default")
    try:
        result = await service.search_context(
            question=payload.question,
            tenant_id=tenant_id,
            limit=payload.limit,
            score_threshold=payload.score_threshold,
        )
        return success_response(result)
    except Exception as e:
        return error_response(
            KEErrorCode.EMBEDDING_SERVICE_UNAVAILABLE,
            {"question": payload.question, "error": str(e)},
        )


@router.get("/context/table/{table_id}", response_model=KEResponse[dict])
async def get_table_context(
    table_id: str,
    service: QueryService = Depends(_get_query_service),
):
    try:
        result = await service.get_table_context(table_id=table_id)
        if result is None:
            return error_response(KEErrorCode.ENTITY_NOT_FOUND, {"id": table_id})
        return success_response(result)
    except Exception as e:
        return error_response(
            KEErrorCode.INTERNAL_ERROR,
            {"table_id": table_id, "error": str(e)},
        )


@router.post("/render-ddl", response_model=KEResponse[dict])
async def render_ddl(
    payload: DDLRenderRequest,
    service: QueryService = Depends(_get_query_service),
):
    try:
        result = await service.render_ddl(table_ids=payload.table_ids)
        return success_response({"ddl": result})
    except Exception as e:
        return error_response(
            KEErrorCode.INTERNAL_ERROR,
            {"error": str(e)},
        )


@router.get("/discover", response_model=KEResponse[dict])
async def discover_schemas(
    request: Request,
    service: QueryService = Depends(_get_query_service),
):
    tenant_id = getattr(request.state, "tenant_id", "default")
    try:
        databases = await _discover_for_tenant(tenant_id, service)
        return success_response(databases)
    except Exception as e:
        return error_response(
            KEErrorCode.INTERNAL_ERROR,
            {"error": str(e)},
        )


async def _discover_for_tenant(tenant_id: str, service: QueryService) -> list[dict]:
    return [{"tenant_id": tenant_id, "note": "Use /v1/ke/schema endpoints for full discovery"}]


class PipelineQuery(BaseModel):
    query: str
    context: dict[str, Any] | None = None
    session_id: str | None = None
    tenant_tier: str = "pro"
    num_candidates: int = 1
    reflect: bool = True
    timeout: float = 30.0
    page: int = 1
    page_size: int = 1000
    dry_run: bool = False


@router.post("/pipeline", response_model=PipelineResult)
async def query_pipeline(
    request: Request,
    payload: PipelineQuery,
    session: AsyncSession = Depends(get_session),
) -> PipelineResult:
    tenant_id = getattr(request.state, "tenant_id", "default")
    user_id = getattr(request.state, "user_id", None)
    context = dict(payload.context or {})

    resolver = SchemaResolver(
        table_repo=TableRepository(session),
        column_repo=ColumnRepository(session),
        rel_repo=RelationshipRepository(session),
    )

    session_svc = await _get_or_init_session_service()
    result = await _pipeline.execute(
        query=payload.query,
        context=context,
        schema_resolver=resolver,
        session_service=session_svc,
        session_id=payload.session_id,
        tenant_id=tenant_id,
        tenant_tier=payload.tenant_tier,
        num_candidates=payload.num_candidates,
        reflect=payload.reflect,
        timeout=payload.timeout,
        page=payload.page,
        page_size=payload.page_size,
        dry_run=payload.dry_run,
    )

    history_service = QueryHistoryService(
        history_repo=QueryHistoryRepository(session),
        feedback_repo=QueryFeedbackRepository(session),
    )
    await history_service.save(
        tenant_id=tenant_id,
        user_id=user_id,
        query=payload.query,
        sql=result.sql,
        status=result.status.value,
        duration_ms=result.total_duration_ms,
        model_tier=result.model_tier,
        model_name=result.model_name,
        guard_passed=result.guard_passed,
        guard_stopped_at=result.guard_stopped_at,
        stage_data=[s.model_dump() for s in result.stages],
    )

    return result
