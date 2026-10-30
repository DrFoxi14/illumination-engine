"""Build Prototype 001 as an original procedural stylized cinematic character.

No third-party character mesh is imported. The body, head, face, hairstyle, clothing,
and footwear are generated from editable parametric surfaces in Blender.
"""

from __future__ import annotations

import bpy
import json
from mathutils import Vector
from pathlib import Path
from typing import Any

from engine.blender.body import build_body
from engine.blender.face import build_face
from engine.blender.geometry import create_ellipsoid, create_material
from engine.blender.hair import build_hair
from engine.blender.head import build_head
from engine.blender.outfit import build_outfit
from engine.blender.skin import unify_skin_surface
from engine.blender.validation import validate_character_scene
from engine.core.config import CharacterConfig


def _new_collection(name: str) -> bpy.types.Collection:
    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)
    return collection


def _look_at(obj: bpy.types.Object, target: Vector) -> None:
    direction = target - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def _set_eevee_engine(scene: bpy.types.Scene) -> str:
    """Choose the EEVEE engine identifier exposed by the running Blender version."""

    from engine.blender.compat import choose_eevee_engine

    engine_enum = scene.render.bl_rna.properties["engine"]
    available = {item.identifier for item in engine_enum.enum_items}
    selected = choose_eevee_engine(available)
    scene.render.engine = selected
    return selected


def _build_phone(
    collection: bpy.types.Collection,
    *,
    body_material: bpy.types.Material,
    lens_material: bpy.types.Material,
) -> list[bpy.types.Object]:
    """Create a small beveled phone prop beside the raised selfie hand."""

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.355, -0.535, 4.625))
    phone = bpy.context.object
    phone.name = "Phone_Back"
    phone.dimensions = (0.180, 0.040, 0.305)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    phone.rotation_euler[1] = -0.055
    bevel = phone.modifiers.new(name="Phone_Edge_Radius", type="BEVEL")
    bevel.width = 0.014
    bevel.segments = 5
    phone.modifiers.new(name="Phone_Weighted_Normals", type="WEIGHTED_NORMAL")
    phone.data.materials.append(body_material)
    for current in tuple(phone.users_collection):
        current.objects.unlink(phone)
    collection.objects.link(phone)

    lenses = []
    for index, offset in enumerate((-0.035, 0.035), start=1):
        lens = create_ellipsoid(
            f"Phone_Camera_Lens_{index}",
            (0.355 + offset, -0.560, 4.735),
            (0.018, 0.007, 0.018),
            lens_material,
            collection,
            segments=20,
            rings=14,
            subdivision=1,
        )
        lenses.append(lens)
    return [phone, *lenses]


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

    _set_eevee_engine(scene)
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
        "top_detail": create_material(
            "Fabric_Navy_Stitching",
            "#344C7A",
            roughness=0.78,
        ),
        "shorts": create_material(
            "Fabric_Light_Grey",
            config.outfit.shorts_color,
            roughness=0.83,
        ),
        "shorts_detail": create_material(
            "Fabric_Grey_Stitching",
            "#92948E",
            roughness=0.88,
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
    render_color_preview: bool = True,
    render_engine: str = "EEVEE",
    preview_samples: int = 16,
    save_blend: bool = True,
) -> dict[str, Any]:
    """Generate Prototype 001 from custom parametric geometry."""

    if render_engine in {"BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"}:
        render_engine = "EEVEE"
    if render_engine not in {"EEVEE", "CYCLES"}:
        raise ValueError(f"Unsupported preview render engine: {render_engine}")
    if not 1 <= preview_samples <= 128:
        raise ValueError("preview_samples must be between 1 and 128")

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

    body_objects = build_body(
        character_collection,
        palette["skin"],
        pose=config.pose.style,
    )
    head_scale = 0.98 + (config.proportions.head_to_body_ratio - 0.46) * 0.35
    head = build_head(character_collection, palette["skin"], scale=head_scale)
    skin_object = unify_skin_surface(
        [*body_objects, head],
        palette["skin"],
        voxel_size=0.012,
        smooth_iterations=3,
    )
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
        top_detail=palette["top_detail"],
        shorts=palette["shorts"],
        shorts_detail=palette["shorts_detail"],
        socks=palette["socks"],
        slippers=palette["slippers"],
        sole=palette["sole"],
    )

    props_collection = _new_collection("Handheld_Props")
    phone_objects: list[bpy.types.Object] = []
    if config.pose.phone_visible and config.pose.style == "mirror_selfie":
        phone_objects = _build_phone(
            props_collection,
            body_material=create_material(
                "Phone_Graphite_Glass",
                "#171B24",
                roughness=0.20,
                metallic=0.18,
            ),
            lens_material=create_material(
                "Phone_Camera_Glass",
                "#46546C",
                roughness=0.14,
                metallic=0.28,
            ),
        )

    target = Vector((0.0, 0.0, 2.78))
    camera = _create_stage(studio_collection, target=target)
    preview_path = output_path / f"{config.character_id}_preview.png"
    silhouette_paths: list[str] = []

    validation_report = validate_character_scene()
    validation_report["character_id"] = config.character_id
    validation_report["construction"] = "original_parametric_meshes"
    validation_path = output_path / "validation_report.json"
    validation_path.write_text(
        json.dumps(validation_report, indent=2) + "\n",
        encoding="utf-8",
    )

    if render_preview:
        silhouette_paths = _render_silhouette_views(camera, target, output_path)

    actual_preview_engine: str | None = None
    if render_color_preview:
        camera.location = (5.6, -10.8, 4.1)
        _look_at(camera, target)
        scene = bpy.context.scene
        actual_preview_engine = (
            "CYCLES" if render_engine == "CYCLES" else _set_eevee_engine(scene)
        )
        if render_engine == "CYCLES":
            scene.render.engine = "CYCLES"
        scene.render.resolution_x = 960 if render_engine == "CYCLES" else 1100
        scene.render.resolution_y = 1200 if render_engine == "CYCLES" else 1400
        scene.render.resolution_percentage = 100
        if render_engine == "CYCLES":
            scene.cycles.device = "CPU"
            scene.cycles.samples = preview_samples
            scene.cycles.use_denoising = True
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
        "skin_object": skin_object.name,
        "skin_vertices": len(skin_object.data.vertices),
        "skin_faces": len(skin_object.data.polygons),
        "face_object_count": len(face_objects),
        "hair_object_count": len(hair_objects),
        "outfit_object_count": len(outfit_objects),
        "phone_object_count": len(phone_objects),
        "pose": config.pose.style,
        "mesh_object_count": len(mesh_objects),
        "facial_rig_status": "planned_not_implemented",
        "body_rig_status": "planned_not_implemented",
        "blend_path": str(blend_path) if save_blend else None,
        "preview_path": str(preview_path) if render_color_preview else None,
        "preview_render_engine": actual_preview_engine,
        "preview_samples": preview_samples if render_color_preview else None,
        "silhouette_renders": silhouette_paths,
        "validation_report_path": str(validation_path),
        "validation": validation_report,
    }
