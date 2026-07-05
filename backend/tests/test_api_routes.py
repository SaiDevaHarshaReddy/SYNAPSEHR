"""Tests for API endpoints."""
import pytest


class TestHealthEndpoint:
    """Tests for health check."""

    def test_health_endpoint_exists(self):
        """Verify health endpoint is registered."""
        from app.main import app
        routes = [r.path for r in app.routes]
        assert "/health" in routes


class TestRouteRegistration:
    """Tests for all routes being registered."""

    def test_auth_routes(self):
        from app.main import app
        routes = [r.path for r in app.routes]
        assert any("/api/v1/auth" in r for r in routes)

    def test_employee_routes(self):
        from app.main import app
        routes = [r.path for r in app.routes]
        assert any("/api/v1/employees" in r for r in routes)

    def test_leave_routes(self):
        from app.main import app
        routes = [r.path for r in app.routes]
        assert any("/api/v1/leave" in r for r in routes)

    def test_chat_routes(self):
        from app.main import app
        routes = [r.path for r in app.routes]
        assert any("/api/v1/chat" in r for r in routes)

    def test_document_routes(self):
        from app.main import app
        routes = [r.path for r in app.routes]
        assert any("/api/v1/documents" in r for r in routes)

    def test_analytics_routes(self):
        from app.main import app
        routes = [r.path for r in app.routes]
        assert any("/api/v1/analytics" in r for r in routes)

    def test_notification_routes(self):
        from app.main import app
        routes = [r.path for r in app.routes]
        assert any("/api/v1/notifications" in r for r in routes)

    def test_workflow_routes(self):
        from app.main import app
        routes = [r.path for r in app.routes]
        assert any("/api/v1/workflows" in r for r in routes)

    def test_admin_routes(self):
        from app.main import app
        routes = [r.path for r in app.routes]
        assert any("/api/v1/admin" in r for r in routes)

    def test_knowledge_routes(self):
        from app.main import app
        routes = [r.path for r in app.routes]
        assert any("/api/v1/knowledge" in r for r in routes)

    def test_policy_routes(self):
        from app.main import app
        routes = [r.path for r in app.routes]
        assert any("/api/v1/policies" in r for r in routes)
