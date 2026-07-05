"""Tests for services."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4


class TestEmailService:
    """Tests for EmailService."""

    @pytest.mark.asyncio
    async def test_send_email_without_config(self):
        from app.services.email import EmailService
        service = EmailService()
        service.username = ""
        service.password = ""
        result = await service.send_email("test@test.com", "Subject", "<p>Body</p>")
        assert result is False


class TestChatService:
    """Tests for ChatService."""

    @pytest.mark.asyncio
    async def test_get_or_create_conversation_new(self):
        from unittest.mock import AsyncMock, MagicMock
        from app.services.chat import ChatService
        from uuid import uuid4

        session = AsyncMock()
        service = ChatService(session)
        service.conv_repo = AsyncMock()
        service.conv_repo.create = AsyncMock(return_value=MagicMock(id=uuid4()))

        conv_id, is_new = await service.get_or_create_conversation(uuid4())
        assert is_new is True
        assert conv_id is not None


class TestPolicyService:
    """Tests for PolicyService."""

    @pytest.mark.asyncio
    async def test_list_policies(self):
        from unittest.mock import AsyncMock, MagicMock
        from app.services.policy import PolicyService
        from uuid import uuid4

        session = AsyncMock()
        service = PolicyService(session)
        service.repo = AsyncMock()
        service.repo.get_by_organization = AsyncMock(return_value=[])

        result = await service.list_policies(uuid4())
        assert result == []


class TestNotificationService:
    """Tests for NotificationService."""

    @pytest.mark.asyncio
    async def test_get_unread_count(self):
        from unittest.mock import AsyncMock, MagicMock
        from app.services.notification import NotificationService
        from uuid import uuid4

        session = AsyncMock()
        service = NotificationService(session)
        service.notification_repo = AsyncMock()
        service.notification_repo.get_unread_count = AsyncMock(return_value=5)

        count = await service.get_unread_count(uuid4())
        assert count == 5
