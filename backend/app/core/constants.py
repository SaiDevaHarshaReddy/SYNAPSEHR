"""Application constants."""

# Application
APP_TITLE = "SynapseHR API"
APP_DESCRIPTION = "AI-native Human Resource Operations Platform"
APP_VERSION = "0.1.0"

# Pagination
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# File Upload
ALLOWED_UPLOAD_EXTENSIONS = {
    "pdf": "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "txt": "text/plain",
    "md": "text/markdown",
    "png": "image/png",
    "jpeg": "image/jpeg",
    "jpg": "image/jpeg",
}

# Employee Status
EMPLOYEE_STATUS_ACTIVE = "active"
EMPLOYEE_STATUS_INACTIVE = "inactive"
EMPLOYEE_STATUS_ON_LEAVE = "on_leave"
EMPLOYEE_STATUS_TERMINATED = "terminated"

# Leave Request Status
LEAVE_STATUS_PENDING = "pending"
LEAVE_STATUS_APPROVED = "approved"
LEAVE_STATUS_REJECTED = "rejected"
LEAVE_STATUS_CANCELLED = "cancelled"

# Message Sender Types
SENDER_USER = "user"
SENDER_ASSISTANT = "assistant"
SENDER_SYSTEM = "system"

# Workflow Status
WORKFLOW_STATUS_CREATED = "created"
WORKFLOW_STATUS_VALIDATED = "validated"
WORKFLOW_STATUS_PLANNING = "planning"
WORKFLOW_STATUS_EXECUTING = "executing"
WORKFLOW_STATUS_WAITING_APPROVAL = "waiting_approval"
WORKFLOW_STATUS_COMPLETED = "completed"
WORKFLOW_STATUS_FAILED = "failed"
WORKFLOW_STATUS_CANCELLED = "cancelled"

# Notification Types
NOTIFICATION_TYPE_APPROVAL = "approval"
NOTIFICATION_TYPE_LEAVE = "leave"
NOTIFICATION_TYPE_DOCUMENT = "document"
NOTIFICATION_TYPE_WORKFLOW = "workflow"
NOTIFICATION_TYPE_SYSTEM = "system"
NOTIFICATION_TYPE_AI = "ai"

# Document Types
DOCUMENT_TYPE_OFFER = "offer_letter"
DOCUMENT_TYPE_APPOINTMENT = "appointment_letter"
DOCUMENT_TYPE_EXPERIENCE = "experience_letter"
DOCUMENT_TYPE_SALARY_CERTIFICATE = "salary_certificate"
DOCUMENT_TYPE_PROMOTION = "promotion_letter"
DOCUMENT_TYPE_WARNING = "warning_letter"
DOCUMENT_TYPE_RELIEVING = "relieving_letter"
DOCUMENT_TYPE_TERMINATION = "termination_letter"

# Roles
ROLE_EMPLOYEE = "employee"
ROLE_MANAGER = "manager"
ROLE_HR = "hr"
ROLE_ADMINISTRATOR = "administrator"
