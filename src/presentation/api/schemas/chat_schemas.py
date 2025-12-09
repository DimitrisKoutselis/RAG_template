from typing import Literal

from pydantic import BaseModel, Field


class RAGConfigSchema(BaseModel):
    """Schema for RAG configuration."""

    top_k: int = Field(default=5, ge=1, le=20, description="Number of chunks to retrieve")
    similarity_threshold: float = Field(
        default=0.7, ge=0.0, le=1.0,
        description="Minimum similarity score for retrieved chunks"
    )
    include_metadata: bool = Field(default=True, description="Include metadata in context")
    implementation: Literal["langchain", "langgraph"] = Field(
        default="langchain",
        description="RAG implementation to use"
    )


class ChatRequest(BaseModel):
    """Request schema for chat."""

    message: str = Field(..., min_length=1, description="User message")
    conversation_id: str | None = Field(
        default=None,
        description="Existing conversation ID (creates new if not provided)"
    )
    config: RAGConfigSchema | None = Field(default=None, description="RAG configuration")


class RetrievalResultSchema(BaseModel):
    """Schema for retrieval result."""

    chunk_id: str
    content: str
    document_id: str
    similarity_score: float
    rank: int


class ChatResponse(BaseModel):
    """Response schema for chat."""

    conversation_id: str
    message_id: str
    response: str
    retrieved_chunks: list[RetrievalResultSchema]


class StreamChunk(BaseModel):
    """Schema for streaming response chunk."""

    type: Literal["token", "retrieval", "done", "error"]
    content: str | None = None
    retrieval_results: list[RetrievalResultSchema] | None = None
