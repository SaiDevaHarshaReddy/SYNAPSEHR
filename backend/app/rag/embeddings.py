"""Embedding service using sentence-transformers."""

from typing import Any

import structlog

logger = structlog.get_logger()


class EmbeddingService:
    """Generate embeddings using sentence-transformers."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None

    def _load_model(self) -> Any:
        """Lazy-load the embedding model."""
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            logger.info("loading_embedding_model", model=self.model_name)
            self._model = SentenceTransformer(self.model_name)
            logger.info("embedding_model_loaded", model=self.model_name)
        return self._model

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple document texts."""
        model = self._load_model()
        embeddings = model.encode(texts, show_progress_bar=False)
        result = embeddings.tolist()

        logger.info("documents_embedded", count=len(texts), dimension=len(result[0]) if result else 0)
        return result

    def embed_query(self, text: str) -> list[float]:
        """Embed a single query text."""
        model = self._load_model()
        embedding = model.encode([text], show_progress_bar=False)
        return embedding[0].tolist()

    @property
    def dimension(self) -> int:
        """Get the embedding dimension."""
        model = self._load_model()
        return model.get_sentence_embedding_dimension()
