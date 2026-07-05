"""Base workflow class."""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

import structlog

logger = structlog.get_logger()


class WorkflowStatus(str, Enum):
    """Workflow status states."""
    CREATED = "created"
    VALIDATED = "validated"
    PLANNING = "planning"
    EXECUTING = "executing"
    WAITING_APPROVAL = "waiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowStep:
    """Represents a single step in a workflow."""

    def __init__(
        self,
        name: str,
        agent_name: str | None = None,
        action: str | None = None,
        requires_approval: bool = False,
    ):
        self.id = uuid4()
        self.name = name
        self.agent_name = agent_name
        self.action = action
        self.requires_approval = requires_approval
        self.status = "pending"
        self.output: dict | None = None
        self.duration_ms: int | None = None
        self.created_at = datetime.now(timezone.utc)


class BaseWorkflow(ABC):
    """Base class for all workflows."""

    def __init__(self, workflow_type: str):
        self.id = uuid4()
        self.workflow_type = workflow_type
        self.status = WorkflowStatus.CREATED
        self.steps: list[WorkflowStep] = []
        self.current_step_index = 0
        self.state: dict[str, Any] = {}
        self.started_at: datetime | None = None
        self.completed_at: datetime | None = None
        self.error: str | None = None

    @abstractmethod
    def define_steps(self) -> list[WorkflowStep]:
        """Define the workflow steps. Must be implemented by subclasses."""
        pass

    @abstractmethod
    async def execute_step(self, step: WorkflowStep, context: dict[str, Any]) -> dict[str, Any]:
        """Execute a single workflow step. Must be implemented by subclasses."""
        pass

    async def start(self, context: dict[str, Any]) -> dict[str, Any]:
        """Start the workflow execution."""
        self.started_at = datetime.now(timezone.utc)
        self.status = WorkflowStatus.EXECUTING
        self.steps = self.define_steps()

        logger.info(
            "workflow_started",
            workflow_id=str(self.id),
            workflow_type=self.workflow_type,
            steps_count=len(self.steps),
        )

        return await self._execute_next_step(context)

    async def _execute_next_step(self, context: dict[str, Any]) -> dict[str, Any]:
        """Execute the next step in the workflow."""
        if self.current_step_index >= len(self.steps):
            return await self._complete(context)

        step = self.steps[self.current_step_index]
        step.status = "executing"

        logger.info(
            "workflow_step_started",
            workflow_id=str(self.id),
            step_name=step.name,
            step_index=self.current_step_index,
        )

        try:
            import time
            start_time = time.time()

            result = await self.execute_step(step, context)

            duration = int((time.time() - start_time) * 1000)
            step.duration_ms = duration
            step.output = result
            step.status = "completed"

            # Update state with step result
            self.state[step.name] = result

            logger.info(
                "workflow_step_completed",
                workflow_id=str(self.id),
                step_name=step.name,
                duration_ms=duration,
            )

            # Move to next step
            self.current_step_index += 1

            # Check if next step requires approval
            if (
                self.current_step_index < len(self.steps)
                and self.steps[self.current_step_index].requires_approval
            ):
                self.status = WorkflowStatus.WAITING_APPROVAL
                return {
                    "status": "waiting_approval",
                    "workflow_id": str(self.id),
                    "current_step": step.name,
                    "next_step": self.steps[self.current_step_index].name,
                    "state": self.state,
                }

            # Execute next step
            return await self._execute_next_step(context)

        except Exception as e:
            step.status = "failed"
            self.status = WorkflowStatus.FAILED
            self.error = str(e)

            logger.error(
                "workflow_step_failed",
                workflow_id=str(self.id),
                step_name=step.name,
                error=str(e),
            )

            return {
                "status": "failed",
                "workflow_id": str(self.id),
                "failed_step": step.name,
                "error": str(e),
                "state": self.state,
            }

    async def _complete(self, context: dict[str, Any]) -> dict[str, Any]:
        """Complete the workflow."""
        self.status = WorkflowStatus.COMPLETED
        self.completed_at = datetime.now(timezone.utc)

        duration = None
        if self.started_at:
            duration = int((self.completed_at - self.started_at).total_seconds() * 1000)

        logger.info(
            "workflow_completed",
            workflow_id=str(self.id),
            workflow_type=self.workflow_type,
            duration_ms=duration,
        )

        return {
            "status": "completed",
            "workflow_id": str(self.id),
            "workflow_type": self.workflow_type,
            "duration_ms": duration,
            "state": self.state,
        }

    async def approve(self, context: dict[str, Any]) -> dict[str, Any]:
        """Approve the current step and continue."""
        if self.status != WorkflowStatus.WAITING_APPROVAL:
            return {"status": "error", "message": "Workflow is not waiting for approval"}

        self.status = WorkflowStatus.EXECUTING
        self.current_step_index += 1

        return await self._execute_next_step(context)

    async def cancel(self) -> dict[str, Any]:
        """Cancel the workflow."""
        self.status = WorkflowStatus.CANCELLED
        self.completed_at = datetime.now(timezone.utc)

        logger.info("workflow_cancelled", workflow_id=str(self.id))

        return {
            "status": "cancelled",
            "workflow_id": str(self.id),
        }
