# Illumination Engine

A procedural 3D character and animation framework with a Blender production core and a Three.js inspection viewer.

> **Project status:** P1 in progress. The Python foundation (P0) is implemented. P1 now uses an externally supplied rigged humanoid mesh as the topology source for a stylized character blockout.
>
> **Art direction:** original, expressive, stylized cinematic characters inspired by broad family-animation conventions. This independent project is not affiliated with or endorsed by Illumination, Universal, or any film studio.

## Architecture

- **Blender** is the authoritative source for character geometry, rigging, materials, simulation, and final rendering.
- **Python** drives deterministic scene and character generation through Blender's `bpy` API.
- **External base mesh** supplies animation-friendly body topology and a humanoid armature. The asset is downloaded locally and is not committed to this repository.
- **Body-topology clothing** creates fitted garment shells from the base body's surface and inherits the body's vertex groups.
- **glTF/GLB** is the future exchange format for supported meshes, materials, skinning, morph targets, and animation clips.
- **Three.js / React Three Fiber** will provide an interactive downstream viewer.

See [docs/architecture.md](docs/architecture.md), [docs/character-system.md](docs/character-system.md), [docs/development.md](docs/development.md), and [docs/asset-sources.md](docs/asset-sources.md).

## Repository layout

```text
engine/
  core/                 Blender-independent configuration and clothing-region rules
  blender/              Base-mesh import, topology garments, grooming, footwear, scene build
characters/             Declarative character specifications
scripts/                Blender CLI entry points
viewer/                 Three.js / React Three Fiber viewer (planned)
tests/                  Automated Python tests
docs/                   Architecture, character contract, and asset provenance
.github/workflows/      Continuous integration
```

## Development status

| Milestone | Scope | Status |
|---|---|---|
| P0 | Repository foundation, configuration contract, documentation, CI | Implemented |
| P1 | Asset-backed Prototype 001 geometry and blockout | In progress; local render review required |
| P2 | Facial geometry refinement and eye system | Planned |
| P3 | Facial rig and expressions | Planned |
| P4 | Body deformation and animation validation | Planned |
| P5 | Materials and grooming refinement | Planned |
| P6 | Animation tests | Planned |
| P7 | GLB export and validation | Planned |
| P8 | Three.js viewer | Planned |

## Required base asset

P1 uses the **Universal Base Characters** pack by Quaternius. The Standard pack includes female and male humanoid bases, animation-friendly topology, and humanoid rigs. The assets are released under CC0.

1. Open the [official Universal Base Characters page](https://quaternius.com/packs/universalbasecharacters.html).
2. Download the free Standard pack and extract it locally.
3. Select the female full-body `.gltf` or `.glb` base mesh from the pack.
4. Keep the downloaded asset outside this Git repository. Pass its absolute path to the build command.

The importer selects the largest suitable mesh by default. If the pack's object names or structure differ, use `--body-object` and `--armature-object` to select the exact objects.

See [docs/asset-sources.md](docs/asset-sources.md) for provenance and licensing notes.

## Quick start

Requirements:
- Python 3.10+
- Blender 4.2+
- Git
- Quaternius Universal Base Characters Standard pack (downloaded separately)
- Node.js only when the web viewer is introduced

Set up the Blender-independent Python development environment:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
pytest
ruff check .
```

Build Prototype 001 from Blender's bundled Python runtime:

```bash
blender --background --factory-startup --python scripts/build_character.py -- \
  --base-mesh "/absolute/path/to/female_full_body.gltf"
```

Optional arguments:

```bash
blender --background --factory-startup --python scripts/build_character.py -- \
  --base-mesh "/absolute/path/to/female_full_body.gltf" \
  --body-object "ExactBodyObjectName" \
  --armature-object "ExactArmatureObjectName" \
  --output-dir outputs/prototype_001 \
  --skip-render
```

You can also set `ILLUMINATION_BASE_MESH` instead of passing `--base-mesh`.

The build produces:
- An editable `.blend` source project.
- A color preview render.
- Front, side, and three-quarter silhouette renders for review.

All generated files are written under `outputs/` and ignored by Git.

Blender's `bpy` module is supplied by Blender itself. It is deliberately not installed as a normal pip dependency; pure-Python configuration, clothing-region rules, and tests remain importable without Blender.

## Current P1 boundaries

P1 imports and preserves the base humanoid armature, builds fitted top/shorts/socks from body topology, adds simple slippers, and creates an editable large-lock hair blockout if the imported asset has no hair object.

P1 does **not** yet claim:
- Production facial or body deformation validation.
- A custom facial rig or expressive shape-key library.
- Strand-level hair grooming or simulation.
- A selfie pose, phone prop, or animation.
- Cloth simulation, final Cycles look-development, GLB export, or the web viewer.

The local render and silhouette review are required before P1 can be accepted.

## Project principles

1. Use high-quality, license-compatible starting assets where they improve topology and rigging.
2. Keep Blender as the source of truth.
3. Separate deterministic generation from rendering and web presentation.
4. Validate assets at geometry, rig, export, and visual levels.
5. Treat automated technical checks and artistic approval as separate gates.
6. Keep third-party assets and generated renders out of Git unless there is a specific reason and permission to include them.

## License

No open-source license has been selected for this repository yet. Until one is added, standard copyright restrictions apply to original project code. Third-party assets remain under their own licenses; see [docs/asset-sources.md](docs/asset-sources.md).
