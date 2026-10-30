"""Project path discovery helpers."""

from __future__ import annotations

from pathlib import Path


def find_project_root(start: str | Path | None = None) -> Path:
    """Find the nearest parent containing pyproject.toml.

    Args:
        start: A directory or file from which to begin searching. Defaults to this
            module's location.

    Raises:
        FileNotFoundError: If no project root can be found.
    """

    candidate = Path(start).resolve() if start is not None else Path(__file__).resolve()
    if candidate.is_file():
        candidate = candidate.parent

    for directory in (candidate, *candidate.parents):
        if (directory / "pyproject.toml").is_file():
            return directory

    raise FileNotFoundError(f"Could not locate project root starting from: {candidate}")
