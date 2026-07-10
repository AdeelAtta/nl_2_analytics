#!/usr/bin/env python3
"""Wrapper around alembic upgrade head."""

import subprocess
import sys
from pathlib import Path


def main() -> None:
    backend_dir = Path(__file__).resolve().parent.parent
    alembic_dir = backend_dir / "alembic"
    ini_path = alembic_dir / "alembic.ini"

    if not ini_path.exists():
        print(f"alembic.ini not found at {ini_path}", file=sys.stderr)
        sys.exit(1)

    env = {**{k: str(v) for k, v in _load_dotenv(backend_dir).items()}}
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=backend_dir,
        env=env,
    )
    sys.exit(result.returncode)


def _load_dotenv(backend_dir: Path) -> dict:
    env_file = backend_dir / ".env"
    if not env_file.exists():
        return {}
    env_vars = {}
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        env_vars[key.strip()] = value.strip().strip('"').strip("'")
    return env_vars


if __name__ == "__main__":
    main()
