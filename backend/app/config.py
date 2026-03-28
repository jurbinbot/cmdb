from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://cmdb:cmdb@localhost:5432/cmdb"
    cors_origins: list[str] = ["http://localhost:5173"]
    probe_aggregator_url: str = "http://localhost:8000"
    github_pat: str = ""
    secret_key: str = "changeme"

    class Config:
        env_file = ".env"


settings = Settings()
