"""Transfer workflow."""

from app.workflows.base import BaseWorkflow, WorkflowStep


class TransferWorkflow(BaseWorkflow):
    """Employee department transfer multi-step workflow."""

    def __init__(self, employee_id: str = "", new_department_id: str = "", **kwargs):
        super().__init__(workflow_type="transfer")
        self.state["employee_id"] = employee_id
        self.state["new_department_id"] = new_department_id

    def define_steps(self) -> list[WorkflowStep]:
        return [
            WorkflowStep(name="validate_transfer", action="validate_transfer_eligibility"),
            WorkflowStep(name="current_manager_approval", action="get_current_manager_approval", requires_approval=True),
            WorkflowStep(name="new_manager_approval", action="get_new_manager_approval", requires_approval=True),
            WorkflowStep(name="update_department", action="transfer_employee_department"),
            WorkflowStep(name="update_access", action="update_system_access"),
            WorkflowStep(name="notify_employee", action="send_transfer_notification"),
        ]

    async def execute_step(self, step: WorkflowStep, context: dict) -> dict:
        if step.name == "validate_transfer":
            return {"valid": True}
        elif step.name == "update_department":
            return {"department_transferred": True, "new_department": self.state.get("new_department_id")}
        elif step.name == "update_access":
            return {"access_updated": True}
        elif step.name == "notify_employee":
            return {"employee_notified": True}
        return {"status": "completed"}
