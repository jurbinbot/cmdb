from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routers import applications, environments, deployments, servers, databases, endpoints, teams, relationships, audit

app = FastAPI(title="CMDB API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(applications.router)
app.include_router(environments.router)
app.include_router(deployments.router)
app.include_router(servers.router)
app.include_router(databases.router)
app.include_router(endpoints.router)
app.include_router(teams.router)
app.include_router(relationships.router)
app.include_router(audit.router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "cmdb-api"}


@app.get("/api/status")
async def api_status():
    return {"status": "ok", "version": "0.1.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)
