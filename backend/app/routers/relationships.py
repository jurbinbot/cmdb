import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.database import get_db
from app.models.relationship import CIRelationship
from app.schemas.relationship import CIRelationshipCreate, CIRelationshipUpdate, CIRelationshipResponse

router = APIRouter(tags=["relationships"])


@router.get("/api/relationships", response_model=list[CIRelationshipResponse])
async def list_relationships(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CIRelationship))
    return result.scalars().all()


@router.get("/api/relationships/{rel_id}", response_model=CIRelationshipResponse)
async def get_relationship(rel_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CIRelationship).where(CIRelationship.id == rel_id))
    rel = result.scalar_one_or_none()
    if not rel:
        raise HTTPException(status_code=404, detail="Relationship not found")
    return rel


@router.post("/api/relationships", response_model=CIRelationshipResponse, status_code=status.HTTP_201_CREATED)
async def create_relationship(data: CIRelationshipCreate, db: AsyncSession = Depends(get_db)):
    rel = CIRelationship(**data.model_dump())
    db.add(rel)
    await db.commit()
    await db.refresh(rel)
    return rel


@router.put("/api/relationships/{rel_id}", response_model=CIRelationshipResponse)
async def update_relationship(rel_id: uuid.UUID, data: CIRelationshipUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CIRelationship).where(CIRelationship.id == rel_id))
    rel = result.scalar_one_or_none()
    if not rel:
        raise HTTPException(status_code=404, detail="Relationship not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(rel, field, value)
    await db.commit()
    await db.refresh(rel)
    return rel


@router.delete("/api/relationships/{rel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_relationship(rel_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CIRelationship).where(CIRelationship.id == rel_id))
    rel = result.scalar_one_or_none()
    if not rel:
        raise HTTPException(status_code=404, detail="Relationship not found")
    await db.delete(rel)
    await db.commit()


@router.get("/api/ci/{ci_type}/{ci_id}/relationships", response_model=list[CIRelationshipResponse])
async def get_ci_relationships(ci_type: str, ci_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CIRelationship).where(
            or_(
                (CIRelationship.source_ci_type == ci_type) & (CIRelationship.source_ci_id == ci_id),
                (CIRelationship.target_ci_type == ci_type) & (CIRelationship.target_ci_id == ci_id),
            )
        )
    )
    return result.scalars().all()
