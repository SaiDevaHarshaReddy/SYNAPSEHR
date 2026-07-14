"""Analytics API routes."""

from datetime import datetime
from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user, require_role, require_roles
from app.database.database import get_db
from app.schemas.response import SuccessResponse
from app.services.analytics import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard")
async def get_dashboard_metrics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    department_id: Optional[UUID] = Query(None),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get dashboard KPI metrics."""
    service = AnalyticsService(db)
    org_id = current_user.get("organization_id")
    org_uuid = UUID(org_id) if org_id else None
    try:
        metrics = await service.get_dashboard_metrics(org_uuid, start_date, end_date, department_id)
        return SuccessResponse(
            message="Dashboard metrics retrieved",
            data=metrics,
        )
    except Exception as e:
        import traceback
        return SuccessResponse(
            message=f"Error: {str(e)} | Trace: {traceback.format_exc()}",
            data={}
        )


@router.get("/leave")
async def get_leave_analytics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    department_id: Optional[UUID] = Query(None),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get leave analytics."""
    service = AnalyticsService(db)
    org_id = current_user.get("organization_id")
    org_uuid = UUID(org_id) if org_id else None
    analytics = await service.get_leave_analytics(org_uuid, start_date, end_date, department_id)

    return SuccessResponse(
        message="Leave analytics retrieved",
        data=analytics,
    )


@router.get("/departments")
async def get_department_distribution(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    department_id: Optional[UUID] = Query(None),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get employee distribution by department."""
    service = AnalyticsService(db)
    org_id = current_user.get("organization_id")
    org_uuid = UUID(org_id) if org_id else None
    distribution = await service.get_department_distribution(org_uuid, start_date, end_date, department_id)

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

@router.get("/insights")
async def get_hr_insights(
    current_user: dict = Depends(require_roles("admin", "hr")),
    db: AsyncSession = Depends(get_db),
):
    """Get AI-generated HR insights based on recent data."""
    # Mocking the AI logic for now to demonstrate the UI
    insights = [
        "Recruitment completion increased by 15% this month.",
        "Engineering department has the highest leave utilization.",
        "Three candidates are ready for final interviews.",
        "Average time to hire has decreased by 2 days compared to last quarter."
    ]

    return SuccessResponse(
        message="HR insights retrieved",
        data=insights,
    )
