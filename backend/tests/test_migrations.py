import subprocess
import sys
from pathlib import Path

ALEMBIC_INI = Path(__file__).resolve().parent.parent / "alembic.ini"


def test_alembic_runs_from_any_directory(tmp_path: Path) -> None:
    """Offline migration render must not depend on the current directory."""
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "-c", str(ALEMBIC_INI), "upgrade", "head", "--sql"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "COMMIT;" in result.stdout
