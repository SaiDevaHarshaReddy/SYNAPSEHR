"""ChromaDB vector store service."""

import os
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger()

COLLECTION_NAME = "synapsehr_knowledge"

# Resolve chroma_db path relative to the backend directory (not CWD)
_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent  # app/rag -> app -> backend
DEFAULT_CHROMA_DIR = str(_BACKEND_DIR / "chroma_db")


class VectorStoreService:
    """Manage ChromaDB vector store for document embeddings."""

    def __init__(
        self,
        collection_name: str = COLLECTION_NAME,
        persist_directory: str = None,
    ):
        self.collection_name = collection_name
        self.persist_directory = persist_directory or DEFAULT_CHROMA_DIR
        self._client = None
        self._collection = None

    def _get_collection(self) -> Any:
        """Get or create the ChromaDB collection."""
        if self._collection is None:
            import chromadb

            os.makedirs(self.persist_directory, exist_ok=True)
            self._client = chromadb.PersistentClient(path=self.persist_directory)
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
            logger.info(
                "vector_store_initialized",
                collection=self.collection_name,
                doc_count=self._collection.count(),
                path=self.persist_directory,
            )
        return self._collection

    def add_documents(
        self,
        texts: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict],
        ids: list[str],
    ) -> None:
        """Add documents to the vector store."""
        collection = self._get_collection()

        collection.add(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids,
        )

        logger.info(
            "documents_added_to_vector_store",
            count=len(ids),
            collection=self.collection_name,
        )

    def query(
        self,
        embedding: list[float],
        n_results: int = 5,
        where: dict | None = None,
        where_document: dict | None = None,
    ) -> dict:
        """Query similar documents from the vector store."""
        collection = self._get_collection()

        kwargs: dict[str, Any] = {
            "query_embeddings": [embedding],
            "n_results": min(n_results, collection.count()) if collection.count() > 0 else 1,
        }

        if where:
            kwargs["where"] = where
        if where_document:
            kwargs["where_document"] = where_document

        results = collection.query(**kwargs)

        logger.info(
            "vector_store_queried",
            n_results=n_results,
            returned=len(results.get("documents", [[]])[0]),
        )

        return results

    def delete_documents(self, ids: list[str]) -> None:
        """Delete documents from the vector store."""
        collection = self._get_collection()
        collection.delete(ids=ids)

        logger.info("documents_deleted_from_vector_store", count=len(ids))

    def delete_by_metadata(self, where: dict) -> None:
        """Delete documents matching metadata filter."""
        collection = self._get_collection()
        # Get all matching docs
        results = collection.get(where=where)
        if results and results.get("ids"):
            collection.delete(ids=results["ids"])
            logger.info("documents_deleted_by_metadata", count=len(results["ids"]))

    def get_count(self) -> int:
        """Get total document count."""
        collection = self._get_collection()
        return collection.count()

    def reset(self) -> None:
        """Reset the collection (delete all documents)."""
        collection = self._get_collection()
        collection.delete(where={})
        logger.info("vector_store_reset", collection=self.collection_name)
