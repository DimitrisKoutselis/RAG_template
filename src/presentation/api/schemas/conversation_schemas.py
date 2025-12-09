from pydantic import BaseModel, Field


class CreateConversationRequest(BaseModel):
    """Request schema for creating a conversation."""

    title: str | None = Field(default=None, description="Optional conversation title")


class ConversationResponse(BaseModel):
    """Response schema for a conversation."""

    id: str
    title: str | None
    created_at: str
    message_count: int


class MessageResponse(BaseModel):
    """Response schema for a message."""

    id: str
    role: str
    content: str
    created_at: str
    retrieved_chunks: list[str]


class ConversationHistoryResponse(BaseModel):
    """Response schema for conversation with history."""

    conversation: ConversationResponse
    messages: list[MessageResponse]


class ConversationListResponse(BaseModel):
    """Response schema for conversation list."""

    conversations: list[ConversationResponse]
    total: int
