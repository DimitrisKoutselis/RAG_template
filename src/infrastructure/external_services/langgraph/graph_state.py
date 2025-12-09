from typing import TypedDict

from src.domain.entities.message import Message
from src.domain.entities.retrieval_result import RetrievalResult
from src.domain.value_objects.embedding import Embedding


class RAGState(TypedDict, total=False):
    """State schema for the RAG graph workflow."""

    query_text: str
    conversation_history: list[Message]

    query_embedding: Embedding | None
    retrieval_results: list[RetrievalResult]
    context: str

    response: str

    top_k: int
    similarity_threshold: float
    include_metadata: bool
