"""Planner Agent - Central reasoning engine with multi-agent delegation."""

from typing import Any
from uuid import UUID

import structlog

from app.agents.base import BaseAgent

logger = structlog.get_logger()


class PlannerAgent(BaseAgent):
    """Central planning agent that coordinates all AI workflows."""

    def __init__(self):
        super().__init__(
            name="Planner",
            description="Central reasoning engine that understands user intent and coordinates workflows",
        )
        self.available_agents: dict[str, BaseAgent] = {}

    def register_agent(self, name: str, agent: BaseAgent) -> None:
        """Register a specialized agent."""
        self.available_agents[name] = agent

    async def process(self, input_data: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Process user input and plan the workflow."""
        user_message = input_data.get("message", "")
        user_id = context.get("user_id")
        organization_id = context.get("organization_id")

        logger.info(
            "planner_processing",
            message=user_message[:100],
            user_id=user_id,
        )

        # Step 1: Classify intent using LLM if available, else use keyword matching
        intent = await self._classify_intent(user_message)

        # Step 2: Determine required workflow
        workflow = self._determine_workflow(intent, user_message)

        # Step 3: Check if knowledge retrieval is needed
        needs_knowledge = self._needs_knowledge_retrieval(intent)

        # Step 4: Determine which agent to use
        target_agent = self._select_agent(intent)

        result = {
            "intent": intent,
            "workflow": workflow,
            "needs_knowledge": needs_knowledge,
            "target_agent": target_agent,
            "message": user_message,
        }

        # Step 5: Delegate to appropriate agent if available
        if target_agent and target_agent in self.available_agents:
            agent = self.available_agents[target_agent]
            agent_result = await agent.process(input_data, context)
            result["agent_result"] = agent_result
        else:
            # Use HR agent as default for general queries
            if "hr" in self.available_agents:
                agent_result = await self.available_agents["hr"].process(input_data, context)
                result["agent_result"] = agent_result

        return result

    async def _classify_intent(self, message: str) -> str:
        """Classify the user's intent using LLM if available, else keyword matching."""
        # Try LLM-based classification first
        try:
            from app.core.llm import generate_text
            
            system_prompt = (
                "You are an intent classifier for an HR assistant. "
                "Classify the user's message into exactly one of these categories:\n"
                "- leave_request: Applying for leave, requesting time off, vacation\n"
                "- leave_balance: Checking leave balance, remaining days\n"
                "- leave_history: Viewing past leaves, leave history\n"
                "- policy_query: Asking about policies, rules, guidelines\n"
                "- document_generation: Requesting documents, letters, certificates\n"
                "- employee_info: Asking about employees, staff, team\n"
                "- department_info: Asking about departments, teams\n"
                "- approval: Approving, rejecting, pending requests\n"
                "- analytics: Reports, statistics, metrics\n"
                "- greeting: Hello, hi, greetings\n"
                "- help: Asking for help, capabilities\n"
                "- general_inquiry: Anything else\n\n"
                "Return ONLY the category name, nothing else."
            )
            
            response = await generate_text(
                messages=[{"role": "user", "content": message}],
                system_prompt=system_prompt
            )
            
            if response:
                intent = response.strip().lower().replace(" ", "_").replace("-", "_")
                # Validate intent is one of the known categories
                valid_intents = [
                    "leave_request", "leave_balance", "leave_history", "policy_query",
                    "document_generation", "employee_info", "department_info", "approval",
                    "analytics", "greeting", "help", "general_inquiry"
                ]
                if intent in valid_intents:
                    logger.info("intent_classified_by_llm", intent=intent)
                    return intent
        except Exception as e:
            logger.warning("llm_classification_failed", error=str(e))
        
        # Fallback to keyword-based classification
        return self._classify_intent_keywords(message)

    def _classify_intent_keywords(self, message: str) -> str:
        """Classify intent using keyword matching (fallback method)."""
        message_lower = message.lower()

        intent_patterns = {
            "leave_request": ["leave", "vacation", "time off", "day off", "pto", "apply leave", "take leave", "need leave", "want leave"],
            "leave_balance": ["balance", "remaining leave", "how many days", "leave balance", "check balance"],
            "leave_history": ["history", "past leave", "previous leave", "my leaves", "leave history"],
            "policy_query": ["policy", "policies", "handbook", "rules", "guideline"],
            "document_generation": ["document", "letter", "certificate", "generate", "offer", "experience"],
            "employee_info": ["employee", "staff", "team member", "colleague", "coworker", "who works"],
            "department_info": ["department", "team", "division"],
            "approval": ["approve", "approval", "pending", "reject"],
            "analytics": ["analytics", "report", "statistics", "metrics", "data", "insights"],
            "greeting": ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"],
            "help": ["help", "what can you do", "capabilities", "features"],
        }

        for intent, patterns in intent_patterns.items():
            if any(word in message_lower for word in patterns):
                return intent

        return "general_inquiry"

    def _determine_workflow(self, intent: str, message: str) -> str:
        """Determine the required workflow type."""
        workflow_map = {
            "leave_request": "leave_workflow",
            "leave_balance": "leave_balance_check",
            "leave_history": "leave_history",
            "policy_query": "policy_search",
            "document_generation": "document_generation",
            "employee_info": "employee_lookup",
            "department_info": "department_lookup",
            "approval": "approval_workflow",
            "analytics": "analytics_report",
            "greeting": "general_assistance",
            "help": "general_assistance",
            "general_inquiry": "general_assistance",
        }
        return workflow_map.get(intent, "general_assistance")

    def _needs_knowledge_retrieval(self, intent: str) -> bool:
        """Determine if RAG knowledge retrieval is needed."""
        return intent in ["policy_query", "general_inquiry", "benefits", "holiday"]

    def _select_agent(self, intent: str) -> str | None:
        """Select the appropriate specialized agent."""
        agent_map = {
            "leave_request": "leave",
            "leave_balance": "leave",
            "leave_history": "leave",
            "policy_query": "policy",
            "document_generation": "document",
            "approval": "approval",
            "analytics": "analytics",
            "greeting": "hr",
            "help": "hr",
            "employee_info": "hr",
            "department_info": "hr",
        }
        return agent_map.get(intent)
