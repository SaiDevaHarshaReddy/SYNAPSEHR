"""Employee schemas."""

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema


class EmployeeBase(BaseSchema):
    """Base employee schema."""

    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    employee_code: str = Field(..., min_length=1, max_length=50)
    designation: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = Field(None, max_length=500)
    gender: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[date] = None
    joining_date: Optional[date] = None
    employment_type: str = Field("full_time", max_length=50)
    status: str = Field("active", max_length=20)


class EmployeeCreate(EmployeeBase):
    """Create employee request."""

    department_id: UUID
    manager_id: Optional[UUID] = None
    user_id: UUID


class EmployeeUpdate(BaseSchema):
    """Update employee request."""

    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    designation: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = Field(None, max_length=500)
    department_id: Optional[UUID] = None
    manager_id: Optional[UUID] = None
    employment_type: Optional[str] = None
    status: Optional[str] = None


class EmployeeResponse(EmployeeBase):
    """Employee response schema."""

    id: UUID
    user_id: UUID
    department_id: UUID
    manager_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime


class EmployeeProfile(EmployeeResponse):
    """Detailed employee profile."""

    department_name: Optional[str] = None
    manager_name: Optional[str] = None
    leave_balance: Optional[dict] = None
    email: Optional[str] = None
