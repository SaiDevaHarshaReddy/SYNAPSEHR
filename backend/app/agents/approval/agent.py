"""Approval Agent - Handles approval workflows."""

from typing import Any

import structlog

from app.agents.base import BaseAgent

logger = structlog.get_logger()


class ApprovalAgent(BaseAgent):
    """Agent for managing approval workflows."""

    def __init__(self):
        super().__init__(
            name="Approval",
            description="Manages approval requests and processes",
        )

    async def process(self, input_data: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Process approval-related queries."""
        message = input_data.get("message", "")
        logger.info("approval_agent_processing", message=message[:100])

        message_lower = message.lower()

        if any(w in message_lower for w in ["approve", "approved"]):
            return {
                "action": "process_approval",
                "message": "I can help process approvals. Please provide the request ID or specify which request you'd like to approve.",
            }
        elif any(w in message_lower for w in ["reject", "rejected", "deny"]):
            return {
                "action": "process_rejection",
                "message": "I can help reject requests. Please provide the request ID and reason for rejection.",
            }
        elif any(w in message_lower for w in ["pending", "waiting"]):
            return {
                "action": "check_pending",
                "message": "Let me check for pending approvals in the system.",
            }
        else:
            return {
                "action": "approval_general",
                "message": "I manage approval workflows. I can help you approve, reject, or check pending requests.",
            }
