"""Workflow repositories."""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workflow import Workflow, WorkflowStep
from app.repositories.base import BaseRepository


class WorkflowRepository(BaseRepository[Workflow]):
    """Repository for workflow data access."""

    def __init__(self, session: AsyncSession):
        super().__init__(Workflow, session)

    async def get_by_employee(self, employee_id: UUID) -> list[Workflow]:
        """Get all workflows for an employee."""
        result = await self.session.execute(
            select(Workflow)
            .where(Workflow.employee_id == employee_id)
            .order_by(Workflow.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_type(self, workflow_type: str) -> list[Workflow]:
        """Get all workflows of a specific type."""
        result = await self.session.execute(
            select(Workflow)
            .where(Workflow.workflow_type == workflow_type)
            .order_by(Workflow.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_with_steps(self, workflow_id: UUID) -> Optional[Workflow]:
        """Get workflow with all steps."""
        result = await self.session.execute(
            select(Workflow)
            .where(Workflow.id == workflow_id)
        )
        return result.scalar_one_or_none()


class WorkflowStepRepository(BaseRepository[WorkflowStep]):
    """Repository for workflow step data access."""

    def __init__(self, session: AsyncSession):
        super().__init__(WorkflowStep, session)

    async def get_by_workflow(self, workflow_id: UUID) -> list[WorkflowStep]:
        """Get all steps for a workflow."""
        result = await self.session.execute(
            select(WorkflowStep)
            .where(WorkflowStep.workflow_id == workflow_id)
            .order_by(WorkflowStep.created_at.asc())
        )
        return list(result.scalars().all())
