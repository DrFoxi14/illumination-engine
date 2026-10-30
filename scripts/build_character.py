"""Blender CLI entry point for building Prototype 001 from a rigged base mesh."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _arguments() -> argparse.Namespace:
    blender_args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=PROJECT_ROOT / "characters" / "prototype_001" / "character.json",
        help="Path to a versioned character JSON specification.",
    )
    parser.add_argument(
        "--base-mesh",
        type=Path,
        default=os.environ.get("ILLUMINATION_BASE_MESH"),
        help=(
            "Path to the locally downloaded rigged .gltf/.glb humanoid base mesh. "
            "May also be set through ILLUMINATION_BASE_MESH."
        ),
    )
    parser.add_argument(
        "--body-object",
        default=None,
        help="Optional exact name of the body mesh inside the imported asset.",
    )
    parser.add_argument(
        "--armature-object",
        default=None,
        help="Optional exact name of the armature inside the imported asset.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "outputs" / "prototype_001",
        help="Directory for the .blend file and preview renders.",
    )
    parser.add_argument(
        "--skip-render",
        action="store_true",
        help="Build and save the Blender scene without producing PNG renders.",
    )
    parser.add_argument(
        "--skip-blend-save",
        action="store_true",
        help="Do not save a .blend project file.",
    )
    args = parser.parse_args(blender_args)
    if args.base_mesh is None:
        parser.error(
            "Pass --base-mesh PATH or set ILLUMINATION_BASE_MESH. "
            "Download the Quaternius Universal Base Characters Standard pack first."
        )
    return args


def main() -> int:
    args = _arguments()

    from engine.blender.character_builder import build_character
    from engine.core.config import load_character_config

    config = load_character_config(args.config)
    result = build_character(
        config,
        args.base_mesh,
        args.output_dir,
        body_object_name=args.body_object,
        armature_object_name=args.armature_object,
        render_preview=not args.skip_render,
        save_blend=not args.skip_blend_save,
    )

    print("Illumination Engine character build completed:")
    for key, value in result.items():
        print(f"  {key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
