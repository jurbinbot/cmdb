from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.audit import AuditLog, AuditAction
from app.schemas.audit import AuditLogResponse

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("", response_model=list[AuditLogResponse])
async def list_audit_logs(
    ci_type: Optional[str] = None,
    action: Optional[AuditAction] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    query = select(AuditLog).order_by(AuditLog.changed_at.desc())
    if ci_type:
        query = query.where(AuditLog.ci_type == ci_type)
    if action:
        query = query.where(AuditLog.action == action)
    if date_from:
        query = query.where(AuditLog.changed_at >= date_from)
    if date_to:
        query = query.where(AuditLog.changed_at <= date_to)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()
