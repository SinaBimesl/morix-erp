import io
from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.core.db import utcnow
from app.modules.users import cli
from app.modules.users.models import AuthSession
from app.modules.users.permissions import AUDIT_READ
from tests.users.conftest import PASSWORD, Account, Login, MakeUser

AUDIT = "/api/v1/audit-events"


def test_actions_are_audited(admin: Account) -> None:
    created = admin.client.post(
        "/api/v1/users", json={"username": "worker", "full_name": "W", "password": "x" * 12}
    ).json()

    events = admin.client.get(AUDIT).json()
    assert [e["action"] for e in events["items"]][:2] == ["user.created", "auth.login"]
    first = events["items"][0]
    assert first["actor_id"] == str(admin.user.id)
    assert first["entity_id"] == created["id"]
    assert "password" not in str(first["details"]).lower()

    filtered = admin.client.get(AUDIT, params={"action": "auth.login"}).json()
    assert filtered["total"] == 1


def test_audit_filters_need_timezone_and_permission(
    admin: Account, make_user: MakeUser, login: Login
) -> None:
    assert admin.client.get(AUDIT, params={"since": "2026-01-01T00:00:00"}).status_code == 422
    since = admin.client.get(AUDIT, params={"since": "2026-01-01T00:00:00Z"})
    assert since.status_code == 200
    assert login(make_user()).client.get(AUDIT).status_code == 403
    assert login(make_user(permissions=(AUDIT_READ,))).client.get(AUDIT).status_code == 200


def test_cli_creates_superuser(
    sm: sessionmaker[Session],
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr("sys.stdin", io.StringIO(PASSWORD + "\n"))

    code = cli.main(["create-superuser", "--username", "Owner", "--full-name", "Shop Owner"])

    assert code == 0
    assert "Created superuser owner" in capsys.readouterr().out
    me = client.post("/api/v1/auth/login", json={"username": "owner", "password": PASSWORD})
    assert me.json()["user"]["is_superuser"] is True


@pytest.mark.parametrize(
    ("username", "password", "error"),
    [
        ("owner", "short", "at least 12"),
        ("x", PASSWORD, "pattern"),
        ("ownerowner12", "OWNEROWNER12", "must not equal"),
    ],
)
def test_cli_rejects_invalid_input(
    sm: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    username: str,
    password: str,
    error: str,
) -> None:
    monkeypatch.setattr("sys.stdin", io.StringIO(password + "\n"))

    assert cli.main(["create-superuser", "--username", username, "--full-name", "X"]) == 1
    assert error in capsys.readouterr().err


def test_cli_refuses_duplicate(
    sm: sessionmaker[Session],
    make_user: MakeUser,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    make_user("owner")
    monkeypatch.setattr("sys.stdin", io.StringIO(PASSWORD + "\n"))

    assert cli.main(["create-superuser", "--username", "owner", "--full-name", "X"]) == 1
    assert "already exists" in capsys.readouterr().err


def test_cli_prunes_old_sessions(
    sm: sessionmaker[Session],
    make_user: MakeUser,
    login: Login,
    capsys: pytest.CaptureFixture[str],
) -> None:
    old, current, recent_logout = (login(make_user()) for _ in range(3))
    now = utcnow()
    with sm() as session, session.begin():
        rows = {s.user_id: s for s in session.scalars(select(AuthSession))}
        rows[old.user.id].expires_at = now - timedelta(days=31)
        rows[recent_logout.user.id].revoked_at = now - timedelta(days=1)

    assert cli.main(["prune-sessions"]) == 0

    assert "Deleted 1 sessions" in capsys.readouterr().out
    with sm() as session:
        remaining = set(session.scalars(select(AuthSession.user_id)))
    assert remaining == {current.user.id, recent_logout.user.id}
