from fastapi import FastAPI

from app.core.config import get_settings
from app.core.di import Container
from app.core.logging import configure_logging
from app.middleware.cors import setup_cors
from app.middleware.error_handler import setup_error_handlers
from app.middleware.logging import StructLogMiddleware
from app.middleware.request_id import RequestIDMiddleware


def create_app() -> FastAPI:
    configure_logging()

    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/docs",
        redoc_url=None,
    )

    container = Container()
    app.state.container = container

    setup_cors(app, settings.cors_origins)

    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(StructLogMiddleware)

    setup_error_handlers(app)

    from app.api.v1.health import router as health_router

    app.include_router(health_router)

    return app


app = create_app()
