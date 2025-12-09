from langchain_openai import OpenAIEmbeddings

from src.application.interfaces.embedding_provider import IEmbeddingProvider
from src.domain.exceptions.domain_exceptions import EmbeddingGenerationException
from src.domain.value_objects.embedding import Embedding
from src.infrastructure.configuration.settings import Settings


class LangChainEmbeddingProvider(IEmbeddingProvider):
    """LangChain-based embedding provider implementation."""

    _EMBEDDING_DIMENSIONS = {
        "text-embedding-3-small": 1536,
        "text-embedding-3-large": 3072,
        "text-embedding-ada-002": 1536,
    }

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._embeddings = self._create_embeddings()
        self._model_name = settings.embedding_model
        self._dimensions = self._EMBEDDING_DIMENSIONS.get(
            settings.embedding_model, 1536
        )

    def _create_embeddings(self) -> OpenAIEmbeddings:
        """Create the LangChain embeddings instance."""
        if self._settings.embedding_provider == "openai":
            return OpenAIEmbeddings(
                model=self._settings.embedding_model,
                api_key=self._settings.openai_api_key
            )
        else:
            raise ValueError(
                f"Unsupported embedding provider: {self._settings.embedding_provider}"
            )

    @property
    def model_name(self) -> str:
        """Return the name of the embedding model."""
        return self._model_name

    @property
    def dimensions(self) -> int:
        """Return the dimensionality of the embeddings."""
        return self._dimensions

    async def embed_text(self, text: str) -> Embedding:
        """Generate an embedding for a single text."""
        try:
            vector = await self._embeddings.aembed_query(text)
            return Embedding(
                vector=tuple(vector),
                model_name=self._model_name,
                dimensions=len(vector)
            )
        except Exception as e:
            raise EmbeddingGenerationException(
                f"Failed to generate embedding: {e}"
            ) from e

    async def embed_texts(self, texts: list[str]) -> list[Embedding]:
        """Generate embeddings for multiple texts."""
        try:
            vectors = await self._embeddings.aembed_documents(texts)
            return [
                Embedding(
                    vector=tuple(v),
                    model_name=self._model_name,
                    dimensions=len(v)
                )
                for v in vectors
            ]
        except Exception as e:
            raise EmbeddingGenerationException(
                f"Failed to generate embeddings: {e}"
            ) from e
