"""Build a restrained stylized face with inset eyes and softer facial proportions."""

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
    """Build inset eyes, thin lids, softer brows, a smaller nose, and a closed smile."""

    objects: list[bpy.types.Object] = []
    scale = eye_scale * 0.76

    for side, label in ((-1.0, "L"), (1.0, "R")):
        eye_x = side * 0.205
        eye_y = -0.365
        eye_z = 4.765

        eye = create_ellipsoid(
            f"Face_Eyeball_{label}",
            (eye_x, eye_y, eye_z),
            (0.126 * scale, 0.058, 0.105 * scale),
            eye_white,
            collection,
            segments=48,
            rings=28,
            subdivision=2,
        )
        iris_obj = create_ellipsoid(
            f"Face_Iris_{label}",
            (eye_x - side * 0.004, -0.416, eye_z - 0.004),
            (0.052 * scale, 0.014, 0.060 * scale),
            iris,
            collection,
            segments=36,
            rings=24,
            subdivision=1,
        )
        pupil = create_ellipsoid(
            f"Face_Pupil_{label}",
            (eye_x - side * 0.004, -0.427, eye_z - 0.004),
            (0.027 * scale, 0.008, 0.038 * scale),
            dark,
            collection,
            segments=28,
            rings=20,
            subdivision=1,
        )
        main_glint = create_ellipsoid(
            f"Face_EyeCatchlight_{label}",
            (eye_x - side * 0.022, -0.437, eye_z + 0.022),
            (0.013 * scale, 0.004, 0.016 * scale),
            eye_white,
            collection,
            segments=20,
            rings=14,
            subdivision=1,
        )
        secondary_glint = create_ellipsoid(
            f"Face_EyeSpark_{label}",
            (eye_x + side * 0.018, -0.435, eye_z - 0.025),
            (0.006 * scale, 0.003, 0.008 * scale),
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
                (side * 0.335, -0.397, 4.756, 0.010, 0.009),
                (side * 0.292, -0.423, 4.825, 0.013, 0.010),
                (side * 0.205, -0.431, 4.853, 0.014, 0.011),
                (side * 0.118, -0.423, 4.824, 0.013, 0.010),
                (side * 0.075, -0.397, 4.770, 0.009, 0.008),
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
                (side * 0.332, -0.395, 4.757, 0.008, 0.008),
                (side * 0.290, -0.414, 4.707, 0.010, 0.009),
                (side * 0.205, -0.423, 4.692, 0.011, 0.009),
                (side * 0.120, -0.414, 4.708, 0.010, 0.009),
                (side * 0.078, -0.395, 4.771, 0.008, 0.008),
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
                (side * 0.115, -0.397, 4.888, 0.005, 0.005),
                (side * 0.205, -0.411, 4.901, 0.006, 0.005),
                (side * 0.292, -0.397, 4.876, 0.005, 0.005),
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
                (side * 0.088, -0.388, 4.965, 0.012, 0.010),
                (side * 0.190, -0.414, 4.994, 0.017, 0.012),
                (side * 0.292, -0.393, 4.982, 0.015, 0.011),
                (side * 0.366, -0.365, 4.954, 0.008, 0.007),
            ],
            iris,
            collection,
            radial_segments=14,
            steps_per_span=6,
            subdivision=2,
        )
        objects.extend((upper_lid, lower_lid, lid_crease, brow))

        ear = create_ellipsoid(
            f"Face_Ear_{label}",
            (side * 0.510, 0.010, 4.575),
            (0.085, 0.082, 0.140),
            skin,
            collection,
            segments=32,
            rings=22,
            subdivision=2,
        )
        inner_ear = create_sweep(
            f"Face_InnerEar_{label}",
            [
                (side * 0.503, -0.057, 4.620, 0.007, 0.007),
                (side * 0.530, -0.066, 4.575, 0.009, 0.008),
                (side * 0.505, -0.057, 4.530, 0.006, 0.006),
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
            (0.0, -0.374, 4.680, 0.030, 0.031),
            (0.0, -0.407, 4.555, 0.038, 0.038),
            (0.0, -0.445, 4.448, 0.050, 0.046),
        ],
        skin,
        collection,
        radial_segments=20,
        steps_per_span=7,
        subdivision=2,
    )
    nose_tip = create_ellipsoid(
        "Face_NoseTip",
        (0.0, -0.457, 4.425),
        (0.068, 0.058, 0.052),
        skin,
        collection,
        segments=36,
        rings=24,
        subdivision=2,
    )
    nose_wing_left = create_ellipsoid(
        "Face_NoseWing_L",
        (-0.052, -0.447, 4.414),
        (0.032, 0.030, 0.025),
        skin,
        collection,
        segments=24,
        rings=16,
        subdivision=1,
    )
    nose_wing_right = create_ellipsoid(
        "Face_NoseWing_R",
        (0.052, -0.447, 4.414),
        (0.032, 0.030, 0.025),
        skin,
        collection,
        segments=24,
        rings=16,
        subdivision=1,
    )

    mouth = create_ellipsoid(
        "Face_MouthOpening",
        (0.0, -0.382, 4.198),
        (0.096, 0.014, 0.026),
        dark,
        collection,
        segments=36,
        rings=22,
        subdivision=1,
    )
    teeth = create_ellipsoid(
        "Face_Teeth",
        (0.0, -0.399, 4.207),
        (0.062, 0.006, 0.008),
        eye_white,
        collection,
        segments=32,
        rings=18,
        subdivision=1,
    )
    upper_lip = create_sweep(
        "Face_UpperLip",
        [
            (-0.104, -0.386, 4.204, 0.007, 0.006),
            (-0.052, -0.401, 4.214, 0.010, 0.007),
            (0.0, -0.404, 4.207, 0.009, 0.007),
            (0.052, -0.401, 4.214, 0.010, 0.007),
            (0.104, -0.386, 4.204, 0.007, 0.006),
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
            (-0.098, -0.386, 4.190, 0.006, 0.006),
            (-0.050, -0.402, 4.180, 0.010, 0.008),
            (0.0, -0.405, 4.178, 0.011, 0.008),
            (0.050, -0.402, 4.180, 0.010, 0.008),
            (0.098, -0.386, 4.190, 0.006, 0.006),
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
