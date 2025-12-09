from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from src.domain.entities.chunk import Chunk
from src.domain.entities.retrieval_result import RetrievalResult
from src.domain.value_objects.embedding import Embedding


class IVectorStore(ABC):
    """Interface for vector stores (ChromaDB, Pinecone, Weaviate, etc.)."""

    @abstractmethod
    async def add_chunks(self, chunks: list[Chunk]) -> None:
        """Add chunks with embeddings to the vector store."""
        ...

    @abstractmethod
    async def search(
        self,
        query_embedding: Embedding,
        top_k: int = 5,
        filter_metadata: dict[str, Any] | None = None
    ) -> list[RetrievalResult]:
        """Search for similar chunks."""
        ...

    @abstractmethod
    async def delete_by_document_id(self, document_id: UUID) -> int:
        """Delete all chunks for a document. Returns count of deleted."""
        ...

    @abstractmethod
    async def delete_all(self) -> None:
        """Delete all chunks from the vector store."""
        ...

    @abstractmethod
    async def get_collection_stats(self) -> dict[str, Any]:
        """Get statistics about the vector store collection."""
        ...
