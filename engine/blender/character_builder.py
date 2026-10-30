"""Build Prototype 001 as an original procedural stylized cinematic character.

No third-party character mesh is imported. The body, head, face, hairstyle, clothing,
and footwear are generated from editable parametric surfaces in Blender.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import bpy
from mathutils import Vector

from engine.blender.body import build_body
from engine.blender.face import build_face
from engine.blender.geometry import create_material
from engine.blender.hair import build_hair
from engine.blender.head import build_head
from engine.blender.outfit import build_outfit
from engine.core.config import CharacterConfig


def _new_collection(name: str) -> bpy.types.Collection:
    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)
    return collection


def _look_at(obj: bpy.types.Object, target: Vector) -> None:
    direction = target - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def _create_stage(
    collection: bpy.types.Collection,
    *,
    target: Vector,
) -> bpy.types.Object:
    scene = bpy.context.scene
    bpy.ops.mesh.primitive_plane_add(size=200.0, location=(0.0, 0.0, -0.015))
    floor = bpy.context.object
    floor.name = "Studio_Floor"
    floor_material = create_material("Studio_Floor_Material", "#D8DCE4", roughness=0.92)
    floor.data.materials.append(floor_material)
    for current in tuple(floor.users_collection):
        current.objects.unlink(floor)
    collection.objects.link(floor)

    bpy.ops.object.camera_add(location=(5.6, -10.8, 4.1))
    camera = bpy.context.object
    camera.name = "Character_Review_Camera"
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 6.25
    _look_at(camera, target)
    for current in tuple(camera.users_collection):
        current.objects.unlink(camera)
    collection.objects.link(camera)
    scene.camera = camera

    light_specs = [
        ("Key_Softbox", (-4.4, -6.0, 7.2), 1750.0, 5.0),
        ("Fill_Softbox", (4.8, -4.0, 4.5), 900.0, 4.5),
        ("Hair_Rim", (0.0, 3.0, 6.5), 2200.0, 3.0),
        ("Eye_Catchlight", (0.0, -6.0, 3.8), 180.0, 1.4),
    ]
    for name, location, energy, size in light_specs:
        bpy.ops.object.light_add(type="AREA", location=location)
        light = bpy.context.object
        light.name = name
        light.data.energy = energy
        light.data.shape = "DISK"
        light.data.size = size
        _look_at(light, target)
        for current in tuple(light.users_collection):
            current.objects.unlink(light)
        collection.objects.link(light)

    if scene.world is None:
        scene.world = bpy.data.worlds.new("Illumination_Studio_World")
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    if background is not None:
        background.inputs["Color"].default_value = (0.58, 0.64, 0.76, 1.0)
        background.inputs["Strength"].default_value = 0.42

    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = 1100
    scene.render.resolution_y = 1400
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    camera.data.lens = 50.0
    return camera


def _render_silhouette_views(
    camera: bpy.types.Object,
    target: Vector,
    output_dir: Path,
) -> list[str]:
    scene = bpy.context.scene
    original_engine = scene.render.engine
    original_x = scene.render.resolution_x
    original_y = scene.render.resolution_y
    original_percentage = scene.render.resolution_percentage
    shading = scene.display.shading
    floor = bpy.data.objects.get("Studio_Floor")
    floor_was_hidden = floor.hide_render if floor is not None else False
    if floor is not None:
        floor.hide_render = True
    world_color = tuple(scene.world.color) if scene.world is not None else None
    if scene.world is not None:
        scene.world.color = (0.94, 0.95, 0.98)
    saved_shading = {
        "light": shading.light,
        "color_type": shading.color_type,
        "single_color": tuple(shading.single_color),
        "background_type": shading.background_type,
        "background_color": tuple(shading.background_color),
        "show_shadows": shading.show_shadows,
        "show_cavity": shading.show_cavity,
    }

    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_x = 600
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    shading.light = "FLAT"
    shading.color_type = "SINGLE"
    shading.single_color = (0.012, 0.012, 0.018)
    shading.background_type = "WORLD"
    shading.background_color = (0.94, 0.95, 0.98)
    shading.show_shadows = False
    shading.show_cavity = False

    views = {
        "front": (0.0, -11.5, target.z),
        "side": (11.5, 0.0, target.z),
        "three_quarter": (7.5, -9.0, target.z + 0.15),
    }
    rendered: list[str] = []
    for name, location in views.items():
        camera.location = location
        _look_at(camera, target)
        path = output_dir / f"silhouette_{name}.png"
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        rendered.append(str(path))

    shading.light = saved_shading["light"]
    shading.color_type = saved_shading["color_type"]
    shading.single_color = saved_shading["single_color"]
    shading.background_type = saved_shading["background_type"]
    shading.background_color = saved_shading["background_color"]
    shading.show_shadows = saved_shading["show_shadows"]
    shading.show_cavity = saved_shading["show_cavity"]
    if floor is not None:
        floor.hide_render = floor_was_hidden
    if scene.world is not None and world_color is not None:
        scene.world.color = world_color
    scene.render.engine = original_engine
    scene.render.resolution_x = original_x
    scene.render.resolution_y = original_y
    scene.render.resolution_percentage = original_percentage
    return rendered


def _create_material_palette(config: CharacterConfig) -> dict[str, bpy.types.Material]:
    return {
        "skin": create_material(
            "Skin_Warm_Cinematic",
            config.face.skin_color,
            roughness=0.48,
            subsurface=0.075,
        ),
        "iris": create_material(
            "Iris_Deep_Hazel",
            config.face.iris_color,
            roughness=0.24,
            coat=0.18,
        ),
        "eye_white": create_material(
            "Eye_White_Warm",
            "#FFF9F0",
            roughness=0.19,
            coat=0.12,
        ),
        "dark": create_material("Eye_Pupil_And_Mouth", "#231A1B", roughness=0.25),
        "lip": create_material("Lip_Natural_Rose", "#A85F59", roughness=0.42),
        "hair": create_material(
            "Hair_Warm_Base",
            config.hair.color,
            roughness=0.34,
            coat=0.23,
        ),
        "hair_highlight": create_material(
            "Hair_Golden_Highlight",
            config.hair.highlight_color,
            roughness=0.30,
            coat=0.25,
        ),
        "top": create_material(
            "Fabric_Navy_Blue",
            config.outfit.top_color,
            roughness=0.72,
        ),
        "shorts": create_material(
            "Fabric_Light_Grey",
            config.outfit.shorts_color,
            roughness=0.83,
        ),
        "socks": create_material(
            "Fabric_Off_White",
            config.outfit.socks_color,
            roughness=0.88,
        ),
        "slippers": create_material(
            "Slipper_Soft_Upper",
            config.outfit.slipper_color,
            roughness=0.91,
        ),
        "sole": create_material(
            "Slipper_Sole",
            config.outfit.sole_color,
            roughness=0.94,
        ),
    }


def build_character(
    config: CharacterConfig,
    output_dir: str | Path,
    *,
    render_preview: bool = True,
    save_blend: bool = True,
) -> dict[str, Any]:
    """Generate Prototype 001 from custom parametric geometry."""

    output_path = Path(output_dir).expanduser().resolve()
    output_path.mkdir(parents=True, exist_ok=True)

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

    character_collection = _new_collection(f"{config.character_id}_Character")
    face_collection = _new_collection("Face_Details")
    hair_collection = _new_collection("Hair_Clumps")
    outfit_collection = _new_collection("Outfit")
    studio_collection = _new_collection("Studio_Setup")
    palette = _create_material_palette(config)

    body_objects = build_body(character_collection, palette["skin"])
    head_scale = 0.98 + (config.proportions.head_to_body_ratio - 0.46) * 0.35
    head = build_head(character_collection, palette["skin"], scale=head_scale)
    face_objects = build_face(
        face_collection,
        skin=palette["skin"],
        iris=palette["iris"],
        eye_white=palette["eye_white"],
        dark=palette["dark"],
        lip=palette["lip"],
        eye_scale=config.proportions.eye_scale,
    )
    hair_objects = build_hair(
        hair_collection,
        base=palette["hair"],
        highlight=palette["hair_highlight"],
        part=config.hair.part,
    )
    outfit_objects = build_outfit(
        outfit_collection,
        top=palette["top"],
        shorts=palette["shorts"],
        socks=palette["socks"],
        slippers=palette["slippers"],
        sole=palette["sole"],
    )

    target = Vector((0.0, 0.0, 2.78))
    camera = _create_stage(studio_collection, target=target)
    preview_path = output_path / f"{config.character_id}_preview.png"
    silhouette_paths: list[str] = []

    if render_preview:
        silhouette_paths = _render_silhouette_views(camera, target, output_path)
        camera.location = (5.6, -10.8, 4.1)
        _look_at(camera, target)
        scene = bpy.context.scene
        scene.render.engine = "BLENDER_EEVEE_NEXT"
        scene.render.resolution_x = 1100
        scene.render.resolution_y = 1400
        scene.render.resolution_percentage = 100
        scene.render.filepath = str(preview_path)
        bpy.ops.render.render(write_still=True)

    blend_path = output_path / f"{config.character_id}.blend"
    if save_blend:
        bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

    mesh_objects = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    return {
        "character_id": config.character_id,
        "construction": "original_parametric_meshes",
        "body_object_count": len(body_objects),
        "head_object": head.name,
        "face_object_count": len(face_objects),
        "hair_object_count": len(hair_objects),
        "outfit_object_count": len(outfit_objects),
        "mesh_object_count": len(mesh_objects),
        "facial_rig_status": "planned_not_implemented",
        "body_rig_status": "planned_not_implemented",
        "blend_path": str(blend_path) if save_blend else None,
        "preview_path": str(preview_path) if render_preview else None,
        "silhouette_renders": silhouette_paths,
    }
