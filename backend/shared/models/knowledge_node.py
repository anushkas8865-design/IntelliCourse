from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from shared.database.database import Base


class KnowledgeNode(Base):
    __tablename__ = "knowledge_nodes"

    node_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    course_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("courses.course_id"),
        nullable=False,
    )

    lesson_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("lessons.lesson_id"),
        nullable=False,
    )

    concept_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )