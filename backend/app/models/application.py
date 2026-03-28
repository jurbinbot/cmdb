import uuid
from datetime import datetime
from typing import Optional
import enum

from sqlalchemy import String, Text, Enum as SAEnum, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from ..database import Base


class AppType(str, enum.Enum):
    service = "service"
    frontend = "frontend"
    backend = "backend"
    library = "library"
    database = "database"
    infrastructure = "infrastructure"


class AppStatus(str, enum.Enum):
    active = "active"
    deprecated = "deprecated"
    decommissioned = "decommissioned"
    planned = "planned"


class AppTier(str, enum.Enum):
    tier1 = "tier1"
    tier2 = "tier2"
    tier3 = "tier3"
    internal = "internal"


class EnvType(str, enum.Enum):
    development = "development"
    staging = "staging"
    production = "production"
    dr = "dr"


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    app_type: Mapped[AppType] = mapped_column(SAEnum(AppType), nullable=False)
    status: Mapped[AppStatus] = mapped_column(SAEnum(AppStatus), nullable=False, default=AppStatus.active)
    tier: Mapped[AppTier] = mapped_column(SAEnum(AppTier), nullable=False, default=AppTier.tier3)
    repo_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    docs_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    deployments: Mapped[list["Deployment"]] = relationship("Deployment", back_populates="application", cascade="all, delete-orphan")
    endpoints: Mapped[list["Endpoint"]] = relationship("Endpoint", back_populates="application", cascade="all, delete-orphan")
    ownerships: Mapped[list["ApplicationOwnership"]] = relationship("ApplicationOwnership", back_populates="application", cascade="all, delete-orphan")


class Environment(Base):
    __tablename__ = "environments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    env_type: Mapped[EnvType] = mapped_column(SAEnum(EnvType), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    deployments: Mapped[list["Deployment"]] = relationship("Deployment", back_populates="environment")
    servers: Mapped[list["Server"]] = relationship("Server", back_populates="environment")
    database_instances: Mapped[list["DatabaseInstance"]] = relationship("DatabaseInstance", back_populates="environment")
    endpoints: Mapped[list["Endpoint"]] = relationship("Endpoint", back_populates="environment")


class Deployment(Base):
    __tablename__ = "deployments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("applications.id"), nullable=False)
    environment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("environments.id"), nullable=False)
    version: Mapped[str] = mapped_column(String(255), nullable=False)
    deployed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    deployed_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    ci_cd_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    application: Mapped["Application"] = relationship("Application", back_populates="deployments")
    environment: Mapped["Environment"] = relationship("Environment", back_populates="deployments")
