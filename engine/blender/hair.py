"""Create a layered sculptural hairstyle with a swept fringe and back-draped mass.

The hairstyle is built from broad, flattened clumps with varied paths and tapers.
It is a deliberately stylized groom blockout, not a strand-level simulation.
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
    """Build a scalp cap, layered fringe, face frames, side clumps, and back clumps."""

    objects: list[bpy.types.Object] = []
    cap = create_ellipsoid(
        "Hair_ScalpCap",
        (0.0, 0.105, 5.205),
        (0.555, 0.415, 0.410),
        base,
        collection,
        segments=72,
        rings=40,
        subdivision=2,
    )
    objects.append(cap)

    part_sign = -1.0 if part == "left" else 1.0
    if part == "center":
        part_sign = 0.0

    fringe_main = create_sweep(
        "Hair_SweptFringe",
        [
            (part_sign * 0.105, -0.315, 5.485, 0.043, 0.026),
            (part_sign * 0.035, -0.395, 5.405, 0.059, 0.030),
            (0.145, -0.445, 5.275, 0.061, 0.030),
            (0.335, -0.395, 5.125, 0.043, 0.023),
            (0.425, -0.315, 4.985, 0.006, 0.008),
        ],
        highlight,
        collection,
        radial_segments=22,
        steps_per_span=7,
        subdivision=2,
    )
    objects.append(fringe_main)

    fringe_secondary = create_sweep(
        "Hair_SweptFringe_02",
        [
            (part_sign * 0.220, -0.300, 5.445, 0.034, 0.022),
            (part_sign * 0.125, -0.385, 5.345, 0.048, 0.025),
            (0.045, -0.430, 5.245, 0.043, 0.022),
            (0.245, -0.410, 5.145, 0.007, 0.009),
        ],
        base,
        collection,
        radial_segments=18,
        steps_per_span=7,
        subdivision=2,
    )
    objects.append(fringe_secondary)

    fringe_third = create_sweep(
        "Hair_SweptFringe_03",
        [
            (part_sign * 0.005, -0.285, 5.500, 0.025, 0.019),
            (0.095, -0.390, 5.375, 0.037, 0.021),
            (0.265, -0.425, 5.245, 0.032, 0.018),
            (0.385, -0.360, 5.075, 0.005, 0.007),
        ],
        highlight,
        collection,
        radial_segments=16,
        steps_per_span=7,
        subdivision=2,
    )
    objects.append(fringe_third)

    # Short face-framing locks add a softer transition from the part to the cheeks.
    for side, label in ((-1.0, "L"), (1.0, "R")):
        frame = create_sweep(
            f"Hair_FaceFrame_{label}",
            [
                (side * 0.355, -0.325, 5.205, 0.058, 0.035),
                (side * 0.445, -0.400, 4.825, 0.058, 0.034),
                (side * 0.465, -0.370, 4.365, 0.050, 0.030),
                (side * 0.445, -0.285, 3.780, 0.036, 0.023),
                (side * 0.425, -0.225, 3.510, 0.006, 0.008),
            ],
            highlight if side < 0 else base,
            collection,
            radial_segments=20,
            steps_per_span=7,
            subdivision=2,
        )
        objects.append(frame)

    # Long side clumps sit behind the shoulder line. Their widths and paths vary
    # slightly so the hair reads as layered locks instead of parallel tubes.
    for side, label in ((-1.0, "L"), (1.0, "R")):
        for index in range(4):
            offset = index / 3.0
            root_x = side * (0.335 + offset * 0.115)
            mid_x = side * (0.455 + offset * 0.105)
            end_x = side * (0.465 + offset * 0.115)
            rear_y = 0.17 + offset * 0.105
            width = 0.105 + (index % 2) * 0.018
            depth = 0.034 + (index % 2) * 0.006
            lock = create_sweep(
                f"Hair_SideLock_{label}_{index + 1}",
                [
                    (root_x, 0.075 + offset * 0.07, 5.260 - offset * 0.045, width * 0.83, depth),
                    (mid_x, rear_y, 4.835, width, depth),
                    (mid_x + side * 0.035, rear_y + 0.085, 4.115 - offset * 0.04, width * 0.82, depth * 0.90),
                    (end_x, rear_y + 0.105, 3.355 + offset * 0.04, width * 0.58, depth * 0.76),
                    (end_x - side * 0.030, rear_y + 0.075, 2.715 + offset * 0.045, 0.006, 0.008),
                ],
                highlight if index == 1 else base,
                collection,
                radial_segments=22,
                steps_per_span=7,
                subdivision=2,
            )
            objects.append(lock)

    # Broad rear locks overlap into one coherent long-hair mass behind the torso.
    for index in range(7):
        offset = (index - 3) / 3.0
        width = 0.135 if index % 2 == 0 else 0.115
        depth = 0.047 if index % 2 == 0 else 0.040
        back_lock = create_sweep(
            f"Hair_BackLock_{index + 1}",
            [
                (offset * 0.295, 0.285, 5.285, width * 0.83, depth * 0.90),
                (offset * 0.425, 0.435, 4.875, width, depth),
                (offset * 0.510, 0.505, 4.150, width * 0.86, depth * 0.94),
                (offset * 0.555, 0.470, 3.430, width * 0.66, depth * 0.82),
                (offset * 0.515, 0.415, 2.745, 0.006, 0.008),
            ],
            highlight if index in (1, 5) else base,
            collection,
            radial_segments=22,
            steps_per_span=7,
            subdivision=2,
        )
        objects.append(back_lock)

    return objects
