from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Secret key for security-related features (e.g. signing tokens)
    secret_key: str

    # SQLite database file path (used to build sqlite:/// URL)
    sqlite_database_url: str = "vaultkeep.db"

    # Full PostgreSQL connection string, e.g.:
    # postgresql+psycopg2://user:password@localhost:5432/vaultkeep
    pg_database_url: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()


# Convenience, so other modules can do `from settings import settings`
settings = get_settings()
