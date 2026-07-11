from __future__ import annotations

import logging
import os
import uuid

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from ke.api.schemas import KEErrorCode, error_response

logger = logging.getLogger(__name__)

_ke_api_token: str | None = None


def _get_expected_token() -> str:
    global _ke_api_token
    if _ke_api_token is not None:
        return _ke_api_token
    token = os.environ.get("KE_API_TOKEN")
    if token:
        _ke_api_token = token
        return token
    generated = uuid.uuid4().hex
    logger.warning(
        "KE_API_TOKEN not set. Generated ephemeral token: %s. "
        "Set KE_API_TOKEN environment variable for production.",
        generated,
    )
    _ke_api_token = generated
    return generated


def _verify_service_token(token: str) -> bool:
    expected = _get_expected_token()
    return token == expected


class ServiceAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path in ("/docs", "/openapi.json", "/redoc"):
            return await call_next(request)

        token = request.headers.get("X-Service-Token")
        if not token or not _verify_service_token(token):
            resp = error_response(
                KEErrorCode.INVALID_TOKEN,
                details={"header": "X-Service-Token"},
            )
            return JSONResponse(
                status_code=401,
                content=resp.model_dump(mode="json"),
            )
        return await call_next(request)
