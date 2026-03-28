import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.database import get_db
from app.models.application import Application, AppStatus, AppType
from app.models.infrastructure import Server, DatabaseInstance
from app.models.audit import AuditLog, AuditAction
from app.schemas.application import ApplicationCreate, ApplicationUpdate, ApplicationResponse

router = APIRouter(prefix="/api/applications", tags=["applications"])


def _app_to_dict(app: Application) -> dict:
    return {
        "id": str(app.id),
        "name": app.name,
        "description": app.description,
        "app_type": app.app_type,
        "status": app.status,
        "tier": app.tier,
        "repo_url": app.repo_url,
        "docs_url": app.docs_url,
    }


@router.get("", response_model=list[ApplicationResponse])
async def list_applications(
    status: Optional[str] = None,
    app_type: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Application)
    if status:
        query = query.where(Application.status == status)
    if app_type:
        query = query.where(Application.app_type == app_type)
    if search:
        query = query.where(Application.name.ilike(f"%{search}%"))
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{app_id}", response_model=ApplicationResponse)
async def get_application(app_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Application).where(Application.id == app_id))
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app


@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application(data: ApplicationCreate, db: AsyncSession = Depends(get_db)):
    app = Application(**data.model_dump())
    db.add(app)
    await db.flush()
    audit = AuditLog(
        ci_type="application",
        ci_id=app.id,
        action=AuditAction.create,
        after_json=_app_to_dict(app),
    )
    db.add(audit)
    await db.commit()
    await db.refresh(app)
    return app


@router.put("/{app_id}", response_model=ApplicationResponse)
async def update_application(app_id: uuid.UUID, data: ApplicationUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Application).where(Application.id == app_id))
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    before = _app_to_dict(app)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(app, field, value)
    await db.flush()
    audit = AuditLog(
        ci_type="application",
        ci_id=app.id,
        action=AuditAction.update,
        before_json=before,
        after_json=_app_to_dict(app),
    )
    db.add(audit)
    await db.commit()
    await db.refresh(app)
    return app


@router.delete("/{app_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_application(app_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Application).where(Application.id == app_id))
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    before = _app_to_dict(app)
    app.status = AppStatus.decommissioned
    audit = AuditLog(
        ci_type="application",
        ci_id=app.id,
        action=AuditAction.delete,
        before_json=before,
        after_json=_app_to_dict(app),
    )
    db.add(audit)
    await db.commit()


async def _resolve_ci_name(ci_type: str, ci_id: str, db: AsyncSession) -> dict:
    """Look up a CI's display name and status given its type and id."""
    try:
        uid = uuid.UUID(ci_id)
    except ValueError:
        return {"name": ci_id, "status": "unknown"}

    if ci_type == "application":
        r = await db.execute(select(Application).where(Application.id == uid))
        obj = r.scalar_one_or_none()
        if obj:
            return {"name": obj.name, "status": obj.status}
    elif ci_type == "server":
        r = await db.execute(select(Server).where(Server.id == uid))
        obj = r.scalar_one_or_none()
        if obj:
            return {"name": obj.hostname, "status": obj.status}
    elif ci_type == "database":
        r = await db.execute(select(DatabaseInstance).where(DatabaseInstance.id == uid))
        obj = r.scalar_one_or_none()
        if obj:
            return {"name": obj.name, "status": "active"}
    return {"name": ci_id, "status": "unknown"}


@router.get("/{app_id}/dependency-tree")
async def get_dependency_tree(app_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    # Verify the app exists
    result = await db.execute(select(Application).where(Application.id == app_id))
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    sql = text("""
        WITH RECURSIVE dep_tree AS (
          SELECT
            source_ci_id::text AS source_ci_id,
            target_ci_type,
            target_ci_id::text AS target_ci_id,
            relationship_type,
            0 AS depth
          FROM ci_relationships
          WHERE source_ci_type = 'application' AND source_ci_id = :app_id
          UNION ALL
          SELECT
            r.source_ci_id::text,
            r.target_ci_type,
            r.target_ci_id::text,
            r.relationship_type,
            dt.depth + 1
          FROM ci_relationships r
          JOIN dep_tree dt ON r.source_ci_id::text = dt.target_ci_id
          WHERE dt.depth < 5
        )
        SELECT source_ci_id, target_ci_type, target_ci_id, relationship_type, depth
        FROM dep_tree
    """)

    cte_result = await db.execute(sql, {"app_id": str(app_id)})
    rows = cte_result.fetchall()

    if not rows:
        return {
            "id": str(app_id),
            "name": app.name,
            "type": "application",
            "status": app.status,
            "children": [],
        }

    # Batch-resolve names for all unique CIs
    ci_ids_by_type: dict[str, set] = {}
    for row in rows:
        ci_ids_by_type.setdefault(row.target_ci_type, set()).add(row.target_ci_id)

    ci_info: dict[tuple, dict] = {}
    if "application" in ci_ids_by_type:
        ids = [uuid.UUID(i) for i in ci_ids_by_type["application"]]
        r = await db.execute(select(Application).where(Application.id.in_(ids)))
        for a in r.scalars().all():
            ci_info[("application", str(a.id))] = {"name": a.name, "status": a.status}
    if "server" in ci_ids_by_type:
        ids = [uuid.UUID(i) for i in ci_ids_by_type["server"]]
        r = await db.execute(select(Server).where(Server.id.in_(ids)))
        for s in r.scalars().all():
            ci_info[("server", str(s.id))] = {"name": s.hostname, "status": s.status}
    if "database" in ci_ids_by_type:
        ids = [uuid.UUID(i) for i in ci_ids_by_type["database"]]
        r = await db.execute(select(DatabaseInstance).where(DatabaseInstance.id.in_(ids)))
        for d in r.scalars().all():
            ci_info[("database", str(d.id))] = {"name": d.name, "status": "active"}

    # Build children map: source_ci_id -> list of child nodes (without children filled yet)
    children_map: dict[str, list] = {}
    for row in rows:
        src = row.source_ci_id
        tgt = row.target_ci_id
        ttype = row.target_ci_type
        info = ci_info.get((ttype, tgt), {"name": tgt, "status": "unknown"})
        node = {
            "id": tgt,
            "name": info["name"],
            "type": ttype,
            "status": info["status"],
            "relationship_type": row.relationship_type,
            "children": [],
        }
        children_map.setdefault(src, []).append(node)

    def build_children(ci_id: str, visited: set) -> list:
        if ci_id in visited:
            return []
        visited = visited | {ci_id}
        result = []
        for child in children_map.get(ci_id, []):
            child_copy = dict(child)
            child_copy["children"] = build_children(child["id"], visited)
            result.append(child_copy)
        return result

    return {
        "id": str(app_id),
        "name": app.name,
        "type": "application",
        "status": app.status,
        "children": build_children(str(app_id), set()),
    }


@router.get("/{app_id}/impact")
async def get_impact(app_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    # Verify the app exists
    result = await db.execute(select(Application).where(Application.id == app_id))
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    # Find all CIs that have a relationship pointing TO this app
    sql = text("""
        SELECT source_ci_type, source_ci_id::text AS source_ci_id, relationship_type
        FROM ci_relationships
        WHERE target_ci_type = 'application' AND target_ci_id = :app_id
    """)
    impact_result = await db.execute(sql, {"app_id": str(app_id)})
    rows = impact_result.fetchall()

    items = []
    for row in rows:
        info = await _resolve_ci_name(row.source_ci_type, row.source_ci_id, db)
        items.append({
            "ci_type": row.source_ci_type,
            "ci_id": row.source_ci_id,
            "name": info["name"],
            "relationship_type": row.relationship_type,
        })

    return items
