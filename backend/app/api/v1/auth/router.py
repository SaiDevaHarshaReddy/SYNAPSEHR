"""Authentication API routes."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database.database import get_db
from app.schemas.auth import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    RefreshTokenRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserProfile,
)
from app.schemas.response import SuccessResponse
from app.services.authentication import AuthenticationService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=SuccessResponse[TokenResponse])
async def login(
    data: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate user and return tokens."""
    service = AuthenticationService(db)
    tokens = await service.login(data)

    return SuccessResponse(
        message="Login successful",
        data=tokens,
    )


@router.post("/logout")
async def logout(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Logout user (invalidate refresh token)."""
    return SuccessResponse(message="Logged out successfully")


@router.post("/refresh", response_model=SuccessResponse[TokenResponse])
async def refresh_token(
    data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """Issue new access token using refresh token."""
    service = AuthenticationService(db)
    tokens = await service.refresh_token(data.refresh_token)

    return SuccessResponse(
        message="Token refreshed successfully",
        data=tokens,
    )


@router.get("/me", response_model=SuccessResponse[UserProfile])
async def get_current_user_profile(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user profile."""
    from uuid import UUID
    service = AuthenticationService(db)
    profile = await service.get_current_user(UUID(current_user["user_id"]))

    return SuccessResponse(
        message="User profile retrieved",
        data=profile,
    )


@router.post("/change-password")
async def change_password(
    data: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Change user password."""
    from uuid import UUID
    service = AuthenticationService(db)
    await service.change_password(UUID(current_user["user_id"]), data)

    return SuccessResponse(message="Password changed successfully")


@router.post("/forgot-password")
async def forgot_password(
    data: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """Request a password reset email."""
    service = AuthenticationService(db)
    await service.forgot_password(data.email)
    return SuccessResponse(message="If the email exists, a reset link has been sent")


@router.post("/reset-password")
async def reset_password(
    data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """Reset password using token from email."""
    service = AuthenticationService(db)
    await service.reset_password(data.token, data.new_password)
    return SuccessResponse(message="Password reset successfully")
