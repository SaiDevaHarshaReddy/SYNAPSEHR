"""Document API routes."""

from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database.database import get_db
from app.schemas.document import DocumentGenerateRequest, DocumentResponse
from app.schemas.response import SuccessResponse
from app.services.document import DocumentService

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/generate", response_model=SuccessResponse[DocumentResponse])
async def generate_document(
    data: DocumentGenerateRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate an HR document."""
    service = DocumentService(db)
    document = await service.generate_document(data, UUID(current_user["user_id"]))

    return SuccessResponse(
        message="Document generated successfully",
        data=document,
    )


@router.get("", response_model=SuccessResponse[list[DocumentResponse]])
async def list_documents(
    employee_id: UUID = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List generated documents."""
    service = DocumentService(db)

    if employee_id is None:
        from app.repositories.employee import EmployeeRepository
        emp_repo = EmployeeRepository(db)
        from uuid import UUID as UUIDType
        employee = await emp_repo.get_by_user_id(UUIDType(current_user["user_id"]))
        if employee is None:
            return SuccessResponse(message="Employee not found", data=[])
        employee_id = employee.id

    documents = await service.list_employee_documents(employee_id)

    return SuccessResponse(
        message="Documents retrieved",
        data=documents,
    )


@router.get("/{document_id}")
async def download_document(
    document_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Download a generated document."""
    import os
    from app.core.exceptions import NotFoundException

    service = DocumentService(db)
    document = await service.get_document(document_id)

    if not os.path.exists(document.storage_path):
        raise NotFoundException("Document file")

    return FileResponse(
        path=document.storage_path,
        filename=os.path.basename(document.storage_path),
        media_type="application/pdf",
    )
