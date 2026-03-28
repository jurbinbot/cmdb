import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from ..models.application import AppType, AppStatus, AppTier, EnvType


class EnvironmentBase(BaseModel):
    name: str
    env_type: EnvType
    description: Optional[str] = None


class EnvironmentCreate(EnvironmentBase):
    pass


class EnvironmentUpdate(BaseModel):
    name: Optional[str] = None
    env_type: Optional[EnvType] = None
    description: Optional[str] = None


class EnvironmentResponse(EnvironmentBase):
    id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class DeploymentBase(BaseModel):
    application_id: uuid.UUID
    environment_id: uuid.UUID
    version: str
    deployed_by: Optional[str] = None
    ci_cd_url: Optional[str] = None
    notes: Optional[str] = None
    is_current: bool = False


class DeploymentCreate(DeploymentBase):
    pass


class DeploymentUpdate(BaseModel):
    version: Optional[str] = None
    deployed_by: Optional[str] = None
    ci_cd_url: Optional[str] = None
    notes: Optional[str] = None
    is_current: Optional[bool] = None


class DeploymentResponse(DeploymentBase):
    id: uuid.UUID
    deployed_at: datetime
    created_at: datetime
    environment: Optional[EnvironmentResponse] = None

    model_config = {"from_attributes": True}


class ApplicationBase(BaseModel):
    name: str
    description: Optional[str] = None
    app_type: AppType
    status: AppStatus = AppStatus.active
    tier: AppTier = AppTier.tier3
    repo_url: Optional[str] = None
    docs_url: Optional[str] = None


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    app_type: Optional[AppType] = None
    status: Optional[AppStatus] = None
    tier: Optional[AppTier] = None
    repo_url: Optional[str] = None
    docs_url: Optional[str] = None


class ApplicationResponse(ApplicationBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    deployment_count: int = 0
    endpoint_count: int = 0
    owner_count: int = 0

    model_config = {"from_attributes": True}


class ApplicationDetailResponse(ApplicationResponse):
    deployments: List[DeploymentResponse] = []
    endpoints: List[dict] = []
    ownerships: List[dict] = []
