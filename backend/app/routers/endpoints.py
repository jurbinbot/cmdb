import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..database import get_db
from ..models.infrastructure import Endpoint
from ..schemas.infrastructure import EndpointCreate, EndpointUpdate, EndpointResponse

router = APIRouter(prefix="/api/endpoints", tags=["endpoints"])


@router.get("", response_model=dict)
async def list_endpoints(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Endpoint))
    items = result.scalars().all()
    return {"items": [EndpointResponse.model_validate(i) for i in items], "total": len(items)}


@router.get("/{endpoint_id}", response_model=EndpointResponse)
async def get_endpoint(endpoint_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Endpoint).where(Endpoint.id == endpoint_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    return EndpointResponse.model_validate(item)


@router.post("", status_code=201, response_model=EndpointResponse)
async def create_endpoint(data: EndpointCreate, db: AsyncSession = Depends(get_db)):
    item = Endpoint(**data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return EndpointResponse.model_validate(item)


@router.put("/{endpoint_id}", response_model=EndpointResponse)
async def update_endpoint(endpoint_id: uuid.UUID, data: EndpointUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Endpoint).where(Endpoint.id == endpoint_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return EndpointResponse.model_validate(item)


@router.delete("/{endpoint_id}", status_code=204)
async def delete_endpoint(endpoint_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Endpoint).where(Endpoint.id == endpoint_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    await db.delete(item)
    await db.commit()
