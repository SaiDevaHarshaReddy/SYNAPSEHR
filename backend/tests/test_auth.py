"""Tests for authentication and security."""
import pytest
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


class TestPasswordHashing:
    """Tests for password hashing."""

    def test_hash_password(self):
        hashed = hash_password("testpassword")
        assert hashed != "testpassword"
        assert len(hashed) > 0

    def test_verify_correct_password(self):
        password = "mysecretpassword"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_wrong_password(self):
        hashed = hash_password("correctpassword")
        assert verify_password("wrongpassword", hashed) is False


class TestJWTTokens:
    """Tests for JWT token creation and verification."""

    def test_create_access_token(self):
        token = create_access_token({"sub": "user123", "role": "admin"})
        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_valid_token(self):
        token = create_access_token({"sub": "user123", "role": "admin"})
        payload = decode_token(token)
        assert payload is not None
        assert payload.get("sub") == "user123"
        assert payload.get("role") == "admin"

    def test_verify_invalid_token(self):
        result = decode_token("invalid.token.here")
        assert result is None

    def test_create_refresh_token(self):
        token = create_refresh_token({"sub": "user123"})
        assert isinstance(token, str)
        assert len(token) > 0
