from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DATABASE_URL: str = "postgresql+asyncpg://cmdb:cmdb@localhost:5432/cmdb"
    CORS_ORIGINS: str = "http://localhost:5173"
    PROBE_AGGREGATOR_URL: str = "http://localhost:8000"
    GITHUB_PAT: str = ""
    SECRET_KEY: str = "changeme"

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]


settings = Settings()
