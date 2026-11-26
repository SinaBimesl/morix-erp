from datetime import UTC, datetime, timedelta, timezone

import pytest
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext
from sqlalchemy import inspect, select
from sqlalchemy.exc import StatementError
from sqlalchemy.orm import Session

from app.core.audit import AuditEvent
from app.core.db import Base
from tests.users.conftest import ALEMBIC_INI, migrated_engine


def test_migrations_match_models() -> None:
    """Fails when a model changes without a matching migration."""
    engine = migrated_engine()
    with engine.connect() as connection:
        diff = compare_metadata(
            MigrationContext.configure(connection, opts={"compare_type": True}), Base.metadata
        )
    assert diff == []


def test_downgrade_removes_all_tables() -> None:
    engine = migrated_engine()
    config = Config(str(ALEMBIC_INI))
    with engine.begin() as connection:
        config.attributes["connection"] = connection
        command.downgrade(config, "base")
    assert set(inspect(engine).get_table_names()) <= {"alembic_version"}


def test_timestamps_are_utc_aware() -> None:
    engine = migrated_engine()
    plus_two = timezone(timedelta(hours=2))
    with Session(engine) as session, session.begin():
        session.add(AuditEvent(action="t", occurred_at=datetime(2026, 1, 1, 12, tzinfo=plus_two)))
    with Session(engine) as session:
        stored = session.scalars(select(AuditEvent.occurred_at)).one()
    assert stored == datetime(2026, 1, 1, 10, tzinfo=UTC)
    assert stored.tzinfo is not None

    with pytest.raises(StatementError, match="naive datetime"), Session(engine) as session:
        session.add(AuditEvent(action="t", occurred_at=datetime(2026, 1, 1)))
        session.flush()
