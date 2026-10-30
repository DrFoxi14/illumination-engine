# Development Guide

## Requirements

- Python 3.10 or newer for the pure-Python package and CI.
- Blender 4.5 LTS or newer. The renderer selects the EEVEE identifier exposed by the running version, so Blender 4.x and 5.x are supported. The automated headless scene build is pinned to Blender 4.5.15.
- Git.
- Node.js will be required when the Three.js viewer is introduced.

Blender's `bpy`, `bmesh`, and `mathutils` modules are supplied by Blender's own Python runtime. Do not add a normal `pip install bpy` step to the base developer setup.

## Python setup

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Run Blender-independent checks:

```bash
ruff check .
pytest -q
python -m compileall -q engine tests scripts
```

## Build Prototype 001

Run the generator inside Blender:

```bash
blender --background --factory-startup --python-exit-code 1 \
  --python scripts/build_character.py
```

The default build reads `characters/prototype_001/character.json` and creates the character from custom parametric meshes. No external base mesh is downloaded or imported.

CPU-only structural validation and silhouette renders:

```bash
blender --background --factory-startup --python-exit-code 1 \
  --python scripts/build_character.py -- \
  --output-dir outputs/validation \
  --silhouette-only
```

The silhouette-only mode uses Blender Workbench and deliberately skips the EEVEE color render. It is designed for headless CI and machines without a configured render GPU.

To build the scene and run geometry validation without rendering:

```bash
blender --background --factory-startup --python-exit-code 1 \
  --python scripts/build_character.py -- \
  --output-dir outputs/validation \
  --skip-render
```

Expected outputs:
- `outputs/validation/prototype_001.blend`
- `outputs/validation/validation_report.json`
- `outputs/validation/silhouette_front.png`
- `outputs/validation/silhouette_side.png`
- `outputs/validation/silhouette_three_quarter.png`

The default local EEVEE preview additionally writes `prototype_001_preview.png`. The first character presentation uses the static `mirror_selfie` pose and includes a phone prop when `phone_visible` is true. For a headless shaded preview, use `--color-only --preview-engine cycles --preview-samples 16`; this selects CPU Cycles and writes the same preview filename.

## Generation modules

- `engine/blender/geometry.py`: profile lofts, parallel-transport sweeps, watertight ellipsoid meshes, and material construction.
- `engine/blender/head.py`: head and jaw profile.
- `engine/blender/body.py`: torso, neck, limbs, hands, and feet.
- `engine/blender/skin.py`: applies anatomical subdivision, joins the anatomical components, and voxel-remeshes one continuous skin mesh.
- `engine/blender/face.py`: inset-style eyes, eyelids, creases, brows, nose, mouth, and ears.
- `engine/blender/hair.py`: layered swept fringe, face frames, flattened side/back hair clumps.
- `engine/blender/outfit.py`: clothing and footwear blockout with seam/hem details.
- `engine/blender/validation.py`: required object, coordinate, face-area, loose-geometry, and manifold checks.
- `engine/blender/character_builder.py`: scene assembly, phone prop, version-aware EEVEE selection, validation report, preview camera, lighting, and render passes.

## Runtime separation

The pure-Python core must not import `bpy`. Blender-specific modules are imported only inside Blender's bundled Python runtime.

The web viewer will be downstream from future Blender exports. Do not implement an independent second character model in Three.js.

## CI policy

The regular Python workflow runs linting, unit tests, and source compilation. A separate Blender workflow downloads the official Blender 4.5.15 LTS Linux archive, verifies its published SHA-256 checksum, builds the character headlessly, runs mesh integrity checks, and produces three Workbench silhouette renders. The Blender project, validation report, and images are uploaded as a short-lived workflow artifact.

That headless workflow validates actual scene construction and Workbench silhouette rendering, and attempts a low-sample CPU Cycles color preview as a best-effort step. It does not certify artistic quality or replace a final local EEVEE/Cycles look-development review.

## Generated files

Keep renders, temporary exports, caches, local environments, and downloaded third-party files out of version control. Commit source specifications, scripts, tests, and documentation only.

## Contribution discipline

- Keep modules focused and typed where practical.
- Validate input at system boundaries.
- Do not import `bpy` from pure-Python core modules.
- Add tests with each new deterministic behavior.
- Document Blender-specific behavior and version assumptions.
- Never mark a visual-quality milestone complete solely because CI is green.
