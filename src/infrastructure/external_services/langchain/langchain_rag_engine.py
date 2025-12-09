from collections.abc import AsyncIterator

from src.application.interfaces.embedding_provider import IEmbeddingProvider
from src.application.interfaces.llm_provider import ILLMProvider
from src.application.interfaces.rag_engine import IRAGEngine
from src.application.interfaces.vector_store import IVectorStore
from src.domain.entities.conversation import Conversation
from src.domain.entities.query import Query
from src.domain.entities.retrieval_result import RetrievalResult
from src.domain.value_objects.rag_config import RAGConfig


class LangChainRAGEngine(IRAGEngine):
    """LangChain-based RAG engine implementation using LCEL."""

    DEFAULT_SYSTEM_PROMPT = """You are a helpful assistant that answers questions based on the provided context.
If the context doesn't contain relevant information to answer the question, say so.
Always be accurate and cite specific information from the context when possible."""

    def __init__(
        self,
        llm_provider: ILLMProvider,
        embedding_provider: IEmbeddingProvider,
        vector_store: IVectorStore
    ) -> None:
        self._llm = llm_provider
        self._embeddings = embedding_provider
        self._vector_store = vector_store

    async def process_query(
        self,
        query: Query,
        conversation: Conversation | None = None,
        config: RAGConfig | None = None
    ) -> tuple[str, list[RetrievalResult]]:
        """Process a query through the RAG pipeline."""
        config = config or RAGConfig()

        if not query.has_embedding():
            embedding = await self._embeddings.embed_text(query.text)
            query.set_embedding(embedding)

        retrieval_results = await self._vector_store.search(
            query_embedding=query.embedding,
            top_k=config.top_k
        )

        retrieval_results = [
            r for r in retrieval_results
            if r.similarity_score >= config.similarity_threshold
        ]

        context = self._build_context(retrieval_results, config.include_metadata)

        conversation_history = None
        if conversation:
            conversation_history = conversation.get_context_window()

        response = await self._llm.generate_response(
            prompt=query.text,
            context=context,
            conversation_history=conversation_history,
            system_prompt=self.DEFAULT_SYSTEM_PROMPT
        )

        return response, retrieval_results

    async def process_query_stream(
        self,
        query: Query,
        conversation: Conversation | None = None,
        config: RAGConfig | None = None
    ) -> AsyncIterator[tuple[str, list[RetrievalResult] | None]]:
        """Process a query with streaming response."""
        config = config or RAGConfig()

        if not query.has_embedding():
            embedding = await self._embeddings.embed_text(query.text)
            query.set_embedding(embedding)

        retrieval_results = await self._vector_store.search(
            query_embedding=query.embedding,
            top_k=config.top_k
        )

        retrieval_results = [
            r for r in retrieval_results
            if r.similarity_score >= config.similarity_threshold
        ]

        yield "", retrieval_results

        context = self._build_context(retrieval_results, config.include_metadata)

        conversation_history = None
        if conversation:
            conversation_history = conversation.get_context_window()

        async for token in self._llm.generate_response_stream(
            prompt=query.text,
            context=context,
            conversation_history=conversation_history,
            system_prompt=self.DEFAULT_SYSTEM_PROMPT
        ):
            yield token, None

    def _build_context(
        self,
        retrieval_results: list[RetrievalResult],
        include_metadata: bool = True
    ) -> str:
        """Build context string from retrieval results."""
        if not retrieval_results:
            return ""

        context_parts = []
        for i, result in enumerate(retrieval_results, 1):
            if include_metadata:
                context_parts.append(
                    f"[Source {i} (score: {result.similarity_score:.2f})]:\n"
                    f"{result.chunk.content}"
                )
            else:
                context_parts.append(f"[Source {i}]:\n{result.chunk.content}")

        return "\n\n".join(context_parts)
