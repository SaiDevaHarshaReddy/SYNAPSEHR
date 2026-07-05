"""Employee repository."""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.employee import Employee
from app.repositories.base import BaseRepository


class EmployeeRepository(BaseRepository[Employee]):
    """Repository for employee data access."""

    def __init__(self, session: AsyncSession):
        super().__init__(Employee, session)

    async def get_by_user_id(self, user_id: UUID) -> Optional[Employee]:
        """Get employee by user ID."""
        result = await self.session.execute(
            select(Employee).where(Employee.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_employee_code(self, employee_code: str) -> Optional[Employee]:
        """Get employee by employee code."""
        result = await self.session.execute(
            select(Employee).where(Employee.employee_code == employee_code)
        )
        return result.scalar_one_or_none()

    async def get_by_department(self, department_id: UUID) -> list[Employee]:
        """Get all employees in a department."""
        result = await self.session.execute(
            select(Employee).where(Employee.department_id == department_id)
        )
        return list(result.scalars().all())

    async def get_by_manager(self, manager_id: UUID) -> list[Employee]:
        """Get all employees reporting to a manager."""
        result = await self.session.execute(
            select(Employee).where(Employee.manager_id == manager_id)
        )
        return list(result.scalars().all())

    async def get_with_department(self, employee_id: UUID) -> Optional[Employee]:
        """Get employee with department loaded."""
        result = await self.session.execute(
            select(Employee)
            .options(selectinload(Employee.department))
            .where(Employee.id == employee_id)
        )
        return result.scalar_one_or_none()
