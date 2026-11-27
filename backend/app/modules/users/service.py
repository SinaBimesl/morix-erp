"""Rules shared by the User Manager routes."""

import uuid
from collections.abc import Iterable
from typing import Any

from fastapi import HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy import exists, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.db import Base, utcnow
from app.modules.users.models import AuthSession, Role, RolePermission, User, UserRole
from app.modules.users.permissions import PERMISSIONS


def not_found(what: str) -> HTTPException:
    return HTTPException(status.HTTP_404_NOT_FOUND, f"{what} not found")


def conflict(detail: str) -> HTTPException:
    return HTTPException(status.HTTP_409_CONFLICT, detail)


def forbidden(detail: str) -> HTTPException:
    return HTTPException(status.HTTP_403_FORBIDDEN, detail)


def get_or_404[M: Base](session: Session, model: type[M], obj_id: uuid.UUID, what: str) -> M:
    obj = session.get(model, obj_id)
    if obj is None:
        raise not_found(what)
    return obj


def flush_or_conflict(session: Session, detail: str) -> None:
    """Flush pending changes; a unique or foreign key violation becomes 409.

    Callers check the common cases first; this covers concurrent requests.
    """
    try:
        session.flush()
    except IntegrityError:
        raise conflict(detail) from None


def changes(data: BaseModel, required: Iterable[str] = ()) -> dict[str, Any]:
    """Fields the client sent in a PATCH body. `required` fields may not be null."""
    sent = data.model_dump(exclude_unset=True)
    nulls = [name for name in required if name in sent and sent[name] is None]
    if nulls:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT, f"cannot be null: {', '.join(nulls)}"
        )
    return sent


def client_ip(request: Request) -> str | None:
    # The direct peer. Behind a reverse proxy this is the proxy's address.
    return request.client.host if request.client else None


def user_permissions(session: Session, user: User) -> frozenset[str]:
    if user.is_superuser:
        return frozenset(PERMISSIONS)
    rows = session.scalars(
        select(RolePermission.permission)
        .join(UserRole, UserRole.role_id == RolePermission.role_id)
        .where(UserRole.user_id == user.id)
    )
    # Ignore codes no longer defined in code (e.g. a removed permission).
    return frozenset(rows) & PERMISSIONS.keys()


def ensure_can_grant(
    actor: User, actor_permissions: frozenset[str], permissions: Iterable[str]
) -> None:
    """Block privilege escalation: only grant or remove permissions you hold."""
    if actor.is_superuser:
        return
    missing = sorted(set(permissions) - actor_permissions)
    if missing:
        raise forbidden(f"you cannot grant or remove permissions you lack: {', '.join(missing)}")


def role_permissions(roles: Iterable[Role]) -> set[str]:
    return {code for role in roles for code in role.permissions}


def ensure_can_manage_user(
    session: Session, actor: User, actor_permissions: frozenset[str], target: User
) -> None:
    """You may only manage accounts whose permissions you hold yourself.

    Otherwise resetting someone's password would let you sign in as them and
    gain their permissions.
    """
    if actor.is_superuser:
        return
    if target.is_superuser:
        raise forbidden("only a superuser can manage a superuser account")
    missing = sorted(user_permissions(session, target) - actor_permissions)
    if missing:
        raise forbidden(f"you cannot manage a user with permissions you lack: {', '.join(missing)}")


def ensure_other_active_superuser(session: Session, user: User) -> None:
    """Refuse a change that would leave no active superuser."""
    others = session.scalar(
        select(exists().where(User.is_superuser, User.is_active, User.id != user.id))
    )
    if not others:
        raise conflict("this is the last active superuser")


def load_roles(session: Session, role_ids: Iterable[uuid.UUID]) -> list[Role]:
    ids = set(role_ids)
    roles = list(session.scalars(select(Role).where(Role.id.in_(ids)))) if ids else []
    if len(roles) != len(ids):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "unknown role id")
    return roles


def revoke_sessions(session: Session, user_id: uuid.UUID, keep: uuid.UUID | None = None) -> None:
    stmt = (
        update(AuthSession)
        .where(AuthSession.user_id == user_id, AuthSession.revoked_at.is_(None))
        .values(revoked_at=utcnow())
    )
    if keep is not None:
        stmt = stmt.where(AuthSession.id != keep)
    session.execute(stmt)


def count(session: Session, stmt: Any) -> int:
    return session.scalar(select(func.count()).select_from(stmt.order_by(None).subquery())) or 0
