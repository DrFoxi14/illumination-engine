"""Create expressive face features as separate, animator-friendly mesh parts."""

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
    """Build paired eyes with lids, brows, nose, ears, and a restrained smile."""

    objects: list[bpy.types.Object] = []

    for side, label in ((-1.0, "L"), (1.0, "R")):
        socket = create_ellipsoid(
            f"Face_EyeSocket_{label}",
            (side * 0.205, -0.365, 4.765),
            (0.184 * eye_scale, 0.096, 0.205 * eye_scale),
            skin,
            collection,
            segments=40,
            rings=24,
            subdivision=1,
        )
        eye = create_ellipsoid(
            f"Face_Eyeball_{label}",
            (side * 0.205, -0.427, 4.765),
            (0.145 * eye_scale, 0.103, 0.164 * eye_scale),
            eye_white,
            collection,
            segments=40,
            rings=24,
            subdivision=1,
        )
        iris_obj = create_ellipsoid(
            f"Face_Iris_{label}",
            (side * 0.190, -0.520, 4.758),
            (0.067 * eye_scale, 0.025, 0.080 * eye_scale),
            iris,
            collection,
            segments=32,
            rings=20,
            subdivision=1,
        )
        pupil = create_ellipsoid(
            f"Face_Pupil_{label}",
            (side * 0.190, -0.541, 4.758),
            (0.032 * eye_scale, 0.014, 0.049 * eye_scale),
            dark,
            collection,
            segments=24,
            rings=16,
            subdivision=1,
        )
        sparkle = create_ellipsoid(
            f"Face_EyeCatchlight_{label}",
            (side * 0.165, -0.556, 4.792),
            (0.020 * eye_scale, 0.010, 0.025 * eye_scale),
            eye_white,
            collection,
            segments=16,
            rings=12,
            subdivision=0,
        )
        objects.extend((socket, eye, iris_obj, pupil, sparkle))

        upper_lid = create_sweep(
            f"Face_UpperEyelid_{label}",
            [
                (side * 0.350, -0.468, 4.755, 0.022, 0.022),
                (side * 0.305, -0.505, 4.865, 0.026, 0.024),
                (side * 0.205, -0.527, 4.900, 0.028, 0.025),
                (side * 0.105, -0.505, 4.860, 0.026, 0.024),
                (side * 0.060, -0.468, 4.770, 0.020, 0.020),
            ],
            skin,
            collection,
            radial_segments=12,
            steps_per_span=5,
            subdivision=1,
        )
        lower_lid = create_sweep(
            f"Face_LowerEyelid_{label}",
            [
                (side * 0.350, -0.466, 4.755, 0.018, 0.018),
                (side * 0.300, -0.495, 4.675, 0.020, 0.020),
                (side * 0.205, -0.510, 4.650, 0.022, 0.020),
                (side * 0.110, -0.495, 4.680, 0.020, 0.020),
                (side * 0.060, -0.466, 4.770, 0.018, 0.018),
            ],
            skin,
            collection,
            radial_segments=12,
            steps_per_span=5,
            subdivision=1,
        )
        brow = create_sweep(
            f"Face_Brow_{label}",
            [
                (side * 0.075, -0.437, 4.985, 0.026, 0.028),
                (side * 0.190, -0.465, 5.025, 0.039, 0.035),
                (side * 0.305, -0.425, 5.010, 0.032, 0.030),
                (side * 0.375, -0.390, 4.965, 0.018, 0.018),
            ],
            dark,
            collection,
            radial_segments=14,
            steps_per_span=5,
            subdivision=1,
        )
        objects.extend((upper_lid, lower_lid, brow))

        ear = create_ellipsoid(
            f"Face_Ear_{label}",
            (side * 0.505, 0.005, 4.570),
            (0.105, 0.105, 0.175),
            skin,
            collection,
            segments=28,
            rings=20,
            subdivision=1,
        )
        objects.append(ear)

    nose_bridge = create_sweep(
        "Face_NoseBridge",
        [
            (0.0, -0.387, 4.690, 0.055, 0.060),
            (0.0, -0.442, 4.555, 0.068, 0.071),
            (0.0, -0.482, 4.440, 0.088, 0.090),
        ],
        skin,
        collection,
        radial_segments=20,
        steps_per_span=6,
        subdivision=2,
    )
    nose_tip = create_ellipsoid(
        "Face_NoseTip",
        (0.0, -0.500, 4.425),
        (0.105, 0.090, 0.078),
        skin,
        collection,
        segments=32,
        rings=20,
        subdivision=1,
    )
    nose_wing_left = create_ellipsoid(
        "Face_NoseWing_L",
        (-0.075, -0.475, 4.410),
        (0.055, 0.050, 0.045),
        skin,
        collection,
        segments=24,
        rings=16,
        subdivision=1,
    )
    nose_wing_right = create_ellipsoid(
        "Face_NoseWing_R",
        (0.075, -0.475, 4.410),
        (0.055, 0.050, 0.045),
        skin,
        collection,
        segments=24,
        rings=16,
        subdivision=1,
    )
    mouth = create_ellipsoid(
        "Face_MouthOpening",
        (0.0, -0.414, 4.195),
        (0.155, 0.030, 0.061),
        dark,
        collection,
        segments=36,
        rings=20,
        subdivision=1,
    )
    teeth = create_ellipsoid(
        "Face_Teeth",
        (0.0, -0.448, 4.211),
        (0.110, 0.016, 0.025),
        eye_white,
        collection,
        segments=32,
        rings=16,
        subdivision=1,
    )
    upper_lip = create_sweep(
        "Face_UpperLip",
        [
            (-0.160, -0.432, 4.205, 0.014, 0.014),
            (-0.080, -0.448, 4.229, 0.018, 0.014),
            (0.0, -0.454, 4.214, 0.017, 0.014),
            (0.080, -0.448, 4.229, 0.018, 0.014),
            (0.160, -0.432, 4.205, 0.014, 0.014),
        ],
        lip,
        collection,
        radial_segments=12,
        steps_per_span=4,
        subdivision=1,
    )
    lower_lip = create_sweep(
        "Face_LowerLip",
        [
            (-0.145, -0.435, 4.191, 0.012, 0.012),
            (-0.075, -0.452, 4.165, 0.021, 0.016),
            (0.0, -0.455, 4.160, 0.023, 0.017),
            (0.075, -0.452, 4.165, 0.021, 0.016),
            (0.145, -0.435, 4.191, 0.012, 0.012),
        ],
        skin,
        collection,
        radial_segments=12,
        steps_per_span=4,
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
