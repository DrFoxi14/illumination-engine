"""Build an expressive stylized face with inset eyes and sculpted-looking features."""

from __future__ import annotations

import bpy

from engine.blender.geometry import create_ellipsoid, create_sweep


def build_face(
    collection: bpy.types.Collection,
    *,
    skin: bpy.types.Material,
    iris: bpy.types.Material,
    eye_white: bpy.types.Material,
    dark: bpy.types.Material,
    lip: bpy.types.Material,
    eye_scale: float = 1.0,
) -> list[bpy.types.Object]:
    """Build eyes, eyelids, brows, nose, ears, and a small readable smile.

    The old full ellipsoid socket created a visible concentric ring around each eye.
    The revised design seats the eyeballs closer to the head and uses upper/lower
    lid arcs to define the opening instead of a separate raised socket sphere.
    """

    objects: list[bpy.types.Object] = []
    scale = eye_scale * 0.90

    for side, label in ((-1.0, "L"), (1.0, "R")):
        eye_x = side * 0.205
        eye_y = -0.401
        eye_z = 4.765

        eye = create_ellipsoid(
            f"Face_Eyeball_{label}",
            (eye_x, eye_y, eye_z),
            (0.135 * scale, 0.074, 0.119 * scale),
            eye_white,
            collection,
            segments=48,
            rings=28,
            subdivision=2,
        )
        iris_obj = create_ellipsoid(
            f"Face_Iris_{label}",
            (eye_x - side * 0.006, -0.466, eye_z - 0.006),
            (0.061 * scale, 0.020, 0.071 * scale),
            iris,
            collection,
            segments=36,
            rings=24,
            subdivision=1,
        )
        pupil = create_ellipsoid(
            f"Face_Pupil_{label}",
            (eye_x - side * 0.006, -0.481, eye_z - 0.006),
            (0.032 * scale, 0.011, 0.044 * scale),
            dark,
            collection,
            segments=28,
            rings=20,
            subdivision=1,
        )
        main_glint = create_ellipsoid(
            f"Face_EyeCatchlight_{label}",
            (eye_x - side * 0.025, -0.493, eye_z + 0.027),
            (0.018 * scale, 0.007, 0.022 * scale),
            eye_white,
            collection,
            segments=20,
            rings=14,
            subdivision=1,
        )
        secondary_glint = create_ellipsoid(
            f"Face_EyeSpark_{label}",
            (eye_x + side * 0.020, -0.491, eye_z - 0.028),
            (0.008 * scale, 0.004, 0.010 * scale),
            eye_white,
            collection,
            segments=12,
            rings=10,
            subdivision=0,
        )
        objects.extend((eye, iris_obj, pupil, main_glint, secondary_glint))

        upper_lid = create_sweep(
            f"Face_UpperEyelid_{label}",
            [
                (side * 0.350, -0.432, 4.754, 0.014, 0.012),
                (side * 0.300, -0.461, 4.836, 0.018, 0.015),
                (side * 0.205, -0.477, 4.866, 0.019, 0.016),
                (side * 0.110, -0.461, 4.835, 0.017, 0.014),
                (side * 0.064, -0.432, 4.770, 0.012, 0.011),
            ],
            skin,
            collection,
            radial_segments=12,
            steps_per_span=6,
            subdivision=1,
        )
        lower_lid = create_sweep(
            f"Face_LowerEyelid_{label}",
            [
                (side * 0.345, -0.428, 4.755, 0.011, 0.010),
                (side * 0.295, -0.450, 4.700, 0.014, 0.012),
                (side * 0.205, -0.466, 4.684, 0.015, 0.013),
                (side * 0.115, -0.450, 4.701, 0.014, 0.012),
                (side * 0.067, -0.428, 4.770, 0.011, 0.010),
            ],
            skin,
            collection,
            radial_segments=12,
            steps_per_span=6,
            subdivision=1,
        )
        lid_crease = create_sweep(
            f"Face_EyelidCrease_{label}",
            [
                (side * 0.105, -0.415, 4.900, 0.007, 0.007),
                (side * 0.205, -0.435, 4.918, 0.009, 0.008),
                (side * 0.300, -0.414, 4.885, 0.007, 0.007),
            ],
            skin,
            collection,
            radial_segments=10,
            steps_per_span=5,
            subdivision=1,
        )
        brow = create_sweep(
            f"Face_Brow_{label}",
            [
                (side * 0.078, -0.414, 4.982, 0.019, 0.018),
                (side * 0.185, -0.444, 5.018, 0.027, 0.022),
                (side * 0.292, -0.417, 5.005, 0.025, 0.021),
                (side * 0.370, -0.385, 4.969, 0.012, 0.012),
            ],
            dark,
            collection,
            radial_segments=14,
            steps_per_span=6,
            subdivision=2,
        )
        objects.extend((upper_lid, lower_lid, lid_crease, brow))

        ear = create_ellipsoid(
            f"Face_Ear_{label}",
            (side * 0.515, 0.010, 4.575),
            (0.094, 0.094, 0.154),
            skin,
            collection,
            segments=32,
            rings=22,
            subdivision=2,
        )
        inner_ear = create_sweep(
            f"Face_InnerEar_{label}",
            [
                (side * 0.505, -0.078, 4.625, 0.010, 0.010),
                (side * 0.540, -0.083, 4.575, 0.013, 0.012),
                (side * 0.505, -0.078, 4.525, 0.008, 0.008),
            ],
            skin,
            collection,
            radial_segments=10,
            steps_per_span=5,
            subdivision=1,
        )
        objects.extend((ear, inner_ear))

    nose_bridge = create_sweep(
        "Face_NoseBridge",
        [
            (0.0, -0.385, 4.680, 0.040, 0.043),
            (0.0, -0.428, 4.555, 0.050, 0.052),
            (0.0, -0.469, 4.448, 0.068, 0.060),
        ],
        skin,
        collection,
        radial_segments=20,
        steps_per_span=7,
        subdivision=2,
    )
    nose_tip = create_ellipsoid(
        "Face_NoseTip",
        (0.0, -0.485, 4.425),
        (0.086, 0.073, 0.060),
        skin,
        collection,
        segments=36,
        rings=24,
        subdivision=2,
    )
    nose_wing_left = create_ellipsoid(
        "Face_NoseWing_L",
        (-0.064, -0.468, 4.414),
        (0.041, 0.038, 0.032),
        skin,
        collection,
        segments=24,
        rings=16,
        subdivision=1,
    )
    nose_wing_right = create_ellipsoid(
        "Face_NoseWing_R",
        (0.064, -0.468, 4.414),
        (0.041, 0.038, 0.032),
        skin,
        collection,
        segments=24,
        rings=16,
        subdivision=1,
    )

    mouth = create_ellipsoid(
        "Face_MouthOpening",
        (0.0, -0.387, 4.199),
        (0.126, 0.021, 0.043),
        dark,
        collection,
        segments=36,
        rings=22,
        subdivision=1,
    )
    teeth = create_ellipsoid(
        "Face_Teeth",
        (0.0, -0.411, 4.214),
        (0.085, 0.010, 0.016),
        eye_white,
        collection,
        segments=32,
        rings=18,
        subdivision=1,
    )
    upper_lip = create_sweep(
        "Face_UpperLip",
        [
            (-0.132, -0.392, 4.205, 0.010, 0.009),
            (-0.068, -0.410, 4.220, 0.014, 0.011),
            (0.0, -0.416, 4.211, 0.013, 0.010),
            (0.068, -0.410, 4.220, 0.014, 0.011),
            (0.132, -0.392, 4.205, 0.010, 0.009),
        ],
        lip,
        collection,
        radial_segments=12,
        steps_per_span=5,
        subdivision=1,
    )
    lower_lip = create_sweep(
        "Face_LowerLip",
        [
            (-0.120, -0.394, 4.190, 0.009, 0.009),
            (-0.062, -0.414, 4.174, 0.015, 0.012),
            (0.0, -0.417, 4.170, 0.016, 0.012),
            (0.062, -0.414, 4.174, 0.015, 0.012),
            (0.120, -0.394, 4.190, 0.009, 0.009),
        ],
        skin,
        collection,
        radial_segments=12,
        steps_per_span=5,
        subdivision=1,
    )
    objects.extend(
        (
            nose_bridge,
            nose_tip,
            nose_wing_left,
            nose_wing_right,
            mouth,
            teeth,
            upper_lip,
            lower_lip,
        )
    )
    return objects
