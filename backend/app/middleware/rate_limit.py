"""Rate limiting middleware using in-memory sliding window."""

import time
from collections import defaultdict
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import get_settings

settings = get_settings()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Sliding window rate limiter per client IP."""

    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.window_size = 60  # seconds
        self.hits: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()

        # Clean old entries
        self.hits[client_ip] = [
            t for t in self.hits[client_ip] if now - t < self.window_size
        ]

        # Check rate limit
        if len(self.hits[client_ip]) >= self.requests_per_minute:
            return Response(
                content='{"success":false,"error":{"code":429,"message":"Rate limit exceeded. Try again later."}}',
                status_code=429,
                media_type="application/json",
            )

        self.hits[client_ip].append(now)
        response = await call_next(request)
        return response


class AIRateLimitMiddleware(BaseHTTPMiddleware):
    """Stricter rate limiter for AI endpoints."""

    def __init__(self, app, requests_per_minute: int = 20):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.window_size = 60
        self.hits: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if "/chat" not in str(request.url.path):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.time()

        self.hits[client_ip] = [
            t for t in self.hits[client_ip] if now - t < self.window_size
        ]

        if len(self.hits[client_ip]) >= self.requests_per_minute:
            return Response(
                content='{"success":false,"error":{"code":429,"message":"AI rate limit exceeded. Please wait before sending another message."}}',
                status_code=429,
                media_type="application/json",
            )

        self.hits[client_ip].append(now)
        return await call_next(request)
