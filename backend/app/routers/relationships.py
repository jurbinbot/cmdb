import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..database import get_db
from ..models.relationship import CIRelationship
from ..schemas.relationship import CIRelationshipCreate, CIRelationshipUpdate, CIRelationshipResponse

router = APIRouter(tags=["relationships"])


@router.get("/api/relationships", response_model=dict)
async def list_relationships(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CIRelationship))
    items = result.scalars().all()
    return {"items": [CIRelationshipResponse.model_validate(r) for r in items], "total": len(items)}


@router.post("/api/relationships", status_code=201, response_model=CIRelationshipResponse)
async def create_relationship(data: CIRelationshipCreate, db: AsyncSession = Depends(get_db)):
    r = CIRelationship(**data.model_dump())
    db.add(r)
    await db.commit()
    await db.refresh(r)
    return CIRelationshipResponse.model_validate(r)


@router.get("/api/relationships/{rel_id}", response_model=CIRelationshipResponse)
async def get_relationship(rel_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CIRelationship).where(CIRelationship.id == rel_id))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Relationship not found")
    return CIRelationshipResponse.model_validate(r)


@router.put("/api/relationships/{rel_id}", response_model=CIRelationshipResponse)
async def update_relationship(rel_id: uuid.UUID, data: CIRelationshipUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CIRelationship).where(CIRelationship.id == rel_id))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Relationship not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(r, field, value)
    await db.commit()
    await db.refresh(r)
    return CIRelationshipResponse.model_validate(r)


@router.delete("/api/relationships/{rel_id}", status_code=204)
async def delete_relationship(rel_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CIRelationship).where(CIRelationship.id == rel_id))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Relationship not found")
    await db.delete(r)
    await db.commit()


@router.get("/api/ci/{ci_type}/{ci_id}/relationships", response_model=dict)
async def get_ci_relationships(ci_type: str, ci_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CIRelationship).where(
            (CIRelationship.source_ci_type == ci_type) & (CIRelationship.source_ci_id == ci_id) |
            (CIRelationship.target_ci_type == ci_type) & (CIRelationship.target_ci_id == ci_id)
        )
    )
    items = result.scalars().all()
    return {"items": [CIRelationshipResponse.model_validate(r) for r in items], "total": len(items)}
