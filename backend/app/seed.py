"""
Seed script for CMDB development data.
Run with: python -m app.seed (from the backend/ directory)
"""
import asyncio
import uuid
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.application import Application, Environment, Deployment, AppType, AppStatus, Tier, EnvType
from app.models.infrastructure import Server, DatabaseInstance, Endpoint, ServerStatus, DbType, Protocol
from app.models.team import Team, Contact, ApplicationOwnership, OwnershipType
from app.models.relationship import CIRelationship, RelationshipType


async def seed(session: AsyncSession) -> None:
    # Check if already seeded
    result = await session.execute(select(Environment))
    if result.scalars().first():
        print("Database already seeded. Skipping.")
        return

    print("Seeding database...")

    # --- Environments ---
    env_dev = Environment(name="Development", env_type=EnvType.development, description="Local development environment")
    env_staging = Environment(name="Staging", env_type=EnvType.staging, description="Pre-production staging environment")
    env_prod = Environment(name="Production", env_type=EnvType.production, description="Live production environment")
    session.add_all([env_dev, env_staging, env_prod])
    await session.flush()

    # --- Teams ---
    team_platform = Team(name="Platform Engineering", slack_channel="#platform-eng", email="platform@example.com", description="Owns core infrastructure and platform services")
    team_commerce = Team(name="Commerce Team", slack_channel="#commerce", email="commerce@example.com", description="Owns customer-facing commerce services")
    team_data = Team(name="Data & Analytics", slack_channel="#data-eng", email="data@example.com", description="Owns data pipelines and analytics")
    session.add_all([team_platform, team_commerce, team_data])
    await session.flush()

    # --- Contacts ---
    contacts = [
        Contact(name="Alice Martin", email="alice@example.com", phone="+1-555-0101", team_id=team_platform.id, role="Tech Lead"),
        Contact(name="Bob Chen", email="bob@example.com", phone="+1-555-0102", team_id=team_platform.id, role="Senior Engineer"),
        Contact(name="Carol Davis", email="carol@example.com", phone="+1-555-0201", team_id=team_commerce.id, role="Engineering Manager"),
        Contact(name="Dave Wilson", email="dave@example.com", phone="+1-555-0202", team_id=team_commerce.id, role="Senior Engineer"),
        Contact(name="Eve Johnson", email="eve@example.com", phone="+1-555-0301", team_id=team_data.id, role="Data Engineer"),
    ]
    session.add_all(contacts)
    await session.flush()

    # --- Applications ---
    app_gateway = Application(
        name="API Gateway",
        description="Central API gateway for all external traffic. Handles auth, rate limiting, and routing.",
        app_type=AppType.infrastructure,
        status=AppStatus.active,
        tier=Tier.tier1,
        repo_url="https://github.com/example/api-gateway",
        docs_url="https://docs.example.com/api-gateway",
    )
    app_portal = Application(
        name="Customer Portal",
        description="React SPA for customer self-service: orders, profile management, support tickets.",
        app_type=AppType.frontend,
        status=AppStatus.active,
        tier=Tier.tier1,
        repo_url="https://github.com/example/customer-portal",
        docs_url="https://docs.example.com/customer-portal",
    )
    app_orders = Application(
        name="Order Service",
        description="Microservice handling order lifecycle: creation, processing, fulfillment, cancellation.",
        app_type=AppType.backend,
        status=AppStatus.active,
        tier=Tier.tier1,
        repo_url="https://github.com/example/order-service",
        docs_url="https://docs.example.com/order-service",
    )
    app_inventory = Application(
        name="Inventory Service",
        description="Manages product inventory, stock levels, reservations, and warehouse locations.",
        app_type=AppType.backend,
        status=AppStatus.active,
        tier=Tier.tier2,
        repo_url="https://github.com/example/inventory-service",
        docs_url="https://docs.example.com/inventory-service",
    )
    app_analytics = Application(
        name="Analytics Pipeline",
        description="Batch and streaming data pipeline for business intelligence and reporting.",
        app_type=AppType.backend,
        status=AppStatus.active,
        tier=Tier.tier2,
        repo_url="https://github.com/example/analytics-pipeline",
        docs_url="https://docs.example.com/analytics-pipeline",
    )
    app_auth = Application(
        name="Legacy Auth",
        description="Legacy authentication service. Being phased out in favour of API Gateway auth.",
        app_type=AppType.backend,
        status=AppStatus.deprecated,
        tier=Tier.tier3,
        repo_url="https://github.com/example/legacy-auth",
        docs_url=None,
    )
    session.add_all([app_gateway, app_portal, app_orders, app_inventory, app_analytics, app_auth])
    await session.flush()

    # --- Servers ---
    server_web1 = Server(hostname="web-01.prod.example.com", ip_address="10.0.1.10", os="Ubuntu 22.04", environment_id=env_prod.id, role="web", status=ServerStatus.active)
    server_web2 = Server(hostname="web-02.prod.example.com", ip_address="10.0.1.11", os="Ubuntu 22.04", environment_id=env_prod.id, role="web", status=ServerStatus.active)
    server_app1 = Server(hostname="app-01.prod.example.com", ip_address="10.0.2.10", os="Ubuntu 22.04", environment_id=env_prod.id, role="app", status=ServerStatus.active)
    server_db1 = Server(hostname="db-01.prod.example.com", ip_address="10.0.3.10", os="Ubuntu 22.04", environment_id=env_prod.id, role="database", status=ServerStatus.active)
    server_staging = Server(hostname="app-01.staging.example.com", ip_address="10.1.2.10", os="Ubuntu 22.04", environment_id=env_staging.id, role="app", status=ServerStatus.active)
    session.add_all([server_web1, server_web2, server_app1, server_db1, server_staging])
    await session.flush()

    # --- Database Instances ---
    db_orders = DatabaseInstance(name="orders-db", db_type=DbType.postgres, host="db-01.prod.example.com", port=5432, environment_id=env_prod.id, description="Primary orders database")
    db_inventory = DatabaseInstance(name="inventory-db", db_type=DbType.postgres, host="db-01.prod.example.com", port=5433, environment_id=env_prod.id, description="Inventory database")
    db_cache = DatabaseInstance(name="app-cache", db_type=DbType.redis, host="cache-01.prod.example.com", port=6379, environment_id=env_prod.id, description="Application cache")
    session.add_all([db_orders, db_inventory, db_cache])
    await session.flush()

    # --- Endpoints ---
    ep_gateway_prod = Endpoint(application_id=app_gateway.id, url="https://api.example.com", protocol=Protocol.https, environment_id=env_prod.id, is_public=True, description="Public API Gateway endpoint")
    ep_portal_prod = Endpoint(application_id=app_portal.id, url="https://portal.example.com", protocol=Protocol.https, environment_id=env_prod.id, is_public=True, description="Customer Portal")
    ep_orders_internal = Endpoint(application_id=app_orders.id, url="http://order-service.internal:8080", protocol=Protocol.http, environment_id=env_prod.id, is_public=False, description="Internal order service endpoint")
    ep_inventory_internal = Endpoint(application_id=app_inventory.id, url="http://inventory-service.internal:8080", protocol=Protocol.http, environment_id=env_prod.id, is_public=False, description="Internal inventory endpoint")
    session.add_all([ep_gateway_prod, ep_portal_prod, ep_orders_internal, ep_inventory_internal])
    await session.flush()

    # --- Deployments ---
    now = datetime.utcnow()
    deployments = [
        Deployment(application_id=app_gateway.id, environment_id=env_prod.id, version="2.4.1", deployed_at=now - timedelta(days=3), deployed_by="alice@example.com", is_current=True, notes="Hotfix for rate limiting bug"),
        Deployment(application_id=app_gateway.id, environment_id=env_staging.id, version="2.5.0-rc1", deployed_at=now - timedelta(days=1), deployed_by="alice@example.com", is_current=True, notes="Release candidate"),
        Deployment(application_id=app_portal.id, environment_id=env_prod.id, version="1.12.0", deployed_at=now - timedelta(days=7), deployed_by="carol@example.com", is_current=True),
        Deployment(application_id=app_orders.id, environment_id=env_prod.id, version="3.1.2", deployed_at=now - timedelta(days=5), deployed_by="dave@example.com", is_current=True),
        Deployment(application_id=app_orders.id, environment_id=env_staging.id, version="3.2.0-beta", deployed_at=now - timedelta(hours=12), deployed_by="dave@example.com", is_current=True),
        Deployment(application_id=app_inventory.id, environment_id=env_prod.id, version="1.8.4", deployed_at=now - timedelta(days=14), deployed_by="bob@example.com", is_current=True),
        Deployment(application_id=app_analytics.id, environment_id=env_prod.id, version="0.9.1", deployed_at=now - timedelta(days=21), deployed_by="eve@example.com", is_current=True),
        Deployment(application_id=app_auth.id, environment_id=env_prod.id, version="0.3.7", deployed_at=now - timedelta(days=90), deployed_by="system", is_current=True, notes="Last deployment before deprecation"),
    ]
    session.add_all(deployments)
    await session.flush()

    # --- Application Ownerships ---
    ownerships = [
        ApplicationOwnership(application_id=app_gateway.id, team_id=team_platform.id, ownership_type=OwnershipType.primary),
        ApplicationOwnership(application_id=app_portal.id, team_id=team_commerce.id, ownership_type=OwnershipType.primary),
        ApplicationOwnership(application_id=app_orders.id, team_id=team_commerce.id, ownership_type=OwnershipType.primary),
        ApplicationOwnership(application_id=app_orders.id, team_id=team_platform.id, ownership_type=OwnershipType.secondary),
        ApplicationOwnership(application_id=app_inventory.id, team_id=team_commerce.id, ownership_type=OwnershipType.primary),
        ApplicationOwnership(application_id=app_analytics.id, team_id=team_data.id, ownership_type=OwnershipType.primary),
        ApplicationOwnership(application_id=app_auth.id, team_id=team_platform.id, ownership_type=OwnershipType.primary),
    ]
    session.add_all(ownerships)
    await session.flush()

    # --- Relationships ---
    relationships = [
        CIRelationship(source_ci_type="application", source_ci_id=app_portal.id, target_ci_type="application", target_ci_id=app_gateway.id, relationship_type=RelationshipType.depends_on, description="Customer Portal routes all API calls through the gateway"),
        CIRelationship(source_ci_type="application", source_ci_id=app_orders.id, target_ci_type="application", target_ci_id=app_inventory.id, relationship_type=RelationshipType.depends_on, description="Order Service checks inventory before confirming orders"),
        CIRelationship(source_ci_type="application", source_ci_id=app_orders.id, target_ci_type="database", target_ci_id=db_orders.id, relationship_type=RelationshipType.uses_database, description="Primary data store for orders"),
        CIRelationship(source_ci_type="application", source_ci_id=app_inventory.id, target_ci_type="database", target_ci_id=db_inventory.id, relationship_type=RelationshipType.uses_database, description="Primary data store for inventory"),
        CIRelationship(source_ci_type="application", source_ci_id=app_gateway.id, target_ci_type="server", target_ci_id=server_web1.id, relationship_type=RelationshipType.hosted_on, description="Gateway runs on web-01"),
        CIRelationship(source_ci_type="application", source_ci_id=app_orders.id, target_ci_type="application", target_ci_id=app_analytics.id, relationship_type=RelationshipType.connects_to, description="Order events streamed to analytics pipeline"),
        CIRelationship(source_ci_type="application", source_ci_id=app_orders.id, target_ci_type="database", target_ci_id=db_cache.id, relationship_type=RelationshipType.uses_database, description="Session and cart caching"),
        CIRelationship(source_ci_type="application", source_ci_id=app_gateway.id, target_ci_type="application", target_ci_id=app_auth.id, relationship_type=RelationshipType.depends_on, description="Legacy auth fallback (being phased out)"),
    ]
    session.add_all(relationships)
    await session.commit()

    print("\nSeed data created successfully!")
    print(f"  Environments: 3 (Development, Staging, Production)")
    print(f"  Teams: 3")
    print(f"  Contacts: 5")
    print(f"  Applications: 6 (API Gateway, Customer Portal, Order Service, Inventory Service, Analytics Pipeline, Legacy Auth)")
    print(f"  Servers: 5")
    print(f"  Database Instances: 3")
    print(f"  Endpoints: 4")
    print(f"  Deployments: 8")
    print(f"  Ownerships: 7")
    print(f"  Relationships: 8")


async def main():
    async with AsyncSessionLocal() as session:
        await seed(session)


if __name__ == "__main__":
    asyncio.run(main())
