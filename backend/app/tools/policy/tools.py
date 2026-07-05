"""Policy AI tools."""

from app.tools.registry import register_tool


@register_tool(
    name="search_policy",
    description="Search company policies by keyword",
)
async def search_policy(query: str = "", category: str = "") -> dict:
    """Search policies."""
    return {
        "query": query,
        "category": category,
        "results": [],
        "message": f"Policy search completed for '{query}'",
    }


@register_tool(
    name="get_policy_details",
    description="Get details of a specific policy document",
)
async def get_policy_details(policy_id: str = "") -> dict:
    """Get policy details."""
    return {
        "policy_id": policy_id,
        "message": f"Retrieved policy {policy_id}",
    }


@register_tool(
    name="list_policies",
    description="List all available policies by category",
)
async def list_policies(category: str = "") -> dict:
    """List policies by category."""
    return {
        "category": category,
        "policies": [],
        "message": f"Listed policies for category '{category}'",
    }
