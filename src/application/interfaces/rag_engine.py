from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from src.domain.entities.conversation import Conversation
from src.domain.entities.query import Query
from src.domain.entities.retrieval_result import RetrievalResult
from src.domain.value_objects.rag_config import RAGConfig


class IRAGEngine(ABC):
    """
    Interface for RAG engine implementations.

    Both LangChain and LangGraph implementations will implement this interface,
    allowing them to be used interchangeably.
    """

    @abstractmethod
    async def process_query(
        self,
        query: Query,
        conversation: Conversation | None = None,
        config: RAGConfig | None = None
    ) -> tuple[str, list[RetrievalResult]]:
        """
        Process a query through the RAG pipeline.

        Args:
            query: The user query with optional embedding
            conversation: Optional conversation for context
            config: RAG configuration options

        Returns:
            Tuple of (response_text, retrieval_results)
        """
        ...

    @abstractmethod
    async def process_query_stream(
        self,
        query: Query,
        conversation: Conversation | None = None,
        config: RAGConfig | None = None
    ) -> AsyncIterator[tuple[str, list[RetrievalResult] | None]]:
        """
        Process a query with streaming response.

        Args:
            query: The user query with optional embedding
            conversation: Optional conversation for context
            config: RAG configuration options

        Yields:
            Tuples of (token, retrieval_results or None)
            The retrieval_results are only included in the first yield.
        """
        ...
