from collections.abc import AsyncIterator
from uuid import UUID, uuid4

from src.application.dtos.chat_dtos import (
    ChatRequestDTO,
    ChatStreamChunkDTO,
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


class ChatStreamUseCase:
    """Use case for streaming chat responses."""

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

    async def execute(
        self,
        dto: ChatRequestDTO
    ) -> AsyncIterator[ChatStreamChunkDTO]:
        """
        Process a chat message with streaming response.

        Yields streaming chunks as the response is generated.
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

        full_response = ""
        retrieved_chunk_ids: list[UUID] = []

        try:
            async for token, retrieval_results in self._rag_engine.process_query_stream(
                query=query,
                conversation=conversation,
                config=config
            ):
                if retrieval_results is not None:
                    retrieved_chunk_ids = [r.chunk.id for r in retrieval_results]
                    yield ChatStreamChunkDTO(
                        type="retrieval",
                        retrieval_results=RetrievalMapper.to_dtos(retrieval_results)
                    )

                if token:
                    full_response += token
                    yield ChatStreamChunkDTO(
                        type="token",
                        content=token
                    )

            assistant_message = self._conversation_service.create_assistant_message(
                conversation, full_response, retrieved_chunk_ids
            )
            await self._message_repo.save(assistant_message)
            await self._conversation_repo.update(conversation)

            yield ChatStreamChunkDTO(type="done")

        except Exception as e:
            yield ChatStreamChunkDTO(
                type="error",
                content=str(e)
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
