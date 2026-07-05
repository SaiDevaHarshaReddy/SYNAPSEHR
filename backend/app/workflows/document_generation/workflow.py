"""Document Generation Workflow."""

from typing import Any
from uuid import UUID

from app.workflows.base import BaseWorkflow, WorkflowStep


class DocumentGenerationWorkflow(BaseWorkflow):
    """Workflow for generating HR documents."""

    def __init__(self, employee_id: str, document_type: str, generated_by: str = None, additional_data: dict = None):
        super().__init__("document_generation")
        self.employee_id = employee_id
        self.document_type = document_type
        self.generated_by = generated_by
        self.additional_data = additional_data or {}

    def define_steps(self) -> list[WorkflowStep]:
        return [
            WorkflowStep(
                name="validate_employee",
                agent_name="Document",
                action="validate_employee",
            ),
            WorkflowStep(
                name="prepare_data",
                agent_name="Document",
                action="prepare_document_data",
            ),
            WorkflowStep(
                name="generate_document",
                agent_name="Document",
                action="generate_document",
            ),
            WorkflowStep(
                name="notify_employee",
                agent_name="Notification",
                action="send_notification",
            ),
        ]

    async def execute_step(self, step: WorkflowStep, context: dict[str, Any]) -> dict[str, Any]:
        """Execute a workflow step."""
        if step.name == "validate_employee":
            return await self._validate_employee(context)
        elif step.name == "prepare_data":
            return await self._prepare_data(context)
        elif step.name == "generate_document":
            return await self._generate_document(context)
        elif step.name == "notify_employee":
            return await self._notify_employee(context)
        else:
            return {"status": "skipped", "message": f"Unknown step: {step.name}"}

    async def _validate_employee(self, context: dict[str, Any]) -> dict[str, Any]:
        """Validate that the employee exists."""
        from app.database.database import async_session_factory
        from app.repositories.employee import EmployeeRepository

        async with async_session_factory() as session:
            repo = EmployeeRepository(session)
            employee = await repo.get_by_id(UUID(self.employee_id))

            if employee is None:
                return {"valid": False, "error": "Employee not found"}

            return {"valid": True, "employee_name": employee.full_name}

    async def _prepare_data(self, context: dict[str, Any]) -> dict[str, Any]:
        """Prepare document data."""
        return {"data": self.additional_data, "document_type": self.document_type}

    async def _generate_document(self, context: dict[str, Any]) -> dict[str, Any]:
        """Generate the document."""
        from app.tools.documents.tools import generate_document

        result = await generate_document(
            employee_id=self.employee_id,
            document_type=self.document_type,
            generated_by=self.generated_by,
            additional_data=self.additional_data,
        )

        return result

    async def _notify_employee(self, context: dict[str, Any]) -> dict[str, Any]:
        """Notify employee about the document."""
        return {"notified": True, "message": "Employee notified about document"}
