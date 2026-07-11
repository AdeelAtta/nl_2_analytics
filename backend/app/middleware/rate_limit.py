from __future__ import annotations

import time
from collections import defaultdict
from typing import Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


class SlidingWindowCounter:
    def __init__(self, max_requests: int, window_seconds: int) -> None:
        self._max = max_requests
        self._window = window_seconds
        self._entries: list[float] = []

    def allow(self) -> bool:
        now = time.time()
        cutoff = now - self._window
        self._entries = [t for t in self._entries if t > cutoff]
        if len(self._entries) >= self._max:
            return False
        self._entries.append(now)
        return True

    @property
    def remaining(self) -> int:
        now = time.time()
        cutoff = now - self._window
        self._entries = [t for t in self._entries if t > cutoff]
        return max(0, self._max - len(self._entries))

    @property
    def reset_at(self) -> float:
        if not self._entries:
            return time.time() + self._window
        return self._entries[0] + self._window


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: Any,
        max_requests: int = 100,
        window_seconds: int = 60,
        exclude_paths: tuple[str, ...] = (
            "/health", "/metrics", "/docs", "/openapi.json", "/redoc"
        ),
    ) -> None:
        super().__init__(app)
        self._max = max_requests
        self._window = window_seconds
        self._exclude = exclude_paths
        self._counters: dict[str, SlidingWindowCounter] = defaultdict(
            lambda: SlidingWindowCounter(max_requests, window_seconds)
        )

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path.startswith(self._exclude):
            return await call_next(request)

        if request.client:
            client_key = request.headers.get("X-Tenant-Id") or request.client.host
        else:
            client_key = "unknown"
        counter = self._counters[client_key]

        if not counter.allow():
            retry_after = int(counter.reset_at - time.time())
            headers = {
                "X-RateLimit-Limit": str(self._max),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(counter.reset_at)),
                "Retry-After": str(max(1, retry_after)),
            }
            return Response(
                status_code=429,
                content=(
                    '{"success":false,"error":{"code":"RATE_LIMITED",'
                    '"message":"Too many requests"}}'
                ),
                media_type="application/json",
                headers=headers,
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self._max)
        response.headers["X-RateLimit-Remaining"] = str(counter.remaining)
        response.headers["X-RateLimit-Reset"] = str(int(counter.reset_at))
        return response
