import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload

from ..database import get_db
from ..models.application import Application, AppStatus, AppType, Deployment, Environment
from ..models.team import ApplicationOwnership, Team
from ..models.infrastructure import Endpoint
from ..models.audit import AuditLog, AuditAction
from ..schemas.application import (
    ApplicationCreate, ApplicationUpdate, ApplicationResponse, ApplicationDetailResponse,
    DeploymentResponse, EnvironmentResponse
)

router = APIRouter(prefix="/api/applications", tags=["applications"])


def _app_to_response(app: Application) -> ApplicationResponse:
    return ApplicationResponse(
        id=app.id,
        name=app.name,
        description=app.description,
        app_type=app.app_type,
        status=app.status,
        tier=app.tier,
        repo_url=app.repo_url,
        docs_url=app.docs_url,
        created_at=app.created_at,
        updated_at=app.updated_at,
        deployment_count=len(app.deployments) if app.deployments else 0,
        endpoint_count=len(app.endpoints) if app.endpoints else 0,
        owner_count=len(app.ownerships) if app.ownerships else 0,
    )


@router.get("", response_model=dict)
async def list_applications(
    status: Optional[AppStatus] = None,
    app_type: Optional[AppType] = None,
    team_id: Optional[uuid.UUID] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Application).options(
        selectinload(Application.deployments),
        selectinload(Application.endpoints),
        selectinload(Application.ownerships),
    )
    if status:
        query = query.where(Application.status == status)
    if app_type:
        query = query.where(Application.app_type == app_type)
    if team_id:
        query = query.join(ApplicationOwnership).where(ApplicationOwnership.team_id == team_id)
    if search:
        query = query.where(
            or_(Application.name.ilike(f"%{search}%"), Application.description.ilike(f"%{search}%"))
        )
    result = await db.execute(query)
    apps = result.scalars().all()
    return {"items": [_app_to_response(a) for a in apps], "total": len(apps)}


@router.get("/{app_id}", response_model=dict)
async def get_application(app_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Application)
        .options(
            selectinload(Application.deployments).selectinload(Deployment.environment),
            selectinload(Application.endpoints),
            selectinload(Application.ownerships).selectinload(ApplicationOwnership.team),
        )
        .where(Application.id == app_id)
    )
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    resp = _app_to_response(app)
    deployments = [DeploymentResponse.model_validate(d) for d in app.deployments]
    endpoints = [{"id": str(e.id), "url": e.url, "protocol": e.protocol, "is_public": e.is_public} for e in app.endpoints]
    ownerships = [{"team_id": str(o.team_id), "team_name": o.team.name if o.team else None, "ownership_type": o.ownership_type} for o in app.ownerships]

    return {
        **resp.model_dump(),
        "deployments": [d.model_dump() for d in deployments],
        "endpoints": endpoints,
        "ownerships": ownerships,
    }


@router.post("", status_code=201, response_model=ApplicationResponse)
async def create_application(data: ApplicationCreate, db: AsyncSession = Depends(get_db)):
    app = Application(**data.model_dump())
    db.add(app)
    await db.flush()
    audit = AuditLog(
        ci_type="application", ci_id=app.id, action=AuditAction.create,
        after_json=data.model_dump()
    )
    db.add(audit)
    await db.commit()
    await db.refresh(app)
    app.deployments = []
    app.endpoints = []
    app.ownerships = []
    return _app_to_response(app)


@router.put("/{app_id}", response_model=ApplicationResponse)
async def update_application(app_id: uuid.UUID, data: ApplicationUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Application).options(
            selectinload(Application.deployments),
            selectinload(Application.endpoints),
            selectinload(Application.ownerships),
        ).where(Application.id == app_id)
    )
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    before = {c.name: str(getattr(app, c.name)) if getattr(app, c.name) is not None else None for c in app.__table__.columns}
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(app, field, value)
    audit = AuditLog(
        ci_type="application", ci_id=app.id, action=AuditAction.update,
        before_json=before, after_json=data.model_dump(exclude_unset=True)
    )
    db.add(audit)
    await db.commit()
    await db.refresh(app)
    return _app_to_response(app)


@router.delete("/{app_id}", status_code=204)
async def delete_application(app_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Application).options(
            selectinload(Application.deployments),
            selectinload(Application.endpoints),
            selectinload(Application.ownerships),
        ).where(Application.id == app_id)
    )
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    before = {c.name: str(getattr(app, c.name)) if getattr(app, c.name) is not None else None for c in app.__table__.columns}
    app.status = AppStatus.decommissioned
    audit = AuditLog(
        ci_type="application", ci_id=app.id, action=AuditAction.delete,
        before_json=before
    )
    db.add(audit)
    await db.commit()
