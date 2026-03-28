# CMDB — Configuration Management Database

A full-featured Configuration Management Database for managing applications, servers, environments, dependencies, and their relationships across your infrastructure.

---

## Overview

This CMDB provides a single source of truth for your technical estate. It tracks:

- **Applications** — services, APIs, frontends, batch jobs, and their deployments per environment
- **Infrastructure** — servers, database instances, load balancer endpoints
- **Environments** — dev, staging, production, and any custom environments
- **Teams & Contacts** — ownership mapping from applications to teams and individuals
- **Relationships** — typed dependency edges between any two configuration items (CIs)
- **Audit Log** — immutable record of every change to every CI

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | [FastAPI](https://fastapi.tiangolo.com/) (Python 3.11+) |
| Database | PostgreSQL 15+ |
| ORM / Migrations | SQLAlchemy 2.x (async) + Alembic |
| Frontend | React 18 + [Vite](https://vitejs.dev/) |
| Graph Visualisation | React Flow or Cytoscape.js |
| Observability | Prometheus + Grafana |
| Deployment | Docker + Nginx Proxy Manager |

---

## Phased Delivery

### Phase 1 — Core Foundation
Full application catalog, supporting entities (servers, databases, environments, teams), CRUD APIs, and React UI with search and filtering.

### Phase 2 — Relationships & Topology
Typed CI relationships, dependency graph queries, impact analysis, and an interactive topology graph UI.

### Phase 3 — Integrations
Probe-aggregator health status, GitHub repo metadata, Prometheus metrics endpoint, Kemp health-check endpoint.

### Phase 4 — Automation & Polish
Audit log UI with diff view, global search, drift detection, and auto-discovery from GitHub orgs and probe-aggregator.

---

## Quick Start

> See [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md) for the full step-by-step build checklist.
> See [STRUCTURE.md](./STRUCTURE.md) for the annotated project layout.
> See [docs/cmdb-project-plan.docx](./docs/cmdb-project-plan.docx) for the full project plan document.

```bash
# Clone the repo
git clone https://github.com/jurbinbot/cmdb.git
cd cmdb

# Backend (see backend/README once scaffolded)
cd backend
cp .env.example .env
# edit .env — set DATABASE_URL etc.
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (see frontend/README once scaffolded)
cd ../frontend
npm install
npm run dev
```

---

## Project Structure

See [STRUCTURE.md](./STRUCTURE.md) for a fully annotated file tree.

---

## Documentation

- [Full Project Plan](./docs/cmdb-project-plan.docx)
- [Implementation Plan](./IMPLEMENTATION_PLAN.md)
- [Structure Map](./STRUCTURE.md)
