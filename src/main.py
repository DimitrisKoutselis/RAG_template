from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.application.interfaces.chunking_strategy import IChunkingStrategy
from src.application.interfaces.rag_engine import IRAGEngine
from src.application.use_cases.chat import ChatUseCase
from src.application.use_cases.chat_stream import ChatStreamUseCase
from src.application.use_cases.delete_document import DeleteDocumentUseCase
from src.application.use_cases.get_conversation_history import GetConversationHistoryUseCase
from src.application.use_cases.get_conversations import GetConversationsUseCase
from src.application.use_cases.get_documents import GetDocumentsUseCase
from src.application.use_cases.ingest_document import IngestDocumentUseCase
from src.domain.services.conversation_service import ConversationService
from src.infrastructure.configuration.settings import Settings, get_settings
from src.infrastructure.external_services.langchain.langchain_embedding_provider import (
    LangChainEmbeddingProvider,
)
from src.infrastructure.external_services.langchain.langchain_llm_provider import (
    LangChainLLMProvider,
)
from src.infrastructure.external_services.langchain.langchain_rag_engine import (
    LangChainRAGEngine,
)
from src.infrastructure.external_services.langgraph.langgraph_rag_engine import (
    LangGraphRAGEngine,
)
from src.infrastructure.external_services.vector_stores.chroma_vector_store import (
    ChromaVectorStore,
)
from src.infrastructure.logging.logger import get_logger, setup_logging
from src.infrastructure.persistence.database import (
    create_engine,
    create_session_factory,
    create_tables,
)
from src.infrastructure.persistence.repositories.sqlalchemy_chunk_repository import (
    SQLAlchemyChunkRepository,
)
from src.infrastructure.persistence.repositories.sqlalchemy_conversation_repository import (
    SQLAlchemyConversationRepository,
)
from src.infrastructure.persistence.repositories.sqlalchemy_document_repository import (
    SQLAlchemyDocumentRepository,
)
from src.infrastructure.persistence.repositories.sqlalchemy_message_repository import (
    SQLAlchemyMessageRepository,
)
from src.presentation.api.controllers.chat_controller import ChatController
from src.presentation.api.controllers.conversation_controller import ConversationController
from src.presentation.api.controllers.document_controller import DocumentController
from src.presentation.api.middleware.error_handler import ErrorHandlerMiddleware
from src.presentation.api.middleware.logging_middleware import LoggingMiddleware
from src.presentation.api.routes import (
    chat_routes,
    conversation_routes,
    document_routes,
    health_routes,
    websocket_routes,
)


class Container:
    """
    Dependency injection container.

    This container manages all application dependencies and their lifecycles.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.logger = setup_logging(settings)

        self._engine = create_engine(settings.database_url)
        self._session_factory = create_session_factory(self._engine)

        self.document_repository = SQLAlchemyDocumentRepository(self._session_factory)
        self.chunk_repository = SQLAlchemyChunkRepository(self._session_factory)
        self.conversation_repository = SQLAlchemyConversationRepository(self._session_factory)
        self.message_repository = SQLAlchemyMessageRepository(self._session_factory)

        self.llm_provider = LangChainLLMProvider(settings)
        self.embedding_provider = LangChainEmbeddingProvider(settings)
        self.vector_store = ChromaVectorStore(settings)

        self._langchain_engine = LangChainRAGEngine(
            self.llm_provider,
            self.embedding_provider,
            self.vector_store
        )
        self._langgraph_engine = LangGraphRAGEngine(
            self.llm_provider,
            self.embedding_provider,
            self.vector_store
        )

        self.conversation_service = ConversationService()

        self._chunking_strategy: IChunkingStrategy | None = None

    def set_chunking_strategy(self, strategy: IChunkingStrategy) -> None:
        """Set the chunking strategy for document ingestion."""
        self._chunking_strategy = strategy

    def get_rag_engine(self, implementation: str | None = None) -> IRAGEngine:
        """Get RAG engine by implementation type."""
        impl = implementation or self.settings.rag_implementation
        if impl == "langgraph":
            return self._langgraph_engine
        return self._langchain_engine

    @property
    def ingest_document_use_case(self) -> IngestDocumentUseCase:
        """Get ingest document use case."""
        if self._chunking_strategy is None:
            raise RuntimeError(
                "Chunking strategy not configured. "
                "Call container.set_chunking_strategy() with your implementation."
            )
        return IngestDocumentUseCase(
            document_repository=self.document_repository,
            chunk_repository=self.chunk_repository,
            chunking_strategy=self._chunking_strategy,
            embedding_provider=self.embedding_provider,
            vector_store=self.vector_store
        )

    @property
    def chat_use_case(self) -> ChatUseCase:
        """Get chat use case."""
        return ChatUseCase(
            conversation_repository=self.conversation_repository,
            message_repository=self.message_repository,
            conversation_service=self.conversation_service,
            rag_engine=self.get_rag_engine(),
            embedding_provider=self.embedding_provider
        )

    @property
    def chat_stream_use_case(self) -> ChatStreamUseCase:
        """Get streaming chat use case."""
        return ChatStreamUseCase(
            conversation_repository=self.conversation_repository,
            message_repository=self.message_repository,
            conversation_service=self.conversation_service,
            rag_engine=self.get_rag_engine(),
            embedding_provider=self.embedding_provider
        )

    @property
    def get_conversations_use_case(self) -> GetConversationsUseCase:
        """Get conversations use case."""
        return GetConversationsUseCase(
            conversation_repository=self.conversation_repository
        )

    @property
    def get_conversation_history_use_case(self) -> GetConversationHistoryUseCase:
        """Get conversation history use case."""
        return GetConversationHistoryUseCase(
            conversation_repository=self.conversation_repository,
            message_repository=self.message_repository
        )

    @property
    def delete_document_use_case(self) -> DeleteDocumentUseCase:
        """Get delete document use case."""
        return DeleteDocumentUseCase(
            document_repository=self.document_repository,
            chunk_repository=self.chunk_repository,
            vector_store=self.vector_store
        )

    @property
    def get_documents_use_case(self) -> GetDocumentsUseCase:
        """Get documents use case."""
        return GetDocumentsUseCase(
            document_repository=self.document_repository,
            chunk_repository=self.chunk_repository
        )

    @property
    def document_controller(self) -> DocumentController:
        """Get document controller."""
        return DocumentController(
            ingest_use_case=self.ingest_document_use_case,
            delete_use_case=self.delete_document_use_case,
            get_documents_use_case=self.get_documents_use_case
        )

    @property
    def chat_controller(self) -> ChatController:
        """Get chat controller."""
        return ChatController(
            chat_use_case=self.chat_use_case,
            chat_stream_use_case=self.chat_stream_use_case
        )

    @property
    def conversation_controller(self) -> ConversationController:
        """Get conversation controller."""
        return ConversationController(
            get_conversations_use_case=self.get_conversations_use_case,
            get_history_use_case=self.get_conversation_history_use_case
        )


_container: Container | None = None


def get_container() -> Container:
    """Get the global container instance."""
    if _container is None:
        raise RuntimeError("Container not initialized")
    return _container


def get_document_controller() -> DocumentController:
    """FastAPI dependency for document controller."""
    return get_container().document_controller


def get_chat_controller() -> ChatController:
    """FastAPI dependency for chat controller."""
    return get_container().chat_controller


def get_conversation_controller() -> ConversationController:
    """FastAPI dependency for conversation controller."""
    return get_container().conversation_controller


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global _container

    settings = get_settings()
    _container = Container(settings)
    logger = get_logger()
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")

    await create_tables(_container._engine)
    logger.info("Database tables created")

    app.state.chat_controller = _container.chat_controller

    yield

    logger.info("Shutting down...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="RAG Template API with Clean Architecture",
        lifespan=lifespan
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(ErrorHandlerMiddleware)
    app.add_middleware(LoggingMiddleware)

    document_routes.get_document_controller = get_document_controller
    chat_routes.get_chat_controller = get_chat_controller
    conversation_routes.get_conversation_controller = get_conversation_controller

    app.include_router(health_routes.router)
    app.include_router(document_routes.router, prefix="/api/v1")
    app.include_router(chat_routes.router, prefix="/api/v1")
    app.include_router(conversation_routes.router, prefix="/api/v1")
    app.include_router(websocket_routes.router)

    return app


def main():
    """Application entry point."""
    import uvicorn

    settings = get_settings()
    app = create_app()

    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )


if __name__ == "__main__":
    main()
