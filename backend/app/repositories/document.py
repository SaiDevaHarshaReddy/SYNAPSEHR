"""Document repository."""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.generated_document import GeneratedDocument
from app.models.policy_document import PolicyDocument
from app.repositories.base import BaseRepository


class GeneratedDocumentRepository(BaseRepository[GeneratedDocument]):
    """Repository for generated document data access."""

    def __init__(self, session: AsyncSession):
        super().__init__(GeneratedDocument, session)

    async def get_by_employee(self, employee_id: UUID) -> list[GeneratedDocument]:
        """Get all generated documents for an employee."""
        result = await self.session.execute(
            select(GeneratedDocument)
            .where(GeneratedDocument.employee_id == employee_id)
            .order_by(GeneratedDocument.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_type(self, document_type: str) -> list[GeneratedDocument]:
        """Get all documents of a specific type."""
        result = await self.session.execute(
            select(GeneratedDocument)
            .where(GeneratedDocument.document_type == document_type)
            .order_by(GeneratedDocument.created_at.desc())
        )
        return list(result.scalars().all())


class PolicyDocumentRepository(BaseRepository[PolicyDocument]):
    """Repository for policy document data access."""

    def __init__(self, session: AsyncSession):
        super().__init__(PolicyDocument, session)

    async def get_by_organization(self, organization_id: UUID) -> list[PolicyDocument]:
        """Get all policy documents for an organization."""
        result = await self.session.execute(
            select(PolicyDocument)
            .where(PolicyDocument.organization_id == organization_id)
            .order_by(PolicyDocument.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_category(
        self, organization_id: UUID, category: str
    ) -> list[PolicyDocument]:
        """Get policy documents by category."""
        result = await self.session.execute(
            select(PolicyDocument)
            .where(
                PolicyDocument.organization_id == organization_id,
                PolicyDocument.category == category,
            )
        )
        return list(result.scalars().all())
