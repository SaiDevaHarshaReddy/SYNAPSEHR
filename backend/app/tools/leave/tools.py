"""Leave tools for AI agents."""

from datetime import date
from uuid import UUID

from app.tools.registry import register_tool


@register_tool(
    name="check_leave_balance",
    description="Check the leave balance for an employee"
)
async def check_leave_balance(
    employee_id: str,
    leave_type_id: str = None,
    year: int = None,
) -> dict:
    """Check leave balance for an employee."""
    from app.database.database import async_session_factory
    from app.repositories.leave import LeaveBalanceRepository

    if year is None:
        from datetime import datetime
        year = datetime.now().year

    async with async_session_factory() as session:
        repo = LeaveBalanceRepository(session)
        balances = await repo.get_by_employee(UUID(employee_id), year)

        result = []
        for balance in balances:
            if leave_type_id and str(balance.leave_type_id) != leave_type_id:
                continue
            result.append({
                "leave_type_id": str(balance.leave_type_id),
                "leave_type_name": balance.leave_type.name if balance.leave_type else "Unknown",
                "available_days": balance.available_days,
                "used_days": balance.used_days,
                "carry_forward_days": balance.carry_forward_days,
            })

        return {
            "employee_id": employee_id,
            "year": year,
            "balances": result,
        }


@register_tool(
    name="create_leave_request",
    description="Create a new leave request for an employee"
)
async def create_leave_request(
    employee_id: str,
    leave_type_id: str,
    start_date: str,
    end_date: str,
    reason: str = None,
) -> dict:
    """Create a new leave request."""
    from app.database.database import async_session_factory
    from app.services.leave import LeaveService
    from app.schemas.leave import LeaveRequestCreate

    async with async_session_factory() as session:
        service = LeaveService(session)

        data = LeaveRequestCreate(
            leave_type_id=UUID(leave_type_id),
            start_date=date.fromisoformat(start_date),
            end_date=date.fromisoformat(end_date),
            reason=reason,
        )

        result = await service.create_leave_request(UUID(employee_id), data)
        await session.commit()

        return {
            "request_id": str(result.id),
            "status": result.status,
            "message": "Leave request created successfully",
        }


@register_tool(
    name="get_leave_types",
    description="Get all leave types for an organization"
)
async def get_leave_types(organization_id: str) -> dict:
    """Get all leave types."""
    from app.database.database import async_session_factory
    from app.repositories.leave import LeaveTypeRepository

    async with async_session_factory() as session:
        repo = LeaveTypeRepository(session)
        types = await repo.get_by_organization(UUID(organization_id))

        return {
            "leave_types": [
                {
                    "id": str(lt.id),
                    "name": lt.name,
                    "days_per_year": lt.days_per_year,
                    "requires_approval": lt.requires_approval,
                    "is_paid": lt.is_paid,
                }
                for lt in types
            ],
        }
