from uuid import uuid4

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from shared.database.database import Base


class LessonVideo(Base):
    __tablename__ = "lesson_videos"

    video_id: Mapped[str] = mapped_column(
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

    youtube_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )