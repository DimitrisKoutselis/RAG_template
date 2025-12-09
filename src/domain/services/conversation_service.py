from datetime import datetime
from uuid import UUID, uuid4

from src.domain.entities.conversation import Conversation
from src.domain.entities.message import Message
from src.domain.value_objects.message_role import MessageRole


class ConversationService:
    """Domain service for conversation-related business logic."""

    def create_conversation(self, title: str | None = None) -> Conversation:
        """Create a new conversation."""
        return Conversation(
            id=uuid4(),
            title=title,
            created_at=datetime.utcnow()
        )

    def create_user_message(
        self,
        conversation: Conversation,
        content: str
    ) -> Message:
        """Create a user message and add it to the conversation."""
        message = Message(
            id=uuid4(),
            conversation_id=conversation.id,
            role=MessageRole.USER,
            content=content,
            created_at=datetime.utcnow()
        )
        conversation.add_message(message)
        return message

    def create_assistant_message(
        self,
        conversation: Conversation,
        content: str,
        retrieved_chunk_ids: list[UUID] | None = None
    ) -> Message:
        """Create an assistant message and add it to the conversation."""
        message = Message(
            id=uuid4(),
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content=content,
            created_at=datetime.utcnow(),
            retrieved_chunks=retrieved_chunk_ids or []
        )
        conversation.add_message(message)
        return message

    def create_system_message(
        self,
        conversation: Conversation,
        content: str
    ) -> Message:
        """Create a system message and add it to the conversation."""
        message = Message(
            id=uuid4(),
            conversation_id=conversation.id,
            role=MessageRole.SYSTEM,
            content=content,
            created_at=datetime.utcnow()
        )
        conversation.add_message(message)
        return message
