"""Conversation and Message repositories."""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation
from app.models.message import Message
from app.repositories.base import BaseRepository


class ConversationRepository(BaseRepository[Conversation]):
    """Repository for conversation data access."""

    def __init__(self, session: AsyncSession):
        super().__init__(Conversation, session)

    async def get_by_employee(self, employee_id: UUID) -> list[Conversation]:
        """Get all conversations for an employee."""
        result = await self.session.execute(
            select(Conversation)
            .where(Conversation.employee_id == employee_id)
            .order_by(Conversation.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_with_messages(self, conversation_id: UUID) -> Optional[Conversation]:
        """Get conversation with all messages."""
        result = await self.session.execute(
            select(Conversation)
            .where(Conversation.id == conversation_id)
            .options(selectinload(Conversation.messages))
        )
        return result.scalar_one_or_none()


class MessageRepository(BaseRepository[Message]):
    """Repository for message data access."""

    def __init__(self, session: AsyncSession):
        super().__init__(Message, session)

    async def get_by_conversation(self, conversation_id: UUID) -> list[Message]:
        """Get all messages in a conversation."""
        result = await self.session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )
        return list(result.scalars().all())
