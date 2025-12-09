from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.persistence.models.base import Base


class MessageModel(Base):
    """SQLAlchemy model for messages."""

    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    conversation_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("conversations.id"),
        nullable=False
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    retrieved_chunk_ids: Mapped[list] = mapped_column(JSON, default=list)

    conversation: Mapped["ConversationModel"] = relationship(
        "ConversationModel",
        back_populates="messages"
    )


from src.infrastructure.persistence.models.conversation_model import ConversationModel  # noqa: E402, F401
