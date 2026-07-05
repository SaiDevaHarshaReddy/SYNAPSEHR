"""Document parser supporting PDF, DOCX, TXT, and Markdown files."""

import os
from pathlib import Path

import structlog

logger = structlog.get_logger()

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md", ".markdown"}


class DocumentParser:
    """Parse uploaded documents into raw text."""

    @staticmethod
    def parse(file_path: str) -> str:
        """Parse a document file and return extracted text."""
        ext = Path(file_path).suffix.lower()

        if ext not in SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {ext}. Supported: {SUPPORTED_EXTENSIONS}")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        parser_map = {
            ".pdf": DocumentParser._parse_pdf,
            ".docx": DocumentParser._parse_docx,
            ".txt": DocumentParser._parse_text,
            ".md": DocumentParser._parse_text,
            ".markdown": DocumentParser._parse_text,
        }

        parser = parser_map[ext]
        text = parser(file_path)

        logger.info(
            "document_parsed",
            file_path=file_path,
            file_type=ext,
            char_count=len(text),
        )

        return text

    @staticmethod
    def _parse_pdf(file_path: str) -> str:
        """Extract text from PDF using pypdf."""
        from pypdf import PdfReader

        reader = PdfReader(file_path)
        pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text.strip())

        return "\n\n".join(pages)

    @staticmethod
    def _parse_docx(file_path: str) -> str:
        """Extract text from DOCX using python-docx."""
        from docx import Document

        doc = Document(file_path)
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

        return "\n\n".join(paragraphs)

    @staticmethod
    def _parse_text(file_path: str) -> str:
        """Read plain text or markdown files."""
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().strip()

    @staticmethod
    def get_metadata(file_path: str) -> dict:
        """Extract metadata from a file."""
        p = Path(file_path)
        stat = os.stat(file_path)

        return {
            "file_name": p.name,
            "file_extension": p.suffix.lower(),
            "file_size_bytes": stat.st_size,
            "file_path": str(p.absolute()),
        }
