"""Workflow engine for managing workflow execution with DB persistence."""

import json
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.workflows.base import BaseWorkflow, WorkflowStatus

logger = structlog.get_logger()


class WorkflowEngine:
    """Engine for managing and executing workflows with optional DB persistence."""

    def __init__(self):
        self.active_workflows: dict[str, BaseWorkflow] = {}
        self.workflow_registry: dict[str, type[BaseWorkflow]] = {}

    def register_workflow(self, workflow_type: str, workflow_class: type[BaseWorkflow]) -> None:
        """Register a workflow type."""
        self.workflow_registry[workflow_type] = workflow_class
        logger.info("workflow_registered", workflow_type=workflow_type)

    def create_workflow(self, workflow_type: str, **kwargs: Any) -> BaseWorkflow:
        """Create a new workflow instance."""
        workflow_class = self.workflow_registry.get(workflow_type)
        if workflow_class is None:
            raise ValueError(f"Unknown workflow type: {workflow_type}")

        kwargs.setdefault("workflow_type", workflow_type)
        workflow = workflow_class(**kwargs)
        self.active_workflows[str(workflow.id)] = workflow

        logger.info(
            "workflow_created",
            workflow_id=str(workflow.id),
            workflow_type=workflow_type,
        )

        return workflow

    async def execute_workflow(self, workflow: BaseWorkflow, context: dict[str, Any]) -> dict[str, Any]:
        """Execute a workflow and persist state to DB."""
        result = await workflow.start(context)
        await self._persist_workflow(workflow, context)
        return result

    async def approve_workflow(self, workflow_id: str, context: dict[str, Any]) -> dict[str, Any]:
        """Approve a waiting workflow."""
        workflow = self.active_workflows.get(workflow_id)
        if workflow is None:
            return {"status": "error", "message": "Workflow not found"}

        result = await workflow.approve(context)
        await self._persist_workflow(workflow, context)
        return result

    async def cancel_workflow(self, workflow_id: str) -> dict[str, Any]:
        """Cancel a workflow."""
        workflow = self.active_workflows.get(workflow_id)
        if workflow is None:
            return {"status": "error", "message": "Workflow not found"}

        result = await workflow.cancel()
        await self._persist_workflow(workflow)
        return result

    def get_workflow(self, workflow_id: str) -> BaseWorkflow | None:
        """Get a workflow by ID."""
        return self.active_workflows.get(workflow_id)

    async def _persist_workflow(self, workflow: BaseWorkflow, context: dict[str, Any] | None = None) -> None:
        """Persist workflow state to the database."""
        try:
            from app.models.workflow import Workflow, WorkflowStep
            from app.database.database import async_session_factory

            async with async_session_factory() as session:
                # Check if workflow record exists
                result = await session.execute(
                    __import__("sqlalchemy").select(Workflow).where(Workflow.id == workflow.id)
                )
                db_workflow = result.scalar_one_or_none()

                # Serialize steps
                steps_data = []
                for step in workflow.steps:
                    steps_data.append({
                        "name": step.name,
                        "status": step.status,
                        "agent_name": step.agent_name,
                        "action": step.action,
                        "duration_ms": step.duration_ms,
                    })

                if db_workflow is None:
                    # Create new workflow record
                    db_workflow = Workflow(
                        id=workflow.id,
                        workflow_type=workflow.workflow_type,
                        status=workflow.status.value if isinstance(workflow.status, WorkflowStatus) else workflow.status,
                        state=json.dumps(workflow.state, default=str),
                        started_at=workflow.started_at,
                        completed_at=workflow.completed_at,
                        employee_id=UUID(context["employee_id"]) if context and context.get("employee_id") else None,
                    )
                    session.add(db_workflow)
                else:
                    # Update existing
                    db_workflow.status = workflow.status.value if isinstance(workflow.status, WorkflowStatus) else workflow.status
                    db_workflow.state = json.dumps(workflow.state, default=str)
                    db_workflow.completed_at = workflow.completed_at
                    db_workflow.updated_at = datetime.now(timezone.utc)

                await session.commit()

                logger.info("workflow_persisted", workflow_id=str(workflow.id), status=str(workflow.status))

        except Exception as e:
            logger.error("workflow_persistence_failed", workflow_id=str(workflow.id), error=str(e))

    async def get_workflow_from_db(self, workflow_id: UUID) -> dict | None:
        """Get workflow state from the database."""
        try:
            from app.models.workflow import Workflow
            from app.database.database import async_session_factory

            async with async_session_factory() as session:
                result = await session.execute(
                    __import__("sqlalchemy").select(Workflow).where(Workflow.id == workflow_id)
                )
                db_workflow = result.scalar_one_or_none()

                if db_workflow is None:
                    return None

                return {
                    "id": str(db_workflow.id),
                    "workflow_type": db_workflow.workflow_type,
                    "status": db_workflow.status,
                    "state": json.loads(db_workflow.state) if db_workflow.state else {},
                    "started_at": db_workflow.started_at.isoformat() if db_workflow.started_at else None,
                    "completed_at": db_workflow.completed_at.isoformat() if db_workflow.completed_at else None,
                }
        except Exception as e:
            logger.error("workflow_fetch_failed", workflow_id=str(workflow_id), error=str(e))
            return None


# Global workflow engine
workflow_engine = WorkflowEngine()


def initialize_workflows() -> None:
    """Initialize and register all workflows."""
    from app.workflows.leave.workflow import LeaveRequestWorkflow
    from app.workflows.document_generation.workflow import DocumentGenerationWorkflow
    from app.workflows.onboarding.workflow import OnboardingWorkflow
    from app.workflows.offboarding.workflow import OffboardingWorkflow
    from app.workflows.promotion.workflow import PromotionWorkflow
    from app.workflows.transfer.workflow import TransferWorkflow

    workflow_engine.register_workflow("leave_request", LeaveRequestWorkflow)
    workflow_engine.register_workflow("document_generation", DocumentGenerationWorkflow)
    workflow_engine.register_workflow("onboarding", OnboardingWorkflow)
    workflow_engine.register_workflow("offboarding", OffboardingWorkflow)
    workflow_engine.register_workflow("promotion", PromotionWorkflow)
    workflow_engine.register_workflow("transfer", TransferWorkflow)

    logger.info("workflows_initialized", count=len(workflow_engine.workflow_registry))
