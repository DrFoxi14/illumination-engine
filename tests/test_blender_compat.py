"""Tests for Blender render-engine identifier compatibility."""

from __future__ import annotations

import pytest

from engine.blender.compat import choose_eevee_engine


def test_uses_blender_5_eevee_identifier() -> None:
    assert choose_eevee_engine({"BLENDER_EEVEE", "BLENDER_WORKBENCH", "CYCLES"}) == (
        "BLENDER_EEVEE"
    )


def test_supports_blender_4_eevee_next_identifier() -> None:
    assert choose_eevee_engine({"BLENDER_EEVEE_NEXT", "BLENDER_WORKBENCH", "CYCLES"}) == (
        "BLENDER_EEVEE_NEXT"
    )


def test_prefers_current_identifier_when_both_are_available() -> None:
    assert choose_eevee_engine({"BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"}) == "BLENDER_EEVEE"


def test_reports_available_engines_when_eevee_is_missing() -> None:
    with pytest.raises(RuntimeError, match="BLENDER_WORKBENCH, CYCLES"):
        choose_eevee_engine({"CYCLES", "BLENDER_WORKBENCH"})
