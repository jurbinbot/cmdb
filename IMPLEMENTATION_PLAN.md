# CMDB Implementation Plan

> Last updated: 2026-03-28
> Status: 🟡 In Progress — Phase 1

---

## Phase 1 — Core Foundation

### Milestone 1.1 — Project Setup
- [x] Create GitHub repository
- [x] Initialize project structure (backend/, frontend/, docs/)
- [x] Add .gitignore, README.md, STRUCTURE.md
- [x] Add IMPLEMENTATION_PLAN.md
- [x] First commit pushed to GitHub

### Milestone 1.2 — Backend Foundation
- [x] Set up FastAPI project with uvicorn
- [x] Configure pydantic-settings and .env loading
- [x] Set up SQLAlchemy with PostgreSQL (asyncpg)
- [x] Set up Alembic for migrations
- [x] Create initial migration (empty)
- [x] Bind to 0.0.0.0:8000, enable CORS for frontend
- [x] Add /health and /api/status endpoints
- [x] Commit: backend foundation

### Milestone 1.3 — Core Data Models
- [x] Application model (id, name, description, type, status, tier, repo_url, docs_url, created_at, updated_at)
- [x] Environment model (id, name, type: dev/staging/prod, description)
- [x] Deployment model (id, application_id, environment_id, version, deployed_at, deployed_by, ci_cd_url, notes)
- [x] Server model (id, hostname, ip_address, os, environment_id, role, status)
- [x] DatabaseInstance model (id, name, type: postgres/mysql/etc, host, port, environment_id)
- [x] Endpoint model (id, application_id, url, protocol, environment_id, is_public)
- [x] Team model (id, name, slack_channel, email)
- [x] Contact model (id, name, email, phone, team_id, role)
- [x] ApplicationOwnership model (application_id, team_id, ownership_type: primary/secondary)
- [x] CIRelationship model (id, source_ci_type, source_ci_id, target_ci_type, target_ci_id, relationship_type, description)
- [x] AuditLog model (id, ci_type, ci_id, action, changed_by, changed_at, before_json, after_json)
- [x] Create Alembic migration for all models
- [x] Commit: core data models

### Milestone 1.4 — Core API (Applications)
- [x] Pydantic schemas for Application (Create, Update, Response)
- [x] GET /api/applications — list with filters (status, type, team)
- [x] GET /api/applications/{id} — detail with deployments, endpoints, ownership
- [x] POST /api/applications — create
- [x] PUT /api/applications/{id} — update
- [x] DELETE /api/applications/{id} — soft delete
- [x] Audit log middleware (auto-log all mutations)
- [x] Commit: applications API

### Milestone 1.5 — Supporting APIs
- [x] Environments CRUD (/api/environments)
- [x] Deployments CRUD (/api/deployments, /api/applications/{id}/deployments)
- [x] Servers CRUD (/api/servers)
- [x] Database instances CRUD (/api/databases)
- [x] Endpoints CRUD (/api/endpoints)
- [x] Teams CRUD (/api/teams)
- [x] Contacts CRUD (/api/contacts)
- [x] Commit: supporting APIs

### Milestone 1.6 — Seed Data
- [x] Create seed script with realistic sample data (5+ apps, 3 environments, teams, servers, deployments)
- [x] Commit: seed data

### Milestone 1.7 — Frontend Foundation
- [x] Scaffold React + Vite project
- [x] Set up React Router
- [x] Design system: CSS variables, dark theme, typography, card/button components
- [x] Sidebar navigation component
- [x] API client module (axios, base URL config)
- [x] Commit: frontend foundation

### Milestone 1.8 — Application Catalog UI
- [x] Applications list page (table with status badges, search, filter by team/type/status)
- [x] Application detail page (overview, deployments table, endpoints, ownership)
- [x] Create/Edit Application modal form
- [x] Delete confirmation
- [x] Commit: application catalog UI

### Milestone 1.9 — Supporting Entity UIs
- [x] Environments page (list + CRUD)
- [x] Servers page (list + CRUD)
- [x] Teams & Contacts page (list + CRUD)
- [x] Dashboard page (summary stats: app count by status/type, recent deployments, recent audit events)
- [x] Commit: supporting entity UIs

---

## Phase 2 — Relationships & Topology

### Milestone 2.1 — Relationship API
- [x] CIRelationship CRUD (/api/relationships)
- [x] GET /api/ci/{type}/{id}/relationships — all relationships for a CI
- [x] GET /api/applications/{id}/dependency-tree — recursive graph query (CTE)
- [x] GET /api/applications/{id}/impact — what would be affected if this app went down
- [x] Commit: relationship API

### Milestone 2.2 — Topology Graph UI
- [ ] Integrate a graph visualization library (React Flow or Cytoscape.js)
- [ ] Topology page: full dependency graph of all applications
- [ ] Application-scoped graph: click app → show its dependency subgraph
- [ ] Color nodes by status (up/down/warning from probe-aggregator)
- [ ] Click node → navigate to app detail
- [ ] Commit: topology graph UI

### Milestone 2.3 — Impact Analysis UI
- [ ] Impact analysis panel on Application detail page
- [ ] "What depends on this?" — upstream list
- [ ] "What does this depend on?" — downstream list
- [ ] Visual impact tree
- [ ] Commit: impact analysis

---

## Phase 3 — Integrations

### Milestone 3.1 — Probe Aggregator Integration
- [ ] Integration config: probe-aggregator base URL in .env
- [ ] Background job: poll probe-aggregator /api/probes, match probes to applications by config
- [ ] Store latest probe status per application (in-memory or cache table)
- [ ] Expose health status on GET /api/applications/{id} response
- [ ] Show health status badge on application catalog and detail pages
- [ ] Commit: probe-aggregator integration

### Milestone 3.2 — GitHub Integration
- [ ] GitHub PAT config in .env
- [ ] GET /api/applications/{id}/github — fetch repo info (last commit, open PRs, CI status)
- [ ] Link GitHub repo on application detail page
- [ ] Commit: GitHub integration

### Milestone 3.3 — Prometheus / Grafana Integration
- [ ] Expose /metrics endpoint on backend (prometheus_fastapi_instrumentator)
- [ ] Add Grafana dashboard JSON for CMDB metrics (app count by status, API latency, etc.)
- [ ] Add scrape job to monitoring-stack prometheus.yml
- [ ] Commit: Prometheus integration

### Milestone 3.4 — Kemp Integration
- [ ] GET /health/app/{id} — Kemp-compatible endpoint (200 if app+probes healthy, 503 otherwise)
- [ ] Document Kemp config in README
- [ ] Commit: Kemp integration

---

## Phase 4 — Automation & Polish

### Milestone 4.1 — Audit Log UI
- [ ] Audit log page: filterable table by CI type, action, user, date range
- [ ] Inline diff view (before/after JSON)
- [ ] Commit: audit log UI

### Milestone 4.2 — Search
- [ ] Global search endpoint: /api/search?q= (searches across apps, servers, teams, endpoints)
- [ ] Search bar in UI header with results dropdown
- [ ] Commit: global search

### Milestone 4.3 — Drift Detection (stretch)
- [ ] Scheduled job: compare current deployment versions against expected
- [ ] Flag applications where actual != expected version
- [ ] Show drift warnings on dashboard
- [ ] Commit: drift detection

### Milestone 4.4 — Auto-discovery (stretch)
- [ ] GitHub org scan: discover repos, suggest new applications
- [ ] Probe-aggregator sync: auto-create application stubs from probe names
- [ ] Commit: auto-discovery

---

## Completion Criteria
- [ ] All Phase 1 milestones complete and tested
- [ ] All Phase 2 milestones complete and tested
- [ ] Deployed behind Nginx Proxy Manager
- [ ] Prometheus metrics scraped and Grafana dashboard live
