from uuid import uuid4

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from shared.database.database import Base


class Lesson(Base):
    __tablename__ = "lessons"

    lesson_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    course_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("courses.course_id"),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    sequence_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )