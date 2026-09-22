from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from shared.database.database import Base


class KnowledgeRelationship(Base):
    __tablename__ = "knowledge_relationships"

    relationship_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    course_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("courses.course_id"),
        nullable=False,
    )

    source_node_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("knowledge_nodes.node_id"),
        nullable=False,
    )

    target_node_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("knowledge_nodes.node_id"),
        nullable=False,
    )

    relationship_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )