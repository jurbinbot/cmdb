import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..database import get_db
from ..models.infrastructure import DatabaseInstance
from ..schemas.infrastructure import DatabaseInstanceCreate, DatabaseInstanceUpdate, DatabaseInstanceResponse

router = APIRouter(prefix="/api/databases", tags=["databases"])


@router.get("", response_model=dict)
async def list_databases(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DatabaseInstance))
    items = result.scalars().all()
    return {"items": [DatabaseInstanceResponse.model_validate(i) for i in items], "total": len(items)}


@router.get("/{db_id}", response_model=DatabaseInstanceResponse)
async def get_database(db_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DatabaseInstance).where(DatabaseInstance.id == db_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Database instance not found")
    return DatabaseInstanceResponse.model_validate(item)


@router.post("", status_code=201, response_model=DatabaseInstanceResponse)
async def create_database(data: DatabaseInstanceCreate, db: AsyncSession = Depends(get_db)):
    item = DatabaseInstance(**data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return DatabaseInstanceResponse.model_validate(item)


@router.put("/{db_id}", response_model=DatabaseInstanceResponse)
async def update_database(db_id: uuid.UUID, data: DatabaseInstanceUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DatabaseInstance).where(DatabaseInstance.id == db_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Database instance not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return DatabaseInstanceResponse.model_validate(item)


@router.delete("/{db_id}", status_code=204)
async def delete_database(db_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DatabaseInstance).where(DatabaseInstance.id == db_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Database instance not found")
    await db.delete(item)
    await db.commit()
