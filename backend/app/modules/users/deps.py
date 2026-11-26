"""Authentication and authorization dependencies for every module's routes."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select

from app.core.db import SessionDep, utcnow
from app.modules.users.models import AuthSession, User
from app.modules.users.security import hash_token
from app.modules.users.service import forbidden, user_permissions

bearer = HTTPBearer(auto_error=False, description="Token from POST /api/v1/auth/login")


@dataclass(frozen=True)
class Auth:
    user: User
    auth_session: AuthSession
    permissions: frozenset[str]


def _unauthorized() -> HTTPException:
    return HTTPException(
        status.HTTP_401_UNAUTHORIZED,
        "Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_auth(
    session: SessionDep,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> Auth:
    if credentials is None:
        raise _unauthorized()
    row = session.execute(
        select(AuthSession, User)
        .join(User, User.id == AuthSession.user_id)
        .where(
            AuthSession.token_hash == hash_token(credentials.credentials),
            AuthSession.revoked_at.is_(None),
            AuthSession.expires_at > utcnow(),
            User.is_active,
        )
    ).one_or_none()
    if row is None:
        raise _unauthorized()
    auth_session, user = row
    return Auth(user, auth_session, user_permissions(session, user))


# Any signed-in user, including one who must still change their password.
CurrentAuth = Annotated[Auth, Depends(get_auth, scope="function")]


def require(*permissions: str) -> Callable[[Auth], Auth]:
    """Dependency: signed in, password not pending change, and all permissions held."""

    def check(auth: CurrentAuth) -> Auth:
        if auth.user.must_change_password:
            raise forbidden("password change required")
        missing = sorted(set(permissions) - auth.permissions)
        if missing:
            raise forbidden(f"missing permission: {', '.join(missing)}")
        return auth

    return check
