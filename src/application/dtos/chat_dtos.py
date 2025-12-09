from dataclasses import dataclass, field
from typing import Literal


@dataclass
class RAGConfigDTO:
    """DTO for RAG configuration."""

    top_k: int = 5
    similarity_threshold: float = 0.7
    include_metadata: bool = True
    implementation: Literal["langchain", "langgraph"] = "langchain"


@dataclass
class ChatRequestDTO:
    """DTO for chat request."""

    message: str
    conversation_id: str | None = None
    config: RAGConfigDTO | None = None


@dataclass
class RetrievalResultDTO:
    """DTO for retrieval result."""

    chunk_id: str
    content: str
    document_id: str
    similarity_score: float
    rank: int


@dataclass
class ChatResponseDTO:
    """DTO for chat response."""

    conversation_id: str
    message_id: str
    response: str
    retrieved_chunks: list[RetrievalResultDTO] = field(default_factory=list)


@dataclass
class ChatStreamChunkDTO:
    """DTO for streaming chat chunk."""

    type: Literal["token", "retrieval", "done", "error"]
    content: str | None = None
    retrieval_results: list[RetrievalResultDTO] | None = None
