from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from shared.database.database import Base


class Course(Base):
    __tablename__ = "courses"

    course_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.user_id"),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    difficulty: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    duration: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    learning_outcomes: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
    DateTime,
    default=lambda: datetime.now(timezone.utc),
    nullable=False,
)