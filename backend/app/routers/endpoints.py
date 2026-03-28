import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.infrastructure import Endpoint
from app.schemas.infrastructure import EndpointCreate, EndpointUpdate, EndpointResponse

router = APIRouter(prefix="/api/endpoints", tags=["endpoints"])


@router.get("", response_model=list[EndpointResponse])
async def list_endpoints(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Endpoint))
    return result.scalars().all()


@router.get("/{endpoint_id}", response_model=EndpointResponse)
async def get_endpoint(endpoint_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Endpoint).where(Endpoint.id == endpoint_id))
    endpoint = result.scalar_one_or_none()
    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    return endpoint


@router.post("", response_model=EndpointResponse, status_code=status.HTTP_201_CREATED)
async def create_endpoint(data: EndpointCreate, db: AsyncSession = Depends(get_db)):
    endpoint = Endpoint(**data.model_dump())
    db.add(endpoint)
    await db.commit()
    await db.refresh(endpoint)
    return endpoint


@router.put("/{endpoint_id}", response_model=EndpointResponse)
async def update_endpoint(endpoint_id: uuid.UUID, data: EndpointUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Endpoint).where(Endpoint.id == endpoint_id))
    endpoint = result.scalar_one_or_none()
    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(endpoint, field, value)
    await db.commit()
    await db.refresh(endpoint)
    return endpoint


@router.delete("/{endpoint_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_endpoint(endpoint_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Endpoint).where(Endpoint.id == endpoint_id))
    endpoint = result.scalar_one_or_none()
    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    await db.delete(endpoint)
    await db.commit()
