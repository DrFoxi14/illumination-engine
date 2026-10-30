"""Normalized region selectors for Prototype 001 fitted clothing.

Coordinates are normalized against the imported base body's local-space bounds:
x and y range approximately from -1 to 1; z ranges from 0 (feet) to 1 (head).
Keeping these rules pure Python makes them easy to test without Blender.
"""

from __future__ import annotations


def keep_crop_top(x: float, _y: float, z: float) -> bool:
    """Keep the torso and upper-arm surface for a simple short-sleeved top."""

    return 0.535 <= z <= 0.795 and abs(x) <= 0.76


def keep_shorts(x: float, _y: float, z: float) -> bool:
    """Keep the pelvis and upper-thigh surface for modest fitted shorts."""

    return 0.365 <= z <= 0.565 and abs(x) <= 0.98


def keep_socks(x: float, _y: float, z: float) -> bool:
    """Keep the lower-leg surface for ankle socks."""

    return 0.035 <= z <= 0.135 and abs(x) <= 0.95
