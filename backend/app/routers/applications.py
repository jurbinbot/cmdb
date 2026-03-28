import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.application import Application, AppStatus, AppType
from app.models.audit import AuditLog, AuditAction
from app.schemas.application import ApplicationCreate, ApplicationUpdate, ApplicationResponse

router = APIRouter(prefix="/api/applications", tags=["applications"])


def _app_to_dict(app: Application) -> dict:
    return {
        "id": str(app.id),
        "name": app.name,
        "description": app.description,
        "app_type": app.app_type,
        "status": app.status,
        "tier": app.tier,
        "repo_url": app.repo_url,
        "docs_url": app.docs_url,
    }


@router.get("", response_model=list[ApplicationResponse])
async def list_applications(
    status: Optional[str] = None,
    app_type: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Application)
    if status:
        query = query.where(Application.status == status)
    if app_type:
        query = query.where(Application.app_type == app_type)
    if search:
        query = query.where(Application.name.ilike(f"%{search}%"))
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{app_id}", response_model=ApplicationResponse)
async def get_application(app_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Application).where(Application.id == app_id))
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app


@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application(data: ApplicationCreate, db: AsyncSession = Depends(get_db)):
    app = Application(**data.model_dump())
    db.add(app)
    await db.flush()
    audit = AuditLog(
        ci_type="application",
        ci_id=app.id,
        action=AuditAction.create,
        after_json=_app_to_dict(app),
    )
    db.add(audit)
    await db.commit()
    await db.refresh(app)
    return app


@router.put("/{app_id}", response_model=ApplicationResponse)
async def update_application(app_id: uuid.UUID, data: ApplicationUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Application).where(Application.id == app_id))
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    before = _app_to_dict(app)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(app, field, value)
    await db.flush()
    audit = AuditLog(
        ci_type="application",
        ci_id=app.id,
        action=AuditAction.update,
        before_json=before,
        after_json=_app_to_dict(app),
    )
    db.add(audit)
    await db.commit()
    await db.refresh(app)
    return app


@router.delete("/{app_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_application(app_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Application).where(Application.id == app_id))
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    before = _app_to_dict(app)
    app.status = AppStatus.decommissioned
    audit = AuditLog(
        ci_type="application",
        ci_id=app.id,
        action=AuditAction.delete,
        before_json=before,
        after_json=_app_to_dict(app),
    )
    db.add(audit)
    await db.commit()
