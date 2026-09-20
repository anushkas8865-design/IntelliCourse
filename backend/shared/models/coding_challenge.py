from uuid import uuid4

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from shared.database.database import Base


class CodingChallenge(Base):
    __tablename__ = "coding_challenges"

    challenge_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    lesson_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("lessons.lesson_id"),
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