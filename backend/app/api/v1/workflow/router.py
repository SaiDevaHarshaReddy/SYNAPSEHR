"""Workflow API routes."""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user, require_roles
from app.database.database import get_db
from app.repositories.workflow import WorkflowRepository
from app.schemas.response import SuccessResponse
from app.schemas.workflow import WorkflowResponse, WorkflowStepResponse

router = APIRouter(prefix="/workflows", tags=["Workflows"])


@router.get("", response_model=SuccessResponse[list[WorkflowResponse]])
async def list_workflows(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List workflow executions."""
    from app.repositories.employee import EmployeeRepository

    emp_repo = EmployeeRepository(db)
    employee = await emp_repo.get_by_user_id(UUID(current_user["user_id"]))

    if employee is None:
        return SuccessResponse(message="No workflows found", data=[])

    workflow_repo = WorkflowRepository(db)
    workflows = await workflow_repo.get_by_employee(employee.id)

    return SuccessResponse(
        message="Workflows retrieved",
        data=[
            WorkflowResponse(
                id=w.id,
                employee_id=w.employee_id,
                workflow_type=w.workflow_type,
                status=w.status,
                started_at=w.started_at,
                completed_at=w.completed_at,
                steps=[
                    WorkflowStepResponse(
                        id=s.id,
                        step_name=s.step_name,
                        agent_name=s.agent_name,
                        status=s.status,
                        duration_ms=s.duration_ms,
                        output=s.output,
                        created_at=s.created_at,
                    )
                    for s in w.steps
                ],
                created_at=w.created_at,
            )
            for w in workflows
        ],
    )


@router.get("/{workflow_id}", response_model=SuccessResponse[WorkflowResponse])
async def get_workflow(
    workflow_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get workflow with detailed execution timeline."""
    workflow_repo = WorkflowRepository(db)
    workflow = await workflow_repo.get_with_steps(workflow_id)

    if workflow is None:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("Workflow", str(workflow_id))

    return SuccessResponse(
        message="Workflow retrieved",
        data=WorkflowResponse(
            id=workflow.id,
            employee_id=workflow.employee_id,
            workflow_type=workflow.workflow_type,
            status=workflow.status,
            started_at=workflow.started_at,
            completed_at=workflow.completed_at,
            steps=[
                WorkflowStepResponse(
                    id=s.id,
                    step_name=s.step_name,
                    agent_name=s.agent_name,
                    status=s.status,
                    duration_ms=s.duration_ms,
                    output=s.output,
                    created_at=s.created_at,
                )
                for s in workflow.steps
            ],
            created_at=workflow.created_at,
        ),
    )


@router.post("/{workflow_id}/approve")
async def approve_workflow(
    workflow_id: UUID,
    current_user: dict = Depends(require_roles("admin", "hr", "manager")),
    db: AsyncSession = Depends(get_db),
):
    """Approve a workflow step."""
    from app.workflows.engine import workflow_engine

    result = await workflow_engine.approve_workflow(
        str(workflow_id),
        context={"user_id": current_user["user_id"]},
    )
    return SuccessResponse(message="Workflow approval processed", data=result)


@router.post("/{workflow_id}/cancel")
async def cancel_workflow(
    workflow_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cancel a workflow."""
    from app.workflows.engine import workflow_engine

    result = await workflow_engine.cancel_workflow(str(workflow_id))
    return SuccessResponse(message="Workflow cancelled", data=result)


@router.get("/{workflow_id}/retry")
async def retry_workflow(
    workflow_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retry a failed workflow."""
    from app.workflows.engine import workflow_engine

    workflow = workflow_engine.get_workflow(str(workflow_id))
    if workflow is None:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("Workflow", str(workflow_id))

    result = await workflow_engine.execute_workflow(workflow, {"user_id": current_user["user_id"]})
    return SuccessResponse(message="Workflow retried", data=result)
