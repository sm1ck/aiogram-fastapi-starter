from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    bot_token: str
    openrouter_api_key: str
    redis_url: str = "redis://redis:6379/0"
    postgres_url: str = "postgresql+asyncpg://postgres:postgres@postgres:5432/bot"
    chromadb_host: str = "chromadb"
    chromadb_port: int = 8000


settings = Settings()  # type: ignore[call-arg]
