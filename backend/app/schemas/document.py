"""Document schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema


class DocumentGenerateRequest(BaseSchema):
    """Generate document request."""

    employee_id: UUID
    document_type: str = Field(
        ...,
        description="Document type: offer_letter, appointment_letter, experience_letter, salary_certificate, promotion_letter, warning_letter, relieving_letter, termination_letter",
    )
    additional_data: Optional[dict] = None


class DocumentResponse(BaseSchema):
    """Document response schema."""

    id: UUID
    employee_id: UUID
    document_type: str
    storage_path: str
    generated_by: Optional[UUID] = None
    generated_at: datetime
    created_at: datetime
