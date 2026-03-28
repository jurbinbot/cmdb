import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from ..models.relationship import RelationshipType


class CIRelationshipBase(BaseModel):
    source_ci_type: str
    source_ci_id: uuid.UUID
    target_ci_type: str
    target_ci_id: uuid.UUID
    relationship_type: RelationshipType
    description: Optional[str] = None


class CIRelationshipCreate(CIRelationshipBase):
    pass


class CIRelationshipUpdate(BaseModel):
    relationship_type: Optional[RelationshipType] = None
    description: Optional[str] = None


class CIRelationshipResponse(CIRelationshipBase):
    id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}
