"""Create a stylized hairstyle from tapered, sculptural mesh clumps."""

from __future__ import annotations


from engine.blender.geometry import create_ellipsoid, create_sweep


def build_hair(
    collection: bpy.types.Collection,
    *,
    base: bpy.types.Material,
    highlight: bpy.types.Material,
    part: str = "left",
) -> list[bpy.types.Object]:
    """Create a scalp cap, swept fringe, and long tapered side/back clumps."""

    objects: list[bpy.types.Object] = []
    cap = create_ellipsoid(
        "Hair_ScalpCap",
        (0.0, 0.085, 5.145),
        (0.575, 0.455, 0.505),
        base,
        collection,
        segments=56,
        rings=32,
        subdivision=2,
    )
    objects.append(cap)

    part_sign = -1.0 if part == "left" else 1.0
    if part == "center":
        part_sign = 0.0

    fringe = create_sweep(
        "Hair_SweptFringe",
        [
            (-0.30 + part_sign * 0.08, -0.350, 5.385, 0.070, 0.048),
            (-0.14 + part_sign * 0.08, -0.445, 5.315, 0.083, 0.052),
            (0.10 + part_sign * 0.09, -0.455, 5.205, 0.076, 0.048),
            (0.34 + part_sign * 0.07, -0.365, 5.035, 0.025, 0.026),
        ],
        highlight,
        collection,
        radial_segments=20,
        steps_per_span=7,
        subdivision=2,
    )
    objects.append(fringe)

    for side, label in ((-1.0, "L"), (1.0, "R")):
        for index in range(6):
            offset = index / 5.0
            root_x = side * (0.34 + offset * 0.10)
            mid_x = side * (0.48 + offset * 0.055)
            end_x = side * (0.47 + offset * 0.065)
            base_y = -0.12 + offset * 0.24
            material = highlight if index in (1, 4) else base
            lock = create_sweep(
                f"Hair_SideLock_{label}_{index + 1}",
                [
                    (root_x, base_y, 5.30 - offset * 0.055, 0.095, 0.072),
                    (mid_x, base_y + 0.08, 4.87, 0.094, 0.070),
                    (mid_x + side * 0.025, base_y + 0.15, 4.16, 0.080, 0.061),
                    (end_x, base_y + 0.12, 3.36 + offset * 0.08, 0.058, 0.052),
                    (end_x - side * 0.045, base_y + 0.08, 2.64 + offset * 0.08, 0.008, 0.010),
                ],
                material,
                collection,
                radial_segments=18,
                steps_per_span=6,
                subdivision=2,
            )
            objects.append(lock)

    for index in range(9):
        offset = (index - 4) / 4.0
        back_lock = create_sweep(
            f"Hair_BackLock_{index + 1}",
            [
                (offset * 0.29, 0.31, 5.30, 0.090, 0.072),
                (offset * 0.40, 0.42, 4.90, 0.093, 0.072),
                (offset * 0.48, 0.47, 4.18, 0.078, 0.064),
                (offset * 0.52, 0.44, 3.45, 0.058, 0.050),
                (offset * 0.48, 0.39, 2.76, 0.009, 0.010),
            ],
            base if index % 3 else highlight,
            collection,
            radial_segments=18,
            steps_per_span=6,
            subdivision=2,
        )
        objects.append(back_lock)

    return objects
