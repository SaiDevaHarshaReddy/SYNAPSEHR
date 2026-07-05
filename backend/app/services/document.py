"""Document service."""

import os
from datetime import datetime, timezone
from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import DOCUMENT_TYPE_OFFER
from app.core.exceptions import NotFoundException, ValidationException
from app.repositories.document import GeneratedDocumentRepository
from app.repositories.employee import EmployeeRepository
from app.schemas.document import DocumentGenerateRequest, DocumentResponse

logger = structlog.get_logger()


class DocumentService:
    """Handle document generation operations."""

    VALID_DOCUMENT_TYPES = {
        "offer_letter",
        "appointment_letter",
        "experience_letter",
        "salary_certificate",
        "promotion_letter",
        "warning_letter",
        "relieving_letter",
        "termination_letter",
    }

    def __init__(self, session: AsyncSession, upload_dir: str = "./generated_documents"):
        self.session = session
        self.doc_repo = GeneratedDocumentRepository(session)
        self.employee_repo = EmployeeRepository(session)
        self.upload_dir = upload_dir

    async def generate_document(
        self, data: DocumentGenerateRequest, generated_by: UUID
    ) -> DocumentResponse:
        """Generate an HR document."""
        if data.document_type not in self.VALID_DOCUMENT_TYPES:
            raise ValidationException(
                f"Invalid document type. Valid types: {', '.join(self.VALID_DOCUMENT_TYPES)}"
            )

        employee = await self.employee_repo.get_by_id(data.employee_id)
        if employee is None:
            raise NotFoundException("Employee", str(data.employee_id))

        # Create document directory
        doc_dir = os.path.join(self.upload_dir, data.document_type)
        os.makedirs(doc_dir, exist_ok=True)

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{employee.employee_code}_{data.document_type}_{timestamp}.pdf"
        storage_path = os.path.join(doc_dir, filename)

        # Generate PDF content (simplified - in production use ReportLab)
        self._generate_pdf(employee, data.document_type, storage_path, data.additional_data)

        # Create database record
        document = await self.doc_repo.create(
            employee_id=data.employee_id,
            document_type=data.document_type,
            storage_path=storage_path,
            generated_by=generated_by,
            generated_at=datetime.now(timezone.utc),
        )

        logger.info(
            "document_generated",
            document_id=str(document.id),
            document_type=data.document_type,
            employee_id=str(data.employee_id),
        )

        return DocumentResponse(
            id=document.id,
            employee_id=document.employee_id,
            document_type=document.document_type,
            storage_path=document.storage_path,
            generated_by=document.generated_by,
            generated_at=document.generated_at,
            created_at=document.created_at,
        )

    async def get_document(self, document_id: UUID) -> DocumentResponse:
        """Get document by ID."""
        document = await self.doc_repo.get_by_id(document_id)
        if document is None:
            raise NotFoundException("Document", str(document_id))

        return DocumentResponse(
            id=document.id,
            employee_id=document.employee_id,
            document_type=document.document_type,
            storage_path=document.storage_path,
            generated_by=document.generated_by,
            generated_at=document.generated_at,
            created_at=document.created_at,
        )

    async def list_employee_documents(
        self, employee_id: UUID
    ) -> list[DocumentResponse]:
        """List all documents for an employee."""
        documents = await self.doc_repo.get_by_employee(employee_id)
        return [
            DocumentResponse(
                id=doc.id,
                employee_id=doc.employee_id,
                document_type=doc.document_type,
                storage_path=doc.storage_path,
                generated_by=doc.generated_by,
                generated_at=doc.generated_at,
                created_at=doc.created_at,
            )
            for doc in documents
        ]

    def _generate_pdf(
        self,
        employee,
        document_type: str,
        output_path: str,
        additional_data: dict | None = None,
    ) -> None:
        """Generate PDF document using ReportLab."""
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import inch
        from reportlab.pdfgen import canvas

        c = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4

        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, height - inch, document_type.replace("_", " ").title())

        # Employee info
        c.setFont("Helvetica", 12)
        y = height - 2 * inch
        c.drawString(inch, y, f"Employee Name: {employee.first_name} {employee.last_name}")
        y -= 20
        c.drawString(inch, y, f"Employee Code: {employee.employee_code}")
        y -= 20
        c.drawString(inch, y, f"Date: {datetime.now().strftime('%B %d, %Y')}")

        # Document body
        y -= 40
        c.setFont("Helvetica", 11)
        c.drawString(inch, y, f"Subject: {document_type.replace('_', ' ').title()}")
        y -= 30

        body_text = self._get_document_body(document_type, employee, additional_data)
        for line in body_text.split('\n'):
            c.drawString(inch, y, line)
            y -= 15

        c.save()

    def _get_document_body(
        self, document_type: str, employee, additional_data: dict | None
    ) -> str:
        """Get document body text based on type."""
        name = f"{employee.first_name} {employee.last_name}"

        bodies = {
            "offer_letter": f"To: {name}\n\nWe are pleased to offer you the position of {employee.designation or 'Employee'} at our organization.\n\nThis offer is contingent upon successful completion of background verification.",
            "appointment_letter": f"To: {name}\n\nThis letter confirms your appointment as {employee.designation or 'Employee'} effective from {employee.joining_date or 'the date of this letter'}.",
            "experience_letter": f"To Whom It May Concern,\n\nThis is to certify that {name} was employed with us as {employee.designation or 'Employee'} from {employee.joining_date or 'N/A'} to the present date.",
            "salary_certificate": f"To Whom It May Concern,\n\nThis is to certify that {name} is employed with us and receives a salary as per company norms.",
            "promotion_letter": f"To: {name}\n\nWe are pleased to inform you of your promotion. Your new designation will be effective from the date mentioned herein.",
            "warning_letter": f"To: {name}\n\nThis letter serves as a formal warning regarding your conduct. Please note that further violations may result in disciplinary action.",
            "relieving_letter": f"To: {name}\n\nThis letter confirms that you have been relieved from your duties effective from the date of this letter.",
            "termination_letter": f"To: {name}\n\nThis letter serves as notice of termination of your employment effective from the date mentioned.",
        }

        return bodies.get(document_type, f"Document for {name}")
