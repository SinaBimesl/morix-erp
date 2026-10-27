from collections.abc import Iterator
from unittest.mock import MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app.core.db import get_session


def test_health_ok(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def _override_session(app: FastAPI, session: MagicMock) -> None:
    def fake_session() -> Iterator[MagicMock]:
        yield session

    app.dependency_overrides[get_session] = fake_session


def test_health_db_ok(app: FastAPI, client: TestClient) -> None:
    session = MagicMock()
    _override_session(app, session)

    response = client.get("/health/db")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}
    session.execute.assert_called_once()


def test_health_db_unavailable(app: FastAPI, client: TestClient) -> None:
    session = MagicMock()
    session.execute.side_effect = OperationalError("SELECT 1", {}, Exception("down"))
    _override_session(app, session)

    response = client.get("/health/db")

    assert response.status_code == 503
    assert response.json() == {"detail": "Database unavailable"}
