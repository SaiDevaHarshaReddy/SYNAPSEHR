"""Notification and Audit repositories."""

from typing import Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.models.audit_log import AuditLog
from app.repositories.base import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    """Repository for notification data access."""

    def __init__(self, session: AsyncSession):
        super().__init__(Notification, session)

    async def get_by_employee(self, employee_id: UUID) -> list[Notification]:
        """Get all notifications for an employee."""
        result = await self.session.execute(
            select(Notification)
            .where(Notification.employee_id == employee_id)
            .order_by(Notification.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_unread_count(self, employee_id: UUID) -> int:
        """Get count of unread notifications."""
        result = await self.session.execute(
            select(func.count()).select_from(Notification).where(
                Notification.employee_id == employee_id,
                Notification.is_read == False,
            )
        )
        return result.scalar() or 0


class AuditRepository(BaseRepository[AuditLog]):
    """Repository for audit log data access."""

    def __init__(self, session: AsyncSession):
        super().__init__(AuditLog, session)

    async def get_by_user(self, user_id: UUID) -> list[AuditLog]:
        """Get audit logs for a user."""
        result = await self.session.execute(
            select(AuditLog)
            .where(AuditLog.user_id == user_id)
            .order_by(AuditLog.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_resource(self, resource: str, resource_id: str) -> list[AuditLog]:
        """Get audit logs for a specific resource."""
        result = await self.session.execute(
            select(AuditLog)
            .where(
                AuditLog.resource == resource,
                AuditLog.resource_id == resource_id,
            )
            .order_by(AuditLog.created_at.desc())
        )
        return list(result.scalars().all())
