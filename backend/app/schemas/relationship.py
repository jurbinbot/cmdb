import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.relationship import RelationshipType


class CIRelationshipCreate(BaseModel):
    source_ci_type: str
    source_ci_id: uuid.UUID
    target_ci_type: str
    target_ci_id: uuid.UUID
    relationship_type: RelationshipType
    description: Optional[str] = None


class CIRelationshipUpdate(BaseModel):
    relationship_type: Optional[RelationshipType] = None
    description: Optional[str] = None


class CIRelationshipResponse(BaseModel):
    id: uuid.UUID
    source_ci_type: str
    source_ci_id: uuid.UUID
    target_ci_type: str
    target_ci_id: uuid.UUID
    relationship_type: RelationshipType
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
