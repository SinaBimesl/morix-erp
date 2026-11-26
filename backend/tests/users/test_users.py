import uuid

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app.modules.users.models import Department, User
from app.modules.users.permissions import (
    ROLES_MANAGE,
    USERS_ASSIGN_ROLES,
    USERS_MANAGE,
    USERS_READ,
)
from tests.users.conftest import PASSWORD, Account, Login, MakeUser

USERS = "/api/v1/users"
NEW_USER = {"username": "Painter.One", "full_name": "Pat Painter", "password": "x" * 12}


def _role(admin: Account, code: str, permissions: list[str]) -> str:
    response = admin.client.post(
        "/api/v1/roles", json={"code": code, "name": code, "permissions": permissions}
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_create_user(admin: Account, sm: sessionmaker[Session]) -> None:
    with sm() as session, session.begin():
        department = Department(code="paint", name="Painting")
        session.add(department)
    role_id = _role(admin, "painter", [USERS_READ])

    response = admin.client.post(
        USERS,
        json={**NEW_USER, "email": "Pat@Example.COM", "department_id": str(department.id),
              "job_title": "Finisher", "role_ids": [role_id]},
    )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["username"] == "painter.one"
    assert body["email"] == "pat@example.com"
    assert body["must_change_password"] is True
    assert body["is_superuser"] is False
    assert [r["code"] for r in body["roles"]] == ["painter"]
    assert "password" not in body and "password_hash" not in body


def test_create_user_validation_and_conflicts(admin: Account) -> None:
    assert admin.client.post(USERS, json=NEW_USER).status_code == 201

    duplicate = admin.client.post(USERS, json={**NEW_USER, "username": "PAINTER.ONE"})
    assert duplicate.status_code == 409
    admin.client.post(USERS, json={**NEW_USER, "username": "a.user", "email": "a@example.com"})
    same_email = admin.client.post(
        USERS, json={**NEW_USER, "username": "b.user", "email": "A@example.com"}
    )
    assert same_email.status_code == 409

    for bad in (
        {"username": "x"},  # too short
        {"username": "has space"},
        {"password": "short"},
        {"email": "not-an-email"},
        {"role_ids": ["00000000-0000-0000-0000-000000000000"]},
        {"department_id": "00000000-0000-0000-0000-000000000000"},
    ):
        response = admin.client.post(USERS, json={**NEW_USER, "username": "valid.name", **bad})
        assert response.status_code == 422, bad


def test_list_users_filters_and_paginates(admin: Account, make_user: MakeUser) -> None:
    make_user("alice", email="alice@example.com")
    make_user("bob", is_active=False)
    make_user("carol")

    page = admin.client.get(USERS, params={"limit": 2}).json()
    assert page["total"] == 4 and len(page["items"]) == 2 and page["limit"] == 2
    assert [u["username"] for u in page["items"]] == ["admin", "alice"]

    def names(**params: object) -> list[str]:
        return [u["username"] for u in admin.client.get(USERS, params=params).json()["items"]]

    assert names(q="ALICE@") == ["alice"]
    assert names(is_active=False) == ["bob"]
    assert names(offset=3) == ["carol"]
    assert admin.client.get(USERS, params={"limit": 0}).status_code == 422


def test_permissions_are_enforced(make_user: MakeUser, login: Login) -> None:
    reader = login(make_user(permissions=(USERS_READ,)))
    nobody = login(make_user())

    assert reader.client.get(USERS).status_code == 200
    assert reader.client.post(USERS, json=NEW_USER).status_code == 403
    denied = nobody.client.get(USERS)
    assert denied.status_code == 403
    assert denied.json() == {"detail": f"missing permission: {USERS_READ}"}


def test_update_user(admin: Account, make_user: MakeUser) -> None:
    user = make_user(email="old@example.com")

    response = admin.client.patch(
        f"{USERS}/{user.id}", json={"full_name": "  New Name ", "email": None, "phone": "+1 555"}
    )

    assert response.status_code == 200
    body = response.json()
    assert (body["full_name"], body["email"], body["phone"]) == ("New Name", None, "+1 555")
    null_name = admin.client.patch(f"{USERS}/{user.id}", json={"full_name": None})
    assert null_name.status_code == 422
    missing = admin.client.patch(f"{USERS}/00000000-0000-0000-0000-000000000000", json={})
    assert missing.status_code == 404


def test_deactivation_signs_user_out(admin: Account, make_user: MakeUser, login: Login) -> None:
    account = login(make_user())

    response = admin.client.patch(f"{USERS}/{account.user.id}", json={"is_active": False})

    assert response.status_code == 200
    assert account.client.get("/api/v1/auth/me").status_code == 401


def test_cannot_deactivate_self_or_last_superuser(admin: Account, make_user: MakeUser) -> None:
    me = f"{USERS}/{admin.user.id}"
    assert admin.client.patch(me, json={"is_active": False}).status_code == 409
    assert admin.client.patch(me, json={"is_superuser": False}).status_code == 409

    make_user("backup", is_superuser=True)
    assert admin.client.patch(me, json={"is_superuser": False}).status_code == 200


def test_only_superusers_manage_superusers(
    admin: Account, make_user: MakeUser, login: Login
) -> None:
    manager = login(make_user(permissions=(USERS_MANAGE, USERS_READ)))
    target = f"{USERS}/{admin.user.id}"

    assert manager.client.post(USERS, json={**NEW_USER, "is_superuser": True}).status_code == 403
    assert manager.client.patch(target, json={"full_name": "Hacked"}).status_code == 403
    reset = manager.client.post(f"{target}/reset-password", json={"new_password": "y" * 12})
    assert reset.status_code == 403
    own = manager.client.patch(f"{USERS}/{manager.user.id}", json={"is_superuser": True})
    assert own.status_code == 403


def test_reset_password(admin: Account, make_user: MakeUser, login: Login, client: TestClient) -> None:
    account = login(make_user("worker"))

    response = admin.client.post(
        f"{USERS}/{account.user.id}/reset-password", json={"new_password": "temporary pass"}
    )

    assert response.status_code == 204
    assert account.client.get("/api/v1/auth/me").status_code == 401
    relogin = client.post(
        "/api/v1/auth/login", json={"username": "worker", "password": "temporary pass"}
    )
    assert relogin.json()["user"]["must_change_password"] is True


def test_unlock(admin: Account, make_user: MakeUser, client: TestClient) -> None:
    user = make_user("worker")
    for _ in range(5):
        client.post("/api/v1/auth/login", json={"username": "worker", "password": "wrong!!"})

    response = admin.client.post(f"{USERS}/{user.id}/unlock")

    assert response.json()["locked_until"] is None
    ok = client.post("/api/v1/auth/login", json={"username": "worker", "password": PASSWORD})
    assert ok.status_code == 200


def test_set_roles(admin: Account, make_user: MakeUser) -> None:
    user = make_user()
    a, b = _role(admin, "ra", [USERS_READ]), _role(admin, "rb", [])

    first = admin.client.put(f"{USERS}/{user.id}/roles", json={"role_ids": [b, a]})
    cleared = admin.client.put(f"{USERS}/{user.id}/roles", json={"role_ids": []})

    assert [r["code"] for r in first.json()["roles"]] == ["ra", "rb"]
    assert cleared.json()["roles"] == []


def test_role_assignment_cannot_escalate(
    admin: Account, make_user: MakeUser, login: Login
) -> None:
    powerful = _role(admin, "role-admin", [ROLES_MANAGE])
    harmless = _role(admin, "reader", [USERS_READ])
    assigner = login(make_user(permissions=(USERS_ASSIGN_ROLES, USERS_READ)))
    url = f"{USERS}/{assigner.user.id}/roles"

    escalate = assigner.client.put(url, json={"role_ids": [powerful]})
    assert escalate.status_code == 403
    assert ROLES_MANAGE in escalate.json()["detail"]

    target = make_user()
    ok = assigner.client.put(f"{USERS}/{target.id}/roles", json={"role_ids": [harmless]})
    assert ok.status_code == 200


def test_create_with_roles_requires_assign_permission(
    admin: Account, make_user: MakeUser, login: Login
) -> None:
    role_id = _role(admin, "reader", [USERS_READ])
    manager = login(make_user(permissions=(USERS_MANAGE, USERS_READ)))

    response = manager.client.post(USERS, json={**NEW_USER, "role_ids": [role_id]})

    assert response.status_code == 403


def test_user_fields_round_trip(admin: Account, sm: sessionmaker[Session]) -> None:
    created = admin.client.post(USERS, json=NEW_USER).json()
    with sm() as session:
        user = session.get_one(User, uuid.UUID(created["id"]))
        assert user.password_hash.startswith("$argon2id$")
        assert user.created_at.tzinfo is not None


def test_cannot_manage_user_with_more_permissions(
    make_user: MakeUser, login: Login
) -> None:
    manager = login(make_user(permissions=(USERS_MANAGE, USERS_READ)))
    stronger = make_user(permissions=(USERS_READ, ROLES_MANAGE))
    peer = make_user(permissions=(USERS_READ,))
    reset = {"new_password": "taken over now"}

    takeover = manager.client.post(f"{USERS}/{stronger.id}/reset-password", json=reset)
    assert takeover.status_code == 403
    assert ROLES_MANAGE in takeover.json()["detail"]
    assert manager.client.patch(f"{USERS}/{stronger.id}", json={"is_active": False}).status_code == 403

    assert manager.client.post(f"{USERS}/{peer.id}/reset-password", json=reset).status_code == 204


def test_update_own_profile(admin: Account, make_user: MakeUser, login: Login) -> None:
    make_user("other", email="taken@example.com")
    account = login(make_user(email="me@example.com"))

    response = account.client.patch(
        "/api/v1/auth/me", json={"full_name": "Renamed", "phone": "123", "email": None}
    )

    assert response.status_code == 200
    body = response.json()
    assert (body["full_name"], body["phone"], body["email"]) == ("Renamed", "123", None)
    taken = account.client.patch("/api/v1/auth/me", json={"email": "TAKEN@example.com"})
    assert taken.status_code == 409
    # Privileged fields are rejected here.
    assert account.client.patch("/api/v1/auth/me", json={"is_superuser": True}).status_code == 422
    assert account.client.get("/api/v1/auth/me").json()["is_superuser"] is False
