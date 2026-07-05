"""Analytics Agent - Handles analytics and reporting queries."""

from typing import Any

import structlog

from app.agents.base import BaseAgent

logger = structlog.get_logger()


class AnalyticsAgent(BaseAgent):
    """Agent for analytics and reporting."""

    def __init__(self):
        super().__init__(
            name="Analytics",
            description="Provides analytics, reports, and data insights",
        )

    async def process(self, input_data: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Process analytics queries."""
        message = input_data.get("message", "")
        logger.info("analytics_agent_processing", message=message[:100])

        message_lower = message.lower()

        if any(w in message_lower for w in ["leave", "absence"]):
            return {
                "action": "leave_analytics",
                "message": "I can provide leave analytics. Let me retrieve the leave statistics for your organization.",
            }
        elif any(w in message_lower for w in ["department", "team"]):
            return {
                "action": "department_analytics",
                "message": "I can show department-level analytics. Let me pull the relevant data.",
            }
        elif any(w in message_lower for w in ["report", "summary"]):
            return {
                "action": "generate_report",
                "message": "I can generate various HR reports. What type of report would you like? (leave, attendance, headcount, etc.)",
            }
        else:
            return {
                "action": "analytics_general",
                "message": "I provide HR analytics and reporting. I can help with leave analytics, department reports, headcount trends, and more.",
            }
