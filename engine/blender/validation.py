"""Structural validation for a generated Prototype 001 Blender scene."""

from __future__ import annotations

import math
from typing import Any

import bmesh
import bpy


REQUIRED_OBJECTS = (
    "Character_Skin",
    "Face_Eyeball_L",
    "Face_Eyeball_R",
    "Face_UpperEyelid_L",
    "Face_UpperEyelid_R",
    "Hair_ScalpCap",
    "Hair_SweptFringe",
    "Outfit_NavyTop",
    "Outfit_ShortsBody",
    "Outfit_AnkleSock_L",
    "Outfit_AnkleSock_R",
    "Outfit_SlipperUpper_L",
    "Outfit_SlipperUpper_R",
    "Character_Review_Camera",
)


def _component_count(bm: bmesh.types.BMesh) -> int:
    visited: set[bmesh.types.BMFace] = set()
    components = 0

    for start in bm.faces:
        if start in visited:
            continue
        components += 1
        stack = [start]
        while stack:
            face = stack.pop()
            if face in visited:
                continue
            visited.add(face)
            for edge in face.edges:
                stack.extend(linked for linked in edge.link_faces if linked not in visited)

    return components


def _mesh_report(obj: bpy.types.Object) -> dict[str, Any]:
    mesh = obj.data
    if len(mesh.vertices) < 8 or len(mesh.polygons) < 6:
        raise RuntimeError(
            f"Mesh '{obj.name}' is unexpectedly small: "
            f"{len(mesh.vertices)} vertices, {len(mesh.polygons)} faces"
        )

    for vertex in mesh.vertices:
        if not all(math.isfinite(value) for value in vertex.co):
            raise RuntimeError(f"Mesh '{obj.name}' contains non-finite vertex coordinates")

    degenerate_faces = [polygon.index for polygon in mesh.polygons if polygon.area <= 1e-12]
    if degenerate_faces:
        raise RuntimeError(
            f"Mesh '{obj.name}' contains {len(degenerate_faces)} zero-area faces"
        )

    bm = bmesh.new()
    try:
        bm.from_mesh(mesh)
        boundary_edges = sum(edge.is_boundary for edge in bm.edges)
        non_manifold_edges = sum(not edge.is_manifold for edge in bm.edges)
        loose_vertices = sum(not vertex.link_edges for vertex in bm.verts)
        loose_edges = sum(not edge.link_faces for edge in bm.edges)
        connected_components = _component_count(bm)
    finally:
        bm.free()

    if boundary_edges or non_manifold_edges or loose_vertices or loose_edges:
        raise RuntimeError(
            f"Mesh '{obj.name}' is not a closed manifold: "
            f"boundary={boundary_edges}, non_manifold={non_manifold_edges}, "
            f"loose_vertices={loose_vertices}, loose_edges={loose_edges}"
        )

    return {
        "name": obj.name,
        "vertices": len(mesh.vertices),
        "faces": len(mesh.polygons),
        "edges": len(mesh.edges),
        "boundary_edges": boundary_edges,
        "non_manifold_edges": non_manifold_edges,
        "loose_vertices": loose_vertices,
        "loose_edges": loose_edges,
        "connected_components": connected_components,
        "materials": len(mesh.materials),
        "modifiers": [modifier.type for modifier in obj.modifiers],
    }


def validate_character_scene() -> dict[str, Any]:
    """Fail fast when required character parts or closed mesh invariants are missing."""

    missing = [name for name in REQUIRED_OBJECTS if bpy.data.objects.get(name) is None]
    if missing:
        raise RuntimeError(f"Generated character is missing required objects: {', '.join(missing)}")

    meshes = [
        obj
        for obj in bpy.context.scene.objects
        if obj.type == "MESH" and obj.name != "Studio_Floor"
    ]
    if len(meshes) < 20:
        raise RuntimeError(
            f"Expected at least 20 character mesh objects, found {len(meshes)}"
        )

    mesh_reports = [_mesh_report(obj) for obj in meshes]
    total_vertices = sum(report["vertices"] for report in mesh_reports)
    total_faces = sum(report["faces"] for report in mesh_reports)

    if total_vertices < 10_000 or total_faces < 8_000:
        raise RuntimeError(
            "Generated character is below the expected geometry budget: "
            f"{total_vertices} vertices, {total_faces} faces"
        )

    skin_report = next(report for report in mesh_reports if report["name"] == "Character_Skin")
    if skin_report["connected_components"] != 1:
        raise RuntimeError(
            "Unified skin surface must be one connected component, found "
            f"{skin_report['connected_components']}"
        )

    return {
        "status": "passed",
        "required_objects": list(REQUIRED_OBJECTS),
        "mesh_object_count": len(mesh_reports),
        "total_vertices": total_vertices,
        "total_faces": total_faces,
        "closed_manifold_mesh_count": len(mesh_reports),
        "meshes": mesh_reports,
    }
