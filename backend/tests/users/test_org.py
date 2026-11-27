from app.modules.users.permissions import ORG_READ
from tests.users.conftest import Account, Login, MakeUser

DEPTS = "/api/v1/departments"
TEAMS = "/api/v1/teams"


def _dept(admin: Account, code: str, parent_id: str | None = None) -> str:
    response = admin.client.post(
        DEPTS, json={"code": code, "name": code.title(), "parent_id": parent_id}
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _team(admin: Account, department_id: str, name: str = "Line A") -> str:
    response = admin.client.post(TEAMS, json={"department_id": department_id, "name": name})
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_department_hierarchy(admin: Account) -> None:
    production = _dept(admin, "production")
    cnc = _dept(admin, "cnc", production)

    assert admin.client.get(f"{DEPTS}/{cnc}").json()["parent_id"] == production
    assert admin.client.post(DEPTS, json={"code": "cnc", "name": "Dup"}).status_code == 409

    unknown = admin.client.post(
        DEPTS, json={"code": "x1", "name": "X", "parent_id": "00000000-0000-0000-0000-000000000000"}
    )
    assert unknown.status_code == 422


def test_department_cycles_are_rejected(admin: Account) -> None:
    top = _dept(admin, "top")
    mid = _dept(admin, "mid", top)
    low = _dept(admin, "low", mid)

    assert admin.client.patch(f"{DEPTS}/{top}", json={"parent_id": low}).status_code == 422
    assert admin.client.patch(f"{DEPTS}/{top}", json={"parent_id": top}).status_code == 422
    assert admin.client.patch(f"{DEPTS}/{low}", json={"parent_id": None}).status_code == 200


def test_department_delete_and_deactivate(admin: Account) -> None:
    parent = _dept(admin, "parent")
    child = _dept(admin, "child", parent)

    assert admin.client.delete(f"{DEPTS}/{parent}").status_code == 409
    admin.client.patch(f"{DEPTS}/{parent}", json={"is_active": False})
    assert [d["code"] for d in admin.client.get(DEPTS).json()] == ["child"]
    listed = admin.client.get(DEPTS, params={"include_inactive": True}).json()
    assert {d["code"] for d in listed} == {"child", "parent"}

    _team(admin, child)
    assert admin.client.delete(f"{DEPTS}/{child}").status_code == 409


def test_department_with_users_cannot_be_deleted(admin: Account) -> None:
    dept = _dept(admin, "sales")
    admin.client.patch(f"/api/v1/users/{admin.user.id}", json={"department_id": dept})

    assert admin.client.delete(f"{DEPTS}/{dept}").status_code == 409
    admin.client.patch(f"/api/v1/users/{admin.user.id}", json={"department_id": None})
    assert admin.client.delete(f"{DEPTS}/{dept}").status_code == 204


def test_team_crud_and_members(admin: Account, make_user: MakeUser) -> None:
    dept = _dept(admin, "painting")
    other = _dept(admin, "repairs")
    team = _team(admin, dept)
    worker = make_user()

    assert (
        admin.client.post(TEAMS, json={"department_id": dept, "name": "Line A"}).status_code == 409
    )
    assert _team(admin, other)  # same name, different department is fine

    added = admin.client.put(f"{TEAMS}/{team}/members/{worker.id}", json={"is_lead": False})
    assert [m["user_id"] for m in added.json()["members"]] == [str(worker.id)]
    lead = admin.client.put(f"{TEAMS}/{team}/members/{worker.id}", json={"is_lead": True})
    assert lead.json()["members"][0]["is_lead"] is True
    assert len(lead.json()["members"]) == 1

    by_user = admin.client.get(TEAMS, params={"user_id": str(worker.id)}).json()
    assert [t["id"] for t in by_user] == [team]

    unknown = admin.client.put(
        f"{TEAMS}/{team}/members/00000000-0000-0000-0000-000000000000", json={}
    )
    assert unknown.status_code == 422
    removed = admin.client.delete(f"{TEAMS}/{team}/members/{worker.id}")
    assert removed.json()["members"] == []
    assert admin.client.delete(f"{TEAMS}/{team}/members/{worker.id}").status_code == 404

    moved = admin.client.patch(f"{TEAMS}/{team}", json={"department_id": other})
    assert moved.status_code == 409  # "Line A" already exists there
    assert admin.client.delete(f"{TEAMS}/{team}").status_code == 204


def test_org_permissions(make_user: MakeUser, login: Login) -> None:
    reader = login(make_user(permissions=(ORG_READ,)))

    assert reader.client.get(DEPTS).status_code == 200
    assert reader.client.post(DEPTS, json={"code": "x1", "name": "X"}).status_code == 403
