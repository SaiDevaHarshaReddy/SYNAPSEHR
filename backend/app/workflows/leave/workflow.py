"""Leave Request Workflow."""

from typing import Any
from uuid import UUID

from app.workflows.base import BaseWorkflow, WorkflowStep


class LeaveRequestWorkflow(BaseWorkflow):
    """Workflow for processing leave requests."""

    def __init__(self, employee_id: str, leave_type_id: str, start_date: str, end_date: str, reason: str = None, **kwargs):
        super().__init__("leave_request")
        self.employee_id = employee_id
        self.leave_type_id = leave_type_id
        self.start_date = start_date
        self.end_date = end_date
        self.reason = reason

    def define_steps(self) -> list[WorkflowStep]:
        return [
            WorkflowStep(
                name="validate_request",
                agent_name="Leave",
                action="validate_leave_request",
            ),
            WorkflowStep(
                name="check_balance",
                agent_name="Leave",
                action="check_leave_balance",
            ),
            WorkflowStep(
                name="check_policy",
                agent_name="Policy",
                action="check_leave_policy",
                requires_approval=False,
            ),
            WorkflowStep(
                name="create_request",
                agent_name="Leave",
                action="create_leave_request",
            ),
            WorkflowStep(
                name="notify_employee",
                agent_name="Notification",
                action="send_notification",
            ),
        ]

    async def execute_step(self, step: WorkflowStep, context: dict[str, Any]) -> dict[str, Any]:
        """Execute a workflow step."""
        if step.name == "validate_request":
            return await self._validate_request(context)
        elif step.name == "check_balance":
            return await self._check_balance(context)
        elif step.name == "check_policy":
            return await self._check_policy(context)
        elif step.name == "create_request":
            return await self._create_request(context)
        elif step.name == "notify_employee":
            return await self._notify_employee(context)
        else:
            return {"status": "skipped", "message": f"Unknown step: {step.name}"}

    async def _validate_request(self, context: dict[str, Any]) -> dict[str, Any]:
        """Validate the leave request."""
        from datetime import date

        start = date.fromisoformat(self.start_date)
        end = date.fromisoformat(self.end_date)

        if end < start:
            return {"valid": False, "error": "End date must be after start date"}

        return {"valid": True, "days_requested": (end - start).days + 1}

    async def _check_balance(self, context: dict[str, Any]) -> dict[str, Any]:
        """Check leave balance."""
        from app.tools.leave.tools import check_leave_balance

        result = await check_leave_balance(
            employee_id=self.employee_id,
            leave_type_id=self.leave_type_id,
        )

        if not result.get("balances"):
            return {"sufficient": False, "error": "No leave balance found"}

        balance = result["balances"][0]
        return {
            "sufficient": balance["available_days"] > 0,
            "available": balance["available_days"],
        }

    async def _check_policy(self, context: dict[str, Any]) -> dict[str, Any]:
        """Check leave policy compliance."""
        # In Phase 8, this will use RAG
        return {"compliant": True, "message": "Leave request complies with policy"}

    async def _create_request(self, context: dict[str, Any]) -> dict[str, Any]:
        """Create the leave request."""
        from app.tools.leave.tools import create_leave_request

        result = await create_leave_request(
            employee_id=self.employee_id,
            leave_type_id=self.leave_type_id,
            start_date=self.start_date,
            end_date=self.end_date,
            reason=self.reason,
        )

        return result

    async def _notify_employee(self, context: dict[str, Any]) -> dict[str, Any]:
        """Send notification to employee."""
        # Notification will be sent via notification service
        return {"notified": True, "message": "Employee notified"}
