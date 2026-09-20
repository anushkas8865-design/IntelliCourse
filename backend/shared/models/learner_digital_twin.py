from uuid import uuid4

from sqlalchemy import Float, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from shared.database.database import Base


class LearnerDigitalTwin(Base):
    __tablename__ = "learner_digital_twin"

    twin_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.user_id"),
        nullable=False,
    )

    strengths: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
    )

    weaknesses: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
    )

    learning_speed: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0,
    )

    quiz_accuracy: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0,
    )

    difficulty_level: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )