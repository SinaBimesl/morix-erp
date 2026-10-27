"""Connections to a server that never answers must fail within the timeout."""

import socket
import subprocess
import sys
import threading
import time
from collections.abc import Iterator
from pathlib import Path

import pytest
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from app.core.db import get_engine

ALEMBIC_INI = Path(__file__).resolve().parent.parent / "alembic.ini"
TIMEOUT = 2  # libpq's minimum
LIMIT = TIMEOUT + 3  # seconds; generous margin for slow machines


@pytest.fixture
def silent_server(monkeypatch: pytest.MonkeyPatch) -> Iterator[int]:
    """A TCP port that completes the handshake but never speaks Postgres."""
    with socket.socket() as server:
        server.bind(("127.0.0.1", 0))
        server.listen()
        port = server.getsockname()[1]
        monkeypatch.setenv("POSTGRES_HOST", "127.0.0.1")
        monkeypatch.setenv("POSTGRES_PORT", str(port))
        monkeypatch.setenv("DB_CONNECT_TIMEOUT", str(TIMEOUT))
        yield port


@pytest.mark.usefixtures("silent_server")
def test_app_engine_connect_times_out() -> None:
    engine = get_engine()
    errors: list[Exception] = []

    def connect() -> None:
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
        except Exception as exc:  # noqa: BLE001 - collected for the assertion
            errors.append(exc)

    # A thread, so a missing timeout fails the test instead of hanging it.
    worker = threading.Thread(target=connect, daemon=True)
    worker.start()
    worker.join(LIMIT)

    assert not worker.is_alive(), "connection attempt did not time out"
    assert len(errors) == 1 and isinstance(errors[0], OperationalError)
    engine.dispose()


@pytest.mark.usefixtures("silent_server")
def test_migration_connect_times_out() -> None:
    start = time.monotonic()
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "-c", str(ALEMBIC_INI), "upgrade", "head"],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    assert result.returncode != 0
    assert "timeout" in result.stderr.lower()
    assert time.monotonic() - start < LIMIT + 3  # plus interpreter startup
