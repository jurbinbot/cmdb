"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-03-28

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # environments
    op.create_table('environments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('env_type', sa.Enum('development', 'staging', 'production', 'dr', name='envtype'), nullable=False),
        sa.Column('description', sa.String(512), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    # applications
    op.create_table('applications',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('app_type', sa.Enum('service', 'frontend', 'backend', 'library', 'database', 'infrastructure', name='apptype'), nullable=False),
        sa.Column('status', sa.Enum('active', 'deprecated', 'decommissioned', 'planned', name='appstatus'), nullable=False),
        sa.Column('tier', sa.Enum('tier1', 'tier2', 'tier3', 'internal', name='apptier'), nullable=False),
        sa.Column('repo_url', sa.String(512), nullable=True),
        sa.Column('docs_url', sa.String(512), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    # deployments
    op.create_table('deployments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('application_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('environment_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('version', sa.String(255), nullable=False),
        sa.Column('deployed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deployed_by', sa.String(255), nullable=True),
        sa.Column('ci_cd_url', sa.String(512), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_current', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ),
        sa.ForeignKeyConstraint(['environment_id'], ['environments.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    # servers
    op.create_table('servers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('hostname', sa.String(255), nullable=False),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('os', sa.String(255), nullable=True),
        sa.Column('server_type', sa.Enum('physical', 'virtual', 'container', 'cloud', name='servertype'), nullable=False),
        sa.Column('environment_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('role', sa.String(255), nullable=True),
        sa.Column('status', sa.Enum('active', 'decommissioned', 'maintenance', name='serverstatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['environment_id'], ['environments.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    # database_instances
    op.create_table('database_instances',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('db_type', sa.Enum('postgresql', 'mysql', 'mssql', 'mongodb', 'redis', 'elasticsearch', 'other', name='dbtype'), nullable=False),
        sa.Column('host', sa.String(255), nullable=False),
        sa.Column('port', sa.Integer(), nullable=True),
        sa.Column('environment_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('status', sa.Enum('active', 'decommissioned', name='dbstatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['environment_id'], ['environments.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    # teams
    op.create_table('teams',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slack_channel', sa.String(255), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    # contacts
    op.create_table('contacts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('phone', sa.String(50), nullable=True),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('role', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    # application_ownerships
    op.create_table('application_ownerships',
        sa.Column('application_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('ownership_type', sa.Enum('primary', 'secondary', name='ownershiptype'), nullable=False),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ),
        sa.PrimaryKeyConstraint('application_id', 'team_id')
    )
    # endpoints
    op.create_table('endpoints',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('application_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('url', sa.String(512), nullable=False),
        sa.Column('protocol', sa.Enum('http', 'https', 'grpc', 'tcp', name='protocol'), nullable=False),
        sa.Column('environment_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=True),
        sa.Column('description', sa.String(512), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ),
        sa.ForeignKeyConstraint(['environment_id'], ['environments.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    # ci_relationships
    op.create_table('ci_relationships',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('source_ci_type', sa.String(100), nullable=False),
        sa.Column('source_ci_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('target_ci_type', sa.String(100), nullable=False),
        sa.Column('target_ci_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('relationship_type', sa.Enum('depends_on', 'hosted_on', 'connects_to', 'owned_by', 'deployed_on', 'uses_database', 'exposes_endpoint', name='relationshiptype'), nullable=False),
        sa.Column('description', sa.String(512), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    # audit_logs
    op.create_table('audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('ci_type', sa.String(100), nullable=False),
        sa.Column('ci_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('action', sa.Enum('create', 'update', 'delete', name='auditaction'), nullable=False),
        sa.Column('changed_by', sa.String(255), nullable=False),
        sa.Column('changed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('before_json', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('after_json', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('ci_relationships')
    op.drop_table('endpoints')
    op.drop_table('application_ownerships')
    op.drop_table('contacts')
    op.drop_table('teams')
    op.drop_table('database_instances')
    op.drop_table('servers')
    op.drop_table('deployments')
    op.drop_table('applications')
    op.drop_table('environments')
    # drop enums
    for enum_name in ['envtype', 'apptype', 'appstatus', 'apptier', 'servertype', 'serverstatus', 'dbtype', 'dbstatus', 'protocol', 'ownershiptype', 'relationshiptype', 'auditaction']:
        op.execute(f'DROP TYPE IF EXISTS {enum_name}')
