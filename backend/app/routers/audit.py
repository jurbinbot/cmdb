import uuid
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..database import get_db
from ..models.audit import AuditLog, AuditAction
from ..schemas.audit import AuditLogResponse

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("", response_model=dict)
async def list_audit_logs(
    ci_type: Optional[str] = None,
    ci_id: Optional[uuid.UUID] = None,
    action: Optional[AuditAction] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    query = select(AuditLog).order_by(AuditLog.changed_at.desc())
    if ci_type:
        query = query.where(AuditLog.ci_type == ci_type)
    if ci_id:
        query = query.where(AuditLog.ci_id == ci_id)
    if action:
        query = query.where(AuditLog.action == action)
    if from_date:
        query = query.where(AuditLog.changed_at >= from_date)
    if to_date:
        query = query.where(AuditLog.changed_at <= to_date)

    count_result = await db.execute(query)
    total = len(count_result.scalars().all())

    paginated = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(paginated)
    items = result.scalars().all()
    return {"items": [AuditLogResponse.model_validate(i) for i in items], "total": total, "page": page, "page_size": page_size}
