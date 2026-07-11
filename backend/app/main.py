from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_client import generate_latest
from starlette.responses import PlainTextResponse

from app.core.config import get_settings
from app.core.di import Container
from app.core.logging import configure_logging
from app.core.telemetry import setup_telemetry, shutdown_telemetry
from app.middleware.cors import setup_cors
from app.middleware.error_handler import setup_error_handlers
from app.middleware.logging import StructLogMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.request_id import RequestIDMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    if settings.enable_tracing:
        setup_telemetry(app, settings.otel_service_name)
    yield
    if settings.enable_tracing:
        shutdown_telemetry()


def create_app() -> FastAPI:
    configure_logging()

    settings = get_settings()

    if settings.enable_sentry and settings.sentry_dsn:
        try:
            import sentry_sdk
            sentry_sdk.init(dsn=settings.sentry_dsn, environment=settings.environment)
        except ImportError:
            pass

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/docs",
        redoc_url=None,
        lifespan=lifespan,
    )

    container = Container()
    app.state.container = container

    setup_cors(app, settings.cors_origins)

    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(StructLogMiddleware)
    app.add_middleware(RateLimitMiddleware)

    setup_error_handlers(app)

    from app.api.v1.admin import router as admin_router
    from app.api.v1.auth.api_keys import router as api_keys_router
    from app.api.v1.auth.login import router as auth_router
    from app.api.v1.auth.members import router as members_router
    from app.api.v1.connections import router as connections_router
    from app.api.v1.feedback import router as feedback_router
    from app.api.v1.health import router as health_router
    from app.api.v1.history import router as history_router
    from app.api.v1.query import router as query_router
    from app.api.v1.schema import router as schema_router
    from app.api.v1.tenants import router as tenants_router

    app.include_router(admin_router)
    app.include_router(api_keys_router)
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(members_router)
    app.include_router(connections_router)
    app.include_router(feedback_router)
    app.include_router(health_router)
    app.include_router(history_router)
    app.include_router(query_router)
    app.include_router(schema_router)
    app.include_router(tenants_router)

    if settings.enable_metrics:
        _add_metrics_endpoint(app)

    return app


def _add_metrics_endpoint(app: FastAPI) -> None:
    @app.get("/metrics", include_in_schema=False)
    async def metrics() -> PlainTextResponse:
        return PlainTextResponse(generate_latest(), media_type="text/plain")


app = create_app()
