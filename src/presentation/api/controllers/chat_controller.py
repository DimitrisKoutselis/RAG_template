from collections.abc import AsyncIterator

from src.application.dtos.chat_dtos import ChatRequestDTO, RAGConfigDTO
from src.application.use_cases.chat import ChatUseCase
from src.application.use_cases.chat_stream import ChatStreamUseCase
from src.presentation.api.schemas.chat_schemas import (
    ChatRequest,
    ChatResponse,
    RetrievalResultSchema,
    StreamChunk,
)


class ChatController:
    """Controller for chat operations."""

    def __init__(
        self,
        chat_use_case: ChatUseCase,
        chat_stream_use_case: ChatStreamUseCase
    ) -> None:
        self._chat = chat_use_case
        self._chat_stream = chat_stream_use_case

    async def chat(self, request: ChatRequest) -> ChatResponse:
        """Process a chat message."""
        dto = ChatRequestDTO(
            message=request.message,
            conversation_id=request.conversation_id,
            config=self._map_config(request.config)
        )

        result = await self._chat.execute(dto)

        return ChatResponse(
            conversation_id=result.conversation_id,
            message_id=result.message_id,
            response=result.response,
            retrieved_chunks=[
                RetrievalResultSchema(
                    chunk_id=chunk.chunk_id,
                    content=chunk.content,
                    document_id=chunk.document_id,
                    similarity_score=chunk.similarity_score,
                    rank=chunk.rank
                )
                for chunk in result.retrieved_chunks
            ]
        )

    async def chat_stream(
        self,
        request: ChatRequest
    ) -> AsyncIterator[StreamChunk]:
        """Process a chat message with streaming response."""
        dto = ChatRequestDTO(
            message=request.message,
            conversation_id=request.conversation_id,
            config=self._map_config(request.config)
        )

        async for chunk in self._chat_stream.execute(dto):
            if chunk.type == "retrieval" and chunk.retrieval_results:
                yield StreamChunk(
                    type="retrieval",
                    retrieval_results=[
                        RetrievalResultSchema(
                            chunk_id=r.chunk_id,
                            content=r.content,
                            document_id=r.document_id,
                            similarity_score=r.similarity_score,
                            rank=r.rank
                        )
                        for r in chunk.retrieval_results
                    ]
                )
            elif chunk.type == "token":
                yield StreamChunk(type="token", content=chunk.content)
            elif chunk.type == "done":
                yield StreamChunk(type="done")
            elif chunk.type == "error":
                yield StreamChunk(type="error", content=chunk.content)

    def _map_config(self, config) -> RAGConfigDTO | None:
        """Map API config schema to DTO."""
        if config is None:
            return None

        return RAGConfigDTO(
            top_k=config.top_k,
            similarity_threshold=config.similarity_threshold,
            include_metadata=config.include_metadata,
            implementation=config.implementation
        )
