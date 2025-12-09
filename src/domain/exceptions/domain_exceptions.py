from uuid import UUID


class DomainException(Exception):
    """Base exception for domain layer."""

    pass


class DocumentNotFoundException(DomainException):
    """Raised when a document is not found."""

    def __init__(self, document_id: UUID) -> None:
        super().__init__(f"Document not found: {document_id}")
        self.document_id = document_id


class ChunkNotFoundException(DomainException):
    """Raised when a chunk is not found."""

    def __init__(self, chunk_id: UUID) -> None:
        super().__init__(f"Chunk not found: {chunk_id}")
        self.chunk_id = chunk_id


class ConversationNotFoundException(DomainException):
    """Raised when a conversation is not found."""

    def __init__(self, conversation_id: UUID) -> None:
        super().__init__(f"Conversation not found: {conversation_id}")
        self.conversation_id = conversation_id


class MessageNotFoundException(DomainException):
    """Raised when a message is not found."""

    def __init__(self, message_id: UUID) -> None:
        super().__init__(f"Message not found: {message_id}")
        self.message_id = message_id


class InvalidDocumentException(DomainException):
    """Raised when a document is invalid."""

    pass


class EmbeddingGenerationException(DomainException):
    """Raised when embedding generation fails."""

    pass


class RetrievalException(DomainException):
    """Raised when retrieval from vector store fails."""

    pass


class LLMGenerationException(DomainException):
    """Raised when LLM response generation fails."""

    pass


class ChunkingException(DomainException):
    """Raised when document chunking fails."""

    pass
