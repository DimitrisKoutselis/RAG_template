from src.application.dtos.conversation_dtos import (
    ConversationResponseDTO,
    MessageResponseDTO,
)
from src.domain.entities.conversation import Conversation
from src.domain.entities.message import Message


class ConversationMapper:
    """Mapper for conversation entities and DTOs."""

    @staticmethod
    def to_response_dto(conversation: Conversation) -> ConversationResponseDTO:
        """Convert a conversation entity to a response DTO."""
        return ConversationResponseDTO(
            id=str(conversation.id),
            title=conversation.title,
            created_at=conversation.created_at.isoformat(),
            message_count=conversation.message_count
        )

    @staticmethod
    def message_to_dto(message: Message) -> MessageResponseDTO:
        """Convert a message entity to a response DTO."""
        return MessageResponseDTO(
            id=str(message.id),
            role=message.role.value,
            content=message.content,
            created_at=message.created_at.isoformat(),
            retrieved_chunks=[str(c) for c in message.retrieved_chunks]
        )

    @staticmethod
    def messages_to_dtos(messages: list[Message]) -> list[MessageResponseDTO]:
        """Convert a list of message entities to response DTOs."""
        return [
            ConversationMapper.message_to_dto(m) for m in messages
        ]
