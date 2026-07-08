"""Authentication service."""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    AuthenticationException,
    DuplicateException,
    ValidationException,
)
from app.core.security import (
    create_token_pair,
    decode_token,
    hash_password,
    verify_password,
)
from app.repositories.employee import EmployeeRepository
from app.repositories.user import UserRepository
from app.schemas.auth import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserProfile,
)

logger = structlog.get_logger()


class AuthenticationService:
    """Handle authentication operations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)
        self.employee_repo = EmployeeRepository(session)

    async def register(self, data: RegisterRequest) -> TokenResponse:
        """Register a new user."""
        from sqlalchemy import select
        from app.models.organization import Organization
        from app.models.role import Role

        # Check if email exists
        user_exists = await self.user_repo.get_by_email(data.email)
        if user_exists:
            raise DuplicateException(f"User with email {data.email} already exists")

        # Get default organization
        org_result = await self.session.execute(select(Organization))
        org = org_result.scalars().first()
        if not org:
            raise ValidationException("No organization found to assign user to")

        # Get employee role
        role_result = await self.session.execute(
            select(Role).where(Role.name == "employee")
        )
        role = role_result.scalars().first()
        if not role:
            raise ValidationException("Employee role not found")

        # Create user
        hashed_password = hash_password(data.password)
        new_user = await self.user_repo.create(
            email=data.email,
            password_hash=hashed_password,
            organization_id=org.id,
            role_id=role.id,
            is_active=True
        )

        # Create employee record
        new_employee = await self.employee_repo.create(
            user_id=new_user.id,
            organization_id=org.id,
            full_name=data.full_name,
            email=data.email,
            job_title="Employee",
            status="active"
        )
        
        await self.session.commit()

        # Generate tokens
        tokens = create_token_pair(
            user_id=new_user.id,
            organization_id=new_user.organization_id,
            role=role.name,
        )

        logger.info("user_registered", user_id=str(new_user.id), email=new_user.email)

        return TokenResponse(**tokens)

    async def login(self, data: LoginRequest) -> TokenResponse:
        """Authenticate user and return tokens."""
        user = await self.user_repo.get_by_email(data.email)
        if user is None:
            raise AuthenticationException("Invalid email or password")

        if not user.is_active:
            raise AuthenticationException("Account is disabled")

        if not verify_password(data.password, user.password_hash):
            raise AuthenticationException("Invalid email or password")

        # Update last login
        await self.user_repo.update(
            user.id, last_login=datetime.now(timezone.utc)
        )

        # Get employee name if exists
        employee = await self.employee_repo.get_by_user_id(user.id)
        employee_name = employee.full_name if employee else None

        tokens = create_token_pair(
            user_id=user.id,
            organization_id=user.organization_id,
            role=user.role.name if user.role else "employee",
        )

        logger.info("user_logged_in", user_id=str(user.id), email=user.email)

        return TokenResponse(**tokens)

    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """Issue new access token using refresh token."""
        payload = decode_token(refresh_token)
        if payload is None:
            raise AuthenticationException("Invalid refresh token")

        if payload.get("type") != "refresh":
            raise AuthenticationException("Invalid token type")

        user_id = payload.get("sub")
        user = await self.user_repo.get_by_id(UUID(user_id))
        if user is None or not user.is_active:
            raise AuthenticationException("User not found or disabled")

        tokens = create_token_pair(
            user_id=user.id,
            organization_id=user.organization_id,
            role=user.role.name if user.role else "employee",
        )

        return TokenResponse(**tokens)

    async def get_current_user(self, user_id: UUID) -> UserProfile:
        """Get current user profile."""
        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise AuthenticationException("User not found")

        employee = await self.employee_repo.get_by_user_id(user.id)

        return UserProfile(
            user_id=user.id,
            email=user.email,
            role=user.role.name if user.role else "employee",
            organization_id=user.organization_id,
            organization_name=user.organization.name if user.organization else None,
            employee_name=employee.full_name if employee else None,
        )

    async def change_password(
        self, user_id: UUID, data: ChangePasswordRequest
    ) -> None:
        """Change user password."""
        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise AuthenticationException("User not found")

        if not verify_password(data.current_password, user.password_hash):
            raise AuthenticationException("Current password is incorrect")

        new_hash = hash_password(data.new_password)
        await self.user_repo.update(user.id, password_hash=new_hash)

        logger.info("password_changed", user_id=str(user.id))

    async def forgot_password(self, email: str) -> None:
        """Send password reset email if user exists."""
        user = await self.user_repo.get_by_email(email)
        if user is None:
            # Silently return to prevent email enumeration
            return

        import secrets
        token = secrets.token_urlsafe(32)
        # Store token with expiry (in production, save to DB with TTL)
        logger.info(
            "password_reset_requested",
            user_id=str(user.id),
            email=email,
            token=token,
        )

    async def reset_password(self, token: str, new_password: str) -> None:
        """Reset password using token from email."""
        # In production, validate token against DB and check expiry
        # For now, log the attempt
        logger.info("password_reset_attempted", token=token[:8] + "...")
        # After validation, the password would be updated
        # This is a placeholder until token storage is implemented
