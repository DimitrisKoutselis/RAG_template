from src.application.dtos.ingestion_dtos import IngestDocumentDTO, IngestionResultDTO
from src.application.interfaces.chunking_strategy import IChunkingStrategy
from src.application.interfaces.embedding_provider import IEmbeddingProvider
from src.application.interfaces.vector_store import IVectorStore
from src.application.mappers.document_mapper import DocumentMapper
from src.domain.exceptions.domain_exceptions import ChunkingException, EmbeddingGenerationException
from src.domain.repositories.chunk_repository import IChunkRepository
from src.domain.repositories.document_repository import IDocumentRepository


class IngestDocumentUseCase:
    """Use case for ingesting a document into the RAG system."""

    def __init__(
        self,
        document_repository: IDocumentRepository,
        chunk_repository: IChunkRepository,
        chunking_strategy: IChunkingStrategy,
        embedding_provider: IEmbeddingProvider,
        vector_store: IVectorStore
    ) -> None:
        self._document_repo = document_repository
        self._chunk_repo = chunk_repository
        self._chunking_strategy = chunking_strategy
        self._embedding_provider = embedding_provider
        self._vector_store = vector_store

    async def execute(self, dto: IngestDocumentDTO) -> IngestionResultDTO:
        """
        Ingest a document into the RAG system.

        Steps:
        1. Create document entity
        2. Save document to repository
        3. Chunk document using strategy
        4. Generate embeddings for chunks
        5. Save chunks to repository
        6. Add chunks to vector store
        """
        try:
            document = DocumentMapper.from_ingest_dto(dto)

            document = await self._document_repo.save(document)

            try:
                chunks = await self._chunking_strategy.chunk_document(document)
            except Exception as e:
                raise ChunkingException(f"Failed to chunk document: {e}") from e

            if not chunks:
                return IngestionResultDTO(
                    document_id=str(document.id),
                    chunk_count=0,
                    success=True
                )

            try:
                chunk_contents = [chunk.content for chunk in chunks]
                embeddings = await self._embedding_provider.embed_texts(chunk_contents)

                for chunk, embedding in zip(chunks, embeddings):
                    chunk.set_embedding(embedding)
            except Exception as e:
                raise EmbeddingGenerationException(
                    f"Failed to generate embeddings: {e}"
                ) from e

            chunks = await self._chunk_repo.save_many(chunks)

            await self._vector_store.add_chunks(chunks)

            return IngestionResultDTO(
                document_id=str(document.id),
                chunk_count=len(chunks),
                success=True
            )

        except (ChunkingException, EmbeddingGenerationException):
            raise
        except Exception as e:
            return IngestionResultDTO(
                document_id="",
                chunk_count=0,
                success=False,
                error_message=str(e)
            )
