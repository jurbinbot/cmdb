import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.team import Team, Contact, ApplicationOwnership
from app.schemas.team import TeamCreate, TeamUpdate, TeamResponse, ContactCreate, ContactUpdate, ContactResponse, OwnershipCreate, OwnershipUpdate, OwnershipResponse

router = APIRouter(tags=["teams"])


@router.get("/api/teams", response_model=list[TeamResponse])
async def list_teams(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Team))
    return result.scalars().all()


@router.get("/api/teams/{team_id}", response_model=TeamResponse)
async def get_team(team_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Team).where(Team.id == team_id))
    team = result.scalar_one_or_none()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@router.post("/api/teams", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(data: TeamCreate, db: AsyncSession = Depends(get_db)):
    team = Team(**data.model_dump())
    db.add(team)
    await db.commit()
    await db.refresh(team)
    return team


@router.put("/api/teams/{team_id}", response_model=TeamResponse)
async def update_team(team_id: uuid.UUID, data: TeamUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Team).where(Team.id == team_id))
    team = result.scalar_one_or_none()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(team, field, value)
    await db.commit()
    await db.refresh(team)
    return team


@router.delete("/api/teams/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(team_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Team).where(Team.id == team_id))
    team = result.scalar_one_or_none()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    await db.delete(team)
    await db.commit()


@router.get("/api/contacts", response_model=list[ContactResponse])
async def list_contacts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Contact))
    return result.scalars().all()


@router.get("/api/contacts/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Contact).where(Contact.id == contact_id))
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.post("/api/contacts", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(data: ContactCreate, db: AsyncSession = Depends(get_db)):
    contact = Contact(**data.model_dump())
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


@router.put("/api/contacts/{contact_id}", response_model=ContactResponse)
async def update_contact(contact_id: uuid.UUID, data: ContactUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Contact).where(Contact.id == contact_id))
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(contact, field, value)
    await db.commit()
    await db.refresh(contact)
    return contact


@router.delete("/api/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Contact).where(Contact.id == contact_id))
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    await db.delete(contact)
    await db.commit()


@router.get("/api/ownerships", response_model=list[OwnershipResponse])
async def list_ownerships(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ApplicationOwnership))
    return result.scalars().all()


@router.post("/api/ownerships", response_model=OwnershipResponse, status_code=status.HTTP_201_CREATED)
async def create_ownership(data: OwnershipCreate, db: AsyncSession = Depends(get_db)):
    ownership = ApplicationOwnership(**data.model_dump())
    db.add(ownership)
    await db.commit()
    await db.refresh(ownership)
    return ownership


@router.put("/api/ownerships/{ownership_id}", response_model=OwnershipResponse)
async def update_ownership(ownership_id: uuid.UUID, data: OwnershipUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ApplicationOwnership).where(ApplicationOwnership.id == ownership_id))
    ownership = result.scalar_one_or_none()
    if not ownership:
        raise HTTPException(status_code=404, detail="Ownership not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(ownership, field, value)
    await db.commit()
    await db.refresh(ownership)
    return ownership


@router.delete("/api/ownerships/{ownership_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ownership(ownership_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ApplicationOwnership).where(ApplicationOwnership.id == ownership_id))
    ownership = result.scalar_one_or_none()
    if not ownership:
        raise HTTPException(status_code=404, detail="Ownership not found")
    await db.delete(ownership)
    await db.commit()
