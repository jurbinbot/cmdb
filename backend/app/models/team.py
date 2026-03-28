import uuid
from datetime import datetime
from typing import Optional
import enum

from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from ..database import Base


class OwnershipType(str, enum.Enum):
    primary = "primary"
    secondary = "secondary"


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    slack_channel: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    contacts: Mapped[list["Contact"]] = relationship("Contact", back_populates="team")
    ownerships: Mapped[list["ApplicationOwnership"]] = relationship("ApplicationOwnership", back_populates="team")


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    team_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True)
    role: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    team: Mapped[Optional["Team"]] = relationship("Team", back_populates="contacts")


class ApplicationOwnership(Base):
    __tablename__ = "application_ownerships"

    application_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("applications.id"), primary_key=True)
    team_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("teams.id"), primary_key=True)
    ownership_type: Mapped[OwnershipType] = mapped_column(SAEnum(OwnershipType), nullable=False, default=OwnershipType.primary)

    application: Mapped["Application"] = relationship("Application", back_populates="ownerships")
    team: Mapped["Team"] = relationship("Team", back_populates="ownerships")
