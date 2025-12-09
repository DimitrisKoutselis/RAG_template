from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.persistence.models.base import Base


class ChunkModel(Base):
    """SQLAlchemy model for chunks."""

    __tablename__ = "chunks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    document_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("documents.id"),
        nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    start_position: Mapped[int] = mapped_column(Integer, nullable=False)
    end_position: Mapped[int] = mapped_column(Integer, nullable=False)
    overlap_previous: Mapped[int] = mapped_column(Integer, default=0)
    overlap_next: Mapped[int] = mapped_column(Integer, default=0)

    document: Mapped["DocumentModel"] = relationship(
        "DocumentModel",
        back_populates="chunks"
    )


from src.infrastructure.persistence.models.document_model import DocumentModel  # noqa: E402, F401
