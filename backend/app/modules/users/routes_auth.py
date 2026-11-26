from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy import select

from app.core import audit
from app.core.config import get_settings
from app.core.db import SessionDep, utcnow
from app.modules.users.deps import CurrentAuth
from app.modules.users.models import AuthSession, User
from app.modules.users.schemas import (
    ChangePasswordRequest,
    LoginRequest,
    LoginResponse,
    MeRead,
    ProfileUpdate,
    UserRead,
)
from app.modules.users.security import (
    burn_verify_time,
    hash_password,
    hash_token,
    needs_rehash,
    new_session_token,
    verify_password,
)
from app.modules.users.service import (
    changes,
    client_ip,
    conflict,
    flush_or_conflict,
    revoke_sessions,
    user_permissions,
)

router = APIRouter(prefix="/auth", tags=["auth"])

INVALID_LOGIN = "Invalid username or password"


def me_read(user: User, permissions: frozenset[str]) -> MeRead:
    return MeRead(
        **UserRead.model_validate(user).model_dump(), permissions=sorted(permissions)
    )


@router.post(
    "/login",
    response_model=LoginResponse,
    responses={401: {"description": INVALID_LOGIN}},
)
def login(
    body: LoginRequest,
    request: Request,
    session: SessionDep,
    user_agent: Annotated[str | None, Header()] = None,
) -> LoginResponse | JSONResponse:
    settings = get_settings()
    now = utcnow()
    ip = client_ip(request)
    # Row lock so concurrent attempts count failures correctly (PostgreSQL).
    user = session.scalar(
        select(User).where(User.username == body.username).with_for_update()
    )

    def reject(reason: str) -> JSONResponse:
        # Returned, not raised, so the failed-attempt count and the audit event
        # are committed. Every reason gets the same response.
        audit.record(
            session,
            "auth.login_failed",
            actor_id=user.id if user else None,
            entity_type="user",
            entity_id=user.id if user else None,
            ip_address=ip,
            details={"username": body.username, "reason": reason},
        )
        return JSONResponse(
            {"detail": INVALID_LOGIN},
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user is None:
        burn_verify_time(body.password)
        return reject("unknown_user")
    if user.locked_until is not None and user.locked_until > now:
        burn_verify_time(body.password)
        return reject("locked")
    if not verify_password(user.password_hash, body.password):
        user.failed_login_count += 1
        if user.failed_login_count >= settings.auth_max_failed_logins:
            user.failed_login_count = 0
            user.locked_until = now + timedelta(minutes=settings.auth_lockout_minutes)
            audit.record(
                session, "auth.account_locked", entity_type="user", entity_id=user.id,
                ip_address=ip,
            )
        return reject("bad_password")
    if not user.is_active:
        return reject("inactive")

    user.failed_login_count = 0
    user.locked_until = None
    user.last_login_at = now
    if needs_rehash(user.password_hash):
        user.password_hash = hash_password(body.password)

    token = new_session_token()
    auth_session = AuthSession(
        user_id=user.id,
        token_hash=hash_token(token),
        expires_at=now + timedelta(hours=settings.auth_session_hours),
        ip_address=ip,
        user_agent=user_agent[:500] if user_agent else None,
    )
    session.add(auth_session)
    session.flush()
    audit.record(
        session, "auth.login", actor_id=user.id, entity_type="user", entity_id=user.id,
        ip_address=ip,
    )
    return LoginResponse(
        access_token=token,
        expires_at=auth_session.expires_at,
        user=me_read(user, user_permissions(session, user)),
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(auth: CurrentAuth, request: Request, session: SessionDep) -> None:
    auth.auth_session.revoked_at = utcnow()
    audit.record(
        session, "auth.logout", actor_id=auth.user.id, entity_type="user",
        entity_id=auth.user.id, ip_address=client_ip(request),
    )


@router.get("/me")
def me(auth: CurrentAuth) -> MeRead:
    return me_read(auth.user, auth.permissions)


@router.patch("/me")
def update_me(
    body: ProfileUpdate, auth: CurrentAuth, request: Request, session: SessionDep
) -> MeRead:
    user = auth.user
    data = changes(body, required=("full_name",))
    email = data.get("email")
    if email and session.scalar(select(User.id).where(User.email == email, User.id != user.id)):
        raise conflict("email already exists")
    for field, value in data.items():
        setattr(user, field, value)
    flush_or_conflict(session, "email already exists")
    audit.record(
        session, "user.profile_updated", actor_id=user.id, entity_type="user",
        entity_id=user.id, ip_address=client_ip(request), details={"fields": sorted(data)},
    )
    return me_read(user, auth.permissions)


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    body: ChangePasswordRequest, auth: CurrentAuth, request: Request, session: SessionDep
) -> None:
    user = auth.user
    if not verify_password(user.password_hash, body.current_password):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "current password is incorrect")
    if body.new_password == body.current_password:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "new password must differ from the current one")
    if body.new_password.lower() == user.username:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "password must not equal the username")
    user.password_hash = hash_password(body.new_password)
    user.password_changed_at = utcnow()
    user.must_change_password = False
    # Sign out everywhere else; this session stays valid.
    revoke_sessions(session, user.id, keep=auth.auth_session.id)
    audit.record(
        session, "auth.password_changed", actor_id=user.id, entity_type="user",
        entity_id=user.id, ip_address=client_ip(request),
    )
