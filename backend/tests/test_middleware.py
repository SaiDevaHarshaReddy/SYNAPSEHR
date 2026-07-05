"""Tests for middleware."""
import pytest
from unittest.mock import MagicMock


class TestRateLimitMiddleware:
    """Tests for rate limiting."""

    def test_rate_limit_init(self):
        from app.middleware.rate_limit import RateLimitMiddleware
        app = MagicMock()
        middleware = RateLimitMiddleware(app, requests_per_minute=60)
        assert middleware.requests_per_minute == 60
        assert middleware.window_size == 60

    def test_ai_rate_limit_init(self):
        from app.middleware.rate_limit import AIRateLimitMiddleware
        app = MagicMock()
        middleware = AIRateLimitMiddleware(app, requests_per_minute=20)
        assert middleware.requests_per_minute == 20


class TestSecurityHeadersMiddleware:
    """Tests for security headers."""

    def test_init(self):
        from app.middleware.security import SecurityHeadersMiddleware
        app = MagicMock()
        middleware = SecurityHeadersMiddleware(app)
        assert middleware is not None


class TestPerformanceMiddleware:
    """Tests for performance middleware."""

    def test_init(self):
        from app.middleware.performance import PerformanceMiddleware
        app = MagicMock()
        middleware = PerformanceMiddleware(app)
        assert middleware.SLOW_THRESHOLD_MS == 1000
