from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.chunk import Chunk


class IChunkRepository(ABC):
    """Interface for chunk persistence operations."""

    @abstractmethod
    async def save(self, chunk: Chunk) -> Chunk:
        """Save a chunk."""
        ...

    @abstractmethod
    async def save_many(self, chunks: list[Chunk]) -> list[Chunk]:
        """Save multiple chunks."""
        ...

    @abstractmethod
    async def get_by_id(self, chunk_id: UUID) -> Chunk | None:
        """Get a chunk by ID."""
        ...

    @abstractmethod
    async def get_by_document_id(self, document_id: UUID) -> list[Chunk]:
        """Get all chunks for a document."""
        ...

    @abstractmethod
    async def delete_by_document_id(self, document_id: UUID) -> int:
        """Delete all chunks for a document. Returns count of deleted chunks."""
        ...
