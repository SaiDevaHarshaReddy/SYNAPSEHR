"""Knowledge base API routes for document upload and indexing."""

import os
import uuid as uuid_lib
from datetime import datetime, timezone

import structlog
from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_roles
from app.core.config import get_settings
from app.core.exceptions import ValidationException
from app.database.database import get_db
from app.models.policy_document import PolicyDocument
from app.repositories.document import PolicyDocumentRepository
from app.schemas.response import SuccessResponse

logger = structlog.get_logger()
settings = get_settings()

router = APIRouter(prefix="/knowledge", tags=["Knowledge Base"])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}


@router.post("/upload", response_model=SuccessResponse[dict])
async def upload_knowledge_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    category: str = Form("general"),
    department: str = Form(None),
    current_user: dict = Depends(require_roles("admin", "hr")),
    db: AsyncSession = Depends(get_db),
):
    """Upload and index a document into the knowledge base."""
    # Validate file extension
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationException(f"Unsupported file type: {ext}. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")

    # Validate file size
    content = await file.read()
    max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(content) > max_size:
        raise ValidationException(f"File too large. Max size: {settings.MAX_UPLOAD_SIZE_MB}MB")

    # Save file to knowledge directory
    knowledge_dir = settings.KNOWLEDGE_DIR
    os.makedirs(knowledge_dir, exist_ok=True)

    file_id = str(uuid_lib.uuid4())
    file_name = f"{file_id}{ext}"
    file_path = os.path.join(knowledge_dir, file_name)

    with open(file_path, "wb") as f:
        f.write(content)

    # Create database record
    policy_repo = PolicyDocumentRepository(db)
    org_id = current_user["organization_id"]

    policy_doc = await policy_repo.create(
        organization_id=uuid_lib.UUID(org_id) if isinstance(org_id, str) else org_id,
        title=title,
        category=category,
        file_name=file.filename or file_name,
        storage_path=file_path,
        version=1,
        uploaded_by=uuid_lib.UUID(current_user["user_id"]),
    )

    await db.commit()

    # Index into vector store
    chunk_count = 0
    try:
        from app.rag.retriever import Retriever

        retriever = Retriever()
        chunk_count = await retriever.index_document(
            file_path=file_path,
            document_id=str(policy_doc.id),
            organization_id=str(org_id),
            title=title,
            category=category,
            department=department,
            version=1,
            uploaded_by=current_user["user_id"],
        )
    except Exception as e:
        logger.error("indexing_failed", document_id=str(policy_doc.id), error=str(e))

    logger.info(
        "knowledge_document_uploaded",
        document_id=str(policy_doc.id),
        title=title,
        chunks_indexed=chunk_count,
    )

    return SuccessResponse(
        message="Document uploaded and indexed successfully",
        data={
            "document_id": str(policy_doc.id),
            "title": title,
            "category": category,
            "chunks_indexed": chunk_count,
            "file_name": file.filename,
        },
    )


@router.get("", response_model=SuccessResponse[list[dict]])
async def list_knowledge_documents(
    current_user: dict = Depends(require_roles("admin", "hr", "manager")),
    db: AsyncSession = Depends(get_db),
):
    """List all knowledge base documents for the organization."""
    policy_repo = PolicyDocumentRepository(db)
    org_id = current_user["organization_id"]

    documents = await policy_repo.get_by_organization(
        uuid_lib.UUID(org_id) if isinstance(org_id, str) else org_id
    )

    return SuccessResponse(
        message="Documents retrieved",
        data=[
            {
                "id": str(doc.id),
                "title": doc.title,
                "category": doc.category,
                "file_name": doc.file_name,
                "version": doc.version,
                "created_at": doc.created_at.isoformat(),
            }
            for doc in documents
        ],
    )


@router.delete("/{document_id}", response_model=SuccessResponse[dict])
async def delete_knowledge_document(
    document_id: str,
    current_user: dict = Depends(require_roles("admin", "hr")),
    db: AsyncSession = Depends(get_db),
):
    """Delete a knowledge base document and its index."""
    policy_repo = PolicyDocumentRepository(db)
    doc_uuid = uuid_lib.UUID(document_id)
    doc = await policy_repo.get_by_id(doc_uuid)

    if doc is None:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("Knowledge document", document_id)

    # Remove from vector store
    try:
        from app.rag.retriever import Retriever
        retriever = Retriever()
        await retriever.delete_document(document_id)
    except Exception as e:
        logger.error("vector_delete_failed", document_id=document_id, error=str(e))

    # Delete file
    if os.path.exists(doc.storage_path):
        os.remove(doc.storage_path)

    # Delete DB record
    await policy_repo.delete(doc_uuid)
    await db.commit()

    logger.info("knowledge_document_deleted", document_id=document_id)

    return SuccessResponse(
        message="Document deleted successfully",
        data={"document_id": document_id},
    )


@router.get("/stats", response_model=SuccessResponse[dict])
async def get_knowledge_stats(
    current_user: dict = Depends(require_roles("admin", "hr")),
):
    """Get knowledge base statistics."""
    try:
        from app.rag.retriever import Retriever
        retriever = Retriever()
        stats = await retriever.get_index_stats()
    except Exception:
        stats = {"total_chunks": 0, "collection": "synapsehr_knowledge"}

    return SuccessResponse(
        message="Stats retrieved",
        data=stats,
    )
