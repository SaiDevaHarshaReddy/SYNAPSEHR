"""Employee AI tools."""

from app.tools.registry import register_tool


@register_tool(
    name="search_employee",
    description="Search for employees by name, department, or designation",
)
async def search_employee(query: str = "", department: str = "", designation: str = "") -> dict:
    """Search for employees."""
    return {
        "query": query,
        "department": department,
        "designation": designation,
        "results": [],
        "message": f"Employee search completed for '{query}'",
    }


@register_tool(
    name="get_employee_details",
    description="Get detailed information about a specific employee",
)
async def get_employee_details(employee_id: str = "") -> dict:
    """Get employee details."""
    return {
        "employee_id": employee_id,
        "message": f"Retrieved details for employee {employee_id}",
    }


@register_tool(
    name="list_employees_by_department",
    description="List all employees in a specific department",
)
async def list_employees_by_department(department: str = "") -> dict:
    """List employees by department."""
    return {
        "department": department,
        "employees": [],
        "message": f"Listed employees in {department}",
    }
