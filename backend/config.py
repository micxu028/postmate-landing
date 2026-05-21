from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    app_name: str = "PostMate API"
    debug: bool = False

    # Database — SQLite for local dev, PostgreSQL (Supabase) for production
    # Local: sqlite+aiosqlite:///./postmate.db
    # Production: postgresql+asyncpg://user:pass@host:5432/db
    database_url: str = "sqlite+aiosqlite:///./postmate.db"

    # JWT
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7  # 7 days

    # DeepSeek API
    deepseek_api_key: str = ""
    deepseek_api_url: str = "https://api.deepseek.com/v1/chat/completions"
    deepseek_model: str = "deepseek-chat"

    # MJ Proxy (domestic)
    mj_api_url: str = ""
    mj_api_key: str = ""

    # Brevo SMTP
    smtp_host: str = "smtp-relay.brevo.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    email_from: str = "hello@postmate.net"
    email_from_name: str = "PostMate Team"

    # CORS
    cors_origins: str = "http://localhost:8000,https://postmate.net,https://app.postmate.net"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache()
def get_settings() -> Settings:
    return Settings()
