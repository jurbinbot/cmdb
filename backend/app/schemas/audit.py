import uuid
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel
from ..models.audit import AuditAction


class AuditLogResponse(BaseModel):
    id: uuid.UUID
    ci_type: str
    ci_id: uuid.UUID
    action: AuditAction
    changed_by: str
    changed_at: datetime
    before_json: Optional[Any] = None
    after_json: Optional[Any] = None

    model_config = {"from_attributes": True}
