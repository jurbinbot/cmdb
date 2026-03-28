"""
Seed script for CMDB development data.
Run with: python -m app.seed
"""
import asyncio
import uuid
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from .database import AsyncSessionLocal
from .models.application import Application, Environment, Deployment, AppType, AppStatus, AppTier, EnvType
from .models.infrastructure import Server, DatabaseInstance, Endpoint, ServerType, ServerStatus, DbType, DbStatus, Protocol
from .models.team import Team, Contact, ApplicationOwnership, OwnershipType
from .models.relationship import CIRelationship, RelationshipType


async def seed():
    async with AsyncSessionLocal() as db:
        # Environments
        env_dev = Environment(name="Development", env_type=EnvType.development, description="Local and CI development environment")
        env_stg = Environment(name="Staging", env_type=EnvType.staging, description="Pre-production staging environment")
        env_prd = Environment(name="Production", env_type=EnvType.production, description="Live production environment")
        db.add_all([env_dev, env_stg, env_prd])
        await db.flush()

        # Teams
        team_platform = Team(name="Platform Engineering", slack_channel="#platform", email="platform@company.com")
        team_product = Team(name="Product", slack_channel="#product", email="product@company.com")
        team_data = Team(name="Data Engineering", slack_channel="#data-eng", email="data@company.com")
        db.add_all([team_platform, team_product, team_data])
        await db.flush()

        # Contacts
        contacts = [
            Contact(name="Alice Chen", email="alice@company.com", phone="+1-555-0101", team_id=team_platform.id, role="Tech Lead"),
            Contact(name="Bob Smith", email="bob@company.com", phone="+1-555-0102", team_id=team_platform.id, role="SRE"),
            Contact(name="Carol White", email="carol@company.com", phone="+1-555-0103", team_id=team_product.id, role="Engineering Manager"),
            Contact(name="Dave Jones", email="dave@company.com", phone="+1-555-0104", team_id=team_product.id, role="Senior Developer"),
            Contact(name="Eve Martinez", email="eve@company.com", phone="+1-555-0105", team_id=team_data.id, role="Data Engineer"),
        ]
        db.add_all(contacts)
        await db.flush()

        # Applications
        app_gateway = Application(
            name="API Gateway", description="Central API gateway routing traffic to all backend services",
            app_type=AppType.backend, status=AppStatus.active, tier=AppTier.tier1,
            repo_url="https://github.com/company/api-gateway", docs_url="https://docs.company.com/api-gateway"
        )
        app_portal = Application(
            name="Customer Portal", description="Customer-facing web application for account management",
            app_type=AppType.frontend, status=AppStatus.active, tier=AppTier.tier1,
            repo_url="https://github.com/company/customer-portal", docs_url="https://docs.company.com/portal"
        )
        app_order = Application(
            name="Order Service", description="Microservice handling order creation, updates, and fulfillment",
            app_type=AppType.service, status=AppStatus.active, tier=AppTier.tier1,
            repo_url="https://github.com/company/order-service"
        )
        app_inventory = Application(
            name="Inventory Service", description="Tracks product inventory and stock levels",
            app_type=AppType.service, status=AppStatus.active, tier=AppTier.tier2,
            repo_url="https://github.com/company/inventory-service"
        )
        app_analytics = Application(
            name="Analytics Pipeline", description="ETL pipeline for business intelligence and reporting",
            app_type=AppType.service, status=AppStatus.active, tier=AppTier.tier3,
            repo_url="https://github.com/company/analytics-pipeline"
        )
        app_legacy = Application(
            name="Legacy Auth", description="Legacy authentication service — migrating to OAuth2",
            app_type=AppType.backend, status=AppStatus.deprecated, tier=AppTier.tier2,
            repo_url="https://github.com/company/legacy-auth"
        )
        db.add_all([app_gateway, app_portal, app_order, app_inventory, app_analytics, app_legacy])
        await db.flush()

        # Servers
        servers = [
            Server(hostname="prod-web-01", ip_address="10.0.1.10", os="Ubuntu 22.04", server_type=ServerType.virtual, environment_id=env_prd.id, role="web", status=ServerStatus.active),
            Server(hostname="prod-app-01", ip_address="10.0.1.20", os="Ubuntu 22.04", server_type=ServerType.virtual, environment_id=env_prd.id, role="application", status=ServerStatus.active),
            Server(hostname="prod-app-02", ip_address="10.0.1.21", os="Ubuntu 22.04", server_type=ServerType.virtual, environment_id=env_prd.id, role="application", status=ServerStatus.active),
            Server(hostname="stg-app-01", ip_address="10.0.2.20", os="Ubuntu 22.04", server_type=ServerType.virtual, environment_id=env_stg.id, role="application", status=ServerStatus.active),
            Server(hostname="dev-app-01", ip_address="10.0.3.20", os="Ubuntu 22.04", server_type=ServerType.virtual, environment_id=env_dev.id, role="application", status=ServerStatus.active),
        ]
        db.add_all(servers)
        await db.flush()

        # Database Instances
        db_orders = DatabaseInstance(name="orders-db", db_type=DbType.postgresql, host="prod-db-01.internal", port=5432, environment_id=env_prd.id, status=DbStatus.active)
        db_inventory = DatabaseInstance(name="inventory-db", db_type=DbType.postgresql, host="prod-db-01.internal", port=5432, environment_id=env_prd.id, status=DbStatus.active)
        db_cache = DatabaseInstance(name="app-cache", db_type=DbType.redis, host="prod-cache-01.internal", port=6379, environment_id=env_prd.id, status=DbStatus.active)
        db_analytics = DatabaseInstance(name="analytics-warehouse", db_type=DbType.elasticsearch, host="prod-elastic-01.internal", port=9200, environment_id=env_prd.id, status=DbStatus.active)
        db.add_all([db_orders, db_inventory, db_cache, db_analytics])
        await db.flush()

        # Endpoints
        endpoints_data = [
            Endpoint(application_id=app_gateway.id, url="https://api.company.com", protocol=Protocol.https, environment_id=env_prd.id, is_public=True, description="Public API Gateway"),
            Endpoint(application_id=app_gateway.id, url="https://api-staging.company.com", protocol=Protocol.https, environment_id=env_stg.id, is_public=False, description="Staging API Gateway"),
            Endpoint(application_id=app_portal.id, url="https://portal.company.com", protocol=Protocol.https, environment_id=env_prd.id, is_public=True, description="Customer Portal"),
            Endpoint(application_id=app_order.id, url="http://order-service.internal:8080", protocol=Protocol.http, environment_id=env_prd.id, is_public=False, description="Order Service internal"),
            Endpoint(application_id=app_inventory.id, url="http://inventory-service.internal:8080", protocol=Protocol.http, environment_id=env_prd.id, is_public=False, description="Inventory Service internal"),
        ]
        db.add_all(endpoints_data)
        await db.flush()

        # Deployments
        base_time = datetime(2026, 3, 1, 10, 0, 0)
        deployments_data = []
        for app, versions in [
            (app_gateway, ["1.2.0", "1.3.0", "1.4.0"]),
            (app_portal, ["2.1.0", "2.2.0"]),
            (app_order, ["3.0.1", "3.1.0"]),
            (app_inventory, ["1.0.5"]),
            (app_analytics, ["0.9.0"]),
            (app_legacy, ["0.3.2"]),
        ]:
            for i, (env, version) in enumerate([
                (env_dev, versions[0]),
                (env_stg, versions[-2] if len(versions) >= 2 else versions[0]),
                (env_prd, versions[-1]),
            ]):
                deployments_data.append(Deployment(
                    application_id=app.id,
                    environment_id=env.id,
                    version=version,
                    deployed_at=base_time + timedelta(days=i * 3),
                    deployed_by="ci-cd-bot",
                    is_current=True,
                ))
        db.add_all(deployments_data)
        await db.flush()

        # Application Ownership
        ownerships = [
            ApplicationOwnership(application_id=app_gateway.id, team_id=team_platform.id, ownership_type=OwnershipType.primary),
            ApplicationOwnership(application_id=app_portal.id, team_id=team_product.id, ownership_type=OwnershipType.primary),
            ApplicationOwnership(application_id=app_portal.id, team_id=team_platform.id, ownership_type=OwnershipType.secondary),
            ApplicationOwnership(application_id=app_order.id, team_id=team_product.id, ownership_type=OwnershipType.primary),
            ApplicationOwnership(application_id=app_inventory.id, team_id=team_product.id, ownership_type=OwnershipType.primary),
            ApplicationOwnership(application_id=app_analytics.id, team_id=team_data.id, ownership_type=OwnershipType.primary),
            ApplicationOwnership(application_id=app_legacy.id, team_id=team_platform.id, ownership_type=OwnershipType.primary),
        ]
        db.add_all(ownerships)
        await db.flush()

        # CI Relationships
        relationships_data = [
            CIRelationship(source_ci_type="application", source_ci_id=app_portal.id, target_ci_type="application", target_ci_id=app_gateway.id, relationship_type=RelationshipType.depends_on, description="Portal routes all API calls through gateway"),
            CIRelationship(source_ci_type="application", source_ci_id=app_gateway.id, target_ci_type="application", target_ci_id=app_order.id, relationship_type=RelationshipType.connects_to, description="Gateway routes order requests"),
            CIRelationship(source_ci_type="application", source_ci_id=app_gateway.id, target_ci_type="application", target_ci_id=app_inventory.id, relationship_type=RelationshipType.connects_to, description="Gateway routes inventory requests"),
            CIRelationship(source_ci_type="application", source_ci_id=app_order.id, target_ci_type="database", target_ci_id=db_orders.id, relationship_type=RelationshipType.uses_database, description="Order Service primary datastore"),
            CIRelationship(source_ci_type="application", source_ci_id=app_inventory.id, target_ci_type="database", target_ci_id=db_inventory.id, relationship_type=RelationshipType.uses_database, description="Inventory Service primary datastore"),
            CIRelationship(source_ci_type="application", source_ci_id=app_order.id, target_ci_type="database", target_ci_id=db_cache.id, relationship_type=RelationshipType.uses_database, description="Session caching"),
            CIRelationship(source_ci_type="application", source_ci_id=app_analytics.id, target_ci_type="database", target_ci_id=db_analytics.id, relationship_type=RelationshipType.uses_database, description="Analytics data store"),
            CIRelationship(source_ci_type="application", source_ci_id=app_gateway.id, target_ci_type="server", target_ci_id=servers[1].id, relationship_type=RelationshipType.hosted_on, description="Primary app server"),
            CIRelationship(source_ci_type="application", source_ci_id=app_portal.id, target_ci_type="server", target_ci_id=servers[0].id, relationship_type=RelationshipType.hosted_on, description="Web server"),
        ]
        db.add_all(relationships_data)
        await db.commit()

        print("Seed data inserted successfully!")
        print(f"  Environments: 3")
        print(f"  Teams: 3")
        print(f"  Contacts: {len(contacts)}")
        print(f"  Applications: 6")
        print(f"  Servers: {len(servers)}")
        print(f"  Database Instances: 4")
        print(f"  Endpoints: {len(endpoints_data)}")
        print(f"  Deployments: {len(deployments_data)}")
        print(f"  Ownerships: {len(ownerships)}")
        print(f"  Relationships: {len(relationships_data)}")


if __name__ == "__main__":
    asyncio.run(seed())
