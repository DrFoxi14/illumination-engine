"""Construct fitted clothing with clean hems and visible garment finish details."""

from __future__ import annotations

import bpy

from engine.blender.geometry import create_ellipsoid, create_loft, create_sweep


def _front_seam(
    name: str,
    points: list[tuple[float, float, float]],
    material: bpy.types.Material,
    collection: bpy.types.Collection,
    *,
    radius: float = 0.010,
) -> bpy.types.Object:
    controls = [(x, y, z, radius, radius * 0.82) for x, y, z in points]
    return create_sweep(
        name,
        controls,
        material,
        collection,
        radial_segments=12,
        steps_per_span=5,
        subdivision=1,
    )


def build_outfit(
    collection: bpy.types.Collection,
    *,
    top: bpy.types.Material,
    top_detail: bpy.types.Material,
    shorts: bpy.types.Material,
    shorts_detail: bpy.types.Material,
    socks: bpy.types.Material,
    slippers: bpy.types.Material,
    sole: bpy.types.Material,
    pose: str = "neutral_standing",
) -> list[bpy.types.Object]:
    """Build the navy top, grey shorts, socks, slippers, and understated seams."""

    if pose not in {"neutral_standing", "mirror_selfie"}:
        raise ValueError(f"Unsupported outfit presentation pose: {pose}")

    objects: list[bpy.types.Object] = []

    top_obj = create_loft(
        "Outfit_NavyTop",
        [
            (3.04, 0.0, 0.0, 0.370, 0.242),
            (3.10, 0.0, 0.0, 0.392, 0.252),
            (3.27, 0.0, 0.0, 0.445, 0.278),
            (3.47, 0.0, 0.0, 0.490, 0.292),
            (3.63, 0.0, 0.0, 0.468, 0.276),
            (3.77, 0.0, 0.0, 0.355, 0.228),
        ],
        top,
        collection,
        radial_segments=72,
        steps_per_span=7,
        subdivision=2,
    )
    objects.append(top_obj)

    waistband = create_loft(
        "Outfit_ShortsWaistband",
        [
            (2.43, 0.0, 0.0, 0.375, 0.245),
            (2.49, 0.0, 0.0, 0.392, 0.257),
            (2.55, 0.0, 0.0, 0.385, 0.250),
        ],
        shorts,
        collection,
        radial_segments=64,
        steps_per_span=5,
        subdivision=2,
    )
    objects.append(waistband)

    shorts_body = create_loft(
        "Outfit_ShortsBody",
        [
            (2.02, 0.0, 0.0, 0.345, 0.235),
            (2.10, 0.0, 0.0, 0.382, 0.250),
            (2.28, 0.0, 0.0, 0.405, 0.265),
            (2.46, 0.0, 0.0, 0.388, 0.255),
        ],
        shorts,
        collection,
        radial_segments=64,
        steps_per_span=6,
        subdivision=2,
    )
    objects.append(shorts_body)

    # A shallow front collar, lower hem, waistband seam, and fly line break up
    # the large uninterrupted fabric surfaces without adding noisy micro-detail.
    objects.append(
        _front_seam(
            "Outfit_TopNeckBinding",
            [
                (-0.265, -0.180, 3.748),
                (-0.185, -0.218, 3.772),
                (-0.095, -0.232, 3.780),
                (0.0, -0.236, 3.782),
                (0.095, -0.232, 3.780),
                (0.185, -0.218, 3.772),
                (0.265, -0.180, 3.748),
            ],
            top_detail,
            collection,
            radius=0.012,
        )
    )
    objects.append(
        _front_seam(
            "Outfit_TopBottomHem",
            [
                (-0.345, -0.195, 3.095),
                (-0.220, -0.232, 3.080),
                (0.0, -0.245, 3.075),
                (0.220, -0.232, 3.080),
                (0.345, -0.195, 3.095),
            ],
            top_detail,
            collection,
            radius=0.009,
        )
    )
    objects.append(
        _front_seam(
            "Outfit_ShortsWaistSeam",
            [
                (-0.315, -0.185, 2.485),
                (-0.180, -0.230, 2.472),
                (0.0, -0.250, 2.470),
                (0.180, -0.230, 2.472),
                (0.315, -0.185, 2.485),
            ],
            shorts_detail,
            collection,
            radius=0.008,
        )
    )
    objects.append(
        _front_seam(
            "Outfit_ShortsFlySeam",
            [
                (0.0, -0.251, 2.435),
                (0.0, -0.259, 2.335),
                (0.0, -0.257, 2.225),
            ],
            shorts_detail,
            collection,
            radius=0.007,
        )
    )

    for side, label in ((-1.0, "L"), (1.0, "R")):
        sleeve = create_sweep(
            f"Outfit_TopSleeve_{label}",
            [
                (side * 0.37, 0.0, 3.63, 0.185, 0.180),
                (side * 0.50, -0.004, 3.54, 0.162, 0.158),
                (side * 0.59, -0.010, 3.36, 0.132, 0.132),
                (side * 0.60, -0.012, 3.29, 0.126, 0.126),
            ],
            top,
            collection,
            radial_segments=32,
            steps_per_span=6,
            subdivision=2,
        )
        objects.append(sleeve)
        cuff = _front_seam(
            f"Outfit_SleeveCuff_{label}",
            [
                (side * 0.505, -0.118, 3.355),
                (side * 0.555, -0.130, 3.325),
                (side * 0.605, -0.115, 3.315),
            ],
            top_detail,
            collection,
            radius=0.008,
        )
        objects.append(cuff)

        short_leg = create_sweep(
            f"Outfit_ShortsLeg_{label}",
            [
                (side * 0.19, 0.0, 2.23, 0.205, 0.200),
                (side * 0.20, 0.0, 2.08, 0.194, 0.185),
                (side * 0.205, 0.0, 1.91, 0.155, 0.150),
            ],
            shorts,
            collection,
            radial_segments=32,
            steps_per_span=6,
            subdivision=2,
        )
        objects.append(short_leg)
        hem = _front_seam(
            f"Outfit_ShortsLegHem_{label}",
            [
                (side * 0.055, -0.176, 1.942),
                (side * 0.180, -0.190, 1.925),
                (side * 0.300, -0.155, 1.952),
            ],
            shorts_detail,
            collection,
            radius=0.008,
        )
        objects.append(hem)

        is_lifted_leg = pose == "mirror_selfie" and side > 0
        if is_lifted_leg:
            sock_controls = [
                (-0.045, -0.205, 1.255, 0.122, 0.126),
                (-0.045, -0.205, 1.155, 0.122, 0.125),
                (-0.045, -0.205, 1.045, 0.112, 0.115),
            ]
            slipper_x, slipper_y, slipper_z = -0.085, -0.385, 0.995
        else:
            sock_controls = [
                (side * 0.205, -0.005, 0.43, 0.122, 0.126),
                (side * 0.205, -0.005, 0.30, 0.122, 0.125),
                (side * 0.205, -0.005, 0.16, 0.112, 0.115),
            ]
            slipper_x, slipper_y, slipper_z = side * 0.205, -0.105, 0.095

        sock = create_sweep(
            f"Outfit_AnkleSock_{label}",
            sock_controls,
            socks,
            collection,
            radial_segments=28,
            steps_per_span=5,
            subdivision=1,
        )
        objects.append(sock)

        sole_obj = create_ellipsoid(
            f"Outfit_SlipperSole_{label}",
            (slipper_x, slipper_y, slipper_z - 0.080),
            (0.155, 0.315, 0.050),
            sole,
            collection,
            segments=36,
            rings=22,
            subdivision=1,
        )
        upper_obj = create_ellipsoid(
            f"Outfit_SlipperUpper_{label}",
            (slipper_x, slipper_y + 0.010, slipper_z),
            (0.145, 0.270, 0.105),
            slippers,
            collection,
            segments=36,
            rings=22,
            subdivision=2,
        )
        objects.extend((sole_obj, upper_obj))

    return objects
