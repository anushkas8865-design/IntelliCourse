from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from shared.database.database import Base


class ConceptRetentionState(Base):
    __tablename__ = "concept_retention_state"

    retention_state_id: Mapped[str] = mapped_column(
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

    knowledge_node_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("knowledge_nodes.node_id"),
        nullable=False,
    )

    stability: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    next_review_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )