"""Tests for character configuration and Blender-independent project contracts."""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from engine.core.config import CharacterConfig, ConfigError, load_character_config
from engine.core.paths import find_project_root

ROOT = Path(__file__).resolve().parents[1]
PROTOTYPE_CONFIG = ROOT / "characters" / "prototype_001" / "character.json"
BUILDER_SCRIPT = ROOT / "engine" / "blender" / "character_builder.py"
CLI_SCRIPT = ROOT / "scripts" / "build_character.py"


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
    assert config.pose.style == "mirror_selfie"
    assert config.pose.phone_visible is True


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


def test_blender_builder_is_valid_python_without_importing_blender() -> None:
    source = BUILDER_SCRIPT.read_text(encoding="utf-8")
    ast.parse(source, filename=str(BUILDER_SCRIPT))


def test_blender_cli_entrypoint_is_valid_python() -> None:
    source = CLI_SCRIPT.read_text(encoding="utf-8")
    ast.parse(source, filename=str(CLI_SCRIPT))


def test_pure_python_core_does_not_import_bpy() -> None:
    core_files = list((ROOT / "engine" / "core").glob("*.py"))
    assert core_files
    for path in core_files:
        assert "import bpy" not in path.read_text(encoding="utf-8")
