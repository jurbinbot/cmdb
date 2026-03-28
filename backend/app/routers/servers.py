import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..database import get_db
from ..models.infrastructure import Server
from ..schemas.infrastructure import ServerCreate, ServerUpdate, ServerResponse

router = APIRouter(prefix="/api/servers", tags=["servers"])


@router.get("", response_model=dict)
async def list_servers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Server))
    items = result.scalars().all()
    return {"items": [ServerResponse.model_validate(s) for s in items], "total": len(items)}


@router.get("/{server_id}", response_model=ServerResponse)
async def get_server(server_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Server).where(Server.id == server_id))
    s = result.scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Server not found")
    return ServerResponse.model_validate(s)


@router.post("", status_code=201, response_model=ServerResponse)
async def create_server(data: ServerCreate, db: AsyncSession = Depends(get_db)):
    s = Server(**data.model_dump())
    db.add(s)
    await db.commit()
    await db.refresh(s)
    return ServerResponse.model_validate(s)


@router.put("/{server_id}", response_model=ServerResponse)
async def update_server(server_id: uuid.UUID, data: ServerUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Server).where(Server.id == server_id))
    s = result.scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Server not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(s, field, value)
    await db.commit()
    await db.refresh(s)
    return ServerResponse.model_validate(s)


@router.delete("/{server_id}", status_code=204)
async def delete_server(server_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Server).where(Server.id == server_id))
    s = result.scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Server not found")
    await db.delete(s)
    await db.commit()
