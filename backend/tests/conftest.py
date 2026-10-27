from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import create_app

TEST_ENV = {
    "ENVIRONMENT": "test",
    "POSTGRES_HOST": "localhost",
    "POSTGRES_PORT": "5432",
    "POSTGRES_USER": "test_user",
    "POSTGRES_PASSWORD": "test_password",
    "POSTGRES_DB": "test_db",
}


@pytest.fixture(autouse=True)
def test_env(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Isolate every test from the host environment and the settings cache."""
    for key in TEST_ENV:
        monkeypatch.delenv(key, raising=False)
    for key, value in TEST_ENV.items():
        monkeypatch.setenv(key, value)
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def app() -> FastAPI:
    return create_app()


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    with TestClient(app) as c:
        yield c
