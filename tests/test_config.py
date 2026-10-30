"""Tests for configuration, pure garment rules, and Blender-independent contracts."""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from engine.core.config import CharacterConfig, ConfigError, load_character_config
from engine.core.garment_rules import keep_crop_top, keep_shorts, keep_socks
from engine.core.paths import find_project_root

ROOT = Path(__file__).resolve().parents[1]
PROTOTYPE_CONFIG = ROOT / "characters" / "prototype_001" / "character.json"
BLENDER_MODULES = (
    ROOT / "engine" / "blender" / "base_mesh.py",
    ROOT / "engine" / "blender" / "body_topology.py",
    ROOT / "engine" / "blender" / "character_builder.py",
    ROOT / "engine" / "blender" / "grooming.py",
    ROOT / "engine" / "blender" / "footwear.py",
    ROOT / "scripts" / "build_character.py",
)


def _prototype_payload() -> dict:
    return json.loads(PROTOTYPE_CONFIG.read_text(encoding="utf-8"))


def test_loads_prototype_character_config() -> None:
    config = load_character_config(PROTOTYPE_CONFIG)

    assert isinstance(config, CharacterConfig)
    assert config.character_id == "prototype_001"
    assert config.visual_style == "stylized_cinematic"
    assert config.features.facial_rig is True
    assert config.proportions.eye_scale == pytest.approx(1.22)
    assert config.hair.style == "long_straight"
    assert config.hair.part == "left"
    assert config.pose.style == "neutral_standing"
    assert config.pose.phone_visible is False


def test_rejects_unsupported_schema_version() -> None:
    payload = _prototype_payload()
    payload["schema_version"] = 99

    with pytest.raises(ConfigError, match="Unsupported"):
        CharacterConfig.from_mapping(payload)


def test_rejects_boolean_schema_version() -> None:
    payload = _prototype_payload()
    payload["schema_version"] = True

    with pytest.raises(ConfigError, match="Unsupported"):
        CharacterConfig.from_mapping(payload)


def test_rejects_out_of_range_proportions() -> None:
    payload = _prototype_payload()
    payload["proportions"]["eye_scale"] = 9.0

    with pytest.raises(ConfigError, match="eye_scale"):
        CharacterConfig.from_mapping(payload)


def test_rejects_non_finite_proportions() -> None:
    payload = _prototype_payload()
    payload["proportions"]["head_to_body_ratio"] = float("nan")

    with pytest.raises(ConfigError, match="finite"):
        CharacterConfig.from_mapping(payload)


def test_rejects_invalid_character_identifier() -> None:
    payload = _prototype_payload()
    payload["character_id"] = "../prototype"

    with pytest.raises(ConfigError, match="character_id"):
        CharacterConfig.from_mapping(payload)


def test_rejects_invalid_hex_color() -> None:
    payload = _prototype_payload()
    payload["hair"]["color"] = "blonde"

    with pytest.raises(ConfigError, match="six-digit hex color"):
        CharacterConfig.from_mapping(payload)


def test_rejects_unknown_hair_style() -> None:
    payload = _prototype_payload()
    payload["hair"]["style"] = "photorealistic"

    with pytest.raises(ConfigError, match="style must be one of"):
        CharacterConfig.from_mapping(payload)


def test_rejects_unknown_pose_style() -> None:
    payload = _prototype_payload()
    payload["pose"]["style"] = "flying"

    with pytest.raises(ConfigError, match="style must be one of"):
        CharacterConfig.from_mapping(payload)


def test_project_root_can_be_discovered_from_nested_file() -> None:
    assert find_project_root(PROTOTYPE_CONFIG) == ROOT


@pytest.mark.parametrize(
    ("region", "point", "expected"),
    [
        (keep_crop_top, (0.55, 0.0, 0.66), True),
        (keep_crop_top, (0.9, 0.0, 0.66), False),
        (keep_crop_top, (0.0, 0.0, 0.30), False),
        (keep_shorts, (0.82, 0.0, 0.45), True),
        (keep_shorts, (0.0, 0.0, 0.70), False),
        (keep_socks, (0.2, 0.0, 0.08), True),
        (keep_socks, (0.2, 0.0, 0.48), False),
    ],
)
def test_normalized_garment_regions(region, point, expected) -> None:
    assert region(*point) is expected


@pytest.mark.parametrize("path", BLENDER_MODULES)
def test_blender_runtime_modules_are_valid_python(path: Path) -> None:
    ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def test_pure_python_core_does_not_import_bpy() -> None:
    core_files = list((ROOT / "engine" / "core").glob("*.py"))
    assert core_files
    for path in core_files:
        assert "import bpy" not in path.read_text(encoding="utf-8")
