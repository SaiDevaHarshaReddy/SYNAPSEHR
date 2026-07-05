"""Department repository."""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.department import Department
from app.repositories.base import BaseRepository


class DepartmentRepository(BaseRepository[Department]):
    """Repository for department data access."""

    def __init__(self, session: AsyncSession):
        super().__init__(Department, session)

    async def get_by_organization(self, organization_id: UUID) -> list[Department]:
        """Get all departments in an organization."""
        result = await self.session.execute(
            select(Department).where(Department.organization_id == organization_id)
        )
        return list(result.scalars().all())

    async def get_by_name(self, name: str, organization_id: UUID) -> Optional[Department]:
        """Get department by name within an organization."""
        result = await self.session.execute(
            select(Department).where(
                Department.name == name,
                Department.organization_id == organization_id,
            )
        )
        return result.scalar_one_or_none()
