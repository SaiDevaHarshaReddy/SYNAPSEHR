"""Performance monitoring middleware."""

import time
from typing import Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger()


class PerformanceMiddleware(BaseHTTPMiddleware):
    """Track request duration and log slow requests."""

    SLOW_THRESHOLD_MS = 1000

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        response = await call_next(request)

        duration_ms = int((time.time() - start_time) * 1000)

        response.headers["X-Response-Time"] = f"{duration_ms}ms"
        response.headers["X-Request-Path"] = request.url.path

        if duration_ms > self.SLOW_THRESHOLD_MS:
            logger.warning(
                "slow_request",
                path=request.url.path,
                method=request.method,
                duration_ms=duration_ms,
            )

        return response
