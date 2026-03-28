import uuid
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import String, Text, Enum, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class AppType(str, PyEnum):
    service = "service"
    frontend = "frontend"
    backend = "backend"
    library = "library"
    database = "database"
    infrastructure = "infrastructure"


class AppStatus(str, PyEnum):
    active = "active"
    deprecated = "deprecated"
    decommissioned = "decommissioned"
    planned = "planned"


class Tier(str, PyEnum):
    tier1 = "tier1"
    tier2 = "tier2"
    tier3 = "tier3"
    internal = "internal"


class EnvType(str, PyEnum):
    development = "development"
    staging = "staging"
    production = "production"
    dr = "dr"


class Application(Base):
    __tablename__ = "applications"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    app_type: Mapped[AppType] = mapped_column(Enum(AppType), nullable=False, default=AppType.service)
    status: Mapped[AppStatus] = mapped_column(Enum(AppStatus), nullable=False, default=AppStatus.active)
    tier: Mapped[Tier] = mapped_column(Enum(Tier), nullable=False, default=Tier.tier2)
    repo_url: Mapped[str | None] = mapped_column(String(500))
    docs_url: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deployments: Mapped[list["Deployment"]] = relationship(back_populates="application", cascade="all, delete-orphan")
    endpoints: Mapped[list["Endpoint"]] = relationship(back_populates="application", cascade="all, delete-orphan")
    ownerships: Mapped[list["ApplicationOwnership"]] = relationship(back_populates="application", cascade="all, delete-orphan")


class Environment(Base):
    __tablename__ = "environments"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    env_type: Mapped[EnvType] = mapped_column(Enum(EnvType), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Deployment(Base):
    __tablename__ = "deployments"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("applications.id"), nullable=False)
    environment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("environments.id"), nullable=False)
    version: Mapped[str] = mapped_column(String(100), nullable=False)
    deployed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    deployed_by: Mapped[str | None] = mapped_column(String(255))
    ci_cd_url: Mapped[str | None] = mapped_column(String(500))
    notes: Mapped[str | None] = mapped_column(Text)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    application: Mapped["Application"] = relationship(back_populates="deployments")
    environment: Mapped["Environment"] = relationship()
