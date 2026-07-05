"""Tests for API schemas validation."""
import pytest
from pydantic import ValidationError
from app.schemas.auth import LoginRequest
from app.schemas.chat import ChatRequest
from app.schemas.common import PaginationParams


class TestLoginSchema:
    """Tests for LoginRequest schema."""

    def test_valid_login(self):
        login = LoginRequest(email="test@example.com", password="password123")
        assert login.email == "test@example.com"

    def test_invalid_email(self):
        with pytest.raises(ValidationError):
            LoginRequest(email="not-an-email", password="password123")

    def test_empty_password(self):
        with pytest.raises(ValidationError):
            LoginRequest(email="test@example.com", password="")


class TestChatSchema:
    """Tests for ChatRequest schema."""

    def test_valid_chat_message(self):
        req = ChatRequest(message="Hello, AI!")
        assert req.message == "Hello, AI!"
        assert req.conversation_id is None

    def test_empty_message_fails(self):
        with pytest.raises(ValidationError):
            ChatRequest(message="")

    def test_long_message_fails(self):
        with pytest.raises(ValidationError):
            ChatRequest(message="x" * 5001)


class TestPagination:
    """Tests for PaginationParams."""

    def test_default_pagination(self):
        p = PaginationParams()
        assert p.page == 1
        assert p.limit == 20

    def test_custom_pagination(self):
        p = PaginationParams(page=3, limit=50)
        assert p.page == 3
        assert p.limit == 50
