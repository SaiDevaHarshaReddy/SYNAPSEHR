"""Tests for RAG pipeline components."""
import os
import tempfile

import pytest


class TestDocumentParser:
    """Tests for DocumentParser."""

    def test_parse_txt_file(self):
        from app.rag.parser import DocumentParser
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Hello, this is a test document.")
            f.flush()
            f.close()
            result = DocumentParser.parse(f.name)
            assert "Hello, this is a test document." in result
            os.unlink(f.name)

    def test_parse_nonexistent_file(self):
        from app.rag.parser import DocumentParser
        with pytest.raises(FileNotFoundError):
            DocumentParser.parse("/nonexistent/file.txt")

    def test_parse_unsupported_type(self):
        from app.rag.parser import DocumentParser
        with tempfile.NamedTemporaryFile(suffix='.xyz', delete=False) as f:
            f.write(b"test")
            f.flush()
            f.close()
            with pytest.raises(ValueError, match="Unsupported file type"):
                DocumentParser.parse(f.name)
            os.unlink(f.name)

    def test_get_metadata(self):
        from app.rag.parser import DocumentParser
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("test")
            f.flush()
            f.close()
            meta = DocumentParser.get_metadata(f.name)
            assert meta["file_extension"] == ".txt"
            assert meta["file_size_bytes"] > 0
            os.unlink(f.name)


class TestVectorStoreService:
    """Tests for VectorStoreService."""

    def test_initialization(self):
        from app.rag.vector_store import VectorStoreService
        with tempfile.TemporaryDirectory() as tmpdir:
            vs = VectorStoreService(persist_directory=tmpdir)
            assert vs.collection_name == "synapsehr_knowledge"


class TestRAGIntegration:
    """Integration tests for RAG pipeline."""

    def test_chunker_produces_valid_chunks(self):
        from app.rag.chunker import TextChunker
        chunker = TextChunker(chunk_size=500, chunk_overlap=100)
        text = """
        Company Leave Policy

        Section 1: Annual Leave

        All employees are entitled to 20 days of annual leave per year.
        Leave must be requested at least 2 weeks in advance.
        Unused leave can be carried forward up to 5 days.

        Section 2: Sick Leave

        Employees are entitled to 10 days of sick leave per year.
        A medical certificate is required for absences exceeding 3 consecutive days.
        Sick leave cannot be carried forward to the next year.

        Section 3: Maternity/Paternity Leave

        Primary caregivers are entitled to 16 weeks of paid parental leave.
        Secondary caregivers are entitled to 4 weeks of paid parental leave.
        Leave must be taken within 12 months of the birth/adoption.
        """
        chunks = chunker.chunk(text)
        assert len(chunks) > 0
        for chunk in chunks:
            assert len(chunk.content) > 0

    def test_text_chunker_basic(self):
        from app.rag.chunker import TextChunker
        chunker = TextChunker(chunk_size=100, chunk_overlap=20)
        text = "Word " * 200
        chunks = chunker.chunk(text.strip())
        assert len(chunks) >= 1
