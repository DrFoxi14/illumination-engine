"""Reusable mesh-generation primitives for original procedural characters.

These helpers create actual quad-based meshes from parameterized surfaces. They do
not wrap Blender's primitive-sphere operators and do not depend on external assets.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

import bmesh
import bpy
from mathutils import Vector


Profile = tuple[float, float, float, float, float]
SweepPoint = tuple[float, float, float, float, float]


def srgb_hex_to_linear_rgba(value: str) -> tuple[float, float, float, float]:
    """Convert a six-digit sRGB hex color to linear RGBA for Blender shaders."""

    code = value.removeprefix("#")
    if len(code) != 6:
        raise ValueError(f"Expected six-digit hex color, got {value!r}")
    channels = [int(code[index : index + 2], 16) / 255.0 for index in (0, 2, 4)]
    linear = [
        channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4
        for channel in channels
    ]
    return (linear[0], linear[1], linear[2], 1.0)


def create_material(
    name: str,
    color: str,
    *,
    roughness: float = 0.58,
    metallic: float = 0.0,
    subsurface: float = 0.0,
    coat: float = 0.0,
) -> bpy.types.Material:
    """Create a Principled material from an sRGB hex color."""

    rgba = srgb_hex_to_linear_rgba(color)
    material = bpy.data.materials.new(name=name)
    material.diffuse_color = rgba
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    if shader is not None:
        shader.inputs["Base Color"].default_value = rgba
        shader.inputs["Roughness"].default_value = roughness
        shader.inputs["Metallic"].default_value = metallic
        if "Subsurface Weight" in shader.inputs:
            shader.inputs["Subsurface Weight"].default_value = subsurface
        if "Coat Weight" in shader.inputs:
            shader.inputs["Coat Weight"].default_value = coat
    return material


def _catmull_rom(
    p0: Sequence[float],
    p1: Sequence[float],
    p2: Sequence[float],
    p3: Sequence[float],
    t: float,
) -> tuple[float, ...]:
    """Interpolate a multi-dimensional control point with a Catmull-Rom spline."""

    t2 = t * t
    t3 = t2 * t
    return tuple(
        0.5
        * (
            2.0 * a
            + (-a0 + c) * t
            + (2.0 * a0 - 5.0 * a + 4.0 * c - d) * t2
            + (-a0 + 3.0 * a - 3.0 * c + d) * t3
        )
        for a0, a, c, d in zip(p0, p1, p2, p3, strict=True)
    )


def _sample_controls(
    controls: Sequence[Sequence[float]],
    steps_per_span: int,
) -> list[tuple[float, ...]]:
    if len(controls) < 2:
        raise ValueError("At least two control points are required")
    if steps_per_span < 1:
        raise ValueError("steps_per_span must be positive")

    samples: list[tuple[float, ...]] = []
    for index in range(len(controls) - 1):
        p0 = controls[max(index - 1, 0)]
        p1 = controls[index]
        p2 = controls[index + 1]
        p3 = controls[min(index + 2, len(controls) - 1)]
        for step in range(steps_per_span):
            samples.append(_catmull_rom(p0, p1, p2, p3, step / steps_per_span))
    samples.append(tuple(float(value) for value in controls[-1]))
    return samples


def _mesh_object(
    name: str,
    vertices: list[tuple[float, float, float]],
    faces: list[tuple[int, ...]],
    material: bpy.types.Material,
    collection: bpy.types.Collection,
    *,
    subdivision: int = 1,
) -> bpy.types.Object:
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()

    bm = bmesh.new()
    try:
        bm.from_mesh(mesh)
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        bm.to_mesh(mesh)
    finally:
        bm.free()
    mesh.update()

    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj.data.materials.append(material)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True

    if subdivision:
        modifier = obj.modifiers.new(name="Surface_Smoothing", type="SUBSURF")
        modifier.levels = subdivision
        modifier.render_levels = max(subdivision, 2)
    return obj


def create_loft(
    name: str,
    profile: Sequence[Profile],
    material: bpy.types.Material,
    collection: bpy.types.Collection,
    *,
    radial_segments: int = 48,
    steps_per_span: int = 5,
    subdivision: int = 2,
) -> bpy.types.Object:
    """Create a smooth closed horizontal loft.

    Each profile point is (z, center_x, center_y, radius_x, radius_y).
    """

    if len(profile) < 3:
        raise ValueError("A loft requires at least three profile rings")
    if radial_segments < 8:
        raise ValueError("radial_segments must be at least 8")

    samples = _sample_controls(profile, steps_per_span)
    vertices: list[tuple[float, float, float]] = []
    for z, center_x, center_y, radius_x, radius_y in samples:
        if radius_x <= 0.0 or radius_y <= 0.0:
            raise ValueError("Loft radii must be positive")
        for segment in range(radial_segments):
            angle = math.tau * segment / radial_segments
            vertices.append(
                (
                    center_x + math.cos(angle) * radius_x,
                    center_y + math.sin(angle) * radius_y,
                    z,
                )
            )

    faces: list[tuple[int, ...]] = []
    for ring in range(len(samples) - 1):
        current = ring * radial_segments
        following = (ring + 1) * radial_segments
        for segment in range(radial_segments):
            nxt = (segment + 1) % radial_segments
            faces.append(
                (
                    current + segment,
                    current + nxt,
                    following + nxt,
                    following + segment,
                )
            )

    bottom_center = len(vertices)
    top_center = bottom_center + 1
    vertices.append(tuple(samples[0][1:3]) + (samples[0][0],))
    vertices.append(tuple(samples[-1][1:3]) + (samples[-1][0],))
    for segment in range(radial_segments):
        nxt = (segment + 1) % radial_segments
        faces.append((bottom_center, nxt, segment))
        last = (len(samples) - 1) * radial_segments
        faces.append((top_center, last + segment, last + nxt))

    return _mesh_object(
        name,
        vertices,
        faces,
        material,
        collection,
        subdivision=subdivision,
    )


def create_sweep(
    name: str,
    controls: Sequence[SweepPoint],
    material: bpy.types.Material,
    collection: bpy.types.Collection,
    *,
    radial_segments: int = 20,
    steps_per_span: int = 6,
    subdivision: int = 1,
) -> bpy.types.Object:
    """Create an organic tapered tube through 3D control points.

    Each control point is (x, y, z, radius_u, radius_v). A moving local frame
    keeps the cross-sections oriented along the curve.
    """

    if len(controls) < 2:
        raise ValueError("A sweep requires at least two control points")
    samples = _sample_controls(controls, steps_per_span)
    centers = [Vector(sample[:3]) for sample in samples]
    vertices: list[tuple[float, float, float]] = []

    for index, (sample, center) in enumerate(zip(samples, centers, strict=True)):
        previous = centers[max(index - 1, 0)]
        following = centers[min(index + 1, len(centers) - 1)]
        tangent = (following - previous).normalized()
        if tangent.length < 1e-8:
            tangent = Vector((0.0, 0.0, 1.0))

        reference = Vector((0.0, 1.0, 0.0))
        if abs(tangent.dot(reference)) > 0.92:
            reference = Vector((1.0, 0.0, 0.0))
        axis_u = tangent.cross(reference).normalized()
        axis_v = tangent.cross(axis_u).normalized()
        radius_u = max(sample[3], 0.001)
        radius_v = max(sample[4], 0.001)

        for segment in range(radial_segments):
            angle = math.tau * segment / radial_segments
            point = (
                center
                + axis_u * (math.cos(angle) * radius_u)
                + axis_v * (math.sin(angle) * radius_v)
            )
            vertices.append(tuple(point))

    faces: list[tuple[int, ...]] = []
    for ring in range(len(samples) - 1):
        current = ring * radial_segments
        following = (ring + 1) * radial_segments
        for segment in range(radial_segments):
            nxt = (segment + 1) % radial_segments
            faces.append(
                (
                    current + segment,
                    current + nxt,
                    following + nxt,
                    following + segment,
                )
            )

    start_cap = len(vertices)
    end_cap = start_cap + 1
    vertices.append(tuple(centers[0]))
    vertices.append(tuple(centers[-1]))
    last = (len(samples) - 1) * radial_segments
    for segment in range(radial_segments):
        nxt = (segment + 1) % radial_segments
        faces.append((start_cap, segment, nxt))
        faces.append((end_cap, last + nxt, last + segment))

    return _mesh_object(
        name,
        vertices,
        faces,
        material,
        collection,
        subdivision=subdivision,
    )


def create_ellipsoid(
    name: str,
    location: tuple[float, float, float],
    scale: tuple[float, float, float],
    material: bpy.types.Material,
    collection: bpy.types.Collection,
    *,
    segments: int = 32,
    rings: int = 20,
    subdivision: int = 1,
) -> bpy.types.Object:
    """Create a smooth UV ellipsoid mesh without Blender primitive operators."""

    if min(scale) <= 0.0:
        raise ValueError("Ellipsoid scale values must be positive")
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, ...]] = []
    cx, cy, cz = location
    sx, sy, sz = scale

    for ring in range(rings + 1):
        latitude = -math.pi / 2.0 + math.pi * ring / rings
        z = math.sin(latitude)
        radial = math.cos(latitude)
        for segment in range(segments):
            longitude = math.tau * segment / segments
            vertices.append(
                (
                    cx + sx * radial * math.cos(longitude),
                    cy + sy * radial * math.sin(longitude),
                    cz + sz * z,
                )
            )

    for ring in range(rings):
        current = ring * segments
        following = (ring + 1) * segments
        for segment in range(segments):
            nxt = (segment + 1) % segments
            faces.append(
                (
                    current + segment,
                    current + nxt,
                    following + nxt,
                    following + segment,
                )
            )

    return _mesh_object(
        name,
        vertices,
        faces,
        material,
        collection,
        subdivision=subdivision,
    )
