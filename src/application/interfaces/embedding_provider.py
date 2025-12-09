from abc import ABC, abstractmethod

from src.domain.value_objects.embedding import Embedding


class IEmbeddingProvider(ABC):
    """Interface for embedding providers."""

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the name of the embedding model."""
        ...

    @property
    @abstractmethod
    def dimensions(self) -> int:
        """Return the dimensionality of the embeddings."""
        ...

    @abstractmethod
    async def embed_text(self, text: str) -> Embedding:
        """Generate an embedding for a single text."""
        ...

    @abstractmethod
    async def embed_texts(self, texts: list[str]) -> list[Embedding]:
        """Generate embeddings for multiple texts."""
        ...
