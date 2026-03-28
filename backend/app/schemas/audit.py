import uuid
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel
from app.models.audit import AuditAction


class AuditLogResponse(BaseModel):
    id: uuid.UUID
    ci_type: str
    ci_id: uuid.UUID
    action: AuditAction
    changed_by: str
    changed_at: datetime
    before_json: Optional[Any]
    after_json: Optional[Any]

    class Config:
        from_attributes = True
