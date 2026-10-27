from functools import lru_cache
from typing import Literal

from pydantic import SecretStr
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


@lru_cache
def get_settings() -> Settings:
    return Settings()
