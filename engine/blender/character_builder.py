"""Procedural Blender blockout for the first stylized cinematic character.

Run this module inside Blender's bundled Python runtime. It intentionally does not
attempt to create production facial/body rigs; those are separate milestones.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import bpy
from mathutils import Vector

from engine.core.config import CharacterConfig


def _rgba(hex_color: str) -> tuple[float, float, float, float]:
    value = hex_color.lstrip("#")
    return (
        int(value[0:2], 16) / 255.0,
        int(value[2:4], 16) / 255.0,
        int(value[4:6], 16) / 255.0,
        1.0,
    )


def _material(
    name: str,
    color: str,
    *,
    roughness: float = 0.55,
    metallic: float = 0.0,
) -> bpy.types.Material:
    material = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    material.diffuse_color = _rgba(color)
    material.use_nodes = True
    principled = material.node_tree.nodes.get("Principled BSDF")
    if principled is not None:
        principled.inputs["Base Color"].default_value = _rgba(color)
        principled.inputs["Roughness"].default_value = roughness
        principled.inputs["Metallic"].default_value = metallic
    return material


def _move_to_collection(obj: bpy.types.Object, collection: bpy.types.Collection) -> None:
    for current in tuple(obj.users_collection):
        current.objects.unlink(obj)
    collection.objects.link(obj)


def _ellipsoid(
    name: str,
    location: tuple[float, float, float],
    scale: tuple[float, float, float],
    material: bpy.types.Material,
    collection: bpy.types.Collection,
    *,
    segments: int = 32,
    rings: int = 24,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=segments,
        ring_count=rings,
        radius=1.0,
        location=location,
    )
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(material)
    _move_to_collection(obj, collection)
    bpy.ops.object.shade_smooth()
    return obj


def _capsule(
    name: str,
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    radius: tuple[float, float],
    material: bpy.types.Material,
    collection: bpy.types.Collection,
) -> bpy.types.Object:
    start_vector = Vector(start)
    end_vector = Vector(end)
    direction = end_vector - start_vector
    if direction.length < 1e-5:
        raise ValueError(f"Capsule '{name}' requires two distinct endpoints")

    obj = _ellipsoid(
        name,
        tuple((start_vector + end_vector) / 2.0),
        (radius[0], radius[1], direction.length / 2.0 + max(radius)),
        material,
        collection,
    )
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = direction.to_track_quat("Z", "Y")
    return obj


def _curve(
    name: str,
    points: list[tuple[float, float, float]],
    material: bpy.types.Material,
    collection: bpy.types.Collection,
    *,
    bevel: float,
    resolution: int = 12,
) -> bpy.types.Object:
    curve_data = bpy.data.curves.new(name=f"{name}_Curve", type="CURVE")
    curve_data.dimensions = "3D"
    curve_data.resolution_u = resolution
    curve_data.bevel_depth = bevel
    curve_data.bevel_resolution = 4
    spline = curve_data.splines.new("BEZIER")
    spline.bezier_points.add(len(points) - 1)
    for point, coordinate in zip(spline.bezier_points, points, strict=True):
        point.co = coordinate
        point.handle_left_type = "AUTO"
        point.handle_right_type = "AUTO"

    obj = bpy.data.objects.new(name, curve_data)
    collection.objects.link(obj)
    obj.data.materials.append(material)
    return obj


def _beveled_box(
    name: str,
    location: tuple[float, float, float],
    scale: tuple[float, float, float],
    material: bpy.types.Material,
    collection: bpy.types.Collection,
    *,
    bevel: float = 0.06,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = (scale[0] * 2.0, scale[1] * 2.0, scale[2] * 2.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    modifier = obj.modifiers.new(name="Soft_Edges", type="BEVEL")
    modifier.width = bevel
    modifier.segments = 5
    obj.modifiers.new(name="Weighted_Normals", type="WEIGHTED_NORMAL")
    obj.data.materials.append(material)
    _move_to_collection(obj, collection)
    return obj


def _look_at(obj: bpy.types.Object, target: tuple[float, float, float]) -> None:
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def _build_hair(
    config: CharacterConfig,
    collection: bpy.types.Collection,
    hair_material: bpy.types.Material,
    highlight_material: bpy.types.Material,
    head_scale: float,
) -> None:
    _ellipsoid(
        "Hair_Cap",
        (0.0, 0.055, 4.66),
        (0.625 * head_scale, 0.53, 0.76 * head_scale),
        hair_material,
        collection,
    )
    _ellipsoid(
        "Hair_Back_Mass",
        (0.0, 0.16, 3.95),
        (0.55, 0.39, 0.91),
        hair_material,
        collection,
    )

    # Long side curtains form a readable silhouette before detailed grooming.
    for side in (-1.0, 1.0):
        _ellipsoid(
            f"Hair_Side_Mass_{'L' if side < 0 else 'R'}",
            (side * 0.49, 0.07, 3.82),
            (0.17, 0.22, 0.88),
            hair_material,
            collection,
        )
        for index in range(7):
            offset = index * 0.035
            x = side * (0.39 + offset)
            end_x = side * (0.47 + offset * 0.80)
            strand_material = highlight_material if index in (1, 5) else hair_material
            _curve(
                f"Hair_Lock_{'L' if side < 0 else 'R'}_{index:02d}",
                [
                    (side * 0.10, -0.02, 5.18 - offset * 0.30),
                    (side * 0.33, 0.00, 4.82),
                    (x, 0.06, 4.25),
                    (end_x, 0.13, 3.52),
                    (end_x - side * 0.04, 0.13, 2.92 + offset * 0.30),
                ],
                strand_material,
                collection,
                bevel=0.035 + (index % 3) * 0.004,
            )

    # A swept fringe gives the part a clear direction without hiding the eyes.
    direction = -1.0 if config.hair.part == "left" else 1.0
    if config.hair.part == "center":
        direction = 0.25
    _curve(
        "Hair_Swept_Front",
        [
            (-0.10, -0.36, 5.13),
            (0.05, -0.47, 5.08),
            (direction * 0.31, -0.43, 4.99),
            (direction * 0.43, -0.34, 4.83),
        ],
        highlight_material,
        collection,
        bevel=0.055,
    )


def _build_face(
    config: CharacterConfig,
    collection: bpy.types.Collection,
    skin: bpy.types.Material,
    eye_white: bpy.types.Material,
    iris: bpy.types.Material,
    pupil: bpy.types.Material,
    highlight: bpy.types.Material,
    brow: bpy.types.Material,
    mouth: bpy.types.Material,
) -> None:
    eye_scale = config.proportions.eye_scale
    for side in (-1.0, 1.0):
        x = side * 0.205
        _ellipsoid(
            f"Eye_White_{'L' if side < 0 else 'R'}",
            (x, -0.435, 4.73),
            (0.137 * eye_scale, 0.075, 0.165 * eye_scale),
            eye_white,
            collection,
        )
        _ellipsoid(
            f"Iris_{'L' if side < 0 else 'R'}",
            (x + 0.015, -0.501, 4.72),
            (0.073 * eye_scale, 0.035, 0.092 * eye_scale),
            iris,
            collection,
        )
        _ellipsoid(
            f"Pupil_{'L' if side < 0 else 'R'}",
            (x + 0.020, -0.531, 4.72),
            (0.037 * eye_scale, 0.020, 0.057 * eye_scale),
            pupil,
            collection,
        )
        _ellipsoid(
            f"Eye_Glint_{'L' if side < 0 else 'R'}",
            (x - 0.010, -0.550, 4.77),
            (0.022, 0.012, 0.026),
            highlight,
            collection,
            segments=16,
            rings=12,
        )
        _curve(
            f"Eyebrow_{'L' if side < 0 else 'R'}",
            [
                (x - 0.115, -0.438, 4.94),
                (x, -0.475, 4.985),
                (x + 0.105, -0.438, 4.95),
            ],
            brow,
            collection,
            bevel=0.028,
        )

    _ellipsoid(
        "Nose",
        (0.0, -0.515, 4.57),
        (0.075, 0.075, 0.095),
        skin,
        collection,
        segments=24,
        rings=16,
    )
    _curve(
        "Smile_Line",
        [
            (-0.14, -0.505, 4.43),
            (-0.07, -0.535, 4.395),
            (0.0, -0.542, 4.39),
            (0.07, -0.535, 4.395),
            (0.14, -0.505, 4.43),
        ],
        mouth,
        collection,
        bevel=0.018,
    )


def _build_body(
    config: CharacterConfig,
    collection: bpy.types.Collection,
    materials: dict[str, bpy.types.Material],
) -> None:
    skin = materials["skin"]
    top = materials["top"]
    shorts = materials["shorts"]
    socks = materials["socks"]
    slippers = materials["slippers"]
    sole = materials["sole"]

    head_scale = config.proportions.head_to_body_ratio / 0.46
    _ellipsoid("Pelvis", (0.0, 0.0, 2.72), (0.37, 0.26, 0.30), skin, collection)
    _ellipsoid("Shorts_Main", (0.0, 0.0, 2.78), (0.45, 0.29, 0.32), shorts, collection)
    _ellipsoid("Shorts_Waistband", (0.0, -0.005, 3.02), (0.435, 0.282, 0.075), shorts, collection)

    _capsule("Leg_Support_Thigh", (-0.17, 0.0, 2.66), (-0.18, 0.0, 1.48), (0.18, 0.17), skin, collection)
    _capsule("Leg_Support_Calf", (-0.18, 0.0, 1.52), (-0.16, -0.015, 0.39), (0.135, 0.13), skin, collection)
    _capsule("Leg_Bent_Thigh", (0.17, 0.015, 2.66), (0.37, -0.015, 1.70), (0.17, 0.16), skin, collection)
    _capsule("Leg_Bent_Calf", (0.37, -0.015, 1.70), (0.08, 0.12, 1.02), (0.125, 0.12), skin, collection)

    _ellipsoid("Sock_Support", (-0.16, -0.015, 0.34), (0.145, 0.14, 0.23), socks, collection)
    _ellipsoid("Sock_Bent", (0.08, 0.12, 1.04), (0.13, 0.125, 0.20), socks, collection)
    _ellipsoid("Slipper_Sole_Support", (-0.16, -0.19, 0.14), (0.22, 0.39, 0.075), sole, collection)
    _ellipsoid("Slipper_Upper_Support", (-0.16, -0.15, 0.25), (0.205, 0.30, 0.16), slippers, collection)
    _ellipsoid("Slipper_Sole_Bent", (0.08, -0.015, 0.86), (0.20, 0.34, 0.07), sole, collection)
    _ellipsoid("Slipper_Upper_Bent", (0.08, 0.005, 0.97), (0.185, 0.26, 0.14), slippers, collection)

    _ellipsoid("Torso_Base", (0.0, 0.0, 3.58), (0.40, 0.245, 0.62), skin, collection)
    _ellipsoid("Top_Main", (0.0, -0.005, 3.67), (0.425, 0.265, 0.43), top, collection)
    _ellipsoid("Neck", (0.0, -0.005, 4.12), (0.17, 0.16, 0.25), skin, collection)

    _capsule("Arm_Left_Upper", (-0.37, 0.0, 3.90), (-0.54, -0.02, 3.38), (0.12, 0.12), skin, collection)
    _capsule("Arm_Left_Forearm", (-0.54, -0.02, 3.38), (-0.54, -0.14, 3.02), (0.105, 0.10), skin, collection)
    _ellipsoid("Hand_Left", (-0.54, -0.15, 2.92), (0.12, 0.085, 0.15), skin, collection)
    _ellipsoid("Sleeve_Left", (-0.40, -0.005, 3.83), (0.17, 0.25, 0.20), top, collection)

    if config.pose.style == "mirror_selfie":
        _capsule("Arm_Right_Upper", (0.37, 0.0, 3.91), (0.53, -0.10, 4.24), (0.12, 0.12), skin, collection)
        _capsule("Arm_Right_Forearm", (0.53, -0.10, 4.24), (0.31, -0.40, 4.60), (0.095, 0.09), skin, collection)
        _ellipsoid("Hand_Right", (0.24, -0.52, 4.62), (0.13, 0.085, 0.17), skin, collection)
        _ellipsoid("Sleeve_Right", (0.40, -0.015, 3.86), (0.17, 0.25, 0.20), top, collection)
        if config.pose.phone_visible:
            phone = _beveled_box(
                "Phone_Body",
                (0.18, -0.625, 4.66),
                (0.17, 0.045, 0.28),
                materials["phone"],
                collection,
                bevel=0.035,
            )
            phone.rotation_euler[1] = -0.08
            _ellipsoid(
                "Phone_Camera_Lens",
                (0.28, -0.679, 4.87),
                (0.026, 0.008, 0.026),
                materials["phone_lens"],
                collection,
                segments=16,
                rings=12,
            )
    else:
        _capsule("Arm_Right_Upper", (0.37, 0.0, 3.91), (0.52, -0.02, 3.38), (0.12, 0.12), skin, collection)
        _capsule("Arm_Right_Forearm", (0.52, -0.02, 3.38), (0.52, -0.12, 3.02), (0.105, 0.10), skin, collection)
        _ellipsoid("Hand_Right", (0.52, -0.14, 2.92), (0.12, 0.085, 0.15), skin, collection)
        _ellipsoid("Sleeve_Right", (0.40, -0.005, 3.86), (0.17, 0.25, 0.20), top, collection)

    _ellipsoid(
        "Head",
        (0.0, 0.0, 4.66),
        (0.59 * head_scale, 0.47, 0.70 * head_scale),
        skin,
        collection,
        segments=48,
        rings=32,
    )


def _build_studio(collection: bpy.types.Collection, materials: dict[str, bpy.types.Material]) -> None:
    scene = bpy.context.scene
    bpy.ops.mesh.primitive_plane_add(size=200.0, location=(0.0, 0.0, -0.01))
    floor = bpy.context.object
    floor.name = "Studio_Floor"
    floor.data.materials.append(materials["floor"])
    _move_to_collection(floor, collection)

    bpy.ops.object.camera_add(location=(6.3, -11.5, 5.3))
    camera = bpy.context.object
    camera.name = "Preview_Camera"
    camera.data.lens = 52
    _look_at(camera, (0.0, 0.0, 2.70))
    _move_to_collection(camera, collection)
    scene.camera = camera

    lights: list[tuple[str, tuple[float, float, float], float, float, tuple[float, float, float]]] = [
        ("Key_Light", ( -4.5, -6.5, 8.0), 1050.0, 5.0, (0.0, 0.0, 3.0)),
        ("Fill_Light", (5.0, -4.0, 5.0), 650.0, 4.0, (0.0, 0.0, 3.0)),
        ("Rim_Light", (0.0, 3.5, 6.5), 1250.0, 3.0, (0.0, 0.0, 3.4)),
    ]
    for name, location, power, size, target in lights:
        bpy.ops.object.light_add(type="AREA", location=location)
        light = bpy.context.object
        light.name = name
        light.data.energy = power
        light.data.shape = "DISK"
        light.data.size = size
        _look_at(light, target)
        _move_to_collection(light, collection)

    if scene.world is None:
        scene.world = bpy.data.worlds.new("Studio_World")
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    if background is not None:
        background.inputs["Color"].default_value = (0.48, 0.52, 0.60, 1.0)
        background.inputs["Strength"].default_value = 0.35

    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = 960
    scene.render.resolution_y = 1280
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "AgX"
    scene.render.image_settings.color_mode = "RGBA"


def _make_materials(config: CharacterConfig) -> dict[str, bpy.types.Material]:
    return {
        "skin": _material("Skin_Warm_Neutral", config.face.skin_color, roughness=0.62),
        "top": _material("Top_Navy_Blue", config.outfit.top_color, roughness=0.68),
        "shorts": _material("Shorts_Light_Grey", config.outfit.shorts_color, roughness=0.78),
        "socks": _material("Socks_Off_White", config.outfit.socks_color, roughness=0.85),
        "slippers": _material("Slippers_Soft_White", config.outfit.slipper_color, roughness=0.82),
        "sole": _material("Slipper_Sole", config.outfit.sole_color, roughness=0.9),
        "hair": _material("Hair_Base", config.hair.color, roughness=0.48),
        "hair_highlight": _material("Hair_Highlight", config.hair.highlight_color, roughness=0.44),
        "eye_white": _material("Eye_White", "#FFF9F0", roughness=0.22),
        "iris": _material("Iris", config.face.iris_color, roughness=0.28),
        "pupil": _material("Pupil", "#171311", roughness=0.12),
        "eye_glint": _material("Eye_Glint", "#FFFFFF", roughness=0.08),
        "brow": _material("Eyebrow", config.hair.color, roughness=0.65),
        "mouth": _material("Mouth_Line", "#8F4E4B", roughness=0.75),
        "phone": _material("Phone_Glass_Black", "#11151D", roughness=0.19, metallic=0.25),
        "phone_lens": _material("Phone_Lens", "#303B4C", roughness=0.14, metallic=0.45),
        "floor": _material("Studio_Floor_Matte", "#D5D9DF", roughness=0.9),
    }


def build_character(
    config: CharacterConfig,
    output_dir: str | Path,
    *,
    render_preview: bool = True,
    save_blend: bool = True,
) -> dict[str, Any]:
    """Build the configured character blockout and optional preview outputs."""

    output_path = Path(output_dir).expanduser().resolve()
    output_path.mkdir(parents=True, exist_ok=True)

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

    character_collection = bpy.data.collections.new(f"{config.character_id}_Character")
    bpy.context.scene.collection.children.link(character_collection)
    studio_collection = bpy.data.collections.new("Studio_Setup")
    bpy.context.scene.collection.children.link(studio_collection)

    materials = _make_materials(config)
    _build_body(config, character_collection, materials)
    _build_face(
        config,
        character_collection,
        materials["skin"],
        materials["eye_white"],
        materials["iris"],
        materials["pupil"],
        materials["eye_glint"],
        materials["brow"],
        materials["mouth"],
    )
    _build_hair(
        config,
        character_collection,
        materials["hair"],
        materials["hair_highlight"],
        config.proportions.head_to_body_ratio / 0.46,
    )
    _build_studio(studio_collection, materials)

    scene = bpy.context.scene
    scene.render.filepath = str(output_path / f"{config.character_id}_preview.png")
    blend_path = output_path / f"{config.character_id}.blend"

    if save_blend:
        bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    if render_preview:
        bpy.ops.render.render(write_still=True)

    return {
        "character_id": config.character_id,
        "blend_path": str(blend_path) if save_blend else None,
        "preview_path": scene.render.filepath if render_preview else None,
        "object_count": len(character_collection.objects),
        "rig_status": "not_implemented_in_p1",
    }
