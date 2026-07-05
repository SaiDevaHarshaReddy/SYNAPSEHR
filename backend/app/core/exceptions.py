"""Custom exception classes for the application."""


class AppException(Exception):
    """Base application exception."""

    def __init__(self, message: str = "An error occurred", status_code: int = 500, detail: str | None = None):
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.message)


class NotFoundException(AppException):
    """Resource not found."""

    def __init__(self, resource: str = "Resource", resource_id: str | None = None):
        message = f"{resource} not found"
        if resource_id:
            message = f"{resource} with id '{resource_id}' not found"
        super().__init__(message=message, status_code=404)


class DuplicateException(AppException):
    """Duplicate resource."""

    def __init__(self, resource: str = "Resource", detail: str | None = None):
        super().__init__(
            message=f"{resource} already exists",
            status_code=409,
            detail=detail,
        )


class ValidationException(AppException):
    """Validation error."""

    def __init__(self, message: str = "Validation failed", detail: str | None = None):
        super().__init__(message=message, status_code=422, detail=detail)


class AuthenticationException(AppException):
    """Authentication failed."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message=message, status_code=401)


class AuthorizationException(AppException):
    """Authorization failed."""

    def __init__(self, message: str = "You do not have permission to perform this action"):
        super().__init__(message=message, status_code=403)


class BusinessRuleException(AppException):
    """Business rule violation."""

    def __init__(self, message: str = "Business rule violation", detail: str | None = None):
        super().__init__(message=message, status_code=422, detail=detail)


class LeaveBalanceExceeded(BusinessRuleException):
    """Leave balance exceeded."""

    def __init__(self, available: float, requested: float):
        super().__init__(
            message=f"Insufficient leave balance. Available: {available} days, Requested: {requested} days",
        )


class PolicyViolation(BusinessRuleException):
    """Policy violation."""

    def __init__(self, policy_name: str, detail: str | None = None):
        super().__init__(
            message=f"Policy violation: {policy_name}",
            detail=detail,
        )


class WorkflowException(AppException):
    """Workflow execution error."""

    def __init__(self, message: str = "Workflow execution failed", detail: str | None = None):
        super().__init__(message=message, status_code=500, detail=detail)


class AIException(AppException):
    """AI service error."""

    def __init__(self, message: str = "AI service error", detail: str | None = None):
        super().__init__(message=message, status_code=500, detail=detail)


class ExternalServiceException(AppException):
    """External service error."""

    def __init__(self, service: str, message: str = "External service error"):
        super().__init__(
            message=f"{service}: {message}",
            status_code=502,
        )
