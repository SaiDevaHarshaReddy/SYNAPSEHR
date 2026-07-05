"""Role-based access control dependencies."""

from typing import List

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.exceptions import AuthorizationException, AuthenticationException
from app.core.security import decode_token

security = HTTPBearer(auto_error=False)


class PermissionEvaluator:
    """Evaluate user permissions based on role."""

    ROLE_HIERARCHY = {
        "administrator": 4,
        "admin": 4,
        "hr": 3,
        "manager": 2,
        "employee": 1,
    }

    @staticmethod
    def has_permission(user_role: str, required_role: str) -> bool:
        """Check if user role meets the required role level."""
        user_level = PermissionEvaluator.ROLE_HIERARCHY.get(user_role, 0)
        required_level = PermissionEvaluator.ROLE_HIERARCHY.get(required_role, 0)
        return user_level >= required_level

    @staticmethod
    def has_any_role(user_role: str, required_roles: List[str]) -> bool:
        """Check if user has any of the required roles."""
        return user_role in required_roles


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """Extract and validate the current user from JWT token."""
    if credentials is None:
        raise AuthenticationException("Missing authentication credentials")

    payload = decode_token(credentials.credentials)
    if payload is None:
        raise AuthenticationException("Invalid or expired token")

    if payload.get("type") != "access":
        raise AuthenticationException("Invalid token type")

    return {
        "user_id": payload.get("sub"),
        "organization_id": payload.get("org_id"),
        "role": payload.get("role"),
    }


def require_roles(*roles: str):
    """Dependency that requires the user to have one of the specified roles."""

    async def role_checker(
        current_user: dict = Depends(get_current_user),
    ) -> dict:
        user_role = current_user.get("role", "")
        if not PermissionEvaluator.has_any_role(user_role, list(roles)):
            raise AuthorizationException(
                f"This action requires one of the following roles: {', '.join(roles)}"
            )
        return current_user

    return role_checker


def require_role(role: str):
    """Dependency that requires the user to have a specific role level."""

    async def role_checker(
        current_user: dict = Depends(get_current_user),
    ) -> dict:
        user_role = current_user.get("role", "")
        if not PermissionEvaluator.has_permission(user_role, role):
            raise AuthorizationException(
                f"This action requires the '{role}' role or higher"
            )
        return current_user

    return role_checker
