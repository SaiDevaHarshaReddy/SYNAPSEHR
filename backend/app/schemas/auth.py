"""Auth schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import BaseSchema


class LoginRequest(BaseSchema):
    """Login request schema."""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class TokenResponse(BaseSchema):
    """Token response schema."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseSchema):
    """Refresh token request."""

    refresh_token: str


class ForgotPasswordRequest(BaseSchema):
    """Forgot password request."""

    email: EmailStr


class ResetPasswordRequest(BaseSchema):
    """Reset password request."""

    token: str
    new_password: str = Field(..., min_length=8, max_length=128)


class ChangePasswordRequest(BaseSchema):
    """Change password request."""

    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)


class UserProfile(BaseSchema):
    """User profile response."""

    user_id: UUID
    email: str
    role: str
    organization_id: UUID
    organization_name: Optional[str] = None
    employee_name: Optional[str] = None
