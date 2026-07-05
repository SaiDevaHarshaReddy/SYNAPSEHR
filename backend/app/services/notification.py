"""Notification service."""

from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.repositories.notification import NotificationRepository
from app.schemas.notification import NotificationResponse

logger = structlog.get_logger()


class NotificationService:
    """Handle notification operations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.notification_repo = NotificationRepository(session)

    async def get_notifications(
        self, employee_id: UUID
    ) -> list[NotificationResponse]:
        """Get all notifications for an employee."""
        notifications = await self.notification_repo.get_by_employee(employee_id)
        return [
            NotificationResponse(
                id=n.id,
                employee_id=n.employee_id,
                title=n.title,
                message=n.message,
                type=n.type,
                is_read=n.is_read,
                created_at=n.created_at,
            )
            for n in notifications
        ]

    async def get_unread_count(self, employee_id: UUID) -> int:
        """Get count of unread notifications."""
        return await self.notification_repo.get_unread_count(employee_id)

    async def mark_as_read(self, notification_id: UUID) -> NotificationResponse:
        """Mark a notification as read."""
        notification = await self.notification_repo.get_by_id(notification_id)
        if notification is None:
            from app.core.exceptions import NotFoundException
            raise NotFoundException("Notification", str(notification_id))

        updated = await self.notification_repo.update(notification_id, is_read=True)

        return NotificationResponse(
            id=updated.id,
            employee_id=updated.employee_id,
            title=updated.title,
            message=updated.message,
            type=updated.type,
            is_read=updated.is_read,
            created_at=updated.created_at,
        )

    async def create_notification(
        self,
        employee_id: UUID,
        title: str,
        message: str,
        notification_type: str,
    ) -> NotificationResponse:
        """Create a new notification."""
        notification = await self.notification_repo.create(
            employee_id=employee_id,
            title=title,
            message=message,
            type=notification_type,
            is_read=False,
        )

        logger.info(
            "notification_created",
            notification_id=str(notification.id),
            type=notification_type,
        )

        return NotificationResponse(
            id=notification.id,
            employee_id=notification.employee_id,
            title=notification.title,
            message=notification.message,
            type=notification.type,
            is_read=notification.is_read,
            created_at=notification.created_at,
        )

    async def mark_all_as_read(self, employee_id: UUID) -> int:
        """Mark all notifications as read for an employee."""
        notifications = await self.notification_repo.get_by_employee(employee_id)
        count = 0
        for n in notifications:
            if not n.is_read:
                await self.notification_repo.update(n.id, is_read=True)
                count += 1
        return count
