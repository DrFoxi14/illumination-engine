"""Create fitted clothing shells from a rigged body's own topology.

This keeps clothing aligned to the source surface and inherits its vertex groups.
It is intended for fitted garments such as a T-shirt and shorts, not loose cloth.
"""

from __future__ import annotations

from collections.abc import Callable

import bmesh
import bpy
from mathutils import Vector

RegionPredicate = Callable[[float, float, float], bool]


def _mesh_bounds(mesh: bpy.types.Mesh) -> tuple[Vector, Vector]:
    if not mesh.vertices:
        raise ValueError("Cannot create clothing from an empty body mesh")
    coords = [vertex.co for vertex in mesh.vertices]
    minimum = Vector(
        (min(point.x for point in coords), min(point.y for point in coords), min(point.z for point in coords))
    )
    maximum = Vector(
        (max(point.x for point in coords), max(point.y for point in coords), max(point.z for point in coords))
    )
    if (maximum - minimum).length < 1e-6:
        raise ValueError("Body mesh has invalid bounds")
    return minimum, maximum


def _normalize_point(
    point: Vector,
    minimum: Vector,
    maximum: Vector,
) -> tuple[float, float, float]:
    size = maximum - minimum
    return (
        ((point.x - minimum.x) / size.x) * 2.0 - 1.0 if size.x else 0.0,
        ((point.y - minimum.y) / size.y) * 2.0 - 1.0 if size.y else 0.0,
        (point.z - minimum.z) / size.z if size.z else 0.0,
    )


def _make_material(
    name: str,
    rgba: tuple[float, float, float, float],
    roughness: float,
) -> bpy.types.Material:
    material = bpy.data.materials.new(name=name)
    material.diffuse_color = rgba
    material.use_nodes = True
    principled = material.node_tree.nodes.get("Principled BSDF")
    if principled is not None:
        principled.inputs["Base Color"].default_value = rgba
        principled.inputs["Roughness"].default_value = roughness
    return material


def _connected_face_islands(bm: bmesh.types.BMesh) -> list[list[bmesh.types.BMFace]]:
    visited: set[bmesh.types.BMFace] = set()
    islands: list[list[bmesh.types.BMFace]] = []

    for start in bm.faces:
        if start in visited:
            continue
        island: list[bmesh.types.BMFace] = []
        queue = [start]
        while queue:
            face = queue.pop()
            if face in visited:
                continue
            visited.add(face)
            island.append(face)
            for edge in face.edges:
                queue.extend(
                    linked
                    for linked in edge.link_faces
                    if linked not in visited
                )
        islands.append(island)

    return islands


def build_bodytopo_garment(
    body_obj: bpy.types.Object,
    *,
    name: str,
    keep_region: RegionPredicate,
    rgba: tuple[float, float, float, float],
    roughness: float = 0.72,
    push_distance: float = 0.006,
    solidify_thickness: float = 0.004,
    smooth_passes: int = 4,
    min_island_faces: int = 12,
) -> dict[str, object]:
    """Duplicate and trim body topology to create a fitted garment shell."""

    if body_obj.type != "MESH":
        raise TypeError("body_obj must be a mesh object")
    if bpy.context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")

    garment = body_obj.copy()
    garment.data = body_obj.data.copy()
    garment.name = name
    garment.data.name = f"{name}_Mesh"
    linked_collections = tuple(body_obj.users_collection)
    if linked_collections:
        for collection in linked_collections:
            collection.objects.link(garment)
    else:
        bpy.context.scene.collection.objects.link(garment)

    minimum, maximum = _mesh_bounds(garment.data)
    bm = bmesh.new()
    try:
        bm.from_mesh(garment.data)
        bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=0.0001)
        bm.normal_update()

        faces_to_remove = []
        for face in bm.faces:
            center = face.calc_center_median()
            if not keep_region(*_normalize_point(center, minimum, maximum)):
                faces_to_remove.append(face)
        if faces_to_remove:
            bmesh.ops.delete(bm, geom=faces_to_remove, context="FACES")

        loose_edges = [edge for edge in bm.edges if not edge.link_faces]
        if loose_edges:
            bmesh.ops.delete(bm, geom=loose_edges, context="EDGES")
        loose_verts = [vert for vert in bm.verts if not vert.link_edges]
        if loose_verts:
            bmesh.ops.delete(bm, geom=loose_verts, context="VERTS")
        if not bm.faces:
            raise RuntimeError(
                f"Clothing selector for '{name}' removed every face; check its normalized region."
            )

        bm.normal_update()
        for vertex in bm.verts:
            if vertex.normal.length > 1e-8:
                vertex.co += vertex.normal.normalized() * push_distance

        boundary = {
            vertex
            for edge in bm.edges
            if edge.is_boundary
            for vertex in edge.verts
        }
        for _ in range(smooth_passes):
            new_positions: dict[bmesh.types.BMVert, Vector] = {}
            for vertex in boundary:
                neighbors = [
                    edge.other_vert(vertex).co.copy()
                    for edge in vertex.link_edges
                    if edge.is_boundary and edge.other_vert(vertex) in boundary
                ]
                if neighbors:
                    average = sum(neighbors, Vector()) / len(neighbors)
                    new_positions[vertex] = vertex.co.lerp(average, 0.32)
            for vertex, position in new_positions.items():
                vertex.co = position

        islands = _connected_face_islands(bm)
        small_islands = [
            face
            for island in islands
            if len(island) < min_island_faces
            for face in island
        ]
        if small_islands:
            bmesh.ops.delete(bm, geom=small_islands, context="FACES")

        loose_edges = [edge for edge in bm.edges if not edge.link_faces]
        if loose_edges:
            bmesh.ops.delete(bm, geom=loose_edges, context="EDGES")
        loose_verts = [vert for vert in bm.verts if not vert.link_edges]
        if loose_verts:
            bmesh.ops.delete(bm, geom=loose_verts, context="VERTS")

        bm.normal_update()
        boundary_after_cleanup = {
            vertex
            for edge in bm.edges
            if edge.is_boundary
            for vertex in edge.verts
        }
        for vertex in boundary_after_cleanup:
            if vertex.normal.length > 1e-8:
                vertex.co += vertex.normal.normalized() * 0.002

        bm.to_mesh(garment.data)
        garment.data.update()
        final_islands = _connected_face_islands(bm)
    finally:
        bm.free()

    garment.data.materials.clear()
    garment.data.materials.append(_make_material(f"{name}_Material", rgba, roughness))
    for polygon in garment.data.polygons:
        polygon.material_index = 0

    solidify = garment.modifiers.new(name="Fabric_Thickness", type="SOLIDIFY")
    solidify.thickness = solidify_thickness
    solidify.offset = 0.0
    solidify.use_rim = True

    return {
        "object": garment,
        "vertices": len(garment.data.vertices),
        "polygons": len(garment.data.polygons),
        "island_count": len(final_islands),
        "removed_small_island_faces": len(small_islands),
        "inherited_vertex_groups": len(garment.vertex_groups),
    }
