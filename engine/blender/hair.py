"""Create a sculptural hairstyle from broad, flattened clumps rather than rope-like tubes."""

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
    """Build a low-profile scalp, broad swept fringe, face frames, and layered hair masses."""

    objects: list[bpy.types.Object] = []

    # The old cap extended far above the skull and read as a separate helmet.
    # This lower crown closely follows the head and leaves room for layered volume.
    cap = create_ellipsoid(
        "Hair_ScalpCap",
        (0.0, 0.085, 5.145),
        (0.535, 0.405, 0.245),
        base,
        collection,
        segments=80,
        rings=40,
        subdivision=2,
    )
    objects.append(cap)

    part_sign = -1.0 if part == "left" else 1.0
    if part == "center":
        part_sign = 0.0

    # Broad, flattened locks travel diagonally across the forehead.
    fringe_main = create_sweep(
        "Hair_SweptFringe",
        [
            (part_sign * 0.145, -0.275, 5.390, 0.064, 0.016),
            (part_sign * 0.055, -0.355, 5.335, 0.080, 0.017),
            (0.145, -0.392, 5.245, 0.074, 0.016),
            (0.330, -0.345, 5.115, 0.052, 0.013),
            (0.420, -0.270, 4.985, 0.006, 0.007),
        ],
        base,
        collection,
        radial_segments=16,
        steps_per_span=8,
        subdivision=2,
    )
    objects.append(fringe_main)

    fringe_secondary = create_sweep(
        "Hair_SweptFringe_02",
        [
            (part_sign * 0.245, -0.250, 5.365, 0.052, 0.014),
            (part_sign * 0.145, -0.345, 5.300, 0.062, 0.015),
            (0.025, -0.390, 5.205, 0.060, 0.014),
            (0.225, -0.365, 5.095, 0.008, 0.006),
        ],
        highlight,
        collection,
        radial_segments=16,
        steps_per_span=8,
        subdivision=2,
    )
    objects.append(fringe_secondary)

    fringe_third = create_sweep(
        "Hair_SweptFringe_03",
        [
            (part_sign * 0.015, -0.250, 5.405, 0.038, 0.012),
            (0.085, -0.350, 5.310, 0.050, 0.014),
            (0.275, -0.375, 5.190, 0.040, 0.012),
            (0.385, -0.305, 5.055, 0.006, 0.006),
        ],
        base,
        collection,
        radial_segments=14,
        steps_per_span=8,
        subdivision=2,
    )
    objects.append(fringe_third)

    # Two slender face frames remain in front; their cross sections are flattened.
    for side, label in ((-1.0, "L"), (1.0, "R")):
        frame = create_sweep(
            f"Hair_FaceFrame_{label}",
            [
                (side * 0.360, -0.265, 5.155, 0.050, 0.016),
                (side * 0.445, -0.335, 4.805, 0.050, 0.016),
                (side * 0.455, -0.285, 4.265, 0.046, 0.015),
                (side * 0.435, -0.180, 3.760, 0.036, 0.012),
                (side * 0.415, -0.105, 3.485, 0.006, 0.006),
            ],
            base,
            collection,
            radial_segments=16,
            steps_per_span=8,
            subdivision=2,
        )
        objects.append(frame)

    # Fewer, broader side locks overlap into readable panels rather than parallel ropes.
    for side, label in ((-1.0, "L"), (1.0, "R")):
        for index in range(3):
            offset = index / 2.0
            root_x = side * (0.355 + offset * 0.090)
            mid_x = side * (0.455 + offset * 0.075)
            end_x = side * (0.475 + offset * 0.085)
            rear_y = 0.150 + offset * 0.090
            width = 0.145 + (index % 2) * 0.025
            depth = 0.020 if index % 2 == 0 else 0.024
            material = highlight if index == 1 else base
            lock = create_sweep(
                f"Hair_SideLock_{label}_{index + 1}",
                [
                    (root_x, 0.115 + offset * 0.045, 5.205 - offset * 0.035, width * 0.82, depth),
                    (mid_x, rear_y, 4.825, width, depth),
                    (mid_x + side * 0.020, rear_y + 0.060, 4.120 - offset * 0.025, width * 0.92, depth * 0.92),
                    (end_x, rear_y + 0.080, 3.420 + offset * 0.030, width * 0.72, depth * 0.82),
                    (end_x - side * 0.025, rear_y + 0.040, 2.735 + offset * 0.035, 0.008, 0.006),
                ],
                material,
                collection,
                radial_segments=16,
                steps_per_span=8,
                subdivision=2,
            )
            objects.append(lock)

    # Wide rear panels provide a coherent silhouette and a soft, layered lower edge.
    for index in range(5):
        offset = (index - 2) / 2.0
        width = 0.175 if index % 2 == 0 else 0.155
        depth = 0.026 if index % 2 == 0 else 0.022
        back_lock = create_sweep(
            f"Hair_BackLock_{index + 1}",
            [
                (offset * 0.300, 0.300, 5.235, width * 0.86, depth),
                (offset * 0.405, 0.445, 4.850, width, depth),
                (offset * 0.475, 0.535, 4.150, width * 0.90, depth * 0.95),
                (offset * 0.525, 0.490, 3.430, width * 0.72, depth * 0.82),
                (offset * 0.490, 0.425, 2.735, 0.008, 0.006),
            ],
            highlight if index in (1, 4) else base,
            collection,
            radial_segments=16,
            steps_per_span=8,
            subdivision=2,
        )
        objects.append(back_lock)

    return objects
