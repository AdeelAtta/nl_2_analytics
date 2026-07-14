import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.schemas.health import ProblemDetail

logger = logging.getLogger(__name__)


def setup_error_handlers(app: FastAPI) -> None:
    settings = get_settings()

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "type": "about:blank",
                "title": exc.detail,
                "status": exc.status_code,
                "detail": exc.detail,
                "instance": str(request.url),
            },
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        is_debug = settings.debug or settings.environment == "development"
        logger.exception("Unhandled exception: %s", exc)
        problem = ProblemDetail(
            type="about:blank",
            title="Internal Server Error",
            status=500,
            detail=str(exc) if is_debug else "An internal error occurred",
            instance=str(request.url),
        )
        return JSONResponse(
            status_code=500,
            content=problem.model_dump(),
        )
