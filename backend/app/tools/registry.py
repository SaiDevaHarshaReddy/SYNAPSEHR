"""Tool registry for AI agents."""

from typing import Any, Callable

import structlog

logger = structlog.get_logger()


class Tool:
    """Base tool class for AI agent tools."""

    def __init__(self, name: str, description: str, func: Callable):
        self.name = name
        self.description = description
        self.func = func

    async def execute(self, **kwargs: Any) -> Any:
        """Execute the tool."""
        logger.info("tool_executing", tool=self.name, kwargs=list(kwargs.keys()))
        result = await self.func(**kwargs)
        logger.info("tool_completed", tool=self.name)
        return result


class ToolRegistry:
    """Registry for all AI agent tools."""

    def __init__(self):
        self.tools: dict[str, Tool] = {}

    def register(self, name: str, description: str, func: Callable) -> None:
        """Register a new tool."""
        self.tools[name] = Tool(name=name, description=description, func=func)
        logger.info("tool_registered", tool=name)

    def get(self, name: str) -> Tool | None:
        """Get a tool by name."""
        return self.tools.get(name)

    def list_tools(self) -> list[dict[str, str]]:
        """List all registered tools."""
        return [
            {"name": tool.name, "description": tool.description}
            for tool in self.tools.values()
        ]

    async def execute(self, name: str, **kwargs: Any) -> Any:
        """Execute a tool by name."""
        tool = self.get(name)
        if tool is None:
            raise ValueError(f"Tool not found: {name}")
        return await tool.execute(**kwargs)


# Global tool registry
tool_registry = ToolRegistry()


def register_tool(name: str, description: str):
    """Decorator to register a tool."""
    def decorator(func: Callable):
        tool_registry.register(name, description, func)
        return func
    return decorator
