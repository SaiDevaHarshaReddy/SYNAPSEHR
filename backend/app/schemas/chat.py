"""Chat schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema


class ChatRequest(BaseSchema):
    """Chat request schema."""

    message: str = Field(..., min_length=1, max_length=5000)
    conversation_id: Optional[UUID] = None


class MessageResponse(BaseSchema):
    """Message response schema."""

    id: UUID
    conversation_id: UUID
    sender: str
    message: str
    token_usage: Optional[int] = None
    created_at: datetime


class ConversationResponse(BaseSchema):
    """Conversation response schema."""

    id: UUID
    employee_id: UUID
    title: Optional[str] = None
    started_at: datetime
    ended_at: Optional[datetime] = None
    created_at: datetime


class ConversationDetail(BaseSchema):
    """Detailed conversation with messages."""

    id: UUID
    employee_id: UUID
    title: Optional[str] = None
    started_at: datetime
    ended_at: Optional[datetime] = None
    messages: list[MessageResponse] = []
    created_at: datetime


class ChatResponse(BaseSchema):
    """Chat response schema."""

    response: str
    conversation_id: UUID
    workflow_steps: Optional[list[dict]] = None
    sources_used: Optional[list[str]] = None
    execution_time_ms: Optional[int] = None
