from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from shared.database.database import Base


class AIChatHistory(Base):
    __tablename__ = "ai_chat_history"

    chat_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.user_id"),
        nullable=False,
    )

    lesson_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("lessons.lesson_id"),
        nullable=False,
    )

    question: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    response: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    timestamp: Mapped[datetime] = mapped_column(
    DateTime,
    default=lambda: datetime.now(timezone.utc),
    nullable=False,
)