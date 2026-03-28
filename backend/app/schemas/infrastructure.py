import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.infrastructure import ServerStatus, DbType, Protocol


class ServerCreate(BaseModel):
    hostname: str
    ip_address: Optional[str] = None
    os: Optional[str] = None
    environment_id: Optional[uuid.UUID] = None
    role: Optional[str] = None
    status: ServerStatus = ServerStatus.active
    description: Optional[str] = None


class ServerUpdate(BaseModel):
    hostname: Optional[str] = None
    ip_address: Optional[str] = None
    os: Optional[str] = None
    environment_id: Optional[uuid.UUID] = None
    role: Optional[str] = None
    status: Optional[ServerStatus] = None
    description: Optional[str] = None


class ServerResponse(BaseModel):
    id: uuid.UUID
    hostname: str
    ip_address: Optional[str]
    os: Optional[str]
    environment_id: Optional[uuid.UUID]
    role: Optional[str]
    status: ServerStatus
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DatabaseInstanceCreate(BaseModel):
    name: str
    db_type: DbType = DbType.postgres
    host: str
    port: Optional[int] = None
    environment_id: Optional[uuid.UUID] = None
    description: Optional[str] = None


class DatabaseInstanceUpdate(BaseModel):
    name: Optional[str] = None
    db_type: Optional[DbType] = None
    host: Optional[str] = None
    port: Optional[int] = None
    environment_id: Optional[uuid.UUID] = None
    description: Optional[str] = None


class DatabaseInstanceResponse(BaseModel):
    id: uuid.UUID
    name: str
    db_type: DbType
    host: str
    port: Optional[int]
    environment_id: Optional[uuid.UUID]
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EndpointCreate(BaseModel):
    application_id: uuid.UUID
    url: str
    protocol: Protocol = Protocol.https
    environment_id: Optional[uuid.UUID] = None
    is_public: bool = True
    description: Optional[str] = None


class EndpointUpdate(BaseModel):
    url: Optional[str] = None
    protocol: Optional[Protocol] = None
    environment_id: Optional[uuid.UUID] = None
    is_public: Optional[bool] = None
    description: Optional[str] = None


class EndpointResponse(BaseModel):
    id: uuid.UUID
    application_id: uuid.UUID
    url: str
    protocol: Protocol
    environment_id: Optional[uuid.UUID]
    is_public: bool
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
