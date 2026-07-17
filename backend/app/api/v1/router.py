"""V1 API router aggregation."""

from fastapi import APIRouter

from app.api.v1.admin.router import router as admin_router
from app.api.v1.analytics.router import router as analytics_router
from app.api.v1.auth.router import router as auth_router
from app.api.v1.chat.router import router as chat_router
from app.api.v1.departments.router import router as departments_router
from app.api.v1.documents.router import router as documents_router
from app.api.v1.employees.router import router as employees_router
from app.api.v1.knowledge.router import router as knowledge_router
from app.api.v1.leave.router import router as leave_router
from app.api.v1.notifications.router import router as notifications_router
from app.api.v1.policies.router import router as policies_router
from app.api.v1.recruitment.router import router as recruitment_router
from app.api.v1.workflow.router import router as workflow_router
from app.api.v1.hr_tickets.router import router as hr_tickets_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(employees_router)
api_router.include_router(departments_router)
api_router.include_router(leave_router)
api_router.include_router(documents_router)
api_router.include_router(knowledge_router)
api_router.include_router(policies_router)
api_router.include_router(chat_router)
api_router.include_router(analytics_router)
api_router.include_router(notifications_router)
api_router.include_router(workflow_router)
api_router.include_router(admin_router)
api_router.include_router(recruitment_router)
api_router.include_router(hr_tickets_router)
