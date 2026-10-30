# Development Guide

## Requirements

- Python 3.10 or newer for the pure-Python package and CI.
- Blender 4.2 or newer for the current EEVEE Next preview builder.
- Git.
- Node.js will be required when the Three.js viewer is introduced.

Blender's `bpy` module is supplied by Blender's own Python runtime. Do not add a normal `pip install bpy` step to the base developer setup.

## Python setup

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Run checks:

```bash
ruff check .
pytest -q
python -m compileall -q engine tests scripts
```

## Build Prototype 001

Run the character builder inside Blender:

```bash
blender --background --factory-startup --python scripts/build_character.py
```

The default configuration is `characters/prototype_001/character.json`. The default output directory is `outputs/prototype_001/`.

Useful options:

```bash
blender --background --factory-startup --python scripts/build_character.py -- --skip-render
blender --background --factory-startup --python scripts/build_character.py -- \
  --config characters/prototype_001/character.json \
  --output-dir outputs/prototype_001
```

The builder creates a static geometry blockout, a simple studio scene, a saved `.blend` source, and optionally a PNG preview. It does not create a production rig or character animation yet.

## Runtime separation

The pure-Python configuration package must not import `bpy`. Blender-specific modules are imported only inside Blender's bundled Python runtime.

The web viewer is downstream from Blender exports. Do not implement an independent second character model in Three.js.

## CI policy

GitHub Actions runs pure-Python linting, compilation, and unit tests. The current workflow does not install Blender and does not run 3D renders. Blender integration tests and deterministic scene inspection will be added when a suitable runtime is defined. Artistic visual review remains a separate gate.

## Generated files

Keep renders, temporary exports, caches, and local environments out of version control. Commit source specifications, scripts, tests, documentation, and intentionally curated assets only.

## Contribution discipline

- Keep modules focused and typed where practical.
- Validate input at system boundaries.
- Do not import `bpy` from pure-Python core modules.
- Add tests with each new deterministic behavior.
- Document Blender-specific behavior and version assumptions.
- Never mark a visual-quality milestone complete solely because CI is green.
