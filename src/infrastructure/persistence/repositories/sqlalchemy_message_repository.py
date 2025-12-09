from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.domain.entities.message import Message
from src.domain.repositories.message_repository import IMessageRepository
from src.domain.value_objects.message_role import MessageRole
from src.infrastructure.persistence.models.message_model import MessageModel


class SQLAlchemyMessageRepository(IMessageRepository):
    """SQLAlchemy implementation of message repository."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def save(self, message: Message) -> Message:
        """Save a message."""
        async with self._session_factory() as session:
            model = self._to_model(message)
            session.add(model)
            await session.commit()
            await session.refresh(model)
            return self._to_entity(model)

    async def get_by_id(self, message_id: UUID) -> Message | None:
        """Get a message by ID."""
        async with self._session_factory() as session:
            result = await session.execute(
                select(MessageModel).where(MessageModel.id == str(message_id))
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model) if model else None

    async def get_by_conversation_id(
        self,
        conversation_id: UUID,
        limit: int = 100
    ) -> list[Message]:
        """Get all messages for a conversation."""
        async with self._session_factory() as session:
            result = await session.execute(
                select(MessageModel)
                .where(MessageModel.conversation_id == str(conversation_id))
                .order_by(MessageModel.created_at)
                .limit(limit)
            )
            models = result.scalars().all()
            return [self._to_entity(m) for m in models]

    def _to_model(self, entity: Message) -> MessageModel:
        """Convert domain entity to SQLAlchemy model."""
        return MessageModel(
            id=str(entity.id),
            conversation_id=str(entity.conversation_id),
            role=entity.role.value,
            content=entity.content,
            created_at=entity.created_at,
            retrieved_chunk_ids=[str(c) for c in entity.retrieved_chunks]
        )

    def _to_entity(self, model: MessageModel) -> Message:
        """Convert SQLAlchemy model to domain entity."""
        return Message(
            id=UUID(model.id),
            conversation_id=UUID(model.conversation_id),
            role=MessageRole(model.role),
            content=model.content,
            created_at=model.created_at,
            retrieved_chunks=[UUID(c) for c in (model.retrieved_chunk_ids or [])]
        )
