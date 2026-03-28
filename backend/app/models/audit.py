import uuid
from datetime import datetime
from typing import Optional
import enum

from sqlalchemy import String, DateTime, JSON
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from ..database import Base


class AuditAction(str, enum.Enum):
    create = "create"
    update = "update"
    delete = "delete"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ci_type: Mapped[str] = mapped_column(String(100), nullable=False)
    ci_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    action: Mapped[AuditAction] = mapped_column(SAEnum(AuditAction), nullable=False)
    changed_by: Mapped[str] = mapped_column(String(255), nullable=False, default="system")
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    before_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    after_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
