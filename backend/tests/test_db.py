from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core import db
from app.core.db import SessionDep


@pytest.fixture
def sqlite_sessionmaker(monkeypatch: pytest.MonkeyPatch) -> Iterator[sessionmaker[Session]]:
    """Point get_session at an in-memory SQLite database with one table."""
    engine = create_engine(
        "sqlite://",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE items (x INTEGER)"))
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    monkeypatch.setattr(db, "get_sessionmaker", lambda: factory)
    yield factory
    engine.dispose()


def _write_app() -> FastAPI:
    app = FastAPI()

    @app.post("/items")
    def create_item(session: SessionDep) -> dict[str, bool]:
        session.execute(text("INSERT INTO items VALUES (1)"))
        return {"saved": True}

    return app


def _count(factory: sessionmaker[Session]) -> int:
    with factory() as session:
        return session.execute(text("SELECT COUNT(*) FROM items")).scalar_one()


def test_session_commits_on_success(sqlite_sessionmaker: sessionmaker[Session]) -> None:
    response = TestClient(_write_app()).post("/items")

    assert response.status_code == 200
    assert _count(sqlite_sessionmaker) == 1


def test_failed_commit_is_not_reported_as_success(
    sqlite_sessionmaker: sessionmaker[Session],
) -> None:
    def fail_commit(session: Session) -> None:
        raise RuntimeError("commit failed")

    event.listen(Session, "before_commit", fail_commit)
    try:
        client = TestClient(_write_app(), raise_server_exceptions=False)
        response = client.post("/items")
    finally:
        event.remove(Session, "before_commit", fail_commit)

    assert response.status_code == 500
    assert _count(sqlite_sessionmaker) == 0
