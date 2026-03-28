import uuid
from datetime import datetime
from typing import Optional
import enum

from sqlalchemy import String, Integer, ForeignKey, DateTime, Boolean
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from ..database import Base


class ServerType(str, enum.Enum):
    physical = "physical"
    virtual = "virtual"
    container = "container"
    cloud = "cloud"


class ServerStatus(str, enum.Enum):
    active = "active"
    decommissioned = "decommissioned"
    maintenance = "maintenance"


class DbType(str, enum.Enum):
    postgresql = "postgresql"
    mysql = "mysql"
    mssql = "mssql"
    mongodb = "mongodb"
    redis = "redis"
    elasticsearch = "elasticsearch"
    other = "other"


class DbStatus(str, enum.Enum):
    active = "active"
    decommissioned = "decommissioned"


class Protocol(str, enum.Enum):
    http = "http"
    https = "https"
    grpc = "grpc"
    tcp = "tcp"


class Server(Base):
    __tablename__ = "servers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hostname: Mapped[str] = mapped_column(String(255), nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    os: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    server_type: Mapped[ServerType] = mapped_column(SAEnum(ServerType), nullable=False, default=ServerType.virtual)
    environment_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("environments.id"), nullable=True)
    role: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[ServerStatus] = mapped_column(SAEnum(ServerStatus), nullable=False, default=ServerStatus.active)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    environment: Mapped[Optional["Environment"]] = relationship("Environment", back_populates="servers")


class DatabaseInstance(Base):
    __tablename__ = "database_instances"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    db_type: Mapped[DbType] = mapped_column(SAEnum(DbType), nullable=False)
    host: Mapped[str] = mapped_column(String(255), nullable=False)
    port: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    environment_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("environments.id"), nullable=True)
    status: Mapped[DbStatus] = mapped_column(SAEnum(DbStatus), nullable=False, default=DbStatus.active)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    environment: Mapped[Optional["Environment"]] = relationship("Environment", back_populates="database_instances")


class Endpoint(Base):
    __tablename__ = "endpoints"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("applications.id"), nullable=False)
    url: Mapped[str] = mapped_column(String(512), nullable=False)
    protocol: Mapped[Protocol] = mapped_column(SAEnum(Protocol), nullable=False, default=Protocol.https)
    environment_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("environments.id"), nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    description: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    application: Mapped["Application"] = relationship("Application", back_populates="endpoints")
    environment: Mapped[Optional["Environment"]] = relationship("Environment", back_populates="endpoints")
