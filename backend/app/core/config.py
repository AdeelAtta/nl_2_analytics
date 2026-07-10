from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # App
    app_name: str = "UPL Backend"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: str = "development"

    # Database
    postgres_dsn: str = "postgresql+asyncpg://openquery:openquery_dev@localhost:5432/openquery"
    postgres_dsn_sync: str = "postgresql://openquery:openquery_dev@localhost:5432/openquery"
    redis_url: str = "redis://localhost:6379/0"
    qdrant_url: str = "http://localhost:6333"
    qdrant_grpc_port: int = 6334
    qdrant_api_key: str = ""

    # Auth
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "RS256"
    jwt_token_ttl: int = 3600

    # Observability
    otel_endpoint: str = "http://localhost:4318"
    log_level: str = "INFO"

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
