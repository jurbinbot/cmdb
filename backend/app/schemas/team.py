import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.team import OwnershipType


class TeamCreate(BaseModel):
    name: str
    slack_channel: Optional[str] = None
    email: Optional[str] = None
    description: Optional[str] = None


class TeamUpdate(BaseModel):
    name: Optional[str] = None
    slack_channel: Optional[str] = None
    email: Optional[str] = None
    description: Optional[str] = None


class TeamResponse(BaseModel):
    id: uuid.UUID
    name: str
    slack_channel: Optional[str]
    email: Optional[str]
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ContactCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    team_id: Optional[uuid.UUID] = None
    role: Optional[str] = None


class ContactUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    team_id: Optional[uuid.UUID] = None
    role: Optional[str] = None


class ContactResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: Optional[str]
    phone: Optional[str]
    team_id: Optional[uuid.UUID]
    role: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class OwnershipCreate(BaseModel):
    application_id: uuid.UUID
    team_id: uuid.UUID
    ownership_type: OwnershipType = OwnershipType.primary


class OwnershipUpdate(BaseModel):
    ownership_type: Optional[OwnershipType] = None


class OwnershipResponse(BaseModel):
    id: uuid.UUID
    application_id: uuid.UUID
    team_id: uuid.UUID
    ownership_type: OwnershipType
    created_at: datetime

    class Config:
        from_attributes = True
