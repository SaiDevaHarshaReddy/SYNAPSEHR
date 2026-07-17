"""Analytics service."""
from typing import Optional
from datetime import datetime, timedelta
from uuid import UUID

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.department import Department
from app.models.employee import Employee
from app.models.leave_request import LeaveRequest
from app.models.workflow import Workflow

logger = structlog.get_logger()


class AnalyticsService:
    """Handle analytics and reporting operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_dashboard_metrics(
        self, organization_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        department_id: Optional[UUID] = None
    ) -> dict:
        """Get dashboard KPI metrics."""
        # Total employees
        emp_query = select(func.count()).select_from(Employee).join(
            Department, Employee.department_id == Department.id
        )
        if organization_id:
            emp_query = emp_query.where(Department.organization_id == organization_id)
        if department_id:
            emp_query = emp_query.where(Employee.department_id == department_id)
        if start_date:
            emp_query = emp_query.where(Employee.hire_date >= start_date.date())
        if end_date:
            emp_query = emp_query.where(Employee.hire_date <= end_date.date())
            
        total_employees = (await self.session.execute(emp_query)).scalar() or 0

        # Pending leave requests
        pending_query = select(func.count()).select_from(LeaveRequest).where(
            LeaveRequest.status == "pending"
        )
        pending_query = pending_query.join(Employee, LeaveRequest.employee_id == Employee.id).join(Department, Employee.department_id == Department.id)
        if organization_id:
            pending_query = pending_query.where(
                Department.organization_id == organization_id
            )
        if department_id:
            pending_query = pending_query.where(Employee.department_id == department_id)
        if start_date:
            pending_query = pending_query.where(LeaveRequest.created_at >= start_date)
        if end_date:
            pending_query = pending_query.where(LeaveRequest.created_at <= end_date)
            
        pending_leave_count = (await self.session.execute(pending_query)).scalar() or 0
        
        # Pending workflows
        pending_wf_query = select(func.count()).select_from(Workflow).where(
            Workflow.status == "pending"
        )
        pending_wf_query = pending_wf_query.join(Employee, Workflow.employee_id == Employee.id).join(Department, Employee.department_id == Department.id)
        if organization_id:
            pending_wf_query = pending_wf_query.where(
                Department.organization_id == organization_id
            )
        if department_id:
            pending_wf_query = pending_wf_query.where(Employee.department_id == department_id)
        if start_date:
            pending_wf_query = pending_wf_query.where(Workflow.created_at >= start_date)
        if end_date:
            pending_wf_query = pending_wf_query.where(Workflow.created_at <= end_date)
            
        pending_wf_count = (await self.session.execute(pending_wf_query)).scalar() or 0

        pending_approvals = pending_leave_count + pending_wf_count

        # Today's leave
        today = datetime.now().date()
        today_leave_query = select(func.count(func.distinct(LeaveRequest.employee_id))).select_from(LeaveRequest).where(
            LeaveRequest.start_date <= today,
            LeaveRequest.end_date >= today,
            LeaveRequest.status == "approved",
        )
        today_leave_query = today_leave_query.join(Employee, LeaveRequest.employee_id == Employee.id).join(Department, Employee.department_id == Department.id)
        if organization_id:
            today_leave_query = today_leave_query.where(
                Department.organization_id == organization_id
            )
        if department_id:
            today_leave_query = today_leave_query.where(Employee.department_id == department_id)
            
        todays_leave = (await self.session.execute(today_leave_query)).scalar() or 0

        # Workflows
        workflow_query = select(func.count()).select_from(Workflow).join(Employee, Workflow.employee_id == Employee.id).join(Department, Employee.department_id == Department.id)
        if organization_id:
            workflow_query = workflow_query.where(
                Department.organization_id == organization_id
            )
        if department_id:
            workflow_query = workflow_query.where(Employee.department_id == department_id)
        if start_date:
            workflow_query = workflow_query.where(Workflow.created_at >= start_date)
        if end_date:
            workflow_query = workflow_query.where(Workflow.created_at <= end_date)
            
        total_workflows = (await self.session.execute(workflow_query)).scalar() or 0

        completed_query = select(func.count()).select_from(Workflow).where(
            Workflow.status == "completed"
        ).join(Employee, Workflow.employee_id == Employee.id).join(Department, Employee.department_id == Department.id)
        if organization_id:
            completed_query = completed_query.where(
                Department.organization_id == organization_id
            )
        if department_id:
            completed_query = completed_query.where(Employee.department_id == department_id)
        if start_date:
            completed_query = completed_query.where(Workflow.created_at >= start_date)
        if end_date:
            completed_query = completed_query.where(Workflow.created_at <= end_date)
            
        completed_workflows = (await self.session.execute(completed_query)).scalar() or 0

        success_rate = (
            (completed_workflows / total_workflows * 100)
            if total_workflows > 0
            else 0
        )

        return {
            "total_employees": total_employees,
            "pending_approvals": pending_approvals,
            "todays_leave": todays_leave,
            "total_workflows": total_workflows,
            "completed_workflows": completed_workflows,
            "workflow_success_rate": round(success_rate, 2),
        }

    async def get_leave_analytics(
        self, organization_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        department_id: Optional[UUID] = None
    ) -> dict:
        """Get leave analytics."""
        # Leave requests by status
        status_query = select(LeaveRequest.status, func.count()).join(Employee, LeaveRequest.employee_id == Employee.id).join(Department, Employee.department_id == Department.id)
        
        if organization_id:
            status_query = status_query.where(
                Department.organization_id == organization_id
            )
        if department_id:
            status_query = status_query.where(Employee.department_id == department_id)
        if start_date:
            status_query = status_query.where(LeaveRequest.created_at >= start_date)
        if end_date:
            status_query = status_query.where(LeaveRequest.created_at <= end_date)
            
        status_query = status_query.group_by(LeaveRequest.status)
        status_result = await self.session.execute(status_query)
        status_counts = dict(status_result.all())

        return {
            "pending": status_counts.get("pending", 0),
            "approved": status_counts.get("approved", 0),
            "rejected": status_counts.get("rejected", 0),
            "cancelled": status_counts.get("cancelled", 0),
        }

    async def get_department_distribution(
        self, organization_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        department_id: Optional[UUID] = None
    ) -> list[dict]:
        """Get employee distribution by department."""
        query = (
            select(Department.name, func.count(Employee.id))
            .join(Employee, Department.id == Employee.department_id)
        )
        if organization_id:
            query = query.where(Department.organization_id == organization_id)
        if department_id:
            query = query.where(Employee.department_id == department_id)
        if start_date:
            query = query.where(Employee.hire_date >= start_date.date())
        if end_date:
            query = query.where(Employee.hire_date <= end_date.date())
            
        query = query.group_by(Department.name)
        result = await self.session.execute(query)
        return [{"department": name, "count": count} for name, count in result.all()]
