"""Retriever service - orchestrates chunking, embedding, and vector search."""

import uuid
from pathlib import Path

import structlog

from app.rag.chunker import TextChunker, Chunk
from app.rag.embeddings import EmbeddingService
from app.rag.parser import DocumentParser
from app.rag.vector_store import VectorStoreService

logger = structlog.get_logger()


class Retriever:
    """Orchestrates the RAG pipeline: parse, chunk, embed, store, retrieve."""

    def __init__(
        self,
        embedding_service: EmbeddingService | None = None,
        vector_store: VectorStoreService | None = None,
        chunker: TextChunker | None = None,
    ):
        self.embedding = embedding_service or EmbeddingService()
        self.vector_store = vector_store or VectorStoreService()
        self.chunker = chunker or TextChunker()

    async def index_document(
        self,
        file_path: str,
        document_id: str,
        organization_id: str,
        title: str,
        category: str,
        department: str | None = None,
        version: int = 1,
        uploaded_by: str | None = None,
    ) -> int:
        """Index a document into the vector store. Returns number of chunks indexed."""
        # Step 1: Parse document
        text = DocumentParser.parse(file_path)
        if not text:
            logger.warning("empty_document", file_path=file_path)
            return 0

        # Step 2: Get metadata
        file_metadata = DocumentParser.get_metadata(file_path)

        # Step 3: Chunk the text
        base_metadata = {
            "document_id": document_id,
            "organization_id": organization_id,
            "title": title,
            "category": category,
            "department": department or "",
            "version": str(version),
            "uploaded_by": uploaded_by or "",
            "file_name": file_metadata["file_name"],
        }

        chunks = self.chunker.chunk(text, metadata=base_metadata)
        if not chunks:
            logger.warning("no_chunks_generated", file_path=file_path)
            return 0

        # Step 4: Generate embeddings
        texts = [c.content for c in chunks]
        embeddings = self.embedding.embed_documents(texts)

        # Step 5: Prepare metadata and IDs
        ids = [str(uuid.uuid5(uuid.NAMESPACE_URL, f"{document_id}_{c.index}")) for c in chunks]
        metadatas = []
        for chunk in chunks:
            meta = {**base_metadata, "chunk_index": str(chunk.index)}
            # ChromaDB requires string values
            metadatas.append({k: str(v) for k, v in meta.items()})

        # Step 6: Store in vector DB
        self.vector_store.add_documents(
            texts=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids,
        )

        logger.info(
            "document_indexed",
            document_id=document_id,
            chunks=len(chunks),
            title=title,
        )

        return len(chunks)

    async def retrieve(
        self,
        query: str,
        organization_id: str,
        n_results: int = 5,
        category: str | None = None,
    ) -> list[dict]:
        """Retrieve relevant chunks for a query."""
        # Embed the query
        query_embedding = self.embedding.embed_query(query)

        # Build metadata filter
        where = {"organization_id": organization_id}
        if category:
            where["category"] = category

        # Query vector store
        results = self.vector_store.query(
            embedding=query_embedding,
            n_results=n_results,
            where=where,
        )

        # Format results
        retrieved = []
        if results and results.get("documents") and results["documents"][0]:
            docs = results["documents"][0]
            metadatas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)
            distances = results["distances"][0] if results.get("distances") else [0.0] * len(docs)

            for doc, meta, distance in zip(docs, metadatas, distances):
                retrieved.append({
                    "content": doc,
                    "metadata": meta,
                    "relevance_score": 1 - distance,  # cosine distance to similarity
                    "source": meta.get("title", "Unknown"),
                    "category": meta.get("category", "general"),
                })

        logger.info(
            "retrieval_complete",
            query_length=len(query),
            results_count=len(retrieved),
            organization_id=organization_id,
        )

        return retrieved

    async def delete_document(self, document_id: str) -> None:
        """Remove all chunks for a document from the vector store."""
        self.vector_store.delete_by_metadata({"document_id": document_id})
        logger.info("document_removed_from_index", document_id=document_id)

    async def get_index_stats(self) -> dict:
        """Get vector store statistics."""
        return {
            "total_chunks": self.vector_store.get_count(),
            "collection": self.vector_store.collection_name,
        }
