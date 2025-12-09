from uuid import UUID

from src.application.dtos.conversation_dtos import (
    ConversationResponseDTO,
    MessageResponseDTO,
)
from src.application.mappers.conversation_mapper import ConversationMapper
from src.domain.exceptions.domain_exceptions import ConversationNotFoundException
from src.domain.repositories.conversation_repository import IConversationRepository
from src.domain.repositories.message_repository import IMessageRepository


class GetConversationHistoryUseCase:
    """Use case for retrieving conversation history with messages."""

    def __init__(
        self,
        conversation_repository: IConversationRepository,
        message_repository: IMessageRepository
    ) -> None:
        self._conversation_repo = conversation_repository
        self._message_repo = message_repository

    async def execute(
        self,
        conversation_id: str
    ) -> tuple[ConversationResponseDTO, list[MessageResponseDTO]]:
        """Get conversation with its message history."""
        conv_uuid = UUID(conversation_id)

        conversation = await self._conversation_repo.get_by_id(conv_uuid)
        if not conversation:
            raise ConversationNotFoundException(conv_uuid)

        messages = await self._message_repo.get_by_conversation_id(conv_uuid)

        return (
            ConversationMapper.to_response_dto(conversation),
            ConversationMapper.messages_to_dtos(messages)
        )
