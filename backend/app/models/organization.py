"""Organization model."""

import uuid

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Organization(BaseModel):
    """Organization/company information."""

    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    departments = relationship("Department", back_populates="organization")
    users = relationship("User", back_populates="organization")
    leave_types = relationship("LeaveType", back_populates="organization")
    policy_documents = relationship("PolicyDocument", back_populates="organization")
