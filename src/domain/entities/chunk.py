from dataclasses import dataclass
from uuid import UUID

from src.domain.value_objects.chunk_metadata import ChunkMetadata
from src.domain.value_objects.embedding import Embedding


@dataclass
class Chunk:
    """Domain entity representing a chunk of a document."""

    id: UUID
    document_id: UUID
    content: str
    metadata: ChunkMetadata
    embedding: Embedding | None = None

    def __post_init__(self) -> None:
        if not self.content:
            raise ValueError("Chunk content cannot be empty")

    def has_embedding(self) -> bool:
        """Check if this chunk has an embedding."""
        return self.embedding is not None

    def set_embedding(self, embedding: Embedding) -> None:
        """Set the embedding for this chunk."""
        self.embedding = embedding
