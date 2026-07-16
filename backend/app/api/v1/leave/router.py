"""Leave API routes."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user, require_role
from app.database.database import get_db
from app.schemas.leave import (
    LeaveBalanceResponse,
    LeaveRequestCreate,
    LeaveRequestResponse,
    LeaveTypeResponse,
)
from app.schemas.response import SuccessResponse
from app.services.leave import LeaveService

router = APIRouter(prefix="/leave", tags=["Leave"])


@router.get("/types", response_model=SuccessResponse[list[LeaveTypeResponse]])
async def list_leave_types(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all leave types."""
    service = LeaveService(db)
    types = await service.get_leave_types(UUID(current_user["organization_id"]))

    return SuccessResponse(
        message="Leave types retrieved",
        data=types,
    )


@router.get("/balance", response_model=SuccessResponse[list[LeaveBalanceResponse]])
async def get_leave_balance(
    employee_id: Optional[UUID] = Query(None),
    year: Optional[int] = Query(None),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get leave balance."""
    service = LeaveService(db)

    # If no employee_id provided, use current user's employee
    if employee_id is None:
        from app.repositories.employee import EmployeeRepository
        emp_repo = EmployeeRepository(db)
        from uuid import UUID as UUIDType
        employee = await emp_repo.get_by_user_id(UUIDType(current_user["user_id"]))
        if employee is None:
            return SuccessResponse(message="Employee not found", data=[])
        employee_id = employee.id

    balances = await service.get_leave_balance(employee_id, year)

    return SuccessResponse(
        message="Leave balance retrieved",
        data=balances,
    )


@router.get("/history", response_model=SuccessResponse[list[LeaveRequestResponse]])
async def get_leave_history(
    employee_id: Optional[UUID] = Query(None),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get leave history."""
    service = LeaveService(db)

    # If the user is admin/hr and no employee_id is specified, return organization history
    if employee_id is None and current_user.get("role") in ["admin", "hr"]:
        history = await service.get_organization_leave_history(UUID(current_user["organization_id"]))
    else:
        if employee_id is None:
            from app.repositories.employee import EmployeeRepository
            emp_repo = EmployeeRepository(db)
            from uuid import UUID as UUIDType
            employee = await emp_repo.get_by_user_id(UUIDType(current_user["user_id"]))
            if employee is None:
                return SuccessResponse(message="Employee not found", data=[])
            employee_id = employee.id

        history = await service.get_employee_leave_history(employee_id)

    return SuccessResponse(
        message="Leave history retrieved",
        data=history,
    )

@router.patch("/{request_id}/read", response_model=SuccessResponse[LeaveRequestResponse])
async def mark_leave_read(
    request_id: UUID,
    is_read: bool = Query(True),
    current_user: dict = Depends(require_role("hr")),
    db: AsyncSession = Depends(get_db),
):
    """Mark a leave request as read."""
    service = LeaveService(db)
    result = await service.mark_as_read(request_id, is_read)

    return SuccessResponse(
        message="Leave request marked as read",
        data=result,
    )


@router.post("/request", response_model=SuccessResponse[LeaveRequestResponse])
async def create_leave_request(
    data: LeaveRequestCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a leave request."""
    from app.repositories.employee import EmployeeRepository
    emp_repo = EmployeeRepository(db)
    from uuid import UUID as UUIDType
    employee = await emp_repo.get_by_user_id(UUIDType(current_user["user_id"]))
    if employee is None:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("Employee profile")

    service = LeaveService(db)
    request = await service.create_leave_request(employee.id, data)

    return SuccessResponse(
        message="Leave request created",
        data=request,
    )


@router.post("/{request_id}/approve", response_model=SuccessResponse[LeaveRequestResponse])
async def approve_leave(
    request_id: UUID,
    status: str = Query("approved"),
    current_user: dict = Depends(require_role("hr")),
    db: AsyncSession = Depends(get_db),
):
    """Approve, reject or reset a leave request."""
    from app.repositories.employee import EmployeeRepository
    emp_repo = EmployeeRepository(db)
    from uuid import UUID as UUIDType
    employee = await emp_repo.get_by_user_id(UUIDType(current_user["user_id"]))
    if employee is None:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("Employee profile")

    service = LeaveService(db)
    result = await service.approve_leave(request_id, employee.id, status)

    return SuccessResponse(
        message=f"Leave request status updated to {status}",
        data=result,
    )


@router.post("/{request_id}/cancel", response_model=SuccessResponse[LeaveRequestResponse])
async def cancel_leave(
    request_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cancel a leave request."""
    from app.repositories.employee import EmployeeRepository
    emp_repo = EmployeeRepository(db)
    from uuid import UUID as UUIDType
    employee = await emp_repo.get_by_user_id(UUIDType(current_user["user_id"]))
    if employee is None:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("Employee profile")

    service = LeaveService(db)
    result = await service.cancel_leave(request_id, employee.id)

    return SuccessResponse(
        message="Leave request cancelled",
        data=result,
    )
