import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.application import Deployment
from app.schemas.application import DeploymentCreate, DeploymentUpdate, DeploymentResponse

router = APIRouter(tags=["deployments"])


@router.get("/api/deployments", response_model=list[DeploymentResponse])
async def list_deployments(
    application_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Deployment)
    if application_id:
        query = query.where(Deployment.application_id == application_id)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/api/applications/{app_id}/deployments", response_model=list[DeploymentResponse])
async def list_app_deployments(app_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Deployment).where(Deployment.application_id == app_id))
    return result.scalars().all()


@router.get("/api/deployments/{dep_id}", response_model=DeploymentResponse)
async def get_deployment(dep_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Deployment).where(Deployment.id == dep_id))
    dep = result.scalar_one_or_none()
    if not dep:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return dep


@router.post("/api/deployments", response_model=DeploymentResponse, status_code=status.HTTP_201_CREATED)
async def create_deployment(data: DeploymentCreate, db: AsyncSession = Depends(get_db)):
    dep = Deployment(**data.model_dump())
    db.add(dep)
    await db.commit()
    await db.refresh(dep)
    return dep


@router.put("/api/deployments/{dep_id}", response_model=DeploymentResponse)
async def update_deployment(dep_id: uuid.UUID, data: DeploymentUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Deployment).where(Deployment.id == dep_id))
    dep = result.scalar_one_or_none()
    if not dep:
        raise HTTPException(status_code=404, detail="Deployment not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(dep, field, value)
    await db.commit()
    await db.refresh(dep)
    return dep


@router.delete("/api/deployments/{dep_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_deployment(dep_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Deployment).where(Deployment.id == dep_id))
    dep = result.scalar_one_or_none()
    if not dep:
        raise HTTPException(status_code=404, detail="Deployment not found")
    await db.delete(dep)
    await db.commit()
