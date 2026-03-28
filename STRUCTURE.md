# CMDB — Project Structure Map

> This file is a living reference for the project layout. It is intended to be comprehensive enough that an AI agent (or new developer) can locate any file without needing to browse the directory tree.
>
> **Keep this file updated** as new files and directories are added.

---

```
cmdb/
├── backend/                        # FastAPI Python application — all server-side code lives here
│   ├── app/
│   │   ├── main.py                 # FastAPI app factory: creates the app instance, registers routers, configures CORS, mounts middleware, lifespan events
│   │   ├── config.py               # Application settings loaded from .env via pydantic-settings; single Settings instance imported everywhere
│   │   ├── database.py             # SQLAlchemy async engine, sessionmaker, and get_db() dependency for FastAPI injection
│   │   ├── models/                 # SQLAlchemy ORM table definitions — one file per logical domain
│   │   │   ├── __init__.py         # Re-exports all models so Alembic can discover them via a single import
│   │   │   ├── application.py      # Application, Environment, Deployment — the core CI types for software
│   │   │   ├── infrastructure.py   # Server, DatabaseInstance, Endpoint — infrastructure and network CIs
│   │   │   ├── relationship.py     # CIRelationship — typed directed edges between any two CIs (the graph layer)
│   │   │   ├── team.py             # Team, Contact, ApplicationOwnership — ownership and responsibility mapping
│   │   │   └── audit.py            # AuditLog — immutable record of every mutation; written by audit middleware
│   │   ├── schemas/                # Pydantic v2 request/response models — one file per domain matching models/
│   │   │   ├── application.py      # ApplicationCreate, ApplicationUpdate, ApplicationResponse (with nested deployments/endpoints)
│   │   │   ├── infrastructure.py   # ServerCreate/Response, DatabaseInstanceCreate/Response, EndpointCreate/Response
│   │   │   ├── relationship.py     # CIRelationshipCreate/Response, DependencyTree, ImpactAnalysis schemas
│   │   │   ├── team.py             # TeamCreate/Response, ContactCreate/Response, OwnershipCreate/Response
│   │   │   └── audit.py            # AuditLogResponse schema
│   │   ├── routers/                # FastAPI APIRouter handlers — one file per resource, imported into main.py
│   │   │   ├── applications.py     # /api/applications — CRUD + list with filters
│   │   │   ├── environments.py     # /api/environments — CRUD
│   │   │   ├── deployments.py      # /api/deployments + /api/applications/{id}/deployments — CRUD
│   │   │   ├── servers.py          # /api/servers — CRUD
│   │   │   ├── databases.py        # /api/databases — CRUD for DatabaseInstance
│   │   │   ├── endpoints.py        # /api/endpoints — CRUD
│   │   │   ├── teams.py            # /api/teams + /api/contacts — CRUD
│   │   │   ├── relationships.py    # /api/relationships + /api/ci/{type}/{id}/relationships + dependency-tree + impact
│   │   │   ├── audit.py            # /api/audit — filterable audit log query
│   │   │   ├── search.py           # /api/search?q= — cross-entity full-text search
│   │   │   └── health.py           # /health, /api/status, /health/app/{id} (Kemp-compatible)
│   │   ├── services/               # Business logic layer — routers call services, not the DB directly
│   │   │   ├── application_service.py   # Application CRUD, soft-delete, ownership resolution
│   │   │   ├── relationship_service.py  # Graph queries: dependency tree (CTE), impact analysis
│   │   │   ├── audit_service.py         # Audit log write helpers; called by middleware
│   │   │   └── search_service.py        # Cross-table search query builder
│   │   ├── integrations/           # Connectors to external systems — each integration is self-contained
│   │   │   ├── probe_aggregator.py # Polls probe-aggregator API; maps probe names to application IDs; caches latest status
│   │   │   ├── github.py           # GitHub API client: repo info, last commit, open PRs, CI status
│   │   │   └── kemp.py             # Kemp health endpoint logic: 200 if app+probes healthy, 503 otherwise
│   │   ├── middleware/             # Starlette middleware classes
│   │   │   └── audit_middleware.py # Intercepts all mutating requests, captures before/after state, writes AuditLog row
│   │   └── seed.py                 # Development seed script: inserts realistic sample apps, servers, teams, deployments
│   ├── alembic/                    # Alembic database migration framework
│   │   ├── env.py                  # Alembic env config: loads DATABASE_URL from settings, imports all models for autogenerate
│   │   ├── script.py.mako          # Migration file template
│   │   └── versions/               # Generated migration scripts — one file per schema change
│   ├── tests/                      # Pytest test suite
│   │   ├── conftest.py             # Shared fixtures: test DB, test client, seed helpers
│   │   ├── test_applications.py    # Application API integration tests
│   │   ├── test_relationships.py   # Relationship and graph query tests
│   │   └── test_search.py          # Search endpoint tests
│   ├── requirements.txt            # Python dependencies: fastapi, uvicorn, sqlalchemy, alembic, pydantic-settings, asyncpg, etc.
│   ├── .env.example                # Template .env file — copy to .env and fill in values; never commit the real .env
│   └── Dockerfile                  # Multi-stage Docker image for the backend; runs uvicorn in production mode
│
├── frontend/                       # React 18 + Vite SPA — all client-side code lives here
│   ├── src/
│   │   ├── main.jsx                # React entry point: mounts <App /> into #root, wraps with Router and QueryClient
│   │   ├── App.jsx                 # Top-level router: defines all routes, renders the sidebar layout shell
│   │   ├── api/                    # Axios instance and per-resource API wrapper functions
│   │   │   ├── client.js           # Configured axios instance (baseURL from env, interceptors for error handling)
│   │   │   ├── applications.js     # getApplications(), getApplication(id), createApplication(), updateApplication(), deleteApplication()
│   │   │   ├── servers.js          # Server resource API calls
│   │   │   ├── teams.js            # Team and Contact resource API calls
│   │   │   ├── relationships.js    # Relationship, dependency-tree, and impact API calls
│   │   │   ├── audit.js            # Audit log API calls
│   │   │   └── search.js           # Global search API call
│   │   ├── components/             # Reusable UI components — not tied to a specific page
│   │   │   ├── Sidebar.jsx         # Left navigation sidebar with route links and active state
│   │   │   ├── StatusBadge.jsx     # Coloured pill badge for CI status (up/down/warning/unknown)
│   │   │   ├── DataTable.jsx       # Generic sortable/paginated table component
│   │   │   ├── Modal.jsx           # Generic modal dialog wrapper
│   │   │   ├── ConfirmDialog.jsx   # Delete/destructive action confirmation modal
│   │   │   ├── SearchBar.jsx       # Global search input with results dropdown (header)
│   │   │   └── ErrorBoundary.jsx   # React error boundary for graceful failure UI
│   │   ├── pages/                  # Route-level page components — one file per route
│   │   │   ├── Dashboard.jsx       # Overview: app count by status/type, recent deployments, recent audit events
│   │   │   ├── Applications.jsx    # Application catalog: searchable/filterable table, create button
│   │   │   ├── AppDetail.jsx       # Single application detail: overview, deployments, endpoints, ownership, impact
│   │   │   ├── Topology.jsx        # Interactive dependency graph of all applications using React Flow/Cytoscape
│   │   │   ├── Servers.jsx         # Server inventory: list with environment filter, CRUD
│   │   │   ├── Teams.jsx           # Teams and contacts: list, ownership view, CRUD
│   │   │   └── AuditLog.jsx        # Audit log: filterable table with before/after JSON diff view
│   │   ├── hooks/                  # Custom React hooks
│   │   │   ├── useApplications.js  # useSWR/React Query hook for application list and detail
│   │   │   ├── useTopology.js      # Fetches and formats relationship data for graph rendering
│   │   │   └── useSearch.js        # Debounced global search hook
│   │   └── styles/                 # Global CSS
│   │       ├── global.css          # CSS reset, CSS variables (colours, spacing, typography), dark theme
│   │       └── components.css      # Shared component styles (cards, buttons, badges, tables)
│   ├── public/
│   │   └── favicon.ico             # Application favicon
│   ├── vite.config.js              # Vite config: dev server proxy to backend (/api → localhost:8000), build output
│   ├── package.json                # Node dependencies: react, react-dom, react-router-dom, axios, react-flow, etc.
│   └── index.html                  # Vite HTML entry point — loads main.jsx
│
├── docs/
│   └── cmdb-project-plan.docx     # Full project plan document: scope, architecture decisions, stakeholder requirements
│
├── IMPLEMENTATION_PLAN.md          # Step-by-step phased build checklist with GitHub-flavored checkboxes — update as tasks complete
├── STRUCTURE.md                    # This file — annotated project layout reference for developers and AI agents
├── README.md                       # Project overview, tech stack, quick-start instructions, links to docs
└── .gitignore                      # Python, Node, env, IDE, OS, and compiled asset ignore patterns
```

---

## Key Conventions

- **Backend route → service → DB**: Routers never touch SQLAlchemy directly; all DB logic lives in `services/`.
- **One schema file per model file**: `schemas/application.py` mirrors `models/application.py`.
- **Audit everything**: The `audit_middleware.py` intercepts all `POST`/`PUT`/`DELETE` requests automatically; individual services do not need to write audit records manually.
- **Integration isolation**: Each external system connector lives in `integrations/` and exposes a simple async function. Nothing outside that file imports from the external SDK directly.
- **Frontend API layer**: Components never call `axios` directly — they go through `api/*.js` wrappers, which makes mocking and error handling consistent.
- **Environment config**: All environment-specific values live in `.env` (backend) and `.env.local` (frontend). `.env.example` documents every required key.
