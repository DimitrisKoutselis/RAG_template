from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from src.domain.value_objects.embedding import Embedding


@dataclass
class Query:
    """Domain entity representing a user query."""

    id: UUID
    text: str
    conversation_id: UUID | None = None
    embedding: Embedding | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        if not self.text:
            raise ValueError("Query text cannot be empty")

    def has_embedding(self) -> bool:
        """Check if this query has an embedding."""
        return self.embedding is not None

    def set_embedding(self, embedding: Embedding) -> None:
        """Set the embedding for this query."""
        self.embedding = embedding
