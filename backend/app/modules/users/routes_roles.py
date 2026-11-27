import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy import select

from app.core import audit
from app.core.db import SessionDep
from app.modules.users.deps import Auth, require
from app.modules.users.models import Role, RolePermission
from app.modules.users.permissions import PERMISSIONS, ROLES_MANAGE, ROLES_READ
from app.modules.users.schemas import PermissionRead, RoleCreate, RoleRead, RoleUpdate
from app.modules.users.service import (
    changes,
    client_ip,
    conflict,
    ensure_can_grant,
    flush_or_conflict,
    get_or_404,
)

router = APIRouter(tags=["roles"])

Reader = Annotated[Auth, Depends(require(ROLES_READ))]
Manager = Annotated[Auth, Depends(require(ROLES_MANAGE))]


@router.get("/permissions")
def list_permissions(auth: Reader) -> list[PermissionRead]:
    return [PermissionRead(code=c, description=d) for c, d in sorted(PERMISSIONS.items())]


@router.get("/roles")
def list_roles(auth: Reader, session: SessionDep) -> list[RoleRead]:
    return [RoleRead.model_validate(r) for r in session.scalars(select(Role).order_by(Role.code))]


@router.post("/roles", status_code=status.HTTP_201_CREATED)
def create_role(body: RoleCreate, auth: Manager, request: Request, session: SessionDep) -> RoleRead:
    ensure_can_grant(auth.user, auth.permissions, body.permissions)
    if session.scalar(select(Role.id).where(Role.code == body.code)):
        raise conflict("role code already exists")
    role = Role(
        code=body.code,
        name=body.name,
        description=body.description,
        permission_rows=[RolePermission(permission=p) for p in body.permissions],
    )
    session.add(role)
    flush_or_conflict(session, "role code already exists")
    audit.record(
        session,
        "role.created",
        actor_id=auth.user.id,
        entity_type="role",
        entity_id=role.id,
        ip_address=client_ip(request),
        details={"code": role.code, "permissions": role.permissions},
    )
    return RoleRead.model_validate(role)


@router.get("/roles/{role_id}")
def get_role(role_id: uuid.UUID, auth: Reader, session: SessionDep) -> RoleRead:
    return RoleRead.model_validate(get_or_404(session, Role, role_id, "role"))


@router.patch("/roles/{role_id}")
def update_role(
    role_id: uuid.UUID, body: RoleUpdate, auth: Manager, request: Request, session: SessionDep
) -> RoleRead:
    role = get_or_404(session, Role, role_id, "role")
    data = changes(body, required=("name", "permissions"))
    if "permissions" in data:
        new = set(data.pop("permissions"))
        old = set(role.permissions)
        ensure_can_grant(auth.user, auth.permissions, old ^ new)
        role.permission_rows = [r for r in role.permission_rows if r.permission in new] + [
            RolePermission(permission=p) for p in sorted(new - old)
        ]
        data["permissions"] = sorted(new)
    for field in ("name", "description"):
        if field in data:
            setattr(role, field, data[field])
    flush_or_conflict(session, "role update conflicts with existing data")
    audit.record(
        session,
        "role.updated",
        actor_id=auth.user.id,
        entity_type="role",
        entity_id=role.id,
        ip_address=client_ip(request),
        details={"changes": data},
    )
    return RoleRead.model_validate(role)


@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(role_id: uuid.UUID, auth: Manager, request: Request, session: SessionDep) -> None:
    """Delete a role; users holding it lose its permissions."""
    role = get_or_404(session, Role, role_id, "role")
    ensure_can_grant(auth.user, auth.permissions, role.permissions)
    audit.record(
        session,
        "role.deleted",
        actor_id=auth.user.id,
        entity_type="role",
        entity_id=role.id,
        ip_address=client_ip(request),
        details={"code": role.code, "permissions": role.permissions},
    )
    session.delete(role)
