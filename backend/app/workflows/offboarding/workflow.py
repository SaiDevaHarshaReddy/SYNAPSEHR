"""Offboarding workflow."""

from app.workflows.base import BaseWorkflow, WorkflowStep


class OffboardingWorkflow(BaseWorkflow):
    """Employee offboarding multi-step workflow."""

    def __init__(self, employee_id: str = "", **kwargs):
        super().__init__(workflow_type="offboarding")
        self.state["employee_id"] = employee_id

    def define_steps(self) -> list[WorkflowStep]:
        return [
            WorkflowStep(name="revoke_access", action="revoke_system_access"),
            WorkflowStep(name="collect_assets", action="initiate_asset_return"),
            WorkflowStep(name="final_settlement", action="calculate_final_settlement"),
            WorkflowStep(name="exit_interview", action="schedule_exit_interview"),
            WorkflowStep(name="generate_relieving", action="generate_relieving_letter"),
            WorkflowStep(name="create_it_checklist", action="create_it_revocation_checklist"),
            WorkflowStep(name="update_records", action="update_employee_status"),
        ]

    async def execute_step(self, step: WorkflowStep, context: dict) -> dict:
        if step.name == "revoke_access":
            return {"access_revoked": True}
        elif step.name == "collect_assets":
            return {"asset_return_initiated": True}
        elif step.name == "final_settlement":
            return {
                "settlement_calculated": True,
                "breakdown": {
                    "base_pay_prorated": 4500,
                    "leave_encashment": 1250,
                    "notice_period_deduction": 0,
                    "other_deductions": 200,
                    "net_payable": 5550
                },
                "status": "pending_finance_approval"
            }
        elif step.name == "exit_interview":
            return {
                "exit_interview_scheduled": True,
                "interviewer": "HR Business Partner",
                "status": "invite_sent"
            }
        elif step.name == "generate_relieving":
            return {"relieving_letter_generated": True}
        elif step.name == "create_it_checklist":
            checklist = [
                "Disable Active Directory Account",
                "Revoke VPN Access",
                "Remove from GitHub Organization",
                "Disable Corporate Email",
                "Collect Laptop & Mobile Device",
                "Revoke Building Access Card"
            ]
            return {
                "it_checklist_created": True,
                "tasks": checklist,
                "assigned_to": "IT Operations Team"
            }
        elif step.name == "update_records":
            return {"records_updated": True, "status": "inactive"}
        return {"status": "completed"}
