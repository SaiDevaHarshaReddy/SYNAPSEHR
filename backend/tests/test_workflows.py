"""Tests for workflow engine."""
import pytest
from app.workflows.base import BaseWorkflow, WorkflowStatus, WorkflowStep


class TestWorkflowStatus:
    """Tests for WorkflowStatus enum."""

    def test_all_statuses_exist(self):
        statuses = [
            WorkflowStatus.CREATED,
            WorkflowStatus.VALIDATED,
            WorkflowStatus.PLANNING,
            WorkflowStatus.EXECUTING,
            WorkflowStatus.WAITING_APPROVAL,
            WorkflowStatus.COMPLETED,
            WorkflowStatus.FAILED,
            WorkflowStatus.CANCELLED,
        ]
        assert len(statuses) == 8

    def test_status_string_values(self):
        assert WorkflowStatus.CREATED.value == "created"
        assert WorkflowStatus.COMPLETED.value == "completed"
        assert WorkflowStatus.FAILED.value == "failed"


class TestWorkflowStep:
    """Tests for WorkflowStep."""

    def test_step_creation(self):
        step = WorkflowStep(
            name="test_step",
            agent_name="leave",
            action="validate",
            requires_approval=True,
        )
        assert step.name == "test_step"
        assert step.agent_name == "leave"
        assert step.action == "validate"
        assert step.requires_approval is True
        assert step.status == "pending"
        assert step.output is None

    def test_step_has_uuid(self):
        step = WorkflowStep(name="test")
        assert step.id is not None


class TestWorkflowEngine:
    """Tests for WorkflowEngine."""

    def test_register_workflow(self):
        from app.workflows.engine import WorkflowEngine
        engine = WorkflowEngine()

        class DummyWorkflow(BaseWorkflow):
            def define_steps(self):
                return [WorkflowStep(name="step1")]
            async def execute_step(self, step, context):
                return {"result": "ok"}

        engine.register_workflow("dummy", DummyWorkflow)
        assert "dummy" in engine.workflow_registry

    def test_create_workflow(self):
        from app.workflows.engine import WorkflowEngine
        engine = WorkflowEngine()

        class DummyWorkflow(BaseWorkflow):
            def define_steps(self):
                return [WorkflowStep(name="step1")]
            async def execute_step(self, step, context):
                return {"result": "ok"}

        engine.register_workflow("dummy", DummyWorkflow)
        workflow = engine.create_workflow("dummy")
        assert workflow.workflow_type == "dummy"
        assert workflow.status == WorkflowStatus.CREATED

    def test_create_unknown_workflow_raises(self):
        from app.workflows.engine import WorkflowEngine
        engine = WorkflowEngine()
        with pytest.raises(ValueError, match="Unknown workflow type"):
            engine.create_workflow("nonexistent")
