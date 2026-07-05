"""Policy API routes."""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user, require_roles
from app.database.database import get_db
from app.schemas.response import SuccessResponse
from app.services.policy import PolicyService

router = APIRouter(prefix="/policies", tags=["Policies"])


@router.get("")
async def list_policies(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all policies for the organization."""
    service = PolicyService(db)
    policies = await service.list_policies(UUID(current_user["organization_id"]))

    return SuccessResponse(
        message="Policies retrieved",
        data=[
            {
                "id": str(p.id),
                "title": p.title,
                "category": p.category,
                "file_name": p.file_name,
                "version": p.version,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in policies
        ],
    )


@router.get("/{policy_id}")
async def get_policy(
    policy_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific policy."""
    service = PolicyService(db)
    policy = await service.get_policy(policy_id)

    return SuccessResponse(
        message="Policy retrieved",
        data={
            "id": str(policy.id),
            "title": policy.title,
            "category": policy.category,
            "file_name": policy.file_name,
            "version": policy.version,
            "storage_path": policy.storage_path,
            "created_at": policy.created_at.isoformat() if policy.created_at else None,
        },
    )


@router.delete("/{policy_id}")
async def delete_policy(
    policy_id: UUID,
    current_user: dict = Depends(require_roles("admin", "hr")),
    db: AsyncSession = Depends(get_db),
):
    """Delete a policy document."""
    service = PolicyService(db)
    await service.delete_policy(policy_id, UUID(current_user["organization_id"]))
    return SuccessResponse(message="Policy deleted")
