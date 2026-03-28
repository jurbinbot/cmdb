import uuid
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import String, Text, Enum, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class OwnershipType(str, PyEnum):
    primary = "primary"
    secondary = "secondary"


class Team(Base):
    __tablename__ = "teams"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    slack_channel: Mapped[str | None] = mapped_column(String(255))
    email: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    contacts: Mapped[list["Contact"]] = relationship(back_populates="team", cascade="all, delete-orphan")
    ownerships: Mapped[list["ApplicationOwnership"]] = relationship(back_populates="team", cascade="all, delete-orphan")


class Contact(Base):
    __tablename__ = "contacts"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(50))
    team_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("teams.id"))
    role: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    team: Mapped["Team | None"] = relationship(back_populates="contacts")


class ApplicationOwnership(Base):
    __tablename__ = "application_ownerships"
    __table_args__ = (UniqueConstraint("application_id", "team_id", name="uq_app_team_ownership"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("applications.id"), nullable=False)
    team_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=False)
    ownership_type: Mapped[OwnershipType] = mapped_column(Enum(OwnershipType), nullable=False, default=OwnershipType.primary)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    application: Mapped["Application"] = relationship(back_populates="ownerships")  # type: ignore[name-defined]
    team: Mapped["Team"] = relationship(back_populates="ownerships")
