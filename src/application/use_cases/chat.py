from uuid import UUID, uuid4

from src.application.dtos.chat_dtos import (
    ChatRequestDTO,
    ChatResponseDTO,
    RAGConfigDTO,
)
from src.application.interfaces.embedding_provider import IEmbeddingProvider
from src.application.interfaces.rag_engine import IRAGEngine
from src.application.mappers.retrieval_mapper import RetrievalMapper
from src.domain.entities.query import Query
from src.domain.exceptions.domain_exceptions import ConversationNotFoundException
from src.domain.repositories.conversation_repository import IConversationRepository
from src.domain.repositories.message_repository import IMessageRepository
from src.domain.services.conversation_service import ConversationService
from src.domain.value_objects.rag_config import RAGConfig


class ChatUseCase:
    """Use case for processing a chat message in the RAG system."""

    def __init__(
        self,
        conversation_repository: IConversationRepository,
        message_repository: IMessageRepository,
        conversation_service: ConversationService,
        rag_engine: IRAGEngine,
        embedding_provider: IEmbeddingProvider
    ) -> None:
        self._conversation_repo = conversation_repository
        self._message_repo = message_repository
        self._conversation_service = conversation_service
        self._rag_engine = rag_engine
        self._embedding_provider = embedding_provider

    async def execute(self, dto: ChatRequestDTO) -> ChatResponseDTO:
        """
        Process a chat message through the RAG pipeline.

        Steps:
        1. Get or create conversation
        2. Create user message
        3. Create query entity with embedding
        4. Process through RAG engine
        5. Create assistant message
        6. Save messages and return response
        """
        if dto.conversation_id:
            conversation = await self._conversation_repo.get_by_id(
                UUID(dto.conversation_id)
            )
            if not conversation:
                raise ConversationNotFoundException(UUID(dto.conversation_id))
        else:
            conversation = self._conversation_service.create_conversation()
            conversation = await self._conversation_repo.save(conversation)

        user_message = self._conversation_service.create_user_message(
            conversation, dto.message
        )
        await self._message_repo.save(user_message)

        query_embedding = await self._embedding_provider.embed_text(dto.message)
        query = Query(
            id=uuid4(),
            text=dto.message,
            conversation_id=conversation.id,
            embedding=query_embedding
        )

        config = self._build_config(dto.config)

        response_text, retrieval_results = await self._rag_engine.process_query(
            query=query,
            conversation=conversation,
            config=config
        )

        retrieved_chunk_ids = [r.chunk.id for r in retrieval_results]
        assistant_message = self._conversation_service.create_assistant_message(
            conversation, response_text, retrieved_chunk_ids
        )
        await self._message_repo.save(assistant_message)

        await self._conversation_repo.update(conversation)

        return ChatResponseDTO(
            conversation_id=str(conversation.id),
            message_id=str(assistant_message.id),
            response=response_text,
            retrieved_chunks=RetrievalMapper.to_dtos(retrieval_results)
        )

    def _build_config(self, dto_config: RAGConfigDTO | None) -> RAGConfig:
        """Build RAG config from DTO."""
        if dto_config is None:
            return RAGConfig()

        return RAGConfig(
            top_k=dto_config.top_k,
            similarity_threshold=dto_config.similarity_threshold,
            include_metadata=dto_config.include_metadata,
            implementation=dto_config.implementation
        )
