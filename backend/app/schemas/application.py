import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.application import AppType, AppStatus, Tier, EnvType


class ApplicationCreate(BaseModel):
    name: str
    description: Optional[str] = None
    app_type: AppType = AppType.service
    status: AppStatus = AppStatus.active
    tier: Tier = Tier.tier2
    repo_url: Optional[str] = None
    docs_url: Optional[str] = None


class ApplicationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    app_type: Optional[AppType] = None
    status: Optional[AppStatus] = None
    tier: Optional[Tier] = None
    repo_url: Optional[str] = None
    docs_url: Optional[str] = None


class ApplicationResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str]
    app_type: AppType
    status: AppStatus
    tier: Tier
    repo_url: Optional[str]
    docs_url: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EnvironmentCreate(BaseModel):
    name: str
    env_type: EnvType
    description: Optional[str] = None


class EnvironmentUpdate(BaseModel):
    name: Optional[str] = None
    env_type: Optional[EnvType] = None
    description: Optional[str] = None


class EnvironmentResponse(BaseModel):
    id: uuid.UUID
    name: str
    env_type: EnvType
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class DeploymentCreate(BaseModel):
    application_id: uuid.UUID
    environment_id: uuid.UUID
    version: str
    deployed_by: Optional[str] = None
    ci_cd_url: Optional[str] = None
    notes: Optional[str] = None
    is_current: bool = False


class DeploymentUpdate(BaseModel):
    version: Optional[str] = None
    deployed_by: Optional[str] = None
    ci_cd_url: Optional[str] = None
    notes: Optional[str] = None
    is_current: Optional[bool] = None


class DeploymentResponse(BaseModel):
    id: uuid.UUID
    application_id: uuid.UUID
    environment_id: uuid.UUID
    version: str
    deployed_at: datetime
    deployed_by: Optional[str]
    ci_cd_url: Optional[str]
    notes: Optional[str]
    is_current: bool
    created_at: datetime

    class Config:
        from_attributes = True
