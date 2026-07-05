"""Policy document management service."""

import os
import uuid as uuid_lib
from datetime import datetime, timezone

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ValidationException
from app.repositories.document import PolicyDocumentRepository

logger = structlog.get_logger()


class PolicyService:
    """Handle policy document CRUD operations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = PolicyDocumentRepository(session)

    async def list_policies(self, organization_id: uuid_lib.UUID) -> list:
        """List all policies for an organization."""
        return await self.repo.get_by_organization(organization_id)

    async def get_policy(self, policy_id: uuid_lib.UUID) -> any:
        """Get a policy by ID."""
        policy = await self.repo.get_by_id(policy_id)
        if policy is None:
            raise NotFoundException("Policy", str(policy_id))
        return policy

    async def create_policy(
        self,
        organization_id: uuid_lib.UUID,
        title: str,
        category: str,
        file_name: str,
        storage_path: str,
        uploaded_by: uuid_lib.UUID | None = None,
        version: int = 1,
    ):
        """Create a new policy document record."""
        return await self.repo.create(
            organization_id=organization_id,
            title=title,
            category=category,
            file_name=file_name,
            storage_path=storage_path,
            version=version,
            uploaded_by=uploaded_by,
        )

    async def delete_policy(self, policy_id: uuid_lib.UUID, organization_id: uuid_lib.UUID):
        """Delete a policy document."""
        policy = await self.repo.get_by_id(policy_id)
        if policy is None:
            raise NotFoundException("Policy", str(policy_id))

        if policy.organization_id != organization_id:
            raise ValidationException("You do not have permission to delete this policy")

        # Delete file from disk
        if policy.storage_path and os.path.exists(policy.storage_path):
            os.remove(policy.storage_path)

        # Remove from vector store
        try:
            from app.rag.retriever import Retriever
            retriever = Retriever()
            await retriever.delete_document(str(policy_id))
        except Exception as e:
            logger.warning("vector_delete_failed", policy_id=str(policy_id), error=str(e))

        await self.repo.delete(policy_id)

    async def get_policies_by_category(self, organization_id: uuid_lib.UUID, category: str):
        """Get policies filtered by category."""
        return await self.repo.get_by_category(organization_id, category)
