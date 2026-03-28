import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..database import get_db
from ..models.application import Environment
from ..schemas.application import EnvironmentCreate, EnvironmentUpdate, EnvironmentResponse

router = APIRouter(prefix="/api/environments", tags=["environments"])


@router.get("", response_model=dict)
async def list_environments(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Environment))
    envs = result.scalars().all()
    return {"items": [EnvironmentResponse.model_validate(e) for e in envs], "total": len(envs)}


@router.get("/{env_id}", response_model=EnvironmentResponse)
async def get_environment(env_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Environment).where(Environment.id == env_id))
    env = result.scalar_one_or_none()
    if not env:
        raise HTTPException(status_code=404, detail="Environment not found")
    return EnvironmentResponse.model_validate(env)


@router.post("", status_code=201, response_model=EnvironmentResponse)
async def create_environment(data: EnvironmentCreate, db: AsyncSession = Depends(get_db)):
    env = Environment(**data.model_dump())
    db.add(env)
    await db.commit()
    await db.refresh(env)
    return EnvironmentResponse.model_validate(env)


@router.put("/{env_id}", response_model=EnvironmentResponse)
async def update_environment(env_id: uuid.UUID, data: EnvironmentUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Environment).where(Environment.id == env_id))
    env = result.scalar_one_or_none()
    if not env:
        raise HTTPException(status_code=404, detail="Environment not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(env, field, value)
    await db.commit()
    await db.refresh(env)
    return EnvironmentResponse.model_validate(env)


@router.delete("/{env_id}", status_code=204)
async def delete_environment(env_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Environment).where(Environment.id == env_id))
    env = result.scalar_one_or_none()
    if not env:
        raise HTTPException(status_code=404, detail="Environment not found")
    await db.delete(env)
    await db.commit()
