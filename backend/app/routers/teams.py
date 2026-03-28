import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..database import get_db
from ..models.team import Team, Contact, ApplicationOwnership
from ..schemas.team import (
    TeamCreate, TeamUpdate, TeamResponse,
    ContactCreate, ContactUpdate, ContactResponse,
    OwnershipCreate, OwnershipResponse,
)

router = APIRouter(tags=["teams"])


@router.get("/api/teams", response_model=dict)
async def list_teams(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Team))
    items = result.scalars().all()
    return {"items": [TeamResponse.model_validate(t) for t in items], "total": len(items)}


@router.get("/api/teams/{team_id}", response_model=TeamResponse)
async def get_team(team_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Team).where(Team.id == team_id))
    t = result.scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=404, detail="Team not found")
    return TeamResponse.model_validate(t)


@router.post("/api/teams", status_code=201, response_model=TeamResponse)
async def create_team(data: TeamCreate, db: AsyncSession = Depends(get_db)):
    t = Team(**data.model_dump())
    db.add(t)
    await db.commit()
    await db.refresh(t)
    return TeamResponse.model_validate(t)


@router.put("/api/teams/{team_id}", response_model=TeamResponse)
async def update_team(team_id: uuid.UUID, data: TeamUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Team).where(Team.id == team_id))
    t = result.scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=404, detail="Team not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(t, field, value)
    await db.commit()
    await db.refresh(t)
    return TeamResponse.model_validate(t)


@router.delete("/api/teams/{team_id}", status_code=204)
async def delete_team(team_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Team).where(Team.id == team_id))
    t = result.scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=404, detail="Team not found")
    await db.delete(t)
    await db.commit()


@router.get("/api/contacts", response_model=dict)
async def list_contacts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Contact))
    items = result.scalars().all()
    return {"items": [ContactResponse.model_validate(c) for c in items], "total": len(items)}


@router.post("/api/contacts", status_code=201, response_model=ContactResponse)
async def create_contact(data: ContactCreate, db: AsyncSession = Depends(get_db)):
    c = Contact(**data.model_dump())
    db.add(c)
    await db.commit()
    await db.refresh(c)
    return ContactResponse.model_validate(c)


@router.put("/api/contacts/{contact_id}", response_model=ContactResponse)
async def update_contact(contact_id: uuid.UUID, data: ContactUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Contact).where(Contact.id == contact_id))
    c = result.scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=404, detail="Contact not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(c, field, value)
    await db.commit()
    await db.refresh(c)
    return ContactResponse.model_validate(c)


@router.delete("/api/contacts/{contact_id}", status_code=204)
async def delete_contact(contact_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Contact).where(Contact.id == contact_id))
    c = result.scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=404, detail="Contact not found")
    await db.delete(c)
    await db.commit()


@router.post("/api/ownerships", status_code=201, response_model=OwnershipResponse)
async def create_ownership(data: OwnershipCreate, db: AsyncSession = Depends(get_db)):
    o = ApplicationOwnership(**data.model_dump())
    db.add(o)
    await db.commit()
    return OwnershipResponse.model_validate(o)


@router.delete("/api/ownerships/{app_id}/{team_id}", status_code=204)
async def delete_ownership(app_id: uuid.UUID, team_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ApplicationOwnership).where(
            ApplicationOwnership.application_id == app_id,
            ApplicationOwnership.team_id == team_id
        )
    )
    o = result.scalar_one_or_none()
    if not o:
        raise HTTPException(status_code=404, detail="Ownership not found")
    await db.delete(o)
    await db.commit()
