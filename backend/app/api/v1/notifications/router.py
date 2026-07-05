"""Notification API routes."""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database.database import get_db
from app.repositories.employee import EmployeeRepository
from app.schemas.notification import NotificationResponse
from app.schemas.response import SuccessResponse
from app.services.notification import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])


async def _get_employee_id(current_user: dict, db: AsyncSession) -> UUID:
    """Get employee ID from current user."""
    from app.core.exceptions import NotFoundException
    emp_repo = EmployeeRepository(db)
    employee = await emp_repo.get_by_user_id(UUID(current_user["user_id"]))
    if employee is None:
        raise NotFoundException("Employee profile")
    return employee.id


@router.get("", response_model=SuccessResponse[list[NotificationResponse]])
async def list_notifications(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all notifications."""
    employee_id = await _get_employee_id(current_user, db)
    service = NotificationService(db)
    notifications = await service.get_notifications(employee_id)

    return SuccessResponse(
        message="Notifications retrieved",
        data=notifications,
    )


@router.get("/unread-count")
async def get_unread_count(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get count of unread notifications."""
    employee_id = await _get_employee_id(current_user, db)
    service = NotificationService(db)
    count = await service.get_unread_count(employee_id)

    return SuccessResponse(
        message="Unread count retrieved",
        data={"count": count},
    )


@router.patch("/{notification_id}/read", response_model=SuccessResponse[NotificationResponse])
async def mark_as_read(
    notification_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark a notification as read."""
    service = NotificationService(db)
    notification = await service.mark_as_read(notification_id)

    return SuccessResponse(
        message="Notification marked as read",
        data=notification,
    )


@router.post("/read-all")
async def mark_all_as_read(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark all notifications as read."""
    employee_id = await _get_employee_id(current_user, db)
    service = NotificationService(db)
    count = await service.mark_all_as_read(employee_id)

    return SuccessResponse(
        message=f"Marked {count} notifications as read",
        data={"count": count},
    )


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a notification."""
    service = NotificationService(db)
    await service.delete_notification(notification_id)
    return SuccessResponse(message="Notification deleted")
