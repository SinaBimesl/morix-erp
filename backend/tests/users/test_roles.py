from app.modules.users.permissions import (
    AUDIT_READ,
    PERMISSIONS,
    ROLES_MANAGE,
    ROLES_READ,
    USERS_READ,
)
from tests.users.conftest import Account, Login, MakeUser

ROLES = "/api/v1/roles"


def test_permission_catalog(admin: Account) -> None:
    response = admin.client.get("/api/v1/permissions")

    assert response.status_code == 200
    assert {p["code"] for p in response.json()} == set(PERMISSIONS)


def test_role_crud(admin: Account) -> None:
    created = admin.client.post(
        ROLES,
        json={"code": "Sales-Rep", "name": "Sales rep", "permissions": [USERS_READ, USERS_READ]},
    )
    assert created.status_code == 201, created.text
    role = created.json()
    assert role["code"] == "sales-rep"
    assert role["permissions"] == [USERS_READ]

    updated = admin.client.patch(
        f"{ROLES}/{role['id']}", json={"description": "Front desk", "permissions": [AUDIT_READ]}
    )
    assert updated.json()["permissions"] == [AUDIT_READ]
    assert updated.json()["description"] == "Front desk"
    assert [r["code"] for r in admin.client.get(ROLES).json()] == ["sales-rep"]

    assert admin.client.delete(f"{ROLES}/{role['id']}").status_code == 204
    assert admin.client.get(f"{ROLES}/{role['id']}").status_code == 404


def test_role_validation(admin: Account) -> None:
    admin.client.post(ROLES, json={"code": "dup", "name": "Dup"})

    assert admin.client.post(ROLES, json={"code": "dup", "name": "Again"}).status_code == 409
    unknown = admin.client.post(ROLES, json={"code": "x1", "name": "X", "permissions": ["nope"]})
    assert unknown.status_code == 422
    assert admin.client.post(ROLES, json={"code": "bad code", "name": "X"}).status_code == 422


def test_deleting_role_removes_its_permissions(
    admin: Account, make_user: MakeUser, login: Login
) -> None:
    role = admin.client.post(ROLES, json={"code": "rr", "name": "R", "permissions": [USERS_READ]})
    account = login(make_user())
    admin.client.put(f"/api/v1/users/{account.user.id}/roles", json={"role_ids": [role.json()["id"]]})
    assert account.client.get("/api/v1/users").status_code == 200

    admin.client.delete(f"{ROLES}/{role.json()['id']}")

    assert account.client.get("/api/v1/users").status_code == 403


def test_role_manager_cannot_grant_permissions_they_lack(
    admin: Account, make_user: MakeUser, login: Login
) -> None:
    manager = login(make_user(permissions=(ROLES_MANAGE, ROLES_READ, USERS_READ)))

    escalate = manager.client.post(
        ROLES, json={"code": "audit", "name": "Audit", "permissions": [AUDIT_READ]}
    )
    assert escalate.status_code == 403

    ok = manager.client.post(ROLES, json={"code": "rd", "name": "Rd", "permissions": [USERS_READ]})
    assert ok.status_code == 201
    add = manager.client.patch(f"{ROLES}/{ok.json()['id']}", json={"permissions": [AUDIT_READ]})
    assert add.status_code == 403

    admin_role = admin.client.post(
        ROLES, json={"code": "aud", "name": "Aud", "permissions": [AUDIT_READ]}
    )
    assert manager.client.delete(f"{ROLES}/{admin_role.json()['id']}").status_code == 403
