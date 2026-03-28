import uuid
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import String, Text, Enum, ForeignKey, DateTime, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class ServerStatus(str, PyEnum):
    active = "active"
    maintenance = "maintenance"
    decommissioned = "decommissioned"
    unknown = "unknown"


class DbType(str, PyEnum):
    postgres = "postgres"
    mysql = "mysql"
    mssql = "mssql"
    mongodb = "mongodb"
    redis = "redis"
    elasticsearch = "elasticsearch"
    other = "other"


class Protocol(str, PyEnum):
    http = "http"
    https = "https"
    grpc = "grpc"
    tcp = "tcp"
    udp = "udp"


class Server(Base):
    __tablename__ = "servers"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hostname: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    ip_address: Mapped[str | None] = mapped_column(String(45))
    os: Mapped[str | None] = mapped_column(String(100))
    environment_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("environments.id"))
    role: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[ServerStatus] = mapped_column(Enum(ServerStatus), nullable=False, default=ServerStatus.active)
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    environment: Mapped["Environment | None"] = relationship()  # type: ignore[name-defined]


class DatabaseInstance(Base):
    __tablename__ = "database_instances"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    db_type: Mapped[DbType] = mapped_column(Enum(DbType), nullable=False, default=DbType.postgres)
    host: Mapped[str] = mapped_column(String(255), nullable=False)
    port: Mapped[int | None] = mapped_column(Integer)
    environment_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("environments.id"))
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    environment: Mapped["Environment | None"] = relationship()  # type: ignore[name-defined]


class Endpoint(Base):
    __tablename__ = "endpoints"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("applications.id"), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    protocol: Mapped[Protocol] = mapped_column(Enum(Protocol), nullable=False, default=Protocol.https)
    environment_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("environments.id"))
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    application: Mapped["Application"] = relationship(back_populates="endpoints")  # type: ignore[name-defined]
    environment: Mapped["Environment | None"] = relationship()  # type: ignore[name-defined]
