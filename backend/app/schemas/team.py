import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from ..models.team import OwnershipType


class TeamBase(BaseModel):
    name: str
    slack_channel: Optional[str] = None
    email: Optional[str] = None


class TeamCreate(TeamBase):
    pass


class TeamUpdate(BaseModel):
    name: Optional[str] = None
    slack_channel: Optional[str] = None
    email: Optional[str] = None


class TeamResponse(TeamBase):
    id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class ContactBase(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    team_id: Optional[uuid.UUID] = None
    role: Optional[str] = None


class ContactCreate(ContactBase):
    pass


class ContactUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    team_id: Optional[uuid.UUID] = None
    role: Optional[str] = None


class ContactResponse(ContactBase):
    id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class OwnershipCreate(BaseModel):
    application_id: uuid.UUID
    team_id: uuid.UUID
    ownership_type: OwnershipType = OwnershipType.primary


class OwnershipResponse(BaseModel):
    application_id: uuid.UUID
    team_id: uuid.UUID
    ownership_type: OwnershipType

    model_config = {"from_attributes": True}
