from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.domain.entities.document import Document
from src.domain.repositories.document_repository import IDocumentRepository
from src.domain.value_objects.document_metadata import DocumentMetadata
from src.infrastructure.persistence.models.document_model import DocumentModel


class SQLAlchemyDocumentRepository(IDocumentRepository):
    """SQLAlchemy implementation of document repository."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def save(self, document: Document) -> Document:
        """Save a document."""
        async with self._session_factory() as session:
            model = self._to_model(document)
            session.add(model)
            await session.commit()
            await session.refresh(model)
            return self._to_entity(model)

    async def get_by_id(self, document_id: UUID) -> Document | None:
        """Get a document by ID."""
        async with self._session_factory() as session:
            result = await session.execute(
                select(DocumentModel).where(DocumentModel.id == str(document_id))
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model) if model else None

    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> list[Document]:
        """Get all documents with pagination."""
        async with self._session_factory() as session:
            result = await session.execute(
                select(DocumentModel)
                .order_by(DocumentModel.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            models = result.scalars().all()
            return [self._to_entity(m) for m in models]

    async def delete(self, document_id: UUID) -> bool:
        """Delete a document by ID."""
        async with self._session_factory() as session:
            result = await session.execute(
                select(DocumentModel).where(DocumentModel.id == str(document_id))
            )
            model = result.scalar_one_or_none()
            if model:
                await session.delete(model)
                await session.commit()
                return True
            return False

    async def update(self, document: Document) -> Document:
        """Update a document."""
        async with self._session_factory() as session:
            result = await session.execute(
                select(DocumentModel).where(DocumentModel.id == str(document.id))
            )
            model = result.scalar_one_or_none()
            if model:
                model.content = document.content
                model.source = document.metadata.source
                model.file_type = document.metadata.file_type
                model.additional_metadata = document.metadata.additional_metadata
                model.updated_at = document.updated_at
                await session.commit()
                await session.refresh(model)
                return self._to_entity(model)
            raise ValueError(f"Document not found: {document.id}")

    def _to_model(self, entity: Document) -> DocumentModel:
        """Convert domain entity to SQLAlchemy model."""
        return DocumentModel(
            id=str(entity.id),
            content=entity.content,
            source=entity.metadata.source,
            file_type=entity.metadata.file_type,
            additional_metadata=entity.metadata.additional_metadata,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )

    def _to_entity(self, model: DocumentModel) -> Document:
        """Convert SQLAlchemy model to domain entity."""
        return Document(
            id=UUID(model.id),
            content=model.content,
            metadata=DocumentMetadata(
                source=model.source,
                file_type=model.file_type,
                created_at=model.created_at,
                additional_metadata=model.additional_metadata or {}
            ),
            created_at=model.created_at,
            updated_at=model.updated_at
        )
