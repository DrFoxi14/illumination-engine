"""Simple, editable stylized long-hair blockout for Prototype 001.

The curves are large graphic locks rather than simulated individual strands.
They provide a controllable silhouette until a dedicated groom asset is selected.
"""

from __future__ import annotations

import bpy
from mathutils import Vector


def _hex_rgba(value: str) -> tuple[float, float, float, float]:
    code = value.lstrip("#")
    channels = [int(code[index : index + 2], 16) / 255.0 for index in (0, 2, 4)]
    linear = [
        channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4
        for channel in channels
    ]
    return (linear[0], linear[1], linear[2], 1.0)


def _hair_material(name: str, color: str) -> bpy.types.Material:
    rgba = _hex_rgba(color)
    material = bpy.data.materials.new(name=name)
    material.diffuse_color = rgba
    material.use_nodes = True
    principled = material.node_tree.nodes.get("Principled BSDF")
    if principled is not None:
        principled.inputs["Base Color"].default_value = rgba
        principled.inputs["Roughness"].default_value = 0.46
    return material


def _add_curve_lock(
    name: str,
    points: list[Vector],
    material: bpy.types.Material,
    collection: bpy.types.Collection,
    bevel_depth: float,
) -> bpy.types.Object:
    curve = bpy.data.curves.new(name=f"{name}_Curve", type="CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 16
    curve.bevel_depth = bevel_depth
    curve.bevel_resolution = 5
    curve.fill_mode = "FULL"
    spline = curve.splines.new("BEZIER")
    spline.bezier_points.add(len(points) - 1)
    for bezier_point, coordinate in zip(spline.bezier_points, points, strict=True):
        bezier_point.co = coordinate
        bezier_point.handle_left_type = "AUTO"
        bezier_point.handle_right_type = "AUTO"
    obj = bpy.data.objects.new(name, curve)
    collection.objects.link(obj)
    obj.data.materials.append(material)
    return obj


def build_long_hair_blockout(
    body_obj: bpy.types.Object,
    *,
    armature: bpy.types.Object | None,
    base_color: str,
    highlight_color: str,
    collection: bpy.types.Collection,
    part: str = "left",
) -> list[bpy.types.Object]:
    """Add a large-lock hairstyle positioned from the imported head bounds."""

    coords = [vertex.co for vertex in body_obj.data.vertices]
    if not coords:
        raise ValueError("Cannot place hair on an empty body mesh")
    min_z = min(point.z for point in coords)
    max_z = max(point.z for point in coords)
    height = max_z - min_z
    if height <= 1e-6:
        raise ValueError("Body mesh has invalid height")

    head_points = [point for point in coords if point.z >= min_z + height * 0.76]
    if not head_points:
        raise ValueError("Could not estimate head bounds from the base mesh")

    min_x = min(point.x for point in head_points)
    max_x = max(point.x for point in head_points)
    min_y = min(point.y for point in head_points)
    max_y = max(point.y for point in head_points)
    head_min_z = min(point.z for point in head_points)
    head_max_z = max(point.z for point in head_points)
    head_width = max_x - min_x
    head_depth = max_y - min_y
    head_height = max(head_max_z - head_min_z, height * 0.08)
    center_x = (min_x + max_x) / 2.0
    center_y = (min_y + max_y) / 2.0 + head_depth * 0.20
    local_to_world = body_obj.matrix_world

    base_mat = _hair_material("Hair_Warm_Base", base_color)
    highlight_mat = _hair_material("Hair_Warm_Highlight", highlight_color)
    objects: list[bpy.types.Object] = []

    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=48,
        ring_count=32,
        location=local_to_world @ Vector((center_x, center_y, head_max_z - head_height * 0.27)),
    )
    cap = bpy.context.object
    cap.name = "Hair_Cap_Blockout"
    cap.scale = (head_width * 0.57, head_depth * 0.62, head_height * 0.61)
    bpy.ops.object.shade_smooth()
    if cap.users_collection:
        for current in tuple(cap.users_collection):
            current.objects.unlink(cap)
    collection.objects.link(cap)
    cap.data.materials.append(base_mat)
    objects.append(cap)

    sign = -1.0 if part == "left" else 1.0
    if part == "center":
        sign = 0.0
    lock_radius = max(head_width * 0.045, height * 0.008)
    lower_z = head_min_z - height * 0.16

    for side in (-1.0, 1.0):
        for index in range(5):
            fraction = index / 4.0
            x_root = center_x + side * head_width * (0.34 + fraction * 0.10)
            x_mid = center_x + side * head_width * (0.43 + fraction * 0.11)
            x_end = center_x + side * head_width * (0.46 + fraction * 0.12)
            y_root = min_y - head_depth * 0.04
            y_mid = center_y + head_depth * 0.12
            y_end = center_y + head_depth * (0.18 + fraction * 0.08)
            if index == 0:
                x_root += sign * head_width * 0.05

            points = [
                local_to_world @ Vector((x_root, y_root, head_max_z - head_height * 0.08)),
                local_to_world @ Vector((x_mid, center_y, head_max_z - head_height * 0.38)),
                local_to_world @ Vector((x_mid, y_mid, head_min_z - height * 0.01)),
                local_to_world @ Vector((x_end, y_end, lower_z + height * fraction * 0.025)),
            ]
            material = highlight_mat if index in (1, 4) else base_mat
            lock = _add_curve_lock(
                f"Hair_Side_{'L' if side < 0 else 'R'}_{index + 1}",
                points,
                material,
                collection,
                lock_radius * (1.0 - fraction * 0.18),
            )
            objects.append(lock)

    for index in range(7):
        fraction = (index / 6.0) - 0.5
        x_root = center_x + fraction * head_width * 0.68
        x_end = center_x + fraction * head_width * 0.92
        points = [
            local_to_world @ Vector((x_root, center_y + head_depth * 0.28, head_max_z)),
            local_to_world @ Vector((x_root, center_y + head_depth * 0.36, head_max_z - head_height * 0.42)),
            local_to_world @ Vector((x_end, center_y + head_depth * 0.38, head_min_z - height * 0.02)),
            local_to_world @ Vector((x_end, center_y + head_depth * 0.34, lower_z)),
        ]
        material = highlight_mat if index in (2, 5) else base_mat
        lock = _add_curve_lock(
            f"Hair_Back_{index + 1}",
            points,
            material,
            collection,
            lock_radius * 0.85,
        )
        objects.append(lock)

    if armature is not None:
        head_bone = next(
            (
                bone.name
                for bone in armature.data.bones
                if bone.name.lower() in {"head", "head_end", "head_ctrl"}
                or "head" in bone.name.lower()
            ),
            None,
        )
        if head_bone:
            for obj in objects:
                world_matrix = obj.matrix_world.copy()
                obj.parent = armature
                obj.parent_type = "BONE"
                obj.parent_bone = head_bone
                obj.matrix_world = world_matrix

    return objects
