"""Build an original stylized head with a designed jaw, cheeks, and chin."""

from __future__ import annotations

import bpy

from engine.blender.geometry import create_loft


def build_head(
    collection: bpy.types.Collection,
    skin: bpy.types.Material,
    *,
    scale: float = 1.0,
) -> bpy.types.Object:
    """Create a continuous head surface with a tapered jaw and rounded cranium."""

    profile = [
        (3.98, 0.0, 0.012, 0.17 * scale, 0.19 * scale),
        (4.07, 0.0, 0.008, 0.255 * scale, 0.285 * scale),
        (4.20, 0.0, 0.0, 0.355 * scale, 0.345 * scale),
        (4.36, 0.0, 0.0, 0.455 * scale, 0.392 * scale),
        (4.56, 0.0, 0.0, 0.515 * scale, 0.425 * scale),
        (4.78, 0.0, 0.012, 0.535 * scale, 0.435 * scale),
        (4.99, 0.0, 0.025, 0.505 * scale, 0.415 * scale),
        (5.17, 0.0, 0.040, 0.405 * scale, 0.355 * scale),
        (5.29, 0.0, 0.045, 0.245 * scale, 0.245 * scale),
        (5.34, 0.0, 0.045, 0.08 * scale, 0.10 * scale),
    ]
    return create_loft(
        "Head_Main",
        profile,
        skin,
        collection,
        radial_segments=80,
        steps_per_span=7,
        subdivision=2,
    )
