from collections.abc import Iterator
from datetime import UTC, datetime
from functools import lru_cache
from typing import Annotated, Any

from fastapi import Depends
from sqlalchemy import DateTime, Dialect, Engine, MetaData, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.types import TypeDecorator

from app.core.config import get_settings

# Deterministic constraint names so Alembic migrations stay stable.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


def utcnow() -> datetime:
    return datetime.now(UTC)


class UTCDateTime(TypeDecorator[datetime]):
    """Timezone-aware timestamp, stored and returned in UTC.

    Rejects naive datetimes on write, and attaches UTC on read for databases
    that drop the offset (SQLite in tests).
    """

    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(self, value: datetime | None, dialect: Dialect) -> Any:
        if value is not None:
            if value.tzinfo is None:
                raise ValueError("naive datetime; use a timezone-aware value")
            value = value.astimezone(UTC)
        return value

    def process_result_value(self, value: Any, dialect: Dialect) -> datetime | None:
        if value is not None and value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        return value


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)
    type_annotation_map = {datetime: UTCDateTime}


@lru_cache
def get_engine() -> Engine:
    # Created on first use; creating an engine does not open a connection.
    settings = get_settings()
    return create_engine(
        settings.database_url,
        pool_pre_ping=True,
        connect_args=settings.app_connect_args,
    )


@lru_cache
def get_sessionmaker() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), autoflush=False, expire_on_commit=False)


def get_session() -> Iterator[Session]:
    """One session and one transaction per request.

    Commits when the request handler succeeds, rolls back on any exception.
    Use it through `SessionDep` so this finishes before the response is sent.
    """
    with get_sessionmaker()() as session, session.begin():
        yield session


# Function scope ends the transaction before the response is sent, so a failed
# commit becomes an error response instead of a success for unsaved data.
SessionDep = Annotated[Session, Depends(get_session, scope="function")]
