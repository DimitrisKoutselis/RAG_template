from abc import ABC, abstractmethod
from typing import Any

from src.domain.entities.chunk import Chunk
from src.domain.entities.document import Document


class IChunkingStrategy(ABC):
    """
    Interface for document chunking strategies.

    Implementations should define how documents are split into chunks
    for embedding and retrieval. Different strategies may be optimal
    for different use cases (e.g., code vs prose, short vs long documents).
    """

    @property
    @abstractmethod
    def strategy_name(self) -> str:
        """Return the name of this chunking strategy."""
        ...

    @abstractmethod
    async def chunk_document(self, document: Document) -> list[Chunk]:
        """
        Split a document into chunks.

        Args:
            document: The document to chunk

        Returns:
            List of Chunk entities with proper metadata including:
            - chunk_index
            - start_position and end_position
            - overlap information
        """
        ...

    @abstractmethod
    def get_config(self) -> dict[str, Any]:
        """
        Return the current configuration of this strategy.

        Useful for logging and debugging to understand how
        chunks were created.
        """
        ...
