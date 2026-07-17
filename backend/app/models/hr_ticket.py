"""HR Ticket model."""

import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class HRTicket(BaseModel):
    """Support tickets between employees and HR."""

    __tablename__ = "hr_tickets"

    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False
    )
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="open", nullable=False)
    # messages is a list of dicts: {"sender_id": str, "sender_name": str, "text": str, "timestamp": str, "is_hr": bool}
    messages: Mapped[list | None] = mapped_column(JSON, nullable=True)

    # Relationships
    employee = relationship("Employee")
