from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from src.domain.entities.message import Message


@dataclass
class Conversation:
    """Domain entity representing a conversation."""

    id: UUID
    created_at: datetime
    title: str | None = None
    updated_at: datetime | None = None
    messages: list[Message] = field(default_factory=list)

    def add_message(self, message: Message) -> None:
        """Add a message to the conversation."""
        self.messages.append(message)
        self.updated_at = datetime.utcnow()

    def get_context_window(self, max_messages: int = 10) -> list[Message]:
        """Get the most recent messages for context."""
        return self.messages[-max_messages:]

    @property
    def message_count(self) -> int:
        """Return the number of messages in the conversation."""
        return len(self.messages)
