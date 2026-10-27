import pytest
from pydantic import ValidationError

from app.core.config import Settings, get_settings


def test_reads_environment() -> None:
    settings = Settings()

    assert settings.environment == "test"
    assert settings.postgres_host == "localhost"
    assert settings.postgres_port == 5432
    assert settings.postgres_user == "test_user"
    assert settings.postgres_password.get_secret_value() == "test_password"
    assert settings.postgres_db == "test_db"


def test_defaults_when_optional_vars_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in ("ENVIRONMENT", "POSTGRES_HOST", "POSTGRES_PORT"):
        monkeypatch.delenv(key)

    settings = Settings()

    assert settings.environment == "development"
    assert settings.postgres_host == "db"
    assert settings.postgres_port == 5432


def test_missing_required_var_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("POSTGRES_PASSWORD")

    with pytest.raises(ValidationError):
        Settings()


def test_invalid_environment_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENVIRONMENT", "staging")

    with pytest.raises(ValidationError):
        Settings()


def test_database_url_uses_psycopg_and_escapes_password(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("POSTGRES_PASSWORD", "p@ss:w/rd")

    url = Settings().database_url

    assert url.drivername == "postgresql+psycopg"
    assert url.password == "p@ss:w/rd"
    assert "p%40ss%3Aw%2Frd" in url.render_as_string(hide_password=False)


def test_password_not_exposed() -> None:
    settings = Settings()

    assert "test_password" not in repr(settings)
    assert "test_password" not in str(settings.database_url)


def test_get_settings_is_cached() -> None:
    assert get_settings() is get_settings()
