"""Build Prototype 001 from an external rigged humanoid base mesh.

The source mesh is intentionally external: download the Quaternius Standard CC0
pack yourself and pass the female base mesh path. This keeps third-party binary
assets out of the public Git repository.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import bpy
from mathutils import Vector

from engine.blender.base_mesh import import_humanoid_base
from engine.blender.body_topology import build_bodytopo_garment
from engine.blender.grooming import build_long_hair_blockout
from engine.blender.footwear import build_slippers
from engine.core.config import CharacterConfig
from engine.core.garment_rules import keep_crop_top, keep_shorts, keep_socks


def _linear_rgba(hex_color: str) -> tuple[float, float, float, float]:
    value = hex_color.lstrip("#")
    srgb = [int(value[index : index + 2], 16) / 255.0 for index in (0, 2, 4)]
    linear = [
        channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4
        for channel in srgb
    ]
    return (linear[0], linear[1], linear[2], 1.0)


def _material(
    name: str,
    hex_color: str,
    *,
    roughness: float = 0.68,
    subsurface: float = 0.0,
) -> bpy.types.Material:
    rgba = _linear_rgba(hex_color)
    material = bpy.data.materials.new(name=name)
    material.diffuse_color = rgba
    material.use_nodes = True
    principled = material.node_tree.nodes.get("Principled BSDF")
    if principled is not None:
        principled.inputs["Base Color"].default_value = rgba
        principled.inputs["Roughness"].default_value = roughness
        subsurface_socket = principled.inputs.get("Subsurface Weight")
        if subsurface_socket is not None:
            subsurface_socket.default_value = subsurface
    return material


def _replace_body_material(body: bpy.types.Object, config: CharacterConfig) -> None:
    skin = _material(
        "Skin_Stylized_Warm",
        config.face.skin_color,
        roughness=0.58,
        subsurface=0.035,
    )
    body.data.materials.clear()
    body.data.materials.append(skin)
    for polygon in body.data.polygons:
        polygon.material_index = 0


def _new_collection(name: str) -> bpy.types.Collection:
    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)
    return collection


def _move_to_collection(obj: bpy.types.Object, collection: bpy.types.Collection) -> None:
    for current in tuple(obj.users_collection):
        current.objects.unlink(obj)
    collection.objects.link(obj)


def _world_bounds(body: bpy.types.Object) -> tuple[Vector, Vector]:
    corners = [body.matrix_world @ Vector(corner) for corner in body.bound_box]
    minimum = Vector(
        (
            min(point.x for point in corners),
            min(point.y for point in corners),
            min(point.z for point in corners),
        )
    )
    maximum = Vector(
        (
            max(point.x for point in corners),
            max(point.y for point in corners),
            max(point.z for point in corners),
        )
    )
    return minimum, maximum


def _look_at(obj: bpy.types.Object, target: Vector) -> None:
    direction = target - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def _setup_studio(
    body: bpy.types.Object,
    collection: bpy.types.Collection,
    floor_color: str = "#D5D9DF",
) -> tuple[bpy.types.Object, Vector, float]:
    scene = bpy.context.scene
    minimum, maximum = _world_bounds(body)
    center = (minimum + maximum) * 0.5
    height = max(maximum.z - minimum.z, 1.0)

    floor_material = _material("Studio_Floor_Matte", floor_color, roughness=0.92)
    bpy.ops.mesh.primitive_plane_add(
        size=height * 8.0,
        location=(center.x, center.y, minimum.z - height * 0.008),
    )
    floor = bpy.context.object
    floor.name = "Studio_Floor"
    floor.data.materials.append(floor_material)
    _move_to_collection(floor, collection)

    bpy.ops.object.camera_add(
        location=(center.x + height * 1.45, center.y - height * 2.8, center.z + height * 0.30)
    )
    camera = bpy.context.object
    camera.name = "Review_Camera"
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = height * 1.48
    _look_at(camera, center)
    _move_to_collection(camera, collection)
    scene.camera = camera

    lights = [
        ("Key_Light", (-1.5, -2.0, 1.8), 330.0, 1.7),
        ("Fill_Light", (1.9, -1.4, 0.8), 190.0, 1.8),
        ("Rim_Light", (0.0, 1.5, 1.5), 420.0, 1.4),
    ]
    for name, offset, energy_factor, size_factor in lights:
        location = (
            center.x + offset[0] * height,
            center.y + offset[1] * height,
            center.z + offset[2] * height,
        )
        bpy.ops.object.light_add(type="AREA", location=location)
        light = bpy.context.object
        light.name = name
        light.data.energy = energy_factor * height * height
        light.data.shape = "DISK"
        light.data.size = size_factor * height
        _look_at(light, center)
        _move_to_collection(light, collection)

    if scene.world is None:
        scene.world = bpy.data.worlds.new("Illumination_Studio_World")
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    if background is not None:
        background.inputs["Color"].default_value = (0.72, 0.76, 0.84, 1.0)
        background.inputs["Strength"].default_value = 0.42

    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = 900
    scene.render.resolution_y = 1200
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.view_settings.view_transform = "AgX"
    scene.camera.data.lens = 50.0
    return camera, center, height


def _render_silhouettes(
    body: bpy.types.Object,
    camera: bpy.types.Object,
    center: Vector,
    height: float,
    output_dir: Path,
) -> list[str]:
    scene = bpy.context.scene
    original_engine = scene.render.engine
    original_resolution = (scene.render.resolution_x, scene.render.resolution_y)
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_x = 560
    scene.render.resolution_y = 800
    scene.render.resolution_percentage = 100

    shading = scene.display.shading
    original = {
        "light": shading.light,
        "color_type": shading.color_type,
        "single_color": tuple(shading.single_color),
        "background_type": shading.background_type,
        "show_shadows": shading.show_shadows,
    }
    shading.light = "FLAT"
    shading.color_type = "SINGLE"
    shading.single_color = (0.012, 0.012, 0.018)
    shading.background_type = "WORLD"
    shading.show_shadows = False

    scene.world.color = (1.0, 1.0, 1.0)
    original_hide = body.hide_render
    body.hide_render = False

    views = {
        "front": (center.x, center.y - height * 3.0, center.z),
        "side": (center.x + height * 3.0, center.y, center.z),
        "three_quarter": (
            center.x + height * 2.15,
            center.y - height * 2.45,
            center.z,
        ),
    }
    rendered: list[str] = []
    for name, location in views.items():
        camera.location = location
        _look_at(camera, center)
        path = output_dir / f"silhouette_{name}.png"
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        rendered.append(str(path))

    body.hide_render = original_hide
    shading.light = original["light"]
    shading.color_type = original["color_type"]
    shading.single_color = original["single_color"]
    shading.background_type = original["background_type"]
    shading.show_shadows = original["show_shadows"]
    scene.world.color = (0.05, 0.05, 0.05)
    scene.render.engine = original_engine
    scene.render.resolution_x, scene.render.resolution_y = original_resolution
    scene.render.resolution_percentage = 100
    return rendered


def build_character(
    config: CharacterConfig,
    base_mesh_path: str | Path,
    output_dir: str | Path,
    *,
    body_object_name: str | None = None,
    armature_object_name: str | None = None,
    render_preview: bool = True,
    save_blend: bool = True,
) -> dict[str, Any]:
    """Build Prototype 001 from a locally supplied rigged glTF/GLB base mesh."""

    output_path = Path(output_dir).expanduser().resolve()
    output_path.mkdir(parents=True, exist_ok=True)

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

    imported = import_humanoid_base(
        base_mesh_path,
        body_object_name=body_object_name,
        armature_object_name=armature_object_name,
    )
    if imported.armature is None:
        raise RuntimeError(
            "The selected base character has no armature. Use the rigged Quaternius "
            "Universal Base Characters mesh for this pipeline."
        )

    character_collection = _new_collection(f"{config.character_id}_Character")
    for obj in imported.objects:
        _move_to_collection(obj, character_collection)

    generated_collection = _new_collection("Generated_Character_Assets")
    studio_collection = _new_collection("Studio_Setup")

    body = imported.body
    _replace_body_material(body, config)

    top = build_bodytopo_garment(
        body,
        name="Top_Navy_Cropped",
        keep_region=keep_crop_top,
        rgba=_linear_rgba(config.outfit.top_color),
        roughness=0.72,
        push_distance=0.007,
        solidify_thickness=0.004,
    )
    shorts = build_bodytopo_garment(
        body,
        name="Shorts_Light_Grey",
        keep_region=keep_shorts,
        rgba=_linear_rgba(config.outfit.shorts_color),
        roughness=0.84,
        push_distance=0.008,
        solidify_thickness=0.005,
    )
    socks = build_bodytopo_garment(
        body,
        name="Socks_Off_White",
        keep_region=keep_socks,
        rgba=_linear_rgba(config.outfit.socks_color),
        roughness=0.88,
        push_distance=0.006,
        solidify_thickness=0.002,
    )

    slippers = build_slippers(
        body,
        armature=imported.armature,
        slipper_color=config.outfit.slipper_color,
        sole_color=config.outfit.sole_color,
        collection=generated_collection,
    )

    imported_hair = [
        obj
        for obj in imported.objects
        if obj.type == "MESH" and "hair" in obj.name.lower()
    ]
    if imported_hair:
        hair_objects = imported_hair
        hair_source = "imported_base_asset"
    else:
        hair_objects = build_long_hair_blockout(
            body,
            armature=imported.armature,
            base_color=config.hair.color,
            highlight_color=config.hair.highlight_color,
            collection=generated_collection,
            part=config.hair.part,
        )
        hair_source = "procedural_large_locks"

    camera, center, height = _setup_studio(body, studio_collection)
    preview_path = output_path / f"{config.character_id}_preview.png"
    silhouettes: list[str] = []

    if render_preview:
        silhouettes = _render_silhouettes(
            body,
            camera,
            center,
            height,
            output_path,
        )
        scene = bpy.context.scene
        camera.location = (
            center.x + height * 1.45,
            center.y - height * 2.8,
            center.z + height * 0.30,
        )
        _look_at(camera, center)
        scene.render.engine = "BLENDER_EEVEE_NEXT"
        scene.render.resolution_x = 900
        scene.render.resolution_y = 1200
        scene.render.image_settings.file_format = "PNG"
        scene.render.filepath = str(preview_path)
        bpy.ops.render.render(write_still=True)

    blend_path = output_path / f"{config.character_id}.blend"
    if save_blend:
        bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

    return {
        "character_id": config.character_id,
        "base_mesh_path": str(Path(base_mesh_path).expanduser().resolve()),
        "body_object": body.name,
        "body_vertices": len(body.data.vertices),
        "armature": imported.armature.name,
        "armature_bones": len(imported.armature.data.bones),
        "top": {key: value for key, value in top.items() if key != "object"},
        "shorts": {key: value for key, value in shorts.items() if key != "object"},
        "socks": {key: value for key, value in socks.items() if key != "object"},
        "slipper_object_count": len(slippers),
        "hair_object_count": len(hair_objects),
        "hair_source": hair_source,
        "blend_path": str(blend_path) if save_blend else None,
        "preview_path": str(preview_path) if render_preview else None,
        "silhouette_renders": silhouettes,
        "rig_status": "inherited_from_base_mesh; deformation_not_yet_validated",
    }
