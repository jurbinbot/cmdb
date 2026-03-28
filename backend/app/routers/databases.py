import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.infrastructure import DatabaseInstance
from app.schemas.infrastructure import DatabaseInstanceCreate, DatabaseInstanceUpdate, DatabaseInstanceResponse

router = APIRouter(prefix="/api/databases", tags=["databases"])


@router.get("", response_model=list[DatabaseInstanceResponse])
async def list_databases(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DatabaseInstance))
    return result.scalars().all()


@router.get("/{db_id}", response_model=DatabaseInstanceResponse)
async def get_database(db_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DatabaseInstance).where(DatabaseInstance.id == db_id))
    db_inst = result.scalar_one_or_none()
    if not db_inst:
        raise HTTPException(status_code=404, detail="Database instance not found")
    return db_inst


@router.post("", response_model=DatabaseInstanceResponse, status_code=status.HTTP_201_CREATED)
async def create_database(data: DatabaseInstanceCreate, db: AsyncSession = Depends(get_db)):
    db_inst = DatabaseInstance(**data.model_dump())
    db.add(db_inst)
    await db.commit()
    await db.refresh(db_inst)
    return db_inst


@router.put("/{db_id}", response_model=DatabaseInstanceResponse)
async def update_database(db_id: uuid.UUID, data: DatabaseInstanceUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DatabaseInstance).where(DatabaseInstance.id == db_id))
    db_inst = result.scalar_one_or_none()
    if not db_inst:
        raise HTTPException(status_code=404, detail="Database instance not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(db_inst, field, value)
    await db.commit()
    await db.refresh(db_inst)
    return db_inst


@router.delete("/{db_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_database(db_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DatabaseInstance).where(DatabaseInstance.id == db_id))
    db_inst = result.scalar_one_or_none()
    if not db_inst:
        raise HTTPException(status_code=404, detail="Database instance not found")
    await db.delete(db_inst)
    await db.commit()
