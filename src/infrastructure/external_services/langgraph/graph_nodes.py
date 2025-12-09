from src.application.interfaces.embedding_provider import IEmbeddingProvider
from src.application.interfaces.llm_provider import ILLMProvider
from src.application.interfaces.vector_store import IVectorStore
from src.infrastructure.external_services.langgraph.graph_state import RAGState


class GraphNodes:
    """Collection of reusable graph nodes for RAG workflows."""

    DEFAULT_SYSTEM_PROMPT = """You are a helpful assistant that answers questions based on the provided context.
If the context doesn't contain relevant information to answer the question, say so.
Always be accurate and cite specific information from the context when possible."""

    def __init__(
        self,
        embedding_provider: IEmbeddingProvider,
        vector_store: IVectorStore,
        llm_provider: ILLMProvider
    ) -> None:
        self._embeddings = embedding_provider
        self._vector_store = vector_store
        self._llm = llm_provider

    async def embed_query(self, state: RAGState) -> dict:
        """Node: Generate embedding for the query."""
        query_text = state["query_text"]
        embedding = await self._embeddings.embed_text(query_text)
        return {"query_embedding": embedding}

    async def retrieve_chunks(self, state: RAGState) -> dict:
        """Node: Retrieve relevant chunks from vector store."""
        query_embedding = state["query_embedding"]
        top_k = state.get("top_k", 5)
        similarity_threshold = state.get("similarity_threshold", 0.7)

        results = await self._vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k
        )

        filtered_results = [
            r for r in results
            if r.similarity_score >= similarity_threshold
        ]

        return {"retrieval_results": filtered_results}

    async def build_context(self, state: RAGState) -> dict:
        """Node: Build context string from retrieval results."""
        retrieval_results = state.get("retrieval_results", [])
        include_metadata = state.get("include_metadata", True)

        if not retrieval_results:
            return {"context": ""}

        context_parts = []
        for i, result in enumerate(retrieval_results, 1):
            if include_metadata:
                context_parts.append(
                    f"[Source {i} (score: {result.similarity_score:.2f})]:\n"
                    f"{result.chunk.content}"
                )
            else:
                context_parts.append(f"[Source {i}]:\n{result.chunk.content}")

        return {"context": "\n\n".join(context_parts)}

    async def generate_response(self, state: RAGState) -> dict:
        """Node: Generate LLM response."""
        query_text = state["query_text"]
        context = state.get("context", "")
        conversation_history = state.get("conversation_history")

        response = await self._llm.generate_response(
            prompt=query_text,
            context=context,
            conversation_history=conversation_history,
            system_prompt=self.DEFAULT_SYSTEM_PROMPT
        )

        return {"response": response}

    def should_retrieve(self, state: RAGState) -> str:
        """Conditional edge: Determine if retrieval is needed."""
        return "retrieve"
