"""Leave schemas."""

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema


class LeaveTypeResponse(BaseSchema):
    """Leave type response."""

    id: UUID
    name: str
    days_per_year: int
    requires_approval: bool
    is_paid: bool


class LeaveBalanceResponse(BaseSchema):
    """Leave balance response."""

    id: UUID
    leave_type_id: UUID
    leave_type_name: Optional[str] = None
    available_days: int
    used_days: int
    carry_forward_days: int
    year: int


class LeaveRequestCreate(BaseSchema):
    """Create leave request."""

    leave_type_id: UUID
    start_date: date
    end_date: date
    reason: Optional[str] = None


class LeaveRequestResponse(BaseSchema):
    """Leave request response."""

    id: UUID
    employee_id: UUID
    employee_name: Optional[str] = None
    leave_type_id: UUID
    leave_type_name: Optional[str] = None
    start_date: date
    end_date: date
    reason: Optional[str] = None
    status: str
    is_read: bool = False
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class LeaveApprovalRequest(BaseSchema):
    """Approve or reject leave request."""

    status: str = Field(..., pattern="^(approved|rejected)$")
    reason: Optional[str] = None
