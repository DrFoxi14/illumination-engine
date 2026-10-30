# Development Guide

## Requirements

- Python 3.10 or newer for the pure-Python package and CI.
- Blender 4.2 or newer for the current mesh generation and preview scripts.
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
blender --background --factory-startup --python scripts/build_character.py
```

Optional arguments:

```bash
blender --background --factory-startup --python scripts/build_character.py -- \
  --config characters/prototype_001/character.json \
  --output-dir outputs/prototype_001 \
  --skip-render
```

The default build reads `characters/prototype_001/character.json` and creates the character from custom parametric meshes. No external base mesh is downloaded or imported.

Expected outputs:
- `outputs/prototype_001/prototype_001.blend`
- `outputs/prototype_001/prototype_001_preview.png`
- `outputs/prototype_001/silhouette_front.png`
- `outputs/prototype_001/silhouette_side.png`
- `outputs/prototype_001/silhouette_three_quarter.png`

## Generation modules

- `engine/blender/geometry.py`: profile lofts, tapered swept meshes, ellipsoid meshes, and material construction.
- `engine/blender/head.py`: head and jaw profile.
- `engine/blender/body.py`: torso, neck, limbs, hands, and fingers.
- `engine/blender/face.py`: eyes, lids, brows, nose, mouth, and ears.
- `engine/blender/hair.py`: scalp cap and volumetric hair clumps.
- `engine/blender/outfit.py`: clothing and footwear blockout.
- `engine/blender/character_builder.py`: scene assembly, preview camera, lighting, and render passes.

## Runtime separation

The pure-Python core must not import `bpy`. Blender-specific modules are imported only inside Blender's bundled Python runtime.

The web viewer will be downstream from future Blender exports. Do not implement an independent second character model in Three.js.

## CI policy

GitHub Actions runs pure-Python linting, unit tests, and Python compilation. It does not install Blender or run 3D renders. Blender execution and visual inspection must run locally or on a dedicated Blender runner.

## Generated files

Keep renders, temporary exports, caches, local environments, and downloaded third-party files out of version control. Commit source specifications, scripts, tests, and documentation only.

## Contribution discipline

- Keep modules focused and typed where practical.
- Validate input at system boundaries.
- Do not import `bpy` from pure-Python core modules.
- Add tests with each new deterministic behavior.
- Document Blender-specific behavior and version assumptions.
- Never mark a visual-quality milestone complete solely because CI is green.
