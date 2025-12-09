from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.domain.entities.chunk import Chunk
from src.domain.repositories.chunk_repository import IChunkRepository
from src.domain.value_objects.chunk_metadata import ChunkMetadata
from src.infrastructure.persistence.models.chunk_model import ChunkModel


class SQLAlchemyChunkRepository(IChunkRepository):
    """SQLAlchemy implementation of chunk repository."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def save(self, chunk: Chunk) -> Chunk:
        """Save a chunk."""
        async with self._session_factory() as session:
            model = self._to_model(chunk)
            session.add(model)
            await session.commit()
            await session.refresh(model)
            return self._to_entity(model, chunk.embedding)

    async def save_many(self, chunks: list[Chunk]) -> list[Chunk]:
        """Save multiple chunks."""
        async with self._session_factory() as session:
            models = [self._to_model(chunk) for chunk in chunks]
            session.add_all(models)
            await session.commit()

            for model in models:
                await session.refresh(model)

            return [
                self._to_entity(model, chunk.embedding)
                for model, chunk in zip(models, chunks)
            ]

    async def get_by_id(self, chunk_id: UUID) -> Chunk | None:
        """Get a chunk by ID."""
        async with self._session_factory() as session:
            result = await session.execute(
                select(ChunkModel).where(ChunkModel.id == str(chunk_id))
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model, None) if model else None

    async def get_by_document_id(self, document_id: UUID) -> list[Chunk]:
        """Get all chunks for a document."""
        async with self._session_factory() as session:
            result = await session.execute(
                select(ChunkModel)
                .where(ChunkModel.document_id == str(document_id))
                .order_by(ChunkModel.chunk_index)
            )
            models = result.scalars().all()
            return [self._to_entity(m, None) for m in models]

    async def delete_by_document_id(self, document_id: UUID) -> int:
        """Delete all chunks for a document."""
        async with self._session_factory() as session:
            result = await session.execute(
                delete(ChunkModel).where(
                    ChunkModel.document_id == str(document_id)
                )
            )
            await session.commit()
            return result.rowcount

    def _to_model(self, entity: Chunk) -> ChunkModel:
        """Convert domain entity to SQLAlchemy model."""
        return ChunkModel(
            id=str(entity.id),
            document_id=str(entity.document_id),
            content=entity.content,
            chunk_index=entity.metadata.chunk_index,
            start_position=entity.metadata.start_position,
            end_position=entity.metadata.end_position,
            overlap_previous=entity.metadata.overlap_with_previous,
            overlap_next=entity.metadata.overlap_with_next
        )

    def _to_entity(
        self,
        model: ChunkModel,
        embedding: "Embedding | None"  # noqa: F821
    ) -> Chunk:
        """Convert SQLAlchemy model to domain entity."""
        from src.domain.value_objects.embedding import Embedding  # noqa: F811

        return Chunk(
            id=UUID(model.id),
            document_id=UUID(model.document_id),
            content=model.content,
            metadata=ChunkMetadata(
                chunk_index=model.chunk_index,
                start_position=model.start_position,
                end_position=model.end_position,
                overlap_with_previous=model.overlap_previous,
                overlap_with_next=model.overlap_next
            ),
            embedding=embedding
        )
