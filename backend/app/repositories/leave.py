"""Leave repositories."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.leave_balance import LeaveBalance
from app.models.leave_request import LeaveRequest
from app.models.leave_type import LeaveType
from app.repositories.base import BaseRepository


class LeaveTypeRepository(BaseRepository[LeaveType]):
    """Repository for leave type data access."""

    def __init__(self, session: AsyncSession):
        super().__init__(LeaveType, session)

    async def get_by_organization(self, organization_id: UUID) -> list[LeaveType]:
        """Get all leave types for an organization."""
        result = await self.session.execute(
            select(LeaveType).where(LeaveType.organization_id == organization_id)
        )
        return list(result.scalars().all())


class LeaveBalanceRepository(BaseRepository[LeaveBalance]):
    """Repository for leave balance data access."""

    def __init__(self, session: AsyncSession):
        super().__init__(LeaveBalance, session)

    async def get_by_employee(
        self, employee_id: UUID, year: int
    ) -> list[LeaveBalance]:
        """Get leave balances for an employee."""
        result = await self.session.execute(
            select(LeaveBalance).where(
                LeaveBalance.employee_id == employee_id,
                LeaveBalance.year == year,
            )
        )
        return list(result.scalars().all())

    async def get_by_employee_and_type(
        self, employee_id: UUID, leave_type_id: UUID, year: int
    ) -> Optional[LeaveBalance]:
        """Get specific leave balance for an employee."""
        result = await self.session.execute(
            select(LeaveBalance).where(
                LeaveBalance.employee_id == employee_id,
                LeaveBalance.leave_type_id == leave_type_id,
                LeaveBalance.year == year,
            )
        )
        return result.scalar_one_or_none()


class LeaveRequestRepository(BaseRepository[LeaveRequest]):
    """Repository for leave request data access."""

    def __init__(self, session: AsyncSession):
        super().__init__(LeaveRequest, session)

    async def get_by_employee(self, employee_id: UUID) -> list[LeaveRequest]:
        """Get all leave requests for an employee."""
        result = await self.session.execute(
            select(LeaveRequest)
            .where(LeaveRequest.employee_id == employee_id)
            .order_by(LeaveRequest.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_pending_by_manager(self, manager_id: UUID) -> list[LeaveRequest]:
        """Get pending leave requests for a manager's team."""
        result = await self.session.execute(
            select(LeaveRequest)
            .where(
                LeaveRequest.status == "pending",
            )
            .order_by(LeaveRequest.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_all_by_organization(self, organization_id: UUID) -> list[LeaveRequest]:
        """Get all leave requests for an organization."""
        from app.models.employee import Employee
        result = await self.session.execute(
            select(LeaveRequest)
            .join(Employee, LeaveRequest.employee_id == Employee.id)
            .where(Employee.organization_id == organization_id)
            .order_by(LeaveRequest.created_at.desc())
        )
        return list(result.scalars().all())

    async def update_read_status(self, request_id: UUID, is_read: bool) -> Optional[LeaveRequest]:
        """Update read status of a leave request."""
        return await self.update(request_id, is_read=is_read)
