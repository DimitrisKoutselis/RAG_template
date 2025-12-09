from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.document import Document


class IDocumentRepository(ABC):
    """Interface for document persistence operations."""

    @abstractmethod
    async def save(self, document: Document) -> Document:
        """Save a document."""
        ...

    @abstractmethod
    async def get_by_id(self, document_id: UUID) -> Document | None:
        """Get a document by ID."""
        ...

    @abstractmethod
    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> list[Document]:
        """Get all documents with pagination."""
        ...

    @abstractmethod
    async def delete(self, document_id: UUID) -> bool:
        """Delete a document by ID. Returns True if deleted."""
        ...

    @abstractmethod
    async def update(self, document: Document) -> Document:
        """Update a document."""
        ...
