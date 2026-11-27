"""User Manager admin commands.

    docker compose run --rm backend python -m app.modules.users.cli create-superuser \\
        --username admin --full-name "Workshop Admin"
    docker compose run --rm backend python -m app.modules.users.cli prune-sessions

create-superuser reads the password from a prompt, or from stdin when it is
not a terminal.
"""

import argparse
import getpass
import sys
from datetime import timedelta

from pydantic import TypeAdapter, ValidationError
from sqlalchemy import delete, or_, select

from app.core import audit, db
from app.core.db import utcnow
from app.modules.users.models import AuthSession, User
from app.modules.users.schemas import Name, Password, Username
from app.modules.users.security import hash_password


def _read_password() -> str:
    if not sys.stdin.isatty():
        return sys.stdin.readline().rstrip("\n")
    password = getpass.getpass("Password: ")
    if password != getpass.getpass("Repeat password: "):
        raise SystemExit("Passwords do not match.")
    return password


def create_superuser(username: str, full_name: str, password: str) -> User:
    username = TypeAdapter(Username).validate_python(username)
    full_name = TypeAdapter(Name).validate_python(full_name)
    password = TypeAdapter(Password).validate_python(password)
    if password.lower() == username:
        raise ValueError("password must not equal the username")
    with db.get_sessionmaker()() as session, session.begin():
        if session.scalar(select(User.id).where(User.username == username)):
            raise ValueError(f"user {username!r} already exists")
        user = User(
            username=username,
            full_name=full_name,
            password_hash=hash_password(password),
            is_superuser=True,
            roles=[],
        )
        session.add(user)
        session.flush()
        audit.record(
            session,
            "user.created",
            entity_type="user",
            entity_id=user.id,
            details={"username": username, "is_superuser": True, "via": "cli"},
        )
    return user


def prune_sessions(older_than_days: int) -> int:
    """Delete sessions that expired or were revoked more than N days ago."""
    cutoff = utcnow() - timedelta(days=older_than_days)
    with db.get_sessionmaker()() as session, session.begin():
        result = session.execute(
            delete(AuthSession).where(
                or_(AuthSession.expires_at < cutoff, AuthSession.revoked_at < cutoff)
            )
        )
    return result.rowcount


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m app.modules.users.cli")
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("create-superuser", help="create a superuser account")
    create.add_argument("--username", required=True)
    create.add_argument("--full-name", required=True)
    prune = commands.add_parser("prune-sessions", help="delete old expired or revoked sessions")
    prune.add_argument("--older-than-days", type=int, default=30)
    args = parser.parse_args(argv)

    if args.command == "prune-sessions":
        if args.older_than_days < 0:
            parser.error("--older-than-days must not be negative")
        print(f"Deleted {prune_sessions(args.older_than_days)} sessions")
        return 0

    try:
        user = create_superuser(args.username, args.full_name, _read_password())
    except (ValidationError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"Created superuser {user.username} ({user.id})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
