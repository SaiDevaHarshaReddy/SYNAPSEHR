"""Workflow schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.schemas.common import BaseSchema


class WorkflowStepResponse(BaseSchema):
    """Workflow step response."""

    id: UUID
    step_name: str
    agent_name: Optional[str] = None
    status: str
    duration_ms: Optional[int] = None
    output: Optional[dict] = None
    created_at: datetime


class WorkflowResponse(BaseSchema):
    """Workflow response schema."""

    id: UUID
    employee_id: UUID
    workflow_type: str
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    steps: list[WorkflowStepResponse] = []
    created_at: datetime


class WorkflowRetryRequest(BaseSchema):
    """Retry failed workflow."""
    pass
