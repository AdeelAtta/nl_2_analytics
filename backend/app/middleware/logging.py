import time
from collections.abc import Awaitable, Callable
from uuid import uuid4

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class StructLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        correlation_id = request.headers.get(
            "X-Correlation-Id", str(uuid4())
        )
        request_id = getattr(request.state, "request_id", str(uuid4()))

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            correlation_id=correlation_id,
            method=request.method,
            path=request.url.path,
        )

        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        structlog.contextvars.bind_contextvars(
            status_code=response.status_code,
            duration_ms=round(process_time * 1000, 2),
        )

        logger = structlog.get_logger()
        logger.info("request_completed")

        response.headers["X-Correlation-Id"] = correlation_id

        return response
