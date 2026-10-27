from functools import lru_cache
from typing import Any, Literal

from pydantic import NonNegativeInt, PositiveInt, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class Settings(BaseSettings):
    """Application settings, read from environment variables (case-insensitive)."""

    model_config = SettingsConfigDict(extra="ignore")

    environment: Literal["development", "test", "production"] = "development"

    postgres_host: str = "db"
    postgres_port: int = 5432
    postgres_user: str
    postgres_password: SecretStr
    postgres_db: str

    # Seconds to wait for a connection before failing (libpq minimum is 2).
    db_connect_timeout: PositiveInt = 5
    # Server-side limit for any single app query; 0 disables it.
    db_statement_timeout_ms: NonNegativeInt = 30_000
    # Limit for a migration waiting on a table lock, so it fails instead of
    # queueing behind long transactions and blocking all traffic; 0 disables it.
    migration_lock_timeout_ms: NonNegativeInt = 5_000

    @property
    def database_url(self) -> URL:
        # URL.create escapes special characters in credentials.
        return URL.create(
            drivername="postgresql+psycopg",
            username=self.postgres_user,
            password=self.postgres_password.get_secret_value(),
            host=self.postgres_host,
            port=self.postgres_port,
            database=self.postgres_db,
        )

    @property
    def app_connect_args(self) -> dict[str, Any]:
        return {
            "connect_timeout": self.db_connect_timeout,
            "options": f"-c statement_timeout={self.db_statement_timeout_ms}",
        }

    @property
    def migration_connect_args(self) -> dict[str, Any]:
        # No statement timeout: data migrations may legitimately run long.
        return {
            "connect_timeout": self.db_connect_timeout,
            "options": f"-c lock_timeout={self.migration_lock_timeout_ms}",
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()
