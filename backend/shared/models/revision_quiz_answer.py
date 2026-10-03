from uuid import uuid4

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from shared.database.database import Base


class RevisionQuizAnswer(Base):
    __tablename__ = "revision_quiz_answers"

    answer_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    attempt_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("revision_quiz_attempts.attempt_id"),
        nullable=False,
    )

    quiz_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("quizzes.quiz_id"),
        nullable=False,
    )

    selected_answer: Mapped[str] = mapped_column(
        String(1),
        nullable=False,
    )