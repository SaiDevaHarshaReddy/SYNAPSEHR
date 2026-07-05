"""Common Pydantic schemas."""

from datetime import datetime
from typing import Any, Generic, Optional, TypeVar
from uuid import UUID

from pydantic import BaseModel, Field

T = TypeVar("T")


class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    model_config = {"from_attributes": True}


class TimestampMixin(BaseModel):
    """Schema mixin with timestamps."""

    created_at: datetime
    updated_at: datetime


class IDMixin(BaseModel):
    """Schema mixin with UUID ID."""

    id: UUID


class PaginationParams(BaseModel):
    """Pagination query parameters."""

    page: int = Field(1, ge=1, description="Page number")
    limit: int = Field(20, ge=1, le=100, description="Items per page")
    sort: Optional[str] = Field(None, description="Sort field")
    order: str = Field("desc", description="Sort order: asc or desc")
    search: Optional[str] = Field(None, description="Search term")
