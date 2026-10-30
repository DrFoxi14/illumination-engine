"""Build the character's original stylized body from smooth parameterized surfaces."""

from __future__ import annotations

import bpy

from engine.blender.geometry import create_ellipsoid, create_loft, create_sweep


def build_body(
    collection: bpy.types.Collection,
    skin: bpy.types.Material,
    *,
    pose: str = "neutral_standing",
) -> list[bpy.types.Object]:
    """Create the body in a relaxed pose or a static mirror-selfie presentation pose."""

    if pose not in {"neutral_standing", "mirror_selfie"}:
        raise ValueError(f"Unsupported body presentation pose: {pose}")

    objects: list[bpy.types.Object] = []
    torso = create_loft(
        "Body_Torso",
        [
            (2.18, 0.0, 0.0, 0.28, 0.205),
            (2.36, 0.0, 0.0, 0.34, 0.235),
            (2.62, 0.0, 0.0, 0.31, 0.205),
            (2.92, 0.0, 0.0, 0.345, 0.215),
            (3.20, 0.0, 0.0, 0.425, 0.260),
            (3.47, 0.0, 0.0, 0.500, 0.270),
            (3.67, 0.0, 0.0, 0.455, 0.245),
            (3.82, 0.0, 0.0, 0.275, 0.198),
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
        foot = create_sweep(
            f"Body_Foot_{label}",
            [
                (side * 0.205, -0.005, 0.36, 0.105, 0.105),
                (side * 0.205, -0.125, 0.255, 0.115, 0.145),
                (side * 0.205, -0.285, 0.205, 0.108, 0.185),
                (side * 0.205, -0.365, 0.190, 0.082, 0.135),
            ],
            skin,
            collection,
            radial_segments=28,
            steps_per_span=5,
            subdivision=2,
        )
        objects.append(foot)

        if pose == "mirror_selfie" and side > 0:
            arm = create_sweep(
                f"Body_Arm_{label}",
                [
                    (side * 0.425, 0.0, 3.63, 0.170, 0.160),
                    (side * 0.595, -0.035, 3.89, 0.145, 0.140),
                    (side * 0.545, -0.190, 4.155, 0.118, 0.112),
                    (side * 0.385, -0.355, 4.405, 0.090, 0.088),
                ],
                skin,
                collection,
                radial_segments=28,
                steps_per_span=7,
                subdivision=2,
            )
            palm = create_ellipsoid(
                f"Body_Palm_{label}",
                (side * 0.350, -0.395, 4.475),
                (0.104, 0.070, 0.122),
                skin,
                collection,
                segments=32,
                rings=22,
                subdivision=2,
            )
            objects.extend((arm, palm))

            # Curled fingers wrap around the side of the phone instead of hanging down.
            for finger_index in range(4):
                offset = finger_index - 1.5
                finger = create_sweep(
                    f"Body_Finger_{label}_{finger_index + 1}",
                    [
                        # The first control sits well inside the palm volume so voxel
                        # remeshing fuses each finger root into the hand reliably.
                        (side * (0.350 + offset * 0.015), -0.390, 4.475 + offset * 0.025, 0.025, 0.023),
                        (side * (0.430 + offset * 0.022), -0.475, 4.485 + offset * 0.040, 0.018, 0.017),
                        (side * (0.435 + offset * 0.020), -0.486, 4.455 + offset * 0.040, 0.009, 0.010),
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
                    (side * 0.295, -0.435, 4.465, 0.032, 0.030),
                    (side * 0.270, -0.475, 4.500, 0.025, 0.024),
                    (side * 0.285, -0.490, 4.535, 0.012, 0.013),
                ],
                skin,
                collection,
                radial_segments=12,
                steps_per_span=5,
                subdivision=1,
            )
            objects.append(thumb)
        else:
            arm = create_sweep(
                f"Body_Arm_{label}",
                [
                    (side * 0.425, 0.0, 3.63, 0.170, 0.160),
                    (side * 0.615, -0.005, 3.40, 0.148, 0.142),
                    (side * 0.735, -0.015, 3.10, 0.122, 0.122),
                    (side * 0.765, -0.045, 2.86, 0.092, 0.095),
                ],
                skin,
                collection,
                radial_segments=28,
                steps_per_span=6,
                subdivision=2,
            )
            palm = create_ellipsoid(
                f"Body_Palm_{label}",
                (side * 0.775, -0.055, 2.76),
                (0.108, 0.068, 0.148),
                skin,
                collection,
                segments=28,
                rings=18,
                subdivision=1,
            )
            objects.extend((arm, palm))

            for finger_index in range(4):
                spread = finger_index - 1.5
                start_x = side * (0.775 + spread * 0.037)
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
                    (side * 0.695, -0.075, 2.78, 0.035, 0.034),
                    (side * 0.665, -0.095, 2.72, 0.027, 0.027),
                    (side * 0.660, -0.102, 2.68, 0.014, 0.016),
                ],
                skin,
                collection,
                radial_segments=12,
                steps_per_span=4,
                subdivision=1,
            )
            objects.append(thumb)
    return objects
