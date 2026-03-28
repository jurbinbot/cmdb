import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.infrastructure import Server
from app.schemas.infrastructure import ServerCreate, ServerUpdate, ServerResponse

router = APIRouter(prefix="/api/servers", tags=["servers"])


@router.get("", response_model=list[ServerResponse])
async def list_servers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Server))
    return result.scalars().all()


@router.get("/{server_id}", response_model=ServerResponse)
async def get_server(server_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Server).where(Server.id == server_id))
    server = result.scalar_one_or_none()
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    return server


@router.post("", response_model=ServerResponse, status_code=status.HTTP_201_CREATED)
async def create_server(data: ServerCreate, db: AsyncSession = Depends(get_db)):
    server = Server(**data.model_dump())
    db.add(server)
    await db.commit()
    await db.refresh(server)
    return server


@router.put("/{server_id}", response_model=ServerResponse)
async def update_server(server_id: uuid.UUID, data: ServerUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Server).where(Server.id == server_id))
    server = result.scalar_one_or_none()
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(server, field, value)
    await db.commit()
    await db.refresh(server)
    return server


@router.delete("/{server_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_server(server_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Server).where(Server.id == server_id))
    server = result.scalar_one_or_none()
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    await db.delete(server)
    await db.commit()
