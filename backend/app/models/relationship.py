import uuid
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import String, Text, Enum, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class RelationshipType(str, PyEnum):
    depends_on = "depends_on"
    hosted_on = "hosted_on"
    connects_to = "connects_to"
    owned_by = "owned_by"
    deployed_on = "deployed_on"
    uses_database = "uses_database"
    exposes_endpoint = "exposes_endpoint"


class CIRelationship(Base):
    __tablename__ = "ci_relationships"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_ci_type: Mapped[str] = mapped_column(String(100), nullable=False)
    source_ci_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    target_ci_type: Mapped[str] = mapped_column(String(100), nullable=False)
    target_ci_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    relationship_type: Mapped[RelationshipType] = mapped_column(Enum(RelationshipType), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
