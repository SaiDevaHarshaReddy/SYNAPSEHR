"""Notification schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema


class NotificationResponse(BaseSchema):
    """Notification response schema."""

    id: UUID
    employee_id: UUID
    title: str
    message: str
    type: str
    is_read: bool
    created_at: datetime


class NotificationUpdate(BaseSchema):
    """Update notification (mark as read)."""

    is_read: bool = True
