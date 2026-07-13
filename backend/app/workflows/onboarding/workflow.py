"""Onboarding workflow."""

from app.workflows.base import BaseWorkflow, WorkflowStep


class OnboardingWorkflow(BaseWorkflow):
    """Employee onboarding multi-step workflow."""

    def __init__(self, employee_id: str = "", **kwargs):
        super().__init__(workflow_type="onboarding")
        self.state["employee_id"] = employee_id

    def define_steps(self) -> list[WorkflowStep]:
        return [
            WorkflowStep(name="validate_employee", action="validate_employee_exists"),
            WorkflowStep(name="create_accounts", action="create_user_accounts"),
            WorkflowStep(name="assign_department", action="assign_to_department"),
            WorkflowStep(name="setup_leave_balance", action="initialize_leave_balances"),
            WorkflowStep(name="generate_onboarding_plan", action="generate_30_60_90_day_plan"),
            WorkflowStep(name="trigger_it_asset", action="trigger_it_asset_requests"),
            WorkflowStep(name="schedule_meetings", action="schedule_intro_meetings"),
            WorkflowStep(name="send_welcome_email", action="send_welcome_email"),
            WorkflowStep(name="notify_manager", action="notify_department_manager"),
        ]

    async def execute_step(self, step: WorkflowStep, context: dict) -> dict:
        if step.name == "validate_employee":
            return {"valid": True, "employee_id": self.state.get("employee_id")}
        elif step.name == "create_accounts":
            return {"accounts_created": True, "system_access": "granted"}
        elif step.name == "assign_department":
            return {"department_assigned": True}
        elif step.name == "setup_leave_balance":
            return {"leave_balances_initialized": True}
        elif step.name == "generate_onboarding_plan":
            employee_id = self.state.get("employee_id", "Unknown")
            from app.core.llm import generate_text
            
            prompt = (
                f"Generate a customized 30-60-90 day onboarding plan for a new employee (ID: {employee_id}). "
                "Ensure it's structured, professional, actionable, and includes weekly milestones. "
                "Format the plan clearly using markdown."
            )
            system_prompt = "You are an expert HR Onboarding Specialist."
            plan = await generate_text([{"role": "user", "content": prompt}], system_prompt=system_prompt)
            
            return {"plan_generated": True, "onboarding_plan": plan}
        elif step.name == "trigger_it_asset":
            return {
                "it_ticket_created": True,
                "status": "pending_provisioning",
                "assets_requested": ["Laptop", "Monitor", "Software Licenses", "YubiKey"]
            }
        elif step.name == "schedule_meetings":
            return {
                "meetings_scheduled": True,
                "stakeholders": ["Direct Manager", "HR Buddy", "Team Lead"],
                "status": "invites_sent"
            }
        elif step.name == "send_welcome_email":
            return {"welcome_email_sent": True}
        elif step.name == "notify_manager":
            return {"manager_notified": True}
        return {"status": "completed"}
