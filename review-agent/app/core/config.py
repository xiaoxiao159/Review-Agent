from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "review-agent"
    app_env: str = Field(default="dev", alias="APP_ENV")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")

    postgres_dsn: str = Field(
        default="postgresql+asyncpg://postgres:postgres@postgres:5432/review_agent",
        alias="POSTGRES_DSN",
    )
    redis_url: str = Field(default="redis://redis:6379/0", alias="REDIS_URL")
    chroma_path: str = Field(default="./.chroma", alias="CHROMA_PATH")

    jwt_secret: str = Field(default="change-me", alias="JWT_SECRET")
    jwt_refresh_secret: str = Field(default="change-me-refresh", alias="JWT_REFRESH_SECRET")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_ttl_minutes: int = Field(default=15, alias="ACCESS_TOKEN_TTL_MINUTES")
    refresh_token_ttl_days: int = Field(default=7, alias="REFRESH_TOKEN_TTL_DAYS")

    default_admin_username: str = Field(default="admin", alias="DEFAULT_ADMIN_USERNAME")
    default_admin_email: str = Field(default="admin@example.com", alias="DEFAULT_ADMIN_EMAIL")
    default_admin_password: str = Field(default="Admin@123456", alias="DEFAULT_ADMIN_PASSWORD")
    default_admin_enabled: bool = Field(default=True, alias="DEFAULT_ADMIN_ENABLED")

    dashscope_api_key: str = Field(default="", alias="DASHSCOPE_API_KEY")
    llm_model: str = Field(default="qwen-max", alias="LLM_MODEL")
    embedding_model: str = Field(default="text-embedding-v3", alias="EMBEDDING_MODEL")

    celery_broker_url: str = Field(default="redis://redis:6379/1", alias="CELERY_BROKER_URL")
    celery_result_backend: str = Field(default="redis://redis:6379/2", alias="CELERY_RESULT_BACKEND")


@lru_cache
def get_settings() -> Settings:
    return Settings()
