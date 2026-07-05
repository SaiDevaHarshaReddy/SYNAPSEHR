"""Base agent class for all AI agents."""

from abc import ABC, abstractmethod
from typing import Any, Optional
from uuid import UUID

import structlog

logger = structlog.get_logger()


class BaseAgent(ABC):
    """Base class for all AI agents."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.tools: list = []

    def register_tool(self, tool: Any) -> None:
        """Register a tool with this agent."""
        self.tools.append(tool)

    @abstractmethod
    async def process(self, input_data: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Process input and return response."""
        pass

    async def execute_tool(self, tool_name: str, **kwargs: Any) -> Any:
        """Execute a registered tool by name."""
        for tool in self.tools:
            if hasattr(tool, "name") and tool.name == tool_name:
                return await tool.execute(**kwargs)
        raise ValueError(f"Tool not found: {tool_name}")

    def log_action(self, action: str, **kwargs: Any) -> None:
        """Log an agent action."""
        logger.info(
            "agent_action",
            agent=self.name,
            action=action,
            **kwargs,
        )
