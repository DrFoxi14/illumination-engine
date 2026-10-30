"""Construct fitted clothing, socks, and soft house slippers from custom surfaces."""

from __future__ import annotations

import bpy

from engine.blender.geometry import create_ellipsoid, create_loft, create_sweep


def build_outfit(
    collection: bpy.types.Collection,
    *,
    top: bpy.types.Material,
    shorts: bpy.types.Material,
    socks: bpy.types.Material,
    slippers: bpy.types.Material,
    sole: bpy.types.Material,
) -> list[bpy.types.Object]:
    """Build the initial navy cropped top, grey shorts, socks, and slippers."""

    objects: list[bpy.types.Object] = []

    top_obj = create_loft(
        "Outfit_NavyTop",
        [
            (3.04, 0.0, 0.0, 0.345, 0.225),
            (3.10, 0.0, 0.0, 0.365, 0.238),
            (3.27, 0.0, 0.0, 0.375, 0.236),
            (3.47, 0.0, 0.0, 0.455, 0.272),
            (3.63, 0.0, 0.0, 0.454, 0.265),
            (3.77, 0.0, 0.0, 0.345, 0.210),
        ],
        top,
        collection,
        radial_segments=64,
        steps_per_span=6,
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
        radial_segments=56,
        steps_per_span=4,
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
        radial_segments=56,
        steps_per_span=5,
        subdivision=2,
    )
    objects.append(shorts_body)

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
            radial_segments=28,
            steps_per_span=5,
            subdivision=2,
        )
        objects.append(sleeve)

        short_leg = create_sweep(
            f"Outfit_ShortsLeg_{label}",
            [
                (side * 0.19, 0.0, 2.23, 0.205, 0.200),
                (side * 0.20, 0.0, 2.08, 0.194, 0.185),
                (side * 0.205, 0.0, 1.91, 0.155, 0.150),
            ],
            shorts,
            collection,
            radial_segments=28,
            steps_per_span=5,
            subdivision=2,
        )
        objects.append(short_leg)

        sock = create_sweep(
            f"Outfit_AnkleSock_{label}",
            [
                (side * 0.205, -0.005, 0.43, 0.122, 0.126),
                (side * 0.205, -0.005, 0.30, 0.122, 0.125),
                (side * 0.205, -0.005, 0.16, 0.112, 0.115),
            ],
            socks,
            collection,
            radial_segments=24,
            steps_per_span=4,
            subdivision=1,
        )
        objects.append(sock)

        sole_obj = create_ellipsoid(
            f"Outfit_SlipperSole_{label}",
            (side * 0.205, -0.105, 0.095),
            (0.155, 0.315, 0.050),
            sole,
            collection,
            segments=32,
            rings=20,
            subdivision=1,
        )
        upper_obj = create_ellipsoid(
            f"Outfit_SlipperUpper_{label}",
            (side * 0.205, -0.095, 0.175),
            (0.145, 0.270, 0.105),
            slippers,
            collection,
            segments=32,
            rings=20,
            subdivision=2,
        )
        objects.extend((sole_obj, upper_obj))

    return objects
