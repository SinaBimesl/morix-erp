from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.core.db import get_engine, get_sessionmaker
from app.main import create_app

TEST_ENV = {
    "ENVIRONMENT": "test",
    "POSTGRES_HOST": "localhost",
    "POSTGRES_PORT": "5432",
    "POSTGRES_USER": "test_user",
    "POSTGRES_PASSWORD": "test_password",
    "POSTGRES_DB": "test_db",
}
OPTIONAL_ENV = (
    "DB_CONNECT_TIMEOUT",
    "DB_STATEMENT_TIMEOUT_MS",
    "MIGRATION_LOCK_TIMEOUT_MS",
)


@pytest.fixture(autouse=True)
def test_env(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Isolate every test from the host environment and cached settings/engine."""
    for key in (*TEST_ENV, *OPTIONAL_ENV):
        monkeypatch.delenv(key, raising=False)
    for key, value in TEST_ENV.items():
        monkeypatch.setenv(key, value)
    _clear_caches()
    yield
    _clear_caches()


def _clear_caches() -> None:
    get_settings.cache_clear()
    get_sessionmaker.cache_clear()
    get_engine.cache_clear()


@pytest.fixture
def app() -> FastAPI:
    return create_app()


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    with TestClient(app) as c:
        yield c
