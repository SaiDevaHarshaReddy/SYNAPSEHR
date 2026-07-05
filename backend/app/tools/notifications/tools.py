"""Notification AI tools."""

from app.tools.registry import register_tool


@register_tool(
    name="send_notification",
    description="Send a notification to an employee or group",
)
async def send_notification(recipient_id: str = "", title: str = "", message: str = "") -> dict:
    """Send notification."""
    return {
        "recipient_id": recipient_id,
        "title": title,
        "message": "Notification sent successfully",
    }


@register_tool(
    name="get_notifications",
    description="Get notifications for an employee",
)
async def get_notifications(employee_id: str = "", unread_only: bool = False) -> dict:
    """Get notifications."""
    return {
        "employee_id": employee_id,
        "unread_only": unread_only,
        "notifications": [],
        "message": "Notifications retrieved",
    }
