"""Validated, Blender-independent character configuration.

This module deliberately has no bpy dependency so configuration and validation can
run in ordinary Python, including CI environments without Blender installed.
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


class ConfigError(ValueError):
    """Raised when a character configuration is malformed or unsupported."""


@dataclass(frozen=True, slots=True)
class ProportionConfig:
    """High-level proportion controls for the procedural character blockout."""

    head_to_body_ratio: float
    eye_scale: float

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> ProportionConfig:
        ratio = _number(value, "head_to_body_ratio")
        eye_scale = _number(value, "eye_scale")

        if not 0.2 <= ratio <= 0.8:
            raise ConfigError("proportions.head_to_body_ratio must be between 0.2 and 0.8")
        if not 0.5 <= eye_scale <= 2.5:
            raise ConfigError("proportions.eye_scale must be between 0.5 and 2.5")

        return cls(head_to_body_ratio=ratio, eye_scale=eye_scale)


@dataclass(frozen=True, slots=True)
class FeatureConfig:
    """Feature switches consumed by later character-generation milestones."""

    facial_rig: bool
    body_rig: bool
    grooming: bool

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> FeatureConfig:
        return cls(
            facial_rig=_boolean(value, "facial_rig"),
            body_rig=_boolean(value, "body_rig"),
            grooming=_boolean(value, "grooming"),
        )


@dataclass(frozen=True, slots=True)
class CharacterConfig:
    """Immutable and validated description of one procedural character."""

    character_id: str
    display_name: str
    visual_style: str
    proportions: ProportionConfig
    features: FeatureConfig
    schema_version: int = 1

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> CharacterConfig:
        schema_version = value.get("schema_version")
        if schema_version != 1:
            raise ConfigError(f"Unsupported character config schema_version: {schema_version!r}")

        character_id = value.get("character_id")
        if not isinstance(character_id, str) or not re.fullmatch(
            r"[a-z0-9][a-z0-9_-]{1,63}", character_id
        ):
            raise ConfigError(
                "character_id must be 2-64 lowercase letters, digits, '_' or '-', "
                "and must start with a letter or digit"
            )

        display_name = value.get("display_name")
        if not isinstance(display_name, str) or not display_name.strip():
            raise ConfigError("display_name must be a non-empty string")
        if len(display_name.strip()) > 80:
            raise ConfigError("display_name must be at most 80 characters")

        visual_style = value.get("visual_style")
        if visual_style != "stylized_cinematic":
            raise ConfigError(
                "visual_style must currently be 'stylized_cinematic'; "
                "art direction presets are introduced incrementally"
            )

        proportions = _mapping(value, "proportions")
        features = _mapping(value, "features")

        return cls(
            character_id=character_id,
            display_name=display_name.strip(),
            visual_style=visual_style,
            proportions=ProportionConfig.from_mapping(proportions),
            features=FeatureConfig.from_mapping(features),
            schema_version=schema_version,
        )


def load_character_config(path: str | Path) -> CharacterConfig:
    """Load and validate a character JSON file."""

    config_path = Path(path)
    try:
        raw = json.loads(config_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ConfigError(f"Character config not found: {config_path}") from exc
    except json.JSONDecodeError as exc:
        raise ConfigError(
            f"Invalid JSON in {config_path} at line {exc.lineno}, column {exc.colno}: "
            f"{exc.msg}"
        ) from exc

    if not isinstance(raw, dict):
        raise ConfigError("Character config root must be a JSON object")

    return CharacterConfig.from_mapping(raw)


def _mapping(parent: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = parent.get(key)
    if not isinstance(value, Mapping):
        raise ConfigError(f"{key} must be a JSON object")
    return value


def _number(parent: Mapping[str, Any], key: str) -> float:
    value = parent.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ConfigError(f"{key} must be a number")
    result = float(value)
    if not math.isfinite(result):
        raise ConfigError(f"{key} must be finite")
    return result


def _boolean(parent: Mapping[str, Any], key: str) -> bool:
    value = parent.get(key)
    if not isinstance(value, bool):
        raise ConfigError(f"{key} must be a boolean")
    return value
