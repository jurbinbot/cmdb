import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..database import get_db
from ..models.application import Deployment, Application
from ..schemas.application import DeploymentCreate, DeploymentUpdate, DeploymentResponse

router = APIRouter(tags=["deployments"])


@router.get("/api/deployments", response_model=dict)
async def list_deployments(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Deployment).options(selectinload(Deployment.environment)))
    deps = result.scalars().all()
    return {"items": [DeploymentResponse.model_validate(d) for d in deps], "total": len(deps)}


@router.get("/api/applications/{app_id}/deployments", response_model=dict)
async def list_app_deployments(app_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Deployment).options(selectinload(Deployment.environment))
        .where(Deployment.application_id == app_id)
    )
    deps = result.scalars().all()
    return {"items": [DeploymentResponse.model_validate(d) for d in deps], "total": len(deps)}


@router.post("/api/deployments", status_code=201, response_model=DeploymentResponse)
async def create_deployment(data: DeploymentCreate, db: AsyncSession = Depends(get_db)):
    # unset previous current for same app+env
    result = await db.execute(
        select(Deployment).where(
            Deployment.application_id == data.application_id,
            Deployment.environment_id == data.environment_id,
            Deployment.is_current == True,
        )
    )
    for prev in result.scalars().all():
        prev.is_current = False
    dep = Deployment(**data.model_dump())
    dep.is_current = True
    db.add(dep)
    await db.commit()
    await db.refresh(dep)
    result2 = await db.execute(
        select(Deployment).options(selectinload(Deployment.environment)).where(Deployment.id == dep.id)
    )
    dep = result2.scalar_one()
    return DeploymentResponse.model_validate(dep)


@router.put("/api/deployments/{dep_id}", response_model=DeploymentResponse)
async def update_deployment(dep_id: uuid.UUID, data: DeploymentUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Deployment).options(selectinload(Deployment.environment)).where(Deployment.id == dep_id)
    )
    dep = result.scalar_one_or_none()
    if not dep:
        raise HTTPException(status_code=404, detail="Deployment not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(dep, field, value)
    await db.commit()
    await db.refresh(dep)
    return DeploymentResponse.model_validate(dep)


@router.delete("/api/deployments/{dep_id}", status_code=204)
async def delete_deployment(dep_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Deployment).where(Deployment.id == dep_id))
    dep = result.scalar_one_or_none()
    if not dep:
        raise HTTPException(status_code=404, detail="Deployment not found")
    await db.delete(dep)
    await db.commit()
