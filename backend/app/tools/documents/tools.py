"""Document tools for AI agents."""

from uuid import UUID

from app.tools.registry import register_tool


@register_tool(
    name="generate_document",
    description="Generate an HR document for an employee"
)
async def generate_document(
    employee_id: str,
    document_type: str,
    generated_by: str = None,
    additional_data: dict = None,
) -> dict:
    """Generate an HR document."""
    from app.database.database import async_session_factory
    from app.services.document import DocumentService
    from app.schemas.document import DocumentGenerateRequest

    async with async_session_factory() as session:
        service = DocumentService(session)

        data = DocumentGenerateRequest(
            employee_id=UUID(employee_id),
            document_type=document_type,
            additional_data=additional_data,
        )

        user_id = UUID(generated_by) if generated_by else UUID(employee_id)
        result = await service.generate_document(data, user_id)
        await session.commit()

        return {
            "document_id": str(result.id),
            "document_type": result.document_type,
            "storage_path": result.storage_path,
            "message": f"Document generated successfully",
        }


@register_tool(
    name="list_document_types",
    description="List all supported document types"
)
async def list_document_types() -> dict:
    """List all supported document types."""
    from app.services.document import DocumentService

    return {
        "document_types": [
            {"type": dt, "name": dt.replace("_", " ").title()}
            for dt in DocumentService.VALID_DOCUMENT_TYPES
        ],
    }
