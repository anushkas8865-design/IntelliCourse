from uuid import uuid4

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from shared.database.database import Base


class Quiz(Base):
    __tablename__ = "quizzes"

    quiz_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
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

    option_a: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    option_b: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    option_c: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    option_d: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    correct_answer: Mapped[str] = mapped_column(
        String(1),
        nullable=False,
    )

    explanation: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )