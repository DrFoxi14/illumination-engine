"""Build the character's original stylized body from smooth parameterized surfaces."""

from __future__ import annotations

import bpy

from engine.blender.geometry import create_ellipsoid, create_loft, create_sweep


def build_body(
    collection: bpy.types.Collection,
    skin: bpy.types.Material,
) -> list[bpy.types.Object]:
    """Create a stylized torso, neck, arms, palms, and legs in a relaxed A-pose."""

    objects: list[bpy.types.Object] = []
    torso = create_loft(
        "Body_Torso",
        [
            (2.18, 0.0, 0.0, 0.28, 0.205),
            (2.36, 0.0, 0.0, 0.34, 0.235),
            (2.62, 0.0, 0.0, 0.31, 0.205),
            (2.92, 0.0, 0.0, 0.345, 0.215),
            (3.20, 0.0, 0.0, 0.415, 0.255),
            (3.47, 0.0, 0.0, 0.465, 0.255),
            (3.67, 0.0, 0.0, 0.435, 0.235),
            (3.82, 0.0, 0.0, 0.265, 0.195),
            (3.91, 0.0, 0.0, 0.165, 0.155),
        ],
        skin,
        collection,
        radial_segments=64,
        steps_per_span=6,
        subdivision=2,
    )
    objects.append(torso)
    neck = create_sweep(
        "Body_Neck",
        [
            (0.0, 0.0, 3.72, 0.145, 0.145),
            (0.0, 0.0, 3.91, 0.145, 0.140),
            (0.0, 0.0, 4.13, 0.175, 0.155),
        ],
        skin,
        collection,
        radial_segments=32,
        steps_per_span=5,
        subdivision=2,
    )
    objects.append(neck)

    for side, label in ((-1.0, "L"), (1.0, "R")):
        leg = create_sweep(
            f"Body_Leg_{label}",
            [
                (side * 0.19, 0.005, 2.34, 0.205, 0.205),
                (side * 0.205, 0.0, 1.92, 0.178, 0.175),
                (side * 0.215, -0.015, 1.37, 0.135, 0.135),
                (side * 0.215, 0.0, 0.87, 0.112, 0.115),
                (side * 0.205, -0.015, 0.36, 0.105, 0.11),
            ],
            skin,
            collection,
            radial_segments=32,
            steps_per_span=7,
            subdivision=2,
        )
        objects.append(leg)
        arm = create_sweep(
            f"Body_Arm_{label}",
            [
                (side * 0.39, 0.0, 3.63, 0.155, 0.155),
                (side * 0.57, -0.005, 3.40, 0.135, 0.135),
                (side * 0.69, -0.015, 3.10, 0.112, 0.112),
                (side * 0.72, -0.045, 2.86, 0.085, 0.09),
            ],
            skin,
            collection,
            radial_segments=28,
            steps_per_span=6,
            subdivision=2,
        )
        objects.append(arm)
        palm = create_ellipsoid(
            f"Body_Palm_{label}",
            (side * 0.73, -0.055, 2.76),
            (0.105, 0.065, 0.145),
            skin,
            collection,
            segments=28,
            rings=18,
            subdivision=1,
        )
        objects.append(palm)

        for finger_index in range(4):
            spread = finger_index - 1.5
            start_x = side * (0.73 + spread * 0.036)
            end_x = start_x + side * spread * 0.018
            finger = create_sweep(
                f"Body_Finger_{label}_{finger_index + 1}",
                [
                    (start_x, -0.083, 2.72, 0.024, 0.025),
                    (end_x, -0.095, 2.64, 0.020, 0.021),
                    (end_x + side * 0.004, -0.098, 2.59, 0.010, 0.012),
                ],
                skin,
                collection,
                radial_segments=12,
                steps_per_span=4,
                subdivision=1,
            )
            objects.append(finger)
        thumb = create_sweep(
            f"Body_Thumb_{label}",
            [
                (side * 0.65, -0.075, 2.78, 0.035, 0.034),
                (side * 0.62, -0.095, 2.72, 0.027, 0.027),
                (side * 0.615, -0.102, 2.68, 0.014, 0.016),
            ],
            skin,
            collection,
            radial_segments=12,
            steps_per_span=4,
            subdivision=1,
        )
        objects.append(thumb)
    return objects
