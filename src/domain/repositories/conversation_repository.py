from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.conversation import Conversation


class IConversationRepository(ABC):
    """Interface for conversation persistence operations."""

    @abstractmethod
    async def save(self, conversation: Conversation) -> Conversation:
        """Save a conversation."""
        ...

    @abstractmethod
    async def get_by_id(self, conversation_id: UUID) -> Conversation | None:
        """Get a conversation by ID."""
        ...

    @abstractmethod
    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> list[Conversation]:
        """Get all conversations with pagination."""
        ...

    @abstractmethod
    async def update(self, conversation: Conversation) -> Conversation:
        """Update a conversation."""
        ...

    @abstractmethod
    async def delete(self, conversation_id: UUID) -> bool:
        """Delete a conversation by ID. Returns True if deleted."""
        ...
