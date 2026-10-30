"""Generate simple, soft house-slipper blockout meshes around the imported feet."""

from __future__ import annotations

import bpy
from mathutils import Vector


def _material(name: str, hex_color: str, roughness: float) -> bpy.types.Material:
    code = hex_color.lstrip("#")
    srgb = [int(code[index : index + 2], 16) / 255.0 for index in (0, 2, 4)]
    linear = [
        channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4
        for channel in srgb
    ]
    rgba = (linear[0], linear[1], linear[2], 1.0)
    material = bpy.data.materials.new(name=name)
    material.diffuse_color = rgba
    material.use_nodes = True
    principled = material.node_tree.nodes.get("Principled BSDF")
    if principled is not None:
        principled.inputs["Base Color"].default_value = rgba
        principled.inputs["Roughness"].default_value = roughness
    return material


def _ellipsoid(
    name: str,
    center_local: Vector,
    scale_local: tuple[float, float, float],
    body_obj: bpy.types.Object,
    material: bpy.types.Material,
    collection: bpy.types.Collection,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=32,
        ring_count=20,
        location=body_obj.matrix_world @ center_local,
    )
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale_local
    bpy.ops.object.shade_smooth()
    for current in tuple(obj.users_collection):
        current.objects.unlink(obj)
    collection.objects.link(obj)
    obj.data.materials.append(material)
    return obj


def _parent_to_foot_bone(
    obj: bpy.types.Object,
    armature: bpy.types.Object | None,
    side: str,
) -> None:
    if armature is None:
        return

    tokens = (".l", "_l", "left") if side == "L" else (".r", "_r", "right")
    candidates = [
        bone.name
        for bone in armature.data.bones
        if "foot" in bone.name.lower() and any(token in bone.name.lower() for token in tokens)
    ]
    if not candidates:
        return

    world_matrix = obj.matrix_world.copy()
    obj.parent = armature
    obj.parent_type = "BONE"
    obj.parent_bone = candidates[0]
    obj.matrix_world = world_matrix


def build_slippers(
    body_obj: bpy.types.Object,
    *,
    armature: bpy.types.Object | None,
    slipper_color: str,
    sole_color: str,
    collection: bpy.types.Collection,
) -> list[bpy.types.Object]:
    """Create a pair of simple rounded slippers from the imported foot bounds."""

    vertices = [vertex.co for vertex in body_obj.data.vertices]
    if not vertices:
        return []

    min_z = min(point.z for point in vertices)
    max_z = max(point.z for point in vertices)
    height = max(max_z - min_z, 1.0)
    min_x = min(point.x for point in vertices)
    max_x = max(point.x for point in vertices)
    mid_x = (min_x + max_x) / 2.0
    foot_layer = [
        point
        for point in vertices
        if point.z <= min_z + height * 0.095
    ]

    upper_material = _material("Slipper_Soft_Upper", slipper_color, 0.88)
    sole_material = _material("Slipper_Sole_Matte", sole_color, 0.94)
    created: list[bpy.types.Object] = []

    for side, selected in (
        ("L", [point for point in foot_layer if point.x <= mid_x]),
        ("R", [point for point in foot_layer if point.x > mid_x]),
    ):
        if len(selected) < 8:
            continue

        foot_min_x = min(point.x for point in selected)
        foot_max_x = max(point.x for point in selected)
        foot_min_y = min(point.y for point in selected)
        foot_max_y = max(point.y for point in selected)
        foot_width = foot_max_x - foot_min_x
        foot_depth = foot_max_y - foot_min_y
        if foot_width < 1e-4 or foot_depth < 1e-4:
            continue

        center_x = (foot_min_x + foot_max_x) / 2.0
        center_y = (foot_min_y + foot_max_y) / 2.0
        sole_z = min_z + height * 0.010
        upper_z = min_z + height * 0.052

        sole = _ellipsoid(
            f"Slipper_{side}_Sole",
            Vector((center_x, center_y, sole_z)),
            (foot_width * 0.76, foot_depth * 0.70, height * 0.013),
            body_obj,
            sole_material,
            collection,
        )
        upper = _ellipsoid(
            f"Slipper_{side}_Upper",
            Vector((center_x, center_y + foot_depth * 0.055, upper_z)),
            (foot_width * 0.67, foot_depth * 0.48, height * 0.045),
            body_obj,
            upper_material,
            collection,
        )
        for obj in (sole, upper):
            _parent_to_foot_bone(obj, armature, side)
            created.append(obj)

    return created
