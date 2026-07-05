"""Models module — import all models so Alembic detects them."""

from app.models.base import BaseModel  # noqa: F401
from app.models.organization import Organization  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.role import Role  # noqa: F401
from app.models.employee import Employee  # noqa: F401
from app.models.department import Department  # noqa: F401
from app.models.leave_type import LeaveType  # noqa: F401
from app.models.leave_balance import LeaveBalance  # noqa: F401
from app.models.leave_request import LeaveRequest  # noqa: F401
from app.models.policy_document import PolicyDocument  # noqa: F401
from app.models.conversation import Conversation  # noqa: F401
from app.models.message import Message  # noqa: F401
from app.models.workflow import Workflow, WorkflowStep  # noqa: F401
from app.models.generated_document import GeneratedDocument  # noqa: F401
from app.models.notification import Notification  # noqa: F401
from app.models.audit_log import AuditLog  # noqa: F401

__all__ = [
    "BaseModel",
    "Organization",
    "User",
    "Role",
    "Employee",
    "Department",
    "LeaveType",
    "LeaveBalance",
    "LeaveRequest",
    "PolicyDocument",
    "Conversation",
    "Message",
    "Workflow",
    "WorkflowStep",
    "GeneratedDocument",
    "Notification",
    "AuditLog",
]
