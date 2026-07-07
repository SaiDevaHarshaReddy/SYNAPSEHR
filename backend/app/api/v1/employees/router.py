"""Employee API routes."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user, require_role
from app.database.database import get_db
from app.schemas.common import PaginationParams
from app.schemas.employee import EmployeeCreate, EmployeeResponse, EmployeeUpdate
from app.schemas.response import PaginatedResponse, PaginationInfo, SuccessResponse
from app.services.employee import EmployeeService

router = APIRouter(prefix="/employees", tags=["Employees"])


@router.get("", response_model=PaginatedResponse[EmployeeResponse])
async def list_employees(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort: Optional[str] = Query(None),
    order: str = Query("desc"),
    search: Optional[str] = Query(None),
    department_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List employees with pagination and filters."""
    service = EmployeeService(db)
    pagination = PaginationParams(page=page, limit=limit, sort=sort, order=order, search=search)

    employees, total = await service.list_employees(pagination, department_id, status)

    return PaginatedResponse(
        data=employees,
        pagination=PaginationInfo(
            page=page,
            limit=limit,
            total=total,
            total_pages=(total + limit - 1) // limit,
            has_next=(page * limit) < total,
            has_previous=page > 1,
        ),
    )


@router.get("/{employee_id}", response_model=SuccessResponse[EmployeeResponse])
async def get_employee(
    employee_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get employee by ID."""
    service = EmployeeService(db)
    employee = await service.get_employee(employee_id)

    return SuccessResponse(
        message="Employee retrieved",
        data=employee,
    )


@router.post("", response_model=SuccessResponse[EmployeeResponse])
async def create_employee(
    data: EmployeeCreate,
    current_user: dict = Depends(require_role("hr")),
    db: AsyncSession = Depends(get_db),
):
    """Create a new employee."""
    service = EmployeeService(db)
    employee = await service.create_employee(data)

    return SuccessResponse(
        message="Employee created",
        data=employee,
    )


@router.patch("/{employee_id}", response_model=SuccessResponse[EmployeeResponse])
async def update_employee(
    employee_id: UUID,
    data: EmployeeUpdate,
    current_user: dict = Depends(require_role("hr")),
    db: AsyncSession = Depends(get_db),
):
    """Update an employee."""
    service = EmployeeService(db)
    employee = await service.update_employee(employee_id, data)

    return SuccessResponse(
        message="Employee updated",
        data=employee,
    )


@router.delete("/{employee_id}")
async def deactivate_employee(
    employee_id: UUID,
    current_user: dict = Depends(require_role("hr")),
    db: AsyncSession = Depends(get_db),
):
    """Deactivate an employee."""
    service = EmployeeService(db)
    await service.deactivate_employee(employee_id)

    return SuccessResponse(message="Employee deactivated")
