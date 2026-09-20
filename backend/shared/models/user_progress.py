from uuid import uuid4

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from shared.database.database import Base


class UserProgress(Base):
    __tablename__ = "user_progress"

    progress_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.user_id"),
        nullable=False,
    )

    course_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("courses.course_id"),
        nullable=False,
    )

    completed_lessons: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    quiz_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0,
    )

    progress_percentage: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0,
    )