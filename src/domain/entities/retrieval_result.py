from dataclasses import dataclass

from src.domain.entities.chunk import Chunk


@dataclass
class RetrievalResult:
    """Domain entity representing a retrieval result from vector search."""

    chunk: Chunk
    similarity_score: float
    rank: int

    def __post_init__(self) -> None:
        if not 0.0 <= self.similarity_score <= 1.0:
            raise ValueError("similarity_score must be between 0.0 and 1.0")
        if self.rank < 1:
            raise ValueError("rank must be at least 1")
