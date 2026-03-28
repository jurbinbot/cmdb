import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from ..models.infrastructure import ServerType, ServerStatus, DbType, DbStatus, Protocol


class ServerBase(BaseModel):
    hostname: str
    ip_address: Optional[str] = None
    os: Optional[str] = None
    server_type: ServerType = ServerType.virtual
    environment_id: Optional[uuid.UUID] = None
    role: Optional[str] = None
    status: ServerStatus = ServerStatus.active


class ServerCreate(ServerBase):
    pass


class ServerUpdate(BaseModel):
    hostname: Optional[str] = None
    ip_address: Optional[str] = None
    os: Optional[str] = None
    server_type: Optional[ServerType] = None
    environment_id: Optional[uuid.UUID] = None
    role: Optional[str] = None
    status: Optional[ServerStatus] = None


class ServerResponse(ServerBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DatabaseInstanceBase(BaseModel):
    name: str
    db_type: DbType
    host: str
    port: Optional[int] = None
    environment_id: Optional[uuid.UUID] = None
    status: DbStatus = DbStatus.active


class DatabaseInstanceCreate(DatabaseInstanceBase):
    pass


class DatabaseInstanceUpdate(BaseModel):
    name: Optional[str] = None
    db_type: Optional[DbType] = None
    host: Optional[str] = None
    port: Optional[int] = None
    environment_id: Optional[uuid.UUID] = None
    status: Optional[DbStatus] = None


class DatabaseInstanceResponse(DatabaseInstanceBase):
    id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class EndpointBase(BaseModel):
    application_id: uuid.UUID
    url: str
    protocol: Protocol = Protocol.https
    environment_id: Optional[uuid.UUID] = None
    is_public: bool = False
    description: Optional[str] = None


class EndpointCreate(EndpointBase):
    pass


class EndpointUpdate(BaseModel):
    url: Optional[str] = None
    protocol: Optional[Protocol] = None
    environment_id: Optional[uuid.UUID] = None
    is_public: Optional[bool] = None
    description: Optional[str] = None


class EndpointResponse(EndpointBase):
    id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}
