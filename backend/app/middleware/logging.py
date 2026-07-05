"""Request logging middleware."""

import time
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import structlog

logger = structlog.get_logger()


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware that logs all incoming requests and their processing time."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        method = request.method
        url = str(request.url)
        client_ip = request.client.host if request.client else "unknown"

        logger.info(
            "request_started",
            method=method,
            url=url,
            client_ip=client_ip,
        )

        response = await call_next(request)

        duration_ms = round((time.time() - start_time) * 1000, 2)
        user_id = getattr(request.state, "user_id", None)

        logger.info(
            "request_completed",
            method=method,
            url=url,
            status_code=response.status_code,
            duration_ms=duration_ms,
            user_id=str(user_id) if user_id else None,
            request_id=getattr(request.state, "request_id", None),
        )

        return response
