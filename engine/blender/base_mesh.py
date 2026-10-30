"""Import and identify a rigged external humanoid base mesh in Blender."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import bpy


@dataclass(frozen=True, slots=True)
class ImportedCharacter:
    """Objects imported from one glTF/GLB character asset."""

    body: bpy.types.Object
    armature: bpy.types.Object | None
    objects: tuple[bpy.types.Object, ...]


_EXCLUDED_BODY_TOKENS = (
    "hair",
    "eye",
    "brow",
    "lash",
    "teeth",
    "tooth",
    "tongue",
    "mouth",
    "shoe",
    "accessory",
)


def import_humanoid_base(
    asset_path: str | Path,
    *,
    body_object_name: str | None = None,
    armature_object_name: str | None = None,
) -> ImportedCharacter:
    """Import a Quaternius-style rigged glTF/GLB character.

    The base mesh is not bundled in this repository. The caller supplies the path
    to a locally downloaded asset whose license permits the intended use.
    """

    path = Path(asset_path).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Base character asset was not found: {path}")
    if path.suffix.lower() not in {".gltf", ".glb"}:
        raise ValueError("Base character must be a .gltf or .glb file")

    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    imported = tuple(obj for obj in bpy.data.objects if obj not in before)
    meshes = [obj for obj in imported if obj.type == "MESH"]
    armatures = [obj for obj in imported if obj.type == "ARMATURE"]

    if not meshes:
        raise RuntimeError(f"No mesh objects were imported from {path.name}")

    if body_object_name:
        body = next((obj for obj in meshes if obj.name == body_object_name), None)
        if body is None:
            available = ", ".join(sorted(obj.name for obj in meshes))
            raise RuntimeError(
                f"Body object '{body_object_name}' was not found. Imported meshes: {available}"
            )
    else:
        candidates = [
            obj
            for obj in meshes
            if not any(token in obj.name.lower() for token in _EXCLUDED_BODY_TOKENS)
        ]
        if not candidates:
            candidates = meshes
        body = max(candidates, key=lambda obj: len(obj.data.vertices))

    if len(body.data.vertices) < 250:
        raise RuntimeError(
            f"Selected body mesh '{body.name}' is unexpectedly small "
            f"({len(body.data.vertices)} vertices). Pass --body-object to select the body."
        )

    if armature_object_name:
        armature = next(
            (obj for obj in armatures if obj.name == armature_object_name),
            None,
        )
        if armature is None:
            available = ", ".join(sorted(obj.name for obj in armatures)) or "none"
            raise RuntimeError(
                f"Armature '{armature_object_name}' was not found. Imported armatures: {available}"
            )
    else:
        armature = max(
            armatures,
            key=lambda obj: len(obj.data.bones),
            default=None,
        )

    if armature is not None and not any(
        modifier.type == "ARMATURE" and modifier.object == armature
        for modifier in body.modifiers
    ):
        modifier = body.modifiers.new(name="Base_Armature", type="ARMATURE")
        modifier.object = armature

    body.name = "Character_Body"
    return ImportedCharacter(body=body, armature=armature, objects=imported)
