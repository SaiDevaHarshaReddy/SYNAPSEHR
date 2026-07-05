"""Tests for AI agents."""
import pytest
from unittest.mock import AsyncMock


class TestPlannerAgent:
    """Tests for PlannerAgent."""

    @pytest.mark.asyncio
    async def test_classify_leave_intent(self):
        from app.agents.planner.agent import PlannerAgent
        agent = PlannerAgent()
        intent = agent._classify_intent("I want to take a vacation day")
        assert intent == "leave_request"

    @pytest.mark.asyncio
    async def test_classify_policy_intent(self):
        from app.agents.planner.agent import PlannerAgent
        agent = PlannerAgent()
        intent = agent._classify_intent("What is the company policy on remote work?")
        assert intent == "policy_query"

    @pytest.mark.asyncio
    async def test_classify_document_intent(self):
        from app.agents.planner.agent import PlannerAgent
        agent = PlannerAgent()
        intent = agent._classify_intent("Generate an experience letter")
        assert intent == "document_generation"

    @pytest.mark.asyncio
    async def test_classify_analytics_intent(self):
        from app.agents.planner.agent import PlannerAgent
        agent = PlannerAgent()
        intent = agent._classify_intent("Show me the analytics report")
        assert intent == "analytics"

    @pytest.mark.asyncio
    async def test_classify_general_intent(self):
        from app.agents.planner.agent import PlannerAgent
        agent = PlannerAgent()
        intent = agent._classify_intent("Hello, how are you?")
        assert intent == "general_inquiry"

    @pytest.mark.asyncio
    async def test_register_agent(self):
        from app.agents.planner.agent import PlannerAgent
        from app.agents.hr.agent import HRAgent
        agent = PlannerAgent()
        agent.register_agent("hr", HRAgent())
        assert "hr" in agent.available_agents


class TestHRAgent:
    """Tests for HRAgent."""

    @pytest.mark.asyncio
    async def test_process_headcount(self):
        from app.agents.hr.agent import HRAgent
        agent = HRAgent()
        result = await agent.process({"message": "How many employees do we have?"}, {})
        assert "headcount" in result["action"]

    @pytest.mark.asyncio
    async def test_process_general(self):
        from app.agents.hr.agent import HRAgent
        agent = HRAgent()
        result = await agent.process({"message": "Hello"}, {})
        assert result["action"] == "general_hr"


class TestApprovalAgent:
    """Tests for ApprovalAgent."""

    @pytest.mark.asyncio
    async def test_process_approval(self):
        from app.agents.approval.agent import ApprovalAgent
        agent = ApprovalAgent()
        result = await agent.process({"message": "I want to approve this request"}, {})
        assert "approval" in result["action"]


class TestLeaveAgent:
    """Tests for LeaveAgent."""

    @pytest.mark.asyncio
    async def test_process(self):
        from app.agents.leave.agent import LeaveAgent
        agent = LeaveAgent()
        result = await agent.process({"message": "Check my leave balance"}, {})
        assert result is not None
        assert "message" in result
