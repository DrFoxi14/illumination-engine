"""Blender CLI entry point for building the original Prototype 001 character."""

from __future__ import annotations

import argparse
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
        help="Path to the versioned character JSON specification.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "outputs" / "prototype_001",
        help="Directory for the .blend file and preview renders.",
    )
    render_group = parser.add_mutually_exclusive_group()
    render_group.add_argument(
        "--skip-render",
        action="store_true",
        help="Build and save the scene without rendering PNG previews.",
    )
    render_group.add_argument(
        "--silhouette-only",
        action="store_true",
        help="Render front/side/three-quarter Workbench silhouettes without a color render.",
    )
    render_group.add_argument(
        "--color-only",
        action="store_true",
        help="Render the shaded color preview without silhouette images.",
    )
    parser.add_argument(
        "--preview-engine",
        choices=("eevee", "cycles"),
        default="eevee",
        help="Renderer for the shaded color preview.",
    )
    parser.add_argument(
        "--preview-samples",
        type=int,
        default=16,
        help="Cycles CPU preview samples (1-128); ignored by EEVEE.",
    )
    parser.add_argument(
        "--skip-blend-save",
        action="store_true",
        help="Do not save a .blend project file.",
    )
    return parser.parse_args(blender_args)


def main() -> int:
    args = _arguments()

    from engine.blender.character_builder import build_character
    from engine.core.config import load_character_config

    config = load_character_config(args.config)
    result = build_character(
        config,
        args.output_dir,
        render_preview=not args.skip_render and not args.color_only,
        render_color_preview=not args.skip_render and not args.silhouette_only,
        render_engine=(
            "CYCLES" if args.preview_engine == "cycles" else "EEVEE"
        ),
        preview_samples=args.preview_samples,
        save_blend=not args.skip_blend_save,
    )

    print("Illumination Engine original procedural character build completed:")
    for key, value in result.items():
        print(f"  {key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
