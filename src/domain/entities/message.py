from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from src.domain.value_objects.message_role import MessageRole


@dataclass
class Message:
    """Domain entity representing a message in a conversation."""

    id: UUID
    conversation_id: UUID
    role: MessageRole
    content: str
    created_at: datetime
    retrieved_chunks: list[UUID] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.content:
            raise ValueError("Message content cannot be empty")
