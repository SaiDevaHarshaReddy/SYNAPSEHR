"""Department service."""

from typing import Optional
from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DuplicateException, NotFoundException
from app.repositories.department import DepartmentRepository
from app.schemas.common import PaginationParams
from app.schemas.department import (
    DepartmentCreate,
    DepartmentResponse,
    DepartmentUpdate,
)

logger = structlog.get_logger()


class DepartmentService:
    """Handle department business operations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.department_repo = DepartmentRepository(session)

    async def get_department(self, department_id: UUID) -> DepartmentResponse:
        """Get department by ID."""
        department = await self.department_repo.get_by_id(department_id)
        if department is None:
            raise NotFoundException("Department", str(department_id))

        return DepartmentResponse(
            id=department.id,
            organization_id=department.organization_id,
            name=department.name,
            description=department.description,
            manager_id=department.manager_id,
            created_at=department.created_at,
            updated_at=department.updated_at,
        )

    async def list_departments(
        self,
        organization_id: Optional[UUID],
        pagination: PaginationParams,
    ) -> tuple[list[DepartmentResponse], int]:
        """List departments for an organization."""
        departments, total = await self.department_repo.get_all(pagination)

        responses = [
            DepartmentResponse(
                id=dept.id,
                organization_id=dept.organization_id,
                name=dept.name,
                description=dept.description,
                manager_id=dept.manager_id,
                created_at=dept.created_at,
                updated_at=dept.updated_at,
            )
            for dept in departments
        ]

        return responses, total

    async def create_department(
        self, organization_id: UUID, data: DepartmentCreate
    ) -> DepartmentResponse:
        """Create a new department."""
        existing = await self.department_repo.get_by_name(data.name, organization_id)
        if existing:
            raise DuplicateException("Department", f"Department '{data.name}' already exists")

        department = await self.department_repo.create(
            organization_id=organization_id,
            name=data.name,
            description=data.description,
            manager_id=data.manager_id,
        )

        logger.info("department_created", department_id=str(department.id))

        return DepartmentResponse(
            id=department.id,
            organization_id=department.organization_id,
            name=department.name,
            description=department.description,
            manager_id=department.manager_id,
            created_at=department.created_at,
            updated_at=department.updated_at,
        )

    async def update_department(
        self, department_id: UUID, data: DepartmentUpdate
    ) -> DepartmentResponse:
        """Update a department."""
        department = await self.department_repo.get_by_id(department_id)
        if department is None:
            raise NotFoundException("Department", str(department_id))

        update_data = data.model_dump(exclude_unset=True)
        updated = await self.department_repo.update(department_id, **update_data)

        logger.info("department_updated", department_id=str(department_id))

        return DepartmentResponse(
            id=updated.id,
            organization_id=updated.organization_id,
            name=updated.name,
            description=updated.description,
            manager_id=updated.manager_id,
            created_at=updated.created_at,
            updated_at=updated.updated_at,
        )

    async def delete_department(self, department_id: UUID) -> None:
        """Delete a department."""
        department = await self.department_repo.get_by_id(department_id)
        if department is None:
            raise NotFoundException("Department", str(department_id))

        await self.department_repo.delete(department_id)

        logger.info("department_deleted", department_id=str(department_id))
