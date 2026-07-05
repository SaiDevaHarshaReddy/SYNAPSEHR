"""Tests for API schemas - comprehensive."""
import pytest
from pydantic import ValidationError
from app.schemas.auth import LoginRequest, ForgotPasswordRequest, ResetPasswordRequest, ChangePasswordRequest
from app.schemas.chat import ChatRequest
from app.schemas.common import PaginationParams
from app.schemas.document import DocumentGenerateRequest


class TestLoginSchema:
    def test_valid_login(self):
        login = LoginRequest(email="test@example.com", password="password123")
        assert login.email == "test@example.com"

    def test_invalid_email(self):
        with pytest.raises(ValidationError):
            LoginRequest(email="not-an-email", password="password123")

    def test_empty_password(self):
        with pytest.raises(ValidationError):
            LoginRequest(email="test@example.com", password="")

    def test_password_too_short(self):
        with pytest.raises(ValidationError):
            LoginRequest(email="test@example.com", password="short")


class TestForgotPasswordSchema:
    def test_valid(self):
        req = ForgotPasswordRequest(email="test@example.com")
        assert req.email == "test@example.com"

    def test_invalid_email(self):
        with pytest.raises(ValidationError):
            ForgotPasswordRequest(email="invalid")


class TestResetPasswordSchema:
    def test_valid(self):
        req = ResetPasswordRequest(token="abc123", new_password="newpass123")
        assert req.token == "abc123"

    def test_short_password(self):
        with pytest.raises(ValidationError):
            ResetPasswordRequest(token="abc", new_password="short")


class TestChangePasswordSchema:
    def test_valid(self):
        req = ChangePasswordRequest(current_password="old", new_password="newpassword123")
        assert req.current_password == "old"


class TestChatSchema:
    def test_valid_message(self):
        req = ChatRequest(message="Hello")
        assert req.message == "Hello"

    def test_empty_message(self):
        with pytest.raises(ValidationError):
            ChatRequest(message="")

    def test_long_message(self):
        with pytest.raises(ValidationError):
            ChatRequest(message="x" * 5001)


class TestPagination:
    def test_defaults(self):
        p = PaginationParams()
        assert p.page == 1
        assert p.limit == 20

    def test_custom(self):
        p = PaginationParams(page=5, limit=50)
        assert p.page == 5
        assert p.limit == 50


class TestDocumentGenerateSchema:
    def test_valid_type(self):
        doc = DocumentGenerateRequest(
            employee_id="00000000-0000-0000-0000-000000000000",
            document_type="offer_letter"
        )
        assert doc.document_type == "offer_letter"

    def test_missing_document_type(self):
        with pytest.raises(ValidationError):
            DocumentGenerateRequest(
                employee_id="00000000-0000-0000-0000-000000000000",
            )
