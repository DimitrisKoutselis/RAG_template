from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload

from src.domain.entities.conversation import Conversation
from src.domain.entities.message import Message
from src.domain.repositories.conversation_repository import IConversationRepository
from src.domain.value_objects.message_role import MessageRole
from src.infrastructure.persistence.models.conversation_model import ConversationModel
from src.infrastructure.persistence.models.message_model import MessageModel


class SQLAlchemyConversationRepository(IConversationRepository):
    """SQLAlchemy implementation of conversation repository."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def save(self, conversation: Conversation) -> Conversation:
        """Save a conversation."""
        async with self._session_factory() as session:
            model = self._to_model(conversation)
            session.add(model)
            await session.commit()
            await session.refresh(model, ["messages"])
            return self._to_entity(model)

    async def get_by_id(self, conversation_id: UUID) -> Conversation | None:
        """Get a conversation by ID."""
        async with self._session_factory() as session:
            result = await session.execute(
                select(ConversationModel)
                .options(selectinload(ConversationModel.messages))
                .where(ConversationModel.id == str(conversation_id))
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model) if model else None

    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> list[Conversation]:
        """Get all conversations with pagination."""
        async with self._session_factory() as session:
            result = await session.execute(
                select(ConversationModel)
                .options(selectinload(ConversationModel.messages))
                .order_by(ConversationModel.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            models = result.scalars().all()
            return [self._to_entity(m) for m in models]

    async def update(self, conversation: Conversation) -> Conversation:
        """Update a conversation."""
        async with self._session_factory() as session:
            result = await session.execute(
                select(ConversationModel)
                .options(selectinload(ConversationModel.messages))
                .where(ConversationModel.id == str(conversation.id))
            )
            model = result.scalar_one_or_none()
            if model:
                model.title = conversation.title
                model.updated_at = conversation.updated_at
                await session.commit()
                await session.refresh(model, ["messages"])
                return self._to_entity(model)
            raise ValueError(f"Conversation not found: {conversation.id}")

    async def delete(self, conversation_id: UUID) -> bool:
        """Delete a conversation by ID."""
        async with self._session_factory() as session:
            result = await session.execute(
                select(ConversationModel).where(
                    ConversationModel.id == str(conversation_id)
                )
            )
            model = result.scalar_one_or_none()
            if model:
                await session.delete(model)
                await session.commit()
                return True
            return False

    def _to_model(self, entity: Conversation) -> ConversationModel:
        """Convert domain entity to SQLAlchemy model."""
        return ConversationModel(
            id=str(entity.id),
            title=entity.title,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )

    def _to_entity(self, model: ConversationModel) -> Conversation:
        """Convert SQLAlchemy model to domain entity."""
        messages = [
            Message(
                id=UUID(m.id),
                conversation_id=UUID(m.conversation_id),
                role=MessageRole(m.role),
                content=m.content,
                created_at=m.created_at,
                retrieved_chunks=[UUID(c) for c in (m.retrieved_chunk_ids or [])]
            )
            for m in model.messages
        ] if model.messages else []

        return Conversation(
            id=UUID(model.id),
            title=model.title,
            created_at=model.created_at,
            updated_at=model.updated_at,
            messages=messages
        )
