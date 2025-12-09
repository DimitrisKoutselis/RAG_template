from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.domain.value_objects.document_metadata import DocumentMetadata


@dataclass
class Document:
    """Domain entity representing a document in the RAG system."""

    id: UUID
    content: str
    metadata: DocumentMetadata
    created_at: datetime
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.content:
            raise ValueError("Document content cannot be empty")

    def update_content(self, new_content: str) -> None:
        """Update the document content."""
        if not new_content:
            raise ValueError("Document content cannot be empty")
        self.content = new_content
        self.updated_at = datetime.utcnow()
