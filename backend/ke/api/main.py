from __future__ import annotations

from fastapi import FastAPI

from app.core.config import get_settings
from app.middleware.rate_limit import RateLimitMiddleware
from ke.api.middleware.auth import ServiceAuthMiddleware
from ke.api.middleware.tenant import TenantMiddleware
from ke.api.routes.audit import router as audit_router
from ke.api.routes.cache import router as cache_router
from ke.api.routes.config import router as config_router
from ke.api.routes.executor import router as executor_router
from ke.api.routes.generator import router as generator_router
from ke.api.routes.graph import router as graph_router
from ke.api.routes.history import router as history_router
from ke.api.routes.metrics import router as metrics_router
from ke.api.routes.planner import router as planner_router
from ke.api.routes.schema import router as schema_router
from ke.api.routes.query import router as query_router
from ke.api.routes.sync import router as sync_router
from ke.api.routes.vector import router as vector_router


def create_ke_api() -> FastAPI:
    settings = get_settings()
    is_prod = settings.environment == "production"
    app = FastAPI(
        title="Knowledge Engine API",
        version="0.1.0",
        docs_url=None if is_prod else "/docs",
        redoc_url=None,
    )

    app.add_middleware(TenantMiddleware)
    app.add_middleware(ServiceAuthMiddleware)
    app.add_middleware(RateLimitMiddleware)

    app.include_router(schema_router, prefix="/v1/ke/schema")
    app.include_router(vector_router, prefix="/v1/ke/vector")
    app.include_router(graph_router, prefix="/v1/ke/graph")
    app.include_router(sync_router, prefix="/v1/ke/sync")
    app.include_router(query_router, prefix="/v1/ke/query")
    app.include_router(planner_router)
    app.include_router(generator_router)
    app.include_router(executor_router)
    app.include_router(history_router, prefix="/v1/ke/query")
    app.include_router(config_router, prefix="/v1/ke")
    app.include_router(metrics_router)
    app.include_router(audit_router, prefix="/v1/ke")
    app.include_router(cache_router, prefix="/v1/ke")

    return app
