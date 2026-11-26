import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import or_, select

from app.core import audit
from app.core.db import SessionDep, utcnow
from app.core.pagination import Page, PageParams, page_params
from app.modules.users.deps import Auth, require
from app.modules.users.models import Department, User, UserRole
from app.modules.users.permissions import USERS_ASSIGN_ROLES, USERS_MANAGE, USERS_READ
from app.modules.users.schemas import (
    PasswordReset,
    UserCreate,
    UserRead,
    UserRolesUpdate,
    UserUpdate,
)
from app.modules.users.security import hash_password
from app.modules.users.service import (
    changes,
    client_ip,
    conflict,
    count,
    ensure_can_grant,
    ensure_can_manage_user,
    ensure_other_active_superuser,
    flush_or_conflict,
    forbidden,
    get_or_404,
    load_roles,
    revoke_sessions,
    role_permissions,
)

router = APIRouter(prefix="/users", tags=["users"])

Reader = Annotated[Auth, Depends(require(USERS_READ))]
Manager = Annotated[Auth, Depends(require(USERS_MANAGE))]
RoleAssigner = Annotated[Auth, Depends(require(USERS_ASSIGN_ROLES))]


def _check_department(session: SessionDep, department_id: uuid.UUID | None) -> None:
    if department_id is not None and session.get(Department, department_id) is None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "unknown department_id")


def _check_unique(session: SessionDep, user: User | None, username: str | None, email: str | None) -> None:
    exclude = user.id if user else None
    if username and session.scalar(
        select(User.id).where(User.username == username, User.id != exclude)
    ):
        raise conflict("username already exists")
    if email and session.scalar(select(User.id).where(User.email == email, User.id != exclude)):
        raise conflict("email already exists")


@router.get("")
def list_users(
    auth: Reader,
    session: SessionDep,
    page: Annotated[PageParams, Depends(page_params)],
    q: Annotated[str | None, Query(max_length=100, description="Search name, username, email")] = None,
    is_active: bool | None = None,
    department_id: uuid.UUID | None = None,
    role_id: uuid.UUID | None = None,
) -> Page[UserRead]:
    stmt = select(User).order_by(User.username)
    if q:
        pattern = f"%{q.strip()}%"
        stmt = stmt.where(
            or_(User.username.ilike(pattern), User.full_name.ilike(pattern), User.email.ilike(pattern))
        )
    if is_active is not None:
        stmt = stmt.where(User.is_active == is_active)
    if department_id is not None:
        stmt = stmt.where(User.department_id == department_id)
    if role_id is not None:
        stmt = stmt.where(User.id.in_(select(UserRole.user_id).where(UserRole.role_id == role_id)))
    users = session.scalars(stmt.limit(page.limit).offset(page.offset))
    return Page(
        items=[UserRead.model_validate(u) for u in users],
        total=count(session, stmt),
        limit=page.limit,
        offset=page.offset,
    )


@router.post("", status_code=status.HTTP_201_CREATED)
def create_user(body: UserCreate, auth: Manager, request: Request, session: SessionDep) -> UserRead:
    if body.is_superuser and not auth.user.is_superuser:
        raise forbidden("only a superuser can create a superuser")
    roles = load_roles(session, body.role_ids)
    if roles:
        if USERS_ASSIGN_ROLES not in auth.permissions:
            raise forbidden(f"missing permission: {USERS_ASSIGN_ROLES}")
        ensure_can_grant(auth.user, auth.permissions, role_permissions(roles))
    _check_department(session, body.department_id)
    _check_unique(session, None, body.username, body.email)

    user = User(
        **body.model_dump(exclude={"password", "role_ids"}),
        password_hash=hash_password(body.password),
        roles=roles,
    )
    session.add(user)
    flush_or_conflict(session, "username or email already exists")
    audit.record(
        session, "user.created", actor_id=auth.user.id, entity_type="user", entity_id=user.id,
        ip_address=client_ip(request),
        details={"username": user.username, "is_superuser": user.is_superuser,
                 "roles": [r.code for r in roles]},
    )
    return UserRead.model_validate(user)


@router.get("/{user_id}")
def get_user(user_id: uuid.UUID, auth: Reader, session: SessionDep) -> UserRead:
    return UserRead.model_validate(get_or_404(session, User, user_id, "user"))


@router.patch("/{user_id}")
def update_user(
    user_id: uuid.UUID, body: UserUpdate, auth: Manager, request: Request, session: SessionDep
) -> UserRead:
    user = get_or_404(session, User, user_id, "user")
    ensure_can_manage_user(session, auth.user, auth.permissions, user)
    data = changes(body, required=("full_name", "is_active", "is_superuser"))

    if "is_superuser" in data and data["is_superuser"] != user.is_superuser:
        if not auth.user.is_superuser:
            raise forbidden("only a superuser can change superuser status")
        if not data["is_superuser"]:
            ensure_other_active_superuser(session, user)
    if data.get("is_active") is False and user.is_active:
        if user.id == auth.user.id:
            raise conflict("you cannot deactivate your own account")
        if user.is_superuser:
            ensure_other_active_superuser(session, user)
        revoke_sessions(session, user.id)
    if "department_id" in data:
        _check_department(session, data["department_id"])
    _check_unique(session, user, None, data.get("email"))

    for field, value in data.items():
        setattr(user, field, value)
    flush_or_conflict(session, "email already exists")
    audit.record(
        session, "user.updated", actor_id=auth.user.id, entity_type="user", entity_id=user.id,
        ip_address=client_ip(request), details={"fields": sorted(data)},
    )
    return UserRead.model_validate(user)


@router.post("/{user_id}/reset-password", status_code=status.HTTP_204_NO_CONTENT)
def reset_password(
    user_id: uuid.UUID, body: PasswordReset, auth: Manager, request: Request, session: SessionDep
) -> None:
    """Set a new password for someone else, sign them out, and clear any lockout."""
    user = get_or_404(session, User, user_id, "user")
    ensure_can_manage_user(session, auth.user, auth.permissions, user)
    if body.new_password.lower() == user.username:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "password must not equal the username")
    user.password_hash = hash_password(body.new_password)
    user.password_changed_at = utcnow()
    user.must_change_password = body.must_change_password
    user.failed_login_count = 0
    user.locked_until = None
    revoke_sessions(session, user.id)
    audit.record(
        session, "user.password_reset", actor_id=auth.user.id, entity_type="user",
        entity_id=user.id, ip_address=client_ip(request),
    )


@router.post("/{user_id}/unlock")
def unlock_user(user_id: uuid.UUID, auth: Manager, request: Request, session: SessionDep) -> UserRead:
    user = get_or_404(session, User, user_id, "user")
    ensure_can_manage_user(session, auth.user, auth.permissions, user)
    user.failed_login_count = 0
    user.locked_until = None
    audit.record(
        session, "user.unlocked", actor_id=auth.user.id, entity_type="user", entity_id=user.id,
        ip_address=client_ip(request),
    )
    return UserRead.model_validate(user)


@router.put("/{user_id}/roles")
def set_user_roles(
    user_id: uuid.UUID, body: UserRolesUpdate, auth: RoleAssigner, request: Request,
    session: SessionDep,
) -> UserRead:
    """Replace the user's roles with exactly the given set."""
    user = get_or_404(session, User, user_id, "user")
    ensure_can_manage_user(session, auth.user, auth.permissions, user)
    new_roles = load_roles(session, body.role_ids)
    old_ids = {r.id for r in user.roles}
    new_ids = {r.id for r in new_roles}
    changed = [r for r in [*user.roles, *new_roles] if r.id in old_ids ^ new_ids]
    ensure_can_grant(auth.user, auth.permissions, role_permissions(changed))

    user.roles = sorted(new_roles, key=lambda r: r.code)
    audit.record(
        session, "user.roles_changed", actor_id=auth.user.id, entity_type="user",
        entity_id=user.id, ip_address=client_ip(request),
        details={"roles": [r.code for r in user.roles]},
    )
    return UserRead.model_validate(user)
