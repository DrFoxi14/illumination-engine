"""Tests for the Blender-independent character configuration contract."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from engine.core.config import CharacterConfig, ConfigError, load_character_config
from engine.core.paths import find_project_root


ROOT = Path(__file__).resolve().parents[1]
PROTOTYPE_CONFIG = ROOT / "characters" / "prototype_001" / "character.json"


def test_loads_prototype_character_config() -> None:
    config = load_character_config(PROTOTYPE_CONFIG)

    assert isinstance(config, CharacterConfig)
    assert config.character_id == "prototype_001"
    assert config.visual_style == "stylized_cinematic"
    assert config.features.facial_rig is True
    assert config.proportions.eye_scale == pytest.approx(1.15)


def test_rejects_unsupported_schema_version() -> None:
    payload = json.loads(PROTOTYPE_CONFIG.read_text(encoding="utf-8"))
    payload["schema_version"] = 99

    with pytest.raises(ConfigError, match="Unsupported"):
        CharacterConfig.from_mapping(payload)


def test_rejects_boolean_schema_version() -> None:
    payload = json.loads(PROTOTYPE_CONFIG.read_text(encoding="utf-8"))
    payload["schema_version"] = True

    with pytest.raises(ConfigError, match="Unsupported"):
        CharacterConfig.from_mapping(payload)


def test_rejects_out_of_range_proportions() -> None:
    payload = json.loads(PROTOTYPE_CONFIG.read_text(encoding="utf-8"))
    payload["proportions"]["eye_scale"] = 9.0

    with pytest.raises(ConfigError, match="eye_scale"):
        CharacterConfig.from_mapping(payload)


def test_rejects_non_finite_proportions() -> None:
    payload = json.loads(PROTOTYPE_CONFIG.read_text(encoding="utf-8"))
    payload["proportions"]["head_to_body_ratio"] = float("nan")

    with pytest.raises(ConfigError, match="finite"):
        CharacterConfig.from_mapping(payload)


def test_rejects_invalid_character_identifier() -> None:
    payload = json.loads(PROTOTYPE_CONFIG.read_text(encoding="utf-8"))
    payload["character_id"] = "../prototype"

    with pytest.raises(ConfigError, match="character_id"):
        CharacterConfig.from_mapping(payload)


def test_project_root_can_be_discovered_from_nested_file() -> None:
    assert find_project_root(PROTOTYPE_CONFIG) == ROOT
