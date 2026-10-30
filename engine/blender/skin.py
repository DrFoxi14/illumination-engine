"""Unify the procedural anatomical forms into one continuous skin surface."""

from __future__ import annotations

import bpy


def unify_skin_surface(
    objects: list[bpy.types.Object],
    skin_material: bpy.types.Material,
    *,
    voxel_size: float = 0.012,
    smooth_iterations: int = 3,
) -> bpy.types.Object:
    """Apply source smoothing, join anatomical parts, and voxel-remesh the union.

    Voxel remeshing removes internal intersections between the torso, neck, head,
    arms, hands, and legs. The result is one manifold surface suitable for later
    retopology and rigging. Facial details, hair, and clothing remain separate.
    """

    mesh_objects = [obj for obj in objects if obj is not None and obj.type == "MESH"]
    if len(mesh_objects) < 2:
        raise ValueError("At least two anatomical mesh objects are required")
    if voxel_size <= 0.0:
        raise ValueError("voxel_size must be positive")

    if bpy.context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")

    for obj in mesh_objects:
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        for modifier in list(obj.modifiers):
            if modifier.type == "SUBSURF":
                bpy.ops.object.modifier_apply(modifier=modifier.name)

    bpy.ops.object.select_all(action="DESELECT")
    for obj in mesh_objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = mesh_objects[0]
    bpy.ops.object.join()

    skin = bpy.context.view_layer.objects.active
    if skin is None or skin.type != "MESH":
        raise RuntimeError("Could not join the anatomical source meshes")

    skin.name = "Character_Skin"
    skin.data.name = "Character_Skin_Mesh"
    skin.data.remesh_mode = "VOXEL"
    skin.data.remesh_voxel_size = voxel_size
    skin.data.remesh_voxel_adaptivity = 0.0

    bpy.ops.object.voxel_remesh()

    skin.data.materials.clear()
    skin.data.materials.append(skin_material)
    for polygon in skin.data.polygons:
        polygon.use_smooth = True

    if smooth_iterations:
        smooth = skin.modifiers.new(name="Skin_Surface_Soften", type="SMOOTH")
        smooth.factor = 0.35
        smooth.iterations = smooth_iterations

    return skin
