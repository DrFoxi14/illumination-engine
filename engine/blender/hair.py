"""Create a sculptural long hairstyle with a clear face frame and back-draped mass.

The front silhouette keeps the torso readable: only two short framing locks fall
beside the face, while the longer locks sit behind the shoulders and body.
"""

from __future__ import annotations

import bpy

from engine.blender.geometry import create_ellipsoid, create_sweep


def build_hair(
    collection: bpy.types.Collection,
    *,
    base: bpy.types.Material,
    highlight: bpy.types.Material,
    part: str = "left",
) -> list[bpy.types.Object]:
    """Build a scalp cap, swept fringe, short face frames, and long rear clumps."""

    objects: list[bpy.types.Object] = []
    cap = create_ellipsoid(
        "Hair_ScalpCap",
        (0.0, 0.105, 5.205),
        (0.560, 0.430, 0.430),
        base,
        collection,
        segments=64,
        rings=36,
        subdivision=2,
    )
    objects.append(cap)

    part_sign = -1.0 if part == "left" else 1.0
    if part == "center":
        part_sign = 0.0

    fringe = create_sweep(
        "Hair_SweptFringe",
        [
            (-0.31 + part_sign * 0.075, -0.345, 5.405, 0.068, 0.046),
            (-0.16 + part_sign * 0.075, -0.438, 5.325, 0.082, 0.052),
            (0.08 + part_sign * 0.080, -0.450, 5.215, 0.074, 0.048),
            (0.31 + part_sign * 0.065, -0.375, 5.065, 0.044, 0.034),
            (0.405 + part_sign * 0.035, -0.300, 4.940, 0.010, 0.014),
        ],
        highlight,
        collection,
        radial_segments=20,
        steps_per_span=7,
        subdivision=2,
    )
    objects.append(fringe)

    # Two short front locks frame the cheeks, but stop around the upper chest.
    for side, label in ((-1.0, "L"), (1.0, "R")):
        frame = create_sweep(
            f"Hair_FaceFrame_{label}",
            [
                (side * 0.355, -0.345, 5.205, 0.062, 0.048),
                (side * 0.445, -0.405, 4.835, 0.058, 0.043),
                (side * 0.465, -0.375, 4.355, 0.050, 0.037),
                (side * 0.445, -0.295, 3.765, 0.037, 0.030),
                (side * 0.425, -0.235, 3.485, 0.006, 0.009),
            ],
            highlight if side < 0 else base,
            collection,
            radial_segments=18,
            steps_per_span=6,
            subdivision=2,
        )
        objects.append(frame)

    # Long side panels are positioned behind the shoulder line, not over the torso.
    for side, label in ((-1.0, "L"), (1.0, "R")):
        for index in range(5):
            offset = index / 4.0
            root_x = side * (0.345 + offset * 0.105)
            mid_x = side * (0.455 + offset * 0.085)
            end_x = side * (0.455 + offset * 0.115)
            rear_y = 0.17 + offset * 0.115
            material = highlight if index in (1, 4) else base
            lock = create_sweep(
                f"Hair_SideLock_{label}_{index + 1}",
                [
                    (root_x, 0.075 + offset * 0.07, 5.265 - offset * 0.045, 0.092, 0.070),
                    (mid_x, rear_y, 4.835, 0.092, 0.072),
                    (mid_x + side * 0.030, rear_y + 0.075, 4.105, 0.079, 0.063),
                    (end_x, rear_y + 0.10, 3.335 + offset * 0.045, 0.055, 0.045),
                    (end_x - side * 0.035, rear_y + 0.075, 2.665 + offset * 0.055, 0.006, 0.009),
                ],
                material,
                collection,
                radial_segments=18,
                steps_per_span=6,
                subdivision=2,
            )
            objects.append(lock)

    # Broad overlapping back clumps create a continuous long-hair silhouette.
    for index in range(9):
        offset = (index - 4) / 4.0
        back_lock = create_sweep(
            f"Hair_BackLock_{index + 1}",
            [
                (offset * 0.300, 0.285, 5.285, 0.105, 0.082),
                (offset * 0.425, 0.435, 4.875, 0.112, 0.086),
                (offset * 0.510, 0.505, 4.135, 0.092, 0.072),
                (offset * 0.565, 0.475, 3.420, 0.068, 0.053),
                (offset * 0.515, 0.420, 2.735, 0.006, 0.009),
            ],
            base if index % 3 else highlight,
            collection,
            radial_segments=20,
            steps_per_span=6,
            subdivision=2,
        )
        objects.append(back_lock)

    return objects
