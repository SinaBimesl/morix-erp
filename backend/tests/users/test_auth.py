from datetime import timedelta

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.core.audit import AuditEvent
from app.core.db import utcnow
from app.modules.users.models import AuthSession, User
from app.modules.users.permissions import USERS_READ
from tests.users.conftest import PASSWORD, Login, MakeUser

LOGIN = "/api/v1/auth/login"
INVALID = {"detail": "Invalid username or password"}


def _login(client: TestClient, username: str, password: str = PASSWORD):
    return client.post(LOGIN, json={"username": username, "password": password})


def _reload(sm: sessionmaker[Session], user: User) -> User:
    with sm() as session:
        return session.get_one(User, user.id)


def test_login_returns_token_and_permissions(
    client: TestClient, make_user: MakeUser, sm: sessionmaker[Session]
) -> None:
    user = make_user("luthier", permissions=(USERS_READ,))

    response = _login(client, "  LUTHIER ")  # case and whitespace insensitive

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["user"]["username"] == "luthier"
    assert body["user"]["permissions"] == [USERS_READ]
    assert _reload(sm, user).last_login_at is not None
    with sm() as session:
        stored = session.scalars(select(AuthSession.token_hash)).one()
    assert stored != body["access_token"]  # only the hash is stored


def test_wrong_password_and_unknown_user_look_the_same(
    client: TestClient, make_user: MakeUser, sm: sessionmaker[Session]
) -> None:
    user = make_user("luthier")

    wrong = _login(client, "luthier", "not the password")
    unknown = _login(client, "nobody")

    assert wrong.status_code == unknown.status_code == 401
    assert wrong.json() == unknown.json() == INVALID
    assert _reload(sm, user).failed_login_count == 1
    with sm() as session:
        reasons = [e.details["reason"] for e in session.scalars(select(AuditEvent))]
    assert sorted(reasons) == ["bad_password", "unknown_user"]


def test_account_locks_after_repeated_failures(
    client: TestClient, make_user: MakeUser, sm: sessionmaker[Session]
) -> None:
    user = make_user("luthier")
    for _ in range(5):
        assert _login(client, "luthier", "wrong password!").status_code == 401

    # Locked: even the right password is refused, with the same response.
    response = _login(client, "luthier")
    assert response.status_code == 401
    assert response.json() == INVALID
    assert _reload(sm, user).locked_until is not None

    with sm() as session, session.begin():
        session.get_one(User, user.id).locked_until = utcnow() - timedelta(seconds=1)
    assert _login(client, "luthier").status_code == 200
    assert _reload(sm, user).failed_login_count == 0


def test_inactive_user_cannot_login(client: TestClient, make_user: MakeUser) -> None:
    make_user("former", is_active=False)

    response = _login(client, "former")

    assert response.status_code == 401
    assert response.json() == INVALID


def test_protected_route_requires_token(client: TestClient, sm: sessionmaker[Session]) -> None:
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
    bad = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer nope"})
    assert bad.status_code == 401


def test_logout_revokes_token(make_user: MakeUser, login: Login) -> None:
    account = login(make_user())

    assert account.client.post("/api/v1/auth/logout").status_code == 204
    assert account.client.get("/api/v1/auth/me").status_code == 401


def test_expired_session_is_rejected(
    make_user: MakeUser, login: Login, sm: sessionmaker[Session]
) -> None:
    account = login(make_user())
    with sm() as session, session.begin():
        for row in session.scalars(select(AuthSession)):
            row.expires_at = utcnow() - timedelta(seconds=1)

    assert account.client.get("/api/v1/auth/me").status_code == 401


def test_deactivated_user_token_stops_working(
    make_user: MakeUser, login: Login, sm: sessionmaker[Session]
) -> None:
    account = login(make_user())
    with sm() as session, session.begin():
        session.get_one(User, account.user.id).is_active = False

    assert account.client.get("/api/v1/auth/me").status_code == 401


def test_pending_password_change_blocks_other_routes(make_user: MakeUser, login: Login) -> None:
    account = login(make_user(permissions=(USERS_READ,), must_change_password=True))

    assert account.client.get("/api/v1/auth/me").status_code == 200
    blocked = account.client.get("/api/v1/users")
    assert blocked.status_code == 403
    assert blocked.json() == {"detail": "password change required"}

    changed = account.client.post(
        "/api/v1/auth/change-password",
        json={"current_password": PASSWORD, "new_password": "a brand new passphrase"},
    )
    assert changed.status_code == 204
    assert account.client.get("/api/v1/users").status_code == 200


def test_change_password_revokes_other_sessions(
    client: TestClient, make_user: MakeUser, login: Login
) -> None:
    user = make_user("luthier")
    first = login(user)
    second = login(user)

    response = first.client.post(
        "/api/v1/auth/change-password",
        json={"current_password": PASSWORD, "new_password": "a brand new passphrase"},
    )

    assert response.status_code == 204
    assert first.client.get("/api/v1/auth/me").status_code == 200
    assert second.client.get("/api/v1/auth/me").status_code == 401
    assert _login(client, "luthier").status_code == 401
    assert _login(client, "luthier", "a brand new passphrase").status_code == 200


def test_change_password_validation(make_user: MakeUser, login: Login) -> None:
    account = login(make_user("workshopadmin"))
    url = "/api/v1/auth/change-password"

    wrong = account.client.post(url, json={"current_password": "nope", "new_password": "x" * 12})
    same = account.client.post(url, json={"current_password": PASSWORD, "new_password": PASSWORD})
    short = account.client.post(url, json={"current_password": PASSWORD, "new_password": "short"})
    username = account.client.post(
        url, json={"current_password": PASSWORD, "new_password": "WorkshopAdmin"}
    )

    assert [r.status_code for r in (wrong, same, short, username)] == [400, 400, 422, 400]
