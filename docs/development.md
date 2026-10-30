# Development Guide

## Requirements

- Python 3.10 or newer for the pure-Python package and CI.
- Blender 4.2 or newer for the current build scripts.
- Git.
- A locally downloaded, rigged Quaternius Universal Base Characters Standard female mesh in glTF/GLB format.
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

Run Blender-independent checks:

```bash
ruff check .
pytest -q
python -m compileall -q engine tests scripts
```

## Download the external base mesh

Use the official [Quaternius Universal Base Characters](https://quaternius.com/packs/universalbasecharacters.html) page and download the Standard pack. Extract it outside this repository. Select the female full-body glTF/GLB asset that includes a humanoid armature.

The asset is deliberately not committed to Git. The pack is CC0; the source code and asset provenance are documented in [asset-sources.md](asset-sources.md).

## Build Prototype 001

```bash
blender --background --factory-startup --python scripts/build_character.py -- \
  --base-mesh "/absolute/path/to/female_full_body.gltf"
```

The importer auto-selects the largest suitable mesh and the armature with the most bones. When the imported asset has ambiguous names, pass explicit selectors:

```bash
blender --background --factory-startup --python scripts/build_character.py -- \
  --base-mesh "/absolute/path/to/female_full_body.gltf" \
  --body-object "ExactBodyObjectName" \
  --armature-object "ExactArmatureObjectName"
```

Alternative: set `ILLUMINATION_BASE_MESH` in your shell and omit `--base-mesh`.

The build writes:
- `outputs/prototype_001/prototype_001.blend`
- `outputs/prototype_001/prototype_001_preview.png`
- `outputs/prototype_001/silhouette_front.png`
- `outputs/prototype_001/silhouette_side.png`
- `outputs/prototype_001/silhouette_three_quarter.png`

Use `--skip-render` to generate and save the scene without PNG renders.

## Current character build stages

1. Import a rigged external humanoid mesh.
2. Identify the main body and armature.
3. Create fitted clothing shells by trimming a duplicate of the body's topology.
4. Preserve inherited vertex groups and append a fabric Solidify modifier.
5. Add a stylized long-lock hair blockout if the imported asset has no hair object.
6. Create simple slipper blockout meshes.
7. Produce silhouette and color preview renders.

This is still a blockout. The first local render must be reviewed from front, side, and three-quarter views before P1 is accepted.

## Runtime separation

The pure-Python core must not import `bpy`. Blender-specific modules are imported only inside Blender's bundled Python runtime.

The web viewer is downstream from future Blender exports. Do not implement an independent second character model in Three.js.

## CI policy

GitHub Actions runs pure-Python linting, compilation, and unit tests. It does not install Blender, download the Quaternius asset, or run 3D renders. Blender integration checks and visual review must run locally or on a dedicated Blender runner.

## Generated files

Keep renders, temporary exports, caches, local environments, and third-party base assets out of version control. Commit source specifications, scripts, tests, and documentation only.

## Contribution discipline

- Keep modules focused and typed where practical.
- Validate input at system boundaries.
- Do not import `bpy` from pure-Python core modules.
- Add tests with each new deterministic behavior.
- Document Blender-specific behavior and version assumptions.
- Never mark a visual-quality milestone complete solely because CI is green.
