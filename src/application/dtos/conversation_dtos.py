from dataclasses import dataclass


@dataclass
class CreateConversationDTO:
    """DTO for creating a conversation."""

    title: str | None = None


@dataclass
class ConversationResponseDTO:
    """DTO for conversation response."""

    id: str
    title: str | None
    created_at: str
    message_count: int


@dataclass
class MessageResponseDTO:
    """DTO for message response."""

    id: str
    role: str
    content: str
    created_at: str
    retrieved_chunks: list[str]
