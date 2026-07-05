"""Analytics API routes."""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user, require_role, require_roles
from app.database.database import get_db
from app.schemas.response import SuccessResponse
from app.services.analytics import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard")
async def get_dashboard_metrics(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get dashboard KPI metrics."""
    service = AnalyticsService(db)
    metrics = await service.get_dashboard_metrics(UUID(current_user["organization_id"]))

    return SuccessResponse(
        message="Dashboard metrics retrieved",
        data=metrics,
    )


@router.get("/leave")
async def get_leave_analytics(
    current_user: dict = Depends(require_role("hr")),
    db: AsyncSession = Depends(get_db),
):
    """Get leave analytics."""
    service = AnalyticsService(db)
    analytics = await service.get_leave_analytics(UUID(current_user["organization_id"]))

    return SuccessResponse(
        message="Leave analytics retrieved",
        data=analytics,
    )


@router.get("/departments")
async def get_department_distribution(
    current_user: dict = Depends(require_role("hr")),
    db: AsyncSession = Depends(get_db),
):
    """Get employee distribution by department."""
    service = AnalyticsService(db)
    distribution = await service.get_department_distribution(
        UUID(current_user["organization_id"])
    )

    return SuccessResponse(
        message="Department distribution retrieved",
        data=distribution,
    )


@router.get("/ai")
async def get_ai_analytics(
    current_user: dict = Depends(require_role("hr")),
    db: AsyncSession = Depends(get_db),
):
    """Get AI usage analytics."""
    from sqlalchemy import func, select
    from app.models.conversation import Conversation
    from app.models.message import Message

    conv_count = (await db.execute(select(func.count()).select_from(Conversation))).scalar() or 0
    msg_count = (await db.execute(select(func.count()).select_from(Message))).scalar() or 0

    return SuccessResponse(
        message="AI analytics retrieved",
        data={
            "total_conversations": conv_count,
            "total_messages": msg_count,
            "avg_messages_per_conversation": round(msg_count / max(conv_count, 1), 1),
        },
    )


@router.get("/employees")
async def get_employee_analytics(
    current_user: dict = Depends(require_roles("admin", "hr")),
    db: AsyncSession = Depends(get_db),
):
    """Get employee analytics report."""
    from sqlalchemy import func, select
    from app.models.employee import Employee
    from app.models.department import Department

    total = (await db.execute(select(func.count()).select_from(Employee))).scalar() or 0

    dept_query = (
        select(Department.name, func.count(Employee.id))
        .join(Employee, Department.id == Employee.department_id, isouter=True)
        .group_by(Department.name)
    )
    dept_result = await db.execute(dept_query)
    departments = [{"name": name, "count": count} for name, count in dept_result.all()]

    return SuccessResponse(
        message="Employee analytics retrieved",
        data={
            "total_employees": total,
            "by_department": departments,
        },
    )
