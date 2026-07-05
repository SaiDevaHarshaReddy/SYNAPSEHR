"""Document Agent - Handles document generation."""

from typing import Any

import structlog

from app.agents.base import BaseAgent

logger = structlog.get_logger()


class DocumentAgent(BaseAgent):
    """Agent that handles HR document generation."""

    def __init__(self):
        super().__init__(
            name="Document",
            description="Generates HR documents like offer letters, experience letters, etc.",
        )

    async def process(self, input_data: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Process document generation requests."""
        message = input_data.get("message", "")
        user_id = context.get("user_id")

        logger.info("document_agent_processing", message=message[:100])

        # Determine document type
        doc_type = self._determine_document_type(message)

        result = {
            "action": "generate_document",
            "document_type": doc_type,
            "status": "processing",
            "message": f"I'll help you generate a {doc_type.replace('_', ' ')}.",
        }

        return result

    def _determine_document_type(self, message: str) -> str:
        """Determine the type of document to generate."""
        message_lower = message.lower()

        if "offer" in message_lower:
            return "offer_letter"
        elif "appointment" in message_lower:
            return "appointment_letter"
        elif "experience" in message_lower:
            return "experience_letter"
        elif "salary" in message_lower or "certificate" in message_lower:
            return "salary_certificate"
        elif "promotion" in message_lower:
            return "promotion_letter"
        elif "warning" in message_lower:
            return "warning_letter"
        elif "relieving" in message_lower:
            return "relieving_letter"
        elif "termination" in message_lower:
            return "termination_letter"
        else:
            return "experience_letter"
