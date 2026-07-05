"""Standardized API response schemas."""

from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    """Standard success response format."""

    success: bool = True
    message: str = "Operation successful"
    data: Optional[T] = None


class ErrorDetail(BaseModel):
    """Error detail information."""

    code: str
    message: str
    request_id: Optional[str] = None
    detail: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standard error response format."""

    success: bool = False
    error: ErrorDetail


class PaginationInfo(BaseModel):
    """Pagination metadata."""

    page: int
    limit: int
    total: int
    total_pages: int
    has_next: bool
    has_previous: bool


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated list response format."""

    success: bool = True
    message: str = "Operation successful"
    data: list[T] = []
    pagination: PaginationInfo


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "healthy"
    version: str
    database: str = "connected"
