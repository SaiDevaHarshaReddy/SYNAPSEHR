"""Leave service."""

from datetime import date, datetime, timezone
from typing import Optional
from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    BusinessRuleException,
    LeaveBalanceExceeded,
    NotFoundException,
)
from app.repositories.employee import EmployeeRepository
from app.repositories.leave import (
    LeaveBalanceRepository,
    LeaveRequestRepository,
    LeaveTypeRepository,
)
from app.schemas.leave import (
    LeaveBalanceResponse,
    LeaveRequestCreate,
    LeaveRequestResponse,
    LeaveTypeResponse,
)

logger = structlog.get_logger()


class LeaveService:
    """Handle leave management operations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.leave_type_repo = LeaveTypeRepository(session)
        self.leave_balance_repo = LeaveBalanceRepository(session)
        self.leave_request_repo = LeaveRequestRepository(session)
        self.employee_repo = EmployeeRepository(session)

    async def get_leave_types(self, organization_id: UUID) -> list[LeaveTypeResponse]:
        """Get all leave types for an organization."""
        leave_types = await self.leave_type_repo.get_by_organization(organization_id)
        return [
            LeaveTypeResponse(
                id=lt.id,
                name=lt.name,
                days_per_year=lt.days_per_year,
                requires_approval=lt.requires_approval,
                is_paid=lt.is_paid,
            )
            for lt in leave_types
        ]

    async def get_leave_balance(
        self, employee_id: UUID, year: Optional[int] = None
    ) -> list[LeaveBalanceResponse]:
        """Get leave balance for an employee."""
        if year is None:
            year = datetime.now().year

        balances = await self.leave_balance_repo.get_by_employee(employee_id, year)
        return [
            LeaveBalanceResponse(
                id=lb.id,
                leave_type_id=lb.leave_type_id,
                leave_type_name=lb.leave_type.name if lb.leave_type else None,
                available_days=lb.available_days,
                used_days=lb.used_days,
                carry_forward_days=lb.carry_forward_days,
                year=lb.year,
            )
            for lb in balances
        ]

    async def create_leave_request(
        self, employee_id: UUID, data: LeaveRequestCreate
    ) -> LeaveRequestResponse:
        """Create a new leave request."""
        # Validate employee exists
        employee = await self.employee_repo.get_by_id(employee_id)
        if employee is None:
            raise NotFoundException("Employee", str(employee_id))

        # Validate dates
        if data.end_date < data.start_date:
            raise BusinessRuleException("End date must be after start date")

        # Calculate leave days (simplified - excluding weekends)
        leave_days = self._calculate_leave_days(data.start_date, data.end_date)

        # Check leave balance
        year = data.start_date.year
        balance = await self.leave_balance_repo.get_by_employee_and_type(
            employee_id, data.leave_type_id, year
        )

        if balance and balance.available_days < leave_days:
            raise LeaveBalanceExceeded(
                available=balance.available_days,
                requested=leave_days,
            )

        # Create request
        request = await self.leave_request_repo.create(
            employee_id=employee_id,
            leave_type_id=data.leave_type_id,
            start_date=data.start_date,
            end_date=data.end_date,
            reason=data.reason,
            status="pending",
        )

        logger.info(
            "leave_request_created",
            employee_id=str(employee_id),
            request_id=str(request.id),
        )

        return LeaveRequestResponse(
            id=request.id,
            employee_id=request.employee_id,
            leave_type_id=request.leave_type_id,
            start_date=request.start_date,
            end_date=request.end_date,
            reason=request.reason,
            status=request.status,
            created_at=request.created_at,
            updated_at=request.updated_at,
        )

    async def approve_leave(
        self,
        request_id: UUID,
        approver_id: UUID,
        approved: bool,
        reason: Optional[str] = None,
    ) -> LeaveRequestResponse:
        """Approve or reject a leave request."""
        request = await self.leave_request_repo.get_by_id(request_id)
        if request is None:
            raise NotFoundException("Leave request", str(request_id))

        if request.status != "pending":
            raise BusinessRuleException("Leave request is not pending")

        new_status = "approved" if approved else "rejected"

        # Update request
        updated = await self.leave_request_repo.update(
            request_id,
            status=new_status,
            approved_by=approver_id,
            approved_at=datetime.now(timezone.utc),
        )

        # If approved, update leave balance
        if approved:
            year = request.start_date.year
            balance = await self.leave_balance_repo.get_by_employee_and_type(
                request.employee_id, request.leave_type_id, year
            )
            if balance:
                leave_days = self._calculate_leave_days(
                    request.start_date, request.end_date
                )
                await self.leave_balance_repo.update(
                    balance.id,
                    available_days=balance.available_days - leave_days,
                    used_days=balance.used_days + leave_days,
                )

        logger.info(
            "leave_request_" + new_status,
            request_id=str(request_id),
            approver_id=str(approver_id),
        )

        return LeaveRequestResponse(
            id=updated.id,
            employee_id=updated.employee_id,
            leave_type_id=updated.leave_type_id,
            start_date=updated.start_date,
            end_date=updated.end_date,
            reason=updated.reason,
            status=updated.status,
            approved_by=updated.approved_by,
            approved_at=updated.approved_at,
            created_at=updated.created_at,
            updated_at=updated.updated_at,
        )

    async def cancel_leave(
        self, request_id: UUID, employee_id: UUID
    ) -> LeaveRequestResponse:
        """Cancel a leave request."""
        request = await self.leave_request_repo.get_by_id(request_id)
        if request is None:
            raise NotFoundException("Leave request", str(request_id))

        if request.employee_id != employee_id:
            raise BusinessRuleException("You can only cancel your own leave requests")

        if request.status not in ["pending", "approved"]:
            raise BusinessRuleException("Cannot cancel this leave request")

        updated = await self.leave_request_repo.update(
            request_id, status="cancelled"
        )

        logger.info("leave_request_cancelled", request_id=str(request_id))

        return LeaveRequestResponse(
            id=updated.id,
            employee_id=updated.employee_id,
            leave_type_id=updated.leave_type_id,
            start_date=updated.start_date,
            end_date=updated.end_date,
            reason=updated.reason,
            status=updated.status,
            created_at=updated.created_at,
            updated_at=updated.updated_at,
        )

    async def get_employee_leave_history(
        self, employee_id: UUID
    ) -> list[LeaveRequestResponse]:
        """Get leave history for an employee."""
        requests = await self.leave_request_repo.get_by_employee(employee_id)
        return [
            LeaveRequestResponse(
                id=r.id,
                employee_id=r.employee_id,
                leave_type_id=r.leave_type_id,
                start_date=r.start_date,
                end_date=r.end_date,
                reason=r.reason,
                status=r.status,
                approved_by=r.approved_by,
                approved_at=r.approved_at,
                created_at=r.created_at,
                updated_at=r.updated_at,
            )
            for r in requests
        ]

    def _calculate_leave_days(self, start: date, end: date) -> int:
        """Calculate business days between two dates (excluding weekends)."""
        days = 0
        current = start
        while current <= end:
            if current.weekday() < 5:  # Monday=0 to Friday=4
                days += 1
            current = date.fromordinal(current.toordinal() + 1)
        return max(days, 1)
