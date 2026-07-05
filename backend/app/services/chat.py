"""Chat service for conversation and message management."""

from datetime import datetime, timezone
from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.repositories.conversation import ConversationRepository, MessageRepository

logger = structlog.get_logger()


class ChatService:
    """Handle chat operations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.conv_repo = ConversationRepository(session)
        self.msg_repo = MessageRepository(session)

    async def get_or_create_conversation(
        self, employee_id: UUID, conversation_id: UUID | None = None, title: str | None = None
    ) -> tuple[UUID, bool]:
        """Get existing conversation or create new one. Returns (conversation_id, is_new)."""
        if conversation_id:
            conv = await self.conv_repo.get_by_id(conversation_id)
            if conv and conv.employee_id == employee_id:
                return conversation_id, False
            # If conversation doesn't exist or belongs to another employee, create new
            conversation = await self.conv_repo.create(
                employee_id=employee_id,
                title=title or "New Conversation",
                started_at=datetime.now(timezone.utc),
            )
            await self.session.commit()
            return conversation.id, True

        # Create new conversation
        conversation = await self.conv_repo.create(
            employee_id=employee_id,
            title=title or "New Conversation",
            started_at=datetime.now(timezone.utc),
        )
        await self.session.commit()
        return conversation.id, True

    async def save_message(
        self, conversation_id: UUID, sender: str, message: str, token_usage: int | None = None
    ):
        """Save a message to a conversation."""
        return await self.msg_repo.create(
            conversation_id=conversation_id,
            sender=sender,
            message=message,
            token_usage=token_usage,
        )

    async def get_conversations(self, employee_id: UUID) -> list:
        """Get all conversations for an employee."""
        return await self.conv_repo.get_by_employee(employee_id)

    async def get_conversation_messages(self, conversation_id: UUID) -> list:
        """Get all messages in a conversation."""
        messages = await self.msg_repo.get_by_conversation(conversation_id)
        return messages

    async def delete_conversation(self, conversation_id: UUID, employee_id: UUID):
        """Delete a conversation and its messages."""
        conv = await self.conv_repo.get_by_id(conversation_id)
        if conv is None:
            raise NotFoundException("Conversation", str(conversation_id))
        if conv.employee_id != employee_id:
            raise NotFoundException("Conversation", str(conversation_id))

        # Delete messages first
        messages = await self.msg_repo.get_by_conversation(conversation_id)
        for msg in messages:
            await self.msg_repo.delete(msg.id)

        # Delete conversation
        await self.conv_repo.delete(conversation_id)
        await self.session.commit()

    async def end_conversation(self, conversation_id: UUID):
        """Mark a conversation as ended."""
        conv = await self.conv_repo.get_by_id(conversation_id)
        if conv:
            await self.conv_repo.update(
                conversation_id, ended_at=datetime.now(timezone.utc)
            )
            await self.session.commit()
