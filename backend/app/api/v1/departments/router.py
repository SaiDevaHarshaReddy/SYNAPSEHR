"""Department API routes."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user, require_role
from app.database.database import get_db
from app.schemas.common import PaginationParams
from app.schemas.department import DepartmentCreate, DepartmentResponse, DepartmentUpdate
from app.schemas.response import PaginatedResponse, PaginationInfo, SuccessResponse
from app.services.department import DepartmentService

router = APIRouter(prefix="/departments", tags=["Departments"])


@router.get("", response_model=PaginatedResponse[DepartmentResponse])
async def list_departments(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List departments."""
    service = DepartmentService(db)
    pagination = PaginationParams(page=page, limit=limit)

    departments, total = await service.list_departments(
        UUID(current_user["organization_id"]), pagination
    )

    return PaginatedResponse(
        data=departments,
        pagination=PaginationInfo(
            page=page,
            limit=limit,
            total=total,
            total_pages=(total + limit - 1) // limit,
            has_next=(page * limit) < total,
            has_previous=page > 1,
        ),
    )


@router.get("/{department_id}", response_model=SuccessResponse[DepartmentResponse])
async def get_department(
    department_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get department by ID."""
    service = DepartmentService(db)
    department = await service.get_department(department_id)

    return SuccessResponse(
        message="Department retrieved",
        data=department,
    )


@router.post("", response_model=SuccessResponse[DepartmentResponse])
async def create_department(
    data: DepartmentCreate,
    current_user: dict = Depends(require_role("hr")),
    db: AsyncSession = Depends(get_db),
):
    """Create a new department."""
    service = DepartmentService(db)
    department = await service.create_department(
        UUID(current_user["organization_id"]), data
    )

    return SuccessResponse(
        message="Department created",
        data=department,
    )


@router.patch("/{department_id}", response_model=SuccessResponse[DepartmentResponse])
async def update_department(
    department_id: UUID,
    data: DepartmentUpdate,
    current_user: dict = Depends(require_role("hr")),
    db: AsyncSession = Depends(get_db),
):
    """Update a department."""
    service = DepartmentService(db)
    department = await service.update_department(department_id, data)

    return SuccessResponse(
        message="Department updated",
        data=department,
    )


@router.delete("/{department_id}")
async def delete_department(
    department_id: UUID,
    current_user: dict = Depends(require_role("hr")),
    db: AsyncSession = Depends(get_db),
):
    """Delete a department."""
    service = DepartmentService(db)
    await service.delete_department(department_id)

    return SuccessResponse(message="Department deleted")
