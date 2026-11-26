"""Fixtures for User Manager tests: a migrated SQLite database and signed-in clients."""

from collections.abc import Callable, Iterator
from dataclasses import dataclass
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from argon2 import PasswordHasher
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core import db
from app.modules.users import security
from app.modules.users.models import Role, RolePermission, User

ALEMBIC_INI = Path(__file__).resolve().parents[2] / "alembic.ini"
PASSWORD = "correct horse battery"


def migrated_engine() -> Engine:
    """In-memory SQLite with foreign keys on, schema built by the real migrations."""
    engine = create_engine(
        "sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False}
    )
    event.listen(engine, "connect", lambda conn, _: conn.execute("PRAGMA foreign_keys=ON"))
    config = Config(str(ALEMBIC_INI))
    with engine.begin() as connection:
        config.attributes["connection"] = connection
        command.upgrade(config, "head")
    return engine


@pytest.fixture
def sm(monkeypatch: pytest.MonkeyPatch) -> Iterator[sessionmaker[Session]]:
    engine = migrated_engine()
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    monkeypatch.setattr(db, "get_sessionmaker", lambda: factory)
    # Cheap Argon2 parameters; production cost would make the suite slow.
    monkeypatch.setattr(security, "hasher", PasswordHasher(time_cost=1, memory_cost=8, parallelism=1))
    yield factory
    engine.dispose()


@dataclass
class Account:
    user: User
    client: TestClient
    token: str


MakeUser = Callable[..., User]
Login = Callable[[User], Account]


@pytest.fixture
def make_user(sm: sessionmaker[Session]) -> MakeUser:
    counter = iter(range(1, 10_000))

    def make(
        username: str | None = None,
        *,
        permissions: tuple[str, ...] = (),
        password: str = PASSWORD,
        **fields: object,
    ) -> User:
        with sm() as session, session.begin():
            n = next(counter)
            roles = []
            if permissions:
                roles = [
                    Role(
                        code=f"role-{n}",
                        name=f"Role {n}",
                        permission_rows=[RolePermission(permission=p) for p in permissions],
                    )
                ]
            user = User(
                username=username or f"user{n}",
                full_name=f"User {n}",
                password_hash=security.hash_password(password),
                roles=roles,
                **fields,
            )
            session.add(user)
        return user

    return make


@pytest.fixture
def login(client: TestClient) -> Login:
    def do(user: User, password: str = PASSWORD) -> Account:
        response = client.post(
            "/api/v1/auth/login", json={"username": user.username, "password": password}
        )
        assert response.status_code == 200, response.text
        token = response.json()["access_token"]
        signed_in = TestClient(client.app, headers={"Authorization": f"Bearer {token}"})
        return Account(user, signed_in, token)

    return do


@pytest.fixture
def admin(make_user: MakeUser, login: Login) -> Account:
    return login(make_user("admin", is_superuser=True))
