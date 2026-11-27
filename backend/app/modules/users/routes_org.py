import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import exists, select

from app.core import audit
from app.core.db import SessionDep
from app.modules.users.deps import Auth, require
from app.modules.users.models import Department, Team, TeamMember, User
from app.modules.users.permissions import ORG_MANAGE, ORG_READ
from app.modules.users.schemas import (
    DepartmentCreate,
    DepartmentRead,
    DepartmentUpdate,
    TeamCreate,
    TeamMemberSet,
    TeamRead,
    TeamUpdate,
)
from app.modules.users.service import (
    changes,
    client_ip,
    conflict,
    flush_or_conflict,
    get_or_404,
    not_found,
)

router = APIRouter(tags=["organisation"])

Reader = Annotated[Auth, Depends(require(ORG_READ))]
Manager = Annotated[Auth, Depends(require(ORG_MANAGE))]


def _unprocessable(detail: str) -> HTTPException:
    return HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, detail)


# --- departments ----------------------------------------------------------


def _check_parent(
    session: SessionDep, department: Department | None, parent_id: uuid.UUID | None
) -> None:
    """Parent must exist and must not be the department itself or a descendant."""
    seen: set[uuid.UUID] = set()
    current = parent_id
    while current is not None:
        if department is not None and current == department.id:
            raise _unprocessable("a department cannot be its own ancestor")
        if current in seen:  # existing cycle; should not happen
            break
        seen.add(current)
        parent = session.get(Department, current)
        if parent is None:
            raise _unprocessable("unknown parent_id")
        current = parent.parent_id


@router.get("/departments")
def list_departments(
    auth: Reader, session: SessionDep, include_inactive: bool = False
) -> list[DepartmentRead]:
    stmt = select(Department).order_by(Department.code)
    if not include_inactive:
        stmt = stmt.where(Department.is_active)
    return [DepartmentRead.model_validate(d) for d in session.scalars(stmt)]


@router.post("/departments", status_code=status.HTTP_201_CREATED)
def create_department(
    body: DepartmentCreate, auth: Manager, request: Request, session: SessionDep
) -> DepartmentRead:
    if session.scalar(select(Department.id).where(Department.code == body.code)):
        raise conflict("department code already exists")
    _check_parent(session, None, body.parent_id)
    department = Department(**body.model_dump())
    session.add(department)
    flush_or_conflict(session, "department code already exists")
    audit.record(
        session,
        "department.created",
        actor_id=auth.user.id,
        entity_type="department",
        entity_id=department.id,
        ip_address=client_ip(request),
        details={"code": department.code},
    )
    return DepartmentRead.model_validate(department)


@router.get("/departments/{department_id}")
def get_department(department_id: uuid.UUID, auth: Reader, session: SessionDep) -> DepartmentRead:
    return DepartmentRead.model_validate(
        get_or_404(session, Department, department_id, "department")
    )


@router.patch("/departments/{department_id}")
def update_department(
    department_id: uuid.UUID,
    body: DepartmentUpdate,
    auth: Manager,
    request: Request,
    session: SessionDep,
) -> DepartmentRead:
    department = get_or_404(session, Department, department_id, "department")
    data = changes(body, required=("name", "is_active"))
    if "parent_id" in data:
        _check_parent(session, department, data["parent_id"])
    for field, value in data.items():
        setattr(department, field, value)
    audit.record(
        session,
        "department.updated",
        actor_id=auth.user.id,
        entity_type="department",
        entity_id=department.id,
        ip_address=client_ip(request),
        details={"fields": sorted(data)},
    )
    return DepartmentRead.model_validate(department)


@router.delete("/departments/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_department(
    department_id: uuid.UUID, auth: Manager, request: Request, session: SessionDep
) -> None:
    """Delete an unused department. Deactivate it instead if anything refers to it."""
    department = get_or_404(session, Department, department_id, "department")
    for column, what in (
        (Department.parent_id, "sub-departments"),
        (User.department_id, "users"),
        (Team.department_id, "teams"),
    ):
        if session.scalar(select(exists().where(column == department.id))):
            raise conflict(f"department still has {what}; deactivate it instead")
    audit.record(
        session,
        "department.deleted",
        actor_id=auth.user.id,
        entity_type="department",
        entity_id=department.id,
        ip_address=client_ip(request),
        details={"code": department.code},
    )
    session.delete(department)


# --- teams ----------------------------------------------------------------


def _check_team_department(session: SessionDep, department_id: uuid.UUID) -> None:
    if session.get(Department, department_id) is None:
        raise _unprocessable("unknown department_id")


def _check_team_name(
    session: SessionDep, team: Team | None, department_id: uuid.UUID, name: str
) -> None:
    if session.scalar(
        select(Team.id).where(
            Team.department_id == department_id,
            Team.name == name,
            Team.id != (team.id if team else None),
        )
    ):
        raise conflict("a team with this name already exists in the department")


@router.get("/teams")
def list_teams(
    auth: Reader,
    session: SessionDep,
    department_id: uuid.UUID | None = None,
    user_id: uuid.UUID | None = None,
    include_inactive: bool = False,
) -> list[TeamRead]:
    stmt = select(Team).order_by(Team.name)
    if department_id is not None:
        stmt = stmt.where(Team.department_id == department_id)
    if user_id is not None:
        stmt = stmt.where(
            Team.id.in_(select(TeamMember.team_id).where(TeamMember.user_id == user_id))
        )
    if not include_inactive:
        stmt = stmt.where(Team.is_active)
    return [TeamRead.model_validate(t) for t in session.scalars(stmt)]


@router.post("/teams", status_code=status.HTTP_201_CREATED)
def create_team(body: TeamCreate, auth: Manager, request: Request, session: SessionDep) -> TeamRead:
    _check_team_department(session, body.department_id)
    _check_team_name(session, None, body.department_id, body.name)
    team = Team(**body.model_dump(), members=[])
    session.add(team)
    flush_or_conflict(session, "a team with this name already exists in the department")
    audit.record(
        session,
        "team.created",
        actor_id=auth.user.id,
        entity_type="team",
        entity_id=team.id,
        ip_address=client_ip(request),
        details={"name": team.name},
    )
    return TeamRead.model_validate(team)


@router.get("/teams/{team_id}")
def get_team(team_id: uuid.UUID, auth: Reader, session: SessionDep) -> TeamRead:
    return TeamRead.model_validate(get_or_404(session, Team, team_id, "team"))


@router.patch("/teams/{team_id}")
def update_team(
    team_id: uuid.UUID, body: TeamUpdate, auth: Manager, request: Request, session: SessionDep
) -> TeamRead:
    team = get_or_404(session, Team, team_id, "team")
    data = changes(body, required=("department_id", "name", "is_active"))
    if "department_id" in data:
        _check_team_department(session, data["department_id"])
    if "department_id" in data or "name" in data:
        _check_team_name(
            session,
            team,
            data.get("department_id", team.department_id),
            data.get("name", team.name),
        )
    for field, value in data.items():
        setattr(team, field, value)
    flush_or_conflict(session, "a team with this name already exists in the department")
    audit.record(
        session,
        "team.updated",
        actor_id=auth.user.id,
        entity_type="team",
        entity_id=team.id,
        ip_address=client_ip(request),
        details={"fields": sorted(data)},
    )
    return TeamRead.model_validate(team)


@router.delete("/teams/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(team_id: uuid.UUID, auth: Manager, request: Request, session: SessionDep) -> None:
    team = get_or_404(session, Team, team_id, "team")
    audit.record(
        session,
        "team.deleted",
        actor_id=auth.user.id,
        entity_type="team",
        entity_id=team.id,
        ip_address=client_ip(request),
        details={"name": team.name},
    )
    session.delete(team)


@router.put("/teams/{team_id}/members/{user_id}")
def set_team_member(
    team_id: uuid.UUID,
    user_id: uuid.UUID,
    body: TeamMemberSet,
    auth: Manager,
    request: Request,
    session: SessionDep,
) -> TeamRead:
    """Add a user to the team, or update their lead flag."""
    team = get_or_404(session, Team, team_id, "team")
    if session.get(User, user_id) is None:
        raise _unprocessable("unknown user_id")
    member = next((m for m in team.members if m.user_id == user_id), None)
    if member is None:
        team.members.append(TeamMember(user_id=user_id, is_lead=body.is_lead))
    else:
        member.is_lead = body.is_lead
    flush_or_conflict(session, "membership changed concurrently; retry")
    audit.record(
        session,
        "team.member_set",
        actor_id=auth.user.id,
        entity_type="team",
        entity_id=team.id,
        ip_address=client_ip(request),
        details={"user_id": str(user_id), "is_lead": body.is_lead},
    )
    return TeamRead.model_validate(team)


@router.delete("/teams/{team_id}/members/{user_id}")
def remove_team_member(
    team_id: uuid.UUID, user_id: uuid.UUID, auth: Manager, request: Request, session: SessionDep
) -> TeamRead:
    team = get_or_404(session, Team, team_id, "team")
    member = next((m for m in team.members if m.user_id == user_id), None)
    if member is None:
        raise not_found("team member")
    team.members.remove(member)
    audit.record(
        session,
        "team.member_removed",
        actor_id=auth.user.id,
        entity_type="team",
        entity_id=team.id,
        ip_address=client_ip(request),
        details={"user_id": str(user_id)},
    )
    return TeamRead.model_validate(team)
