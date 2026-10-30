"""Blender version compatibility helpers without a bpy dependency."""

from __future__ import annotations

from collections.abc import Iterable


def choose_eevee_engine(available_engine_ids: Iterable[str]) -> str:
    """Return the EEVEE identifier supported by the running Blender version.

    Blender 5.0 and later use BLENDER_EEVEE. Blender 4.x uses
    BLENDER_EEVEE_NEXT. Prefer the current identifier if both are available.
    """

    available = set(available_engine_ids)
    for identifier in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
        if identifier in available:
            return identifier

    rendered = ", ".join(sorted(available)) or "(none reported)"
    raise RuntimeError(
        "This Blender installation does not expose a supported EEVEE engine. "
        f"Available render engines: {rendered}"
    )
