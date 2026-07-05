"""Admin API routes."""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.auth.dependencies import require_roles
from app.database.database import get_db
from app.schemas.response import SuccessResponse

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users")
async def list_users(
    current_user: dict = Depends(require_roles("admin", "hr")),
    db: AsyncSession = Depends(get_db),
):
    """List all users (admin/hr only)."""
    from app.repositories.user import UserRepository

    user_repo = UserRepository(db)
    users = await user_repo.get_by_organization(UUID(current_user["organization_id"]))

    return SuccessResponse(
        message="Users retrieved",
        data=[
            {
                "id": str(u.id),
                "email": u.email,
                "role": u.role.name if u.role else "unknown",
                "is_active": u.is_active,
                "last_login": str(u.last_login) if u.last_login else None,
            }
            for u in users
        ],
    )


@router.get("/audit")
async def get_audit_logs(
    current_user: dict = Depends(require_roles("admin", "hr")),
    db: AsyncSession = Depends(get_db),
):
    """Get audit logs (admin/hr only)."""
    from app.models.audit_log import AuditLog

    result = await db.execute(
        select(AuditLog).order_by(AuditLog.created_at.desc()).limit(100)
    )
    logs = list(result.scalars().all())

    return SuccessResponse(
        message="Audit logs retrieved",
        data=[
            {
                "id": str(log.id),
                "user_id": str(log.user_id) if log.user_id else None,
                "action": log.action,
                "resource": log.resource,
                "resource_id": log.resource_id,
                "success": log.success,
                "created_at": str(log.created_at),
            }
            for log in logs
        ],
    )


@router.get("/roles")
async def list_roles(
    current_user: dict = Depends(require_roles("admin")),
    db: AsyncSession = Depends(get_db),
):
    """List all roles."""
    from app.models.role import Role

    result = await db.execute(select(Role))
    roles = list(result.scalars().all())

    return SuccessResponse(
        message="Roles retrieved",
        data=[
            {"id": str(r.id), "name": r.name, "description": getattr(r, "description", None)}
            for r in roles
        ],
    )


@router.post("/roles")
async def create_role(
    data: dict,
    current_user: dict = Depends(require_roles("admin")),
    db: AsyncSession = Depends(get_db),
):
    """Create a new role."""
    from app.models.role import Role

    role = Role(
        name=data["name"],
        organization_id=UUID(current_user["organization_id"]),
    )
    db.add(role)
    await db.commit()

    return SuccessResponse(
        message="Role created",
        data={"id": str(role.id), "name": role.name},
    )


@router.patch("/settings")
async def update_system_settings(
    data: dict,
    current_user: dict = Depends(require_roles("admin")),
    db: AsyncSession = Depends(get_db),
):
    """Update system settings (admin only)."""
    # In production, this would update org settings
    return SuccessResponse(
        message="Settings updated",
        data=data,
    )
