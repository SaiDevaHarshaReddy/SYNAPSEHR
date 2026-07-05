"""Promotion workflow."""

from app.workflows.base import BaseWorkflow, WorkflowStep


class PromotionWorkflow(BaseWorkflow):
    """Employee promotion multi-step workflow."""

    def __init__(self, employee_id: str = "", new_designation: str = "", **kwargs):
        super().__init__(workflow_type="promotion")
        self.state["employee_id"] = employee_id
        self.state["new_designation"] = new_designation

    def define_steps(self) -> list[WorkflowStep]:
        return [
            WorkflowStep(name="validate_eligibility", action="check_promotion_eligibility"),
            WorkflowStep(name="manager_approval", action="request_manager_approval", requires_approval=True),
            WorkflowStep(name="hr_approval", action="request_hr_approval", requires_approval=True),
            WorkflowStep(name="update_designation", action="update_employee_designation"),
            WorkflowStep(name="generate_letter", action="generate_promotion_letter"),
            WorkflowStep(name="notify_employee", action="send_promotion_notification"),
        ]

    async def execute_step(self, step: WorkflowStep, context: dict) -> dict:
        if step.name == "validate_eligibility":
            return {"eligible": True, "employee_id": self.state.get("employee_id")}
        elif step.name == "update_designation":
            return {"designation_updated": True, "new_designation": self.state.get("new_designation")}
        elif step.name == "generate_letter":
            return {"letter_generated": True}
        elif step.name == "notify_employee":
            return {"employee_notified": True}
        return {"status": "completed"}
