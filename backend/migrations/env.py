from logging.config import fileConfig

from alembic import context
from sqlalchemy import Connection, create_engine, pool

# Import model modules here as they are added so autogenerate can see them.
import app.core.audit  # noqa: F401
import app.modules.users.models  # noqa: F401
from app.core.config import get_settings
from app.core.db import Base, UTCDateTime

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def render_item(type_: str, obj: object, autogen_context: object) -> str | bool:
    # Migrations must not import app code: render app types as plain SQLAlchemy.
    if type_ == "type" and isinstance(obj, UTCDateTime):
        return "sa.DateTime(timezone=True)"
    return False


def run_migrations_offline() -> None:
    """Emit SQL to stdout without connecting to the database."""
    context.configure(
        url=get_settings().database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        render_item=render_item,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def _run_on(connection: Connection) -> None:
    context.configure(
        connection=connection, target_metadata=target_metadata, render_item=render_item
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    # Tests pass their own connection (e.g. SQLite) instead of the settings URL.
    connection = config.attributes.get("connection")
    if connection is not None:
        _run_on(connection)
        return

    settings = get_settings()
    engine = create_engine(
        settings.database_url,
        poolclass=pool.NullPool,
        connect_args=settings.migration_connect_args,
    )
    with engine.connect() as connection:
        _run_on(connection)
    engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
