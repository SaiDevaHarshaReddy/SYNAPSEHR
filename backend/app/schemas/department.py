"""Department schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema


class DepartmentBase(BaseSchema):
    """Base department schema."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class DepartmentCreate(DepartmentBase):
    """Create department request."""

    manager_id: Optional[UUID] = None


class DepartmentUpdate(BaseSchema):
    """Update department request."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    manager_id: Optional[UUID] = None


class DepartmentResponse(DepartmentBase):
    """Department response schema."""

    id: UUID
    organization_id: UUID
    manager_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
