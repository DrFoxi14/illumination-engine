# Illumination Engine

A procedural 3D character and animation framework with a Blender production core and a Three.js inspection viewer.

> **Project status:** P1 in progress. The Python foundation (P0) is implemented. P1 introduces the first deterministic stylized character blockout.
>
> **Art direction:** original, expressive, stylized cinematic characters inspired by broad family-animation conventions. This independent project is not affiliated with or endorsed by Illumination, Universal, or any film studio.

## Architecture

- **Blender** is the authoritative source for character geometry, rigging, materials, simulation, and final rendering.
- **Python** drives deterministic scene and character generation through Blender's `bpy` API.
- **glTF/GLB** is the interchange format for supported meshes, materials, skinning, morph targets, and animation clips.
- **Three.js / React Three Fiber** provides an interactive web viewer. It is a preview and inspection layer, not a second authoring engine.
- **pytest and GitHub Actions** validate the Python foundation and future integration contracts.

See [docs/architecture.md](docs/architecture.md), [docs/character-system.md](docs/character-system.md), and [docs/development.md](docs/development.md).

## Repository layout

```text
engine/
  core/                 Blender-independent configuration and validation
  blender/              Blender-specific character construction
characters/             Declarative character specifications
scripts/                Blender CLI entry points
viewer/                 Three.js / React Three Fiber viewer (planned)
tests/                  Automated Python tests
docs/                   Architecture and development decisions
.github/workflows/      Continuous integration
```

## Development status

| Milestone | Scope | Status |
|---|---|---|
| P0 | Repository foundation, configuration contract, documentation, CI | Implemented |
| P1 | Prototype 001 character geometry and blockout | In progress |
| P2 | Facial geometry refinement and eye system | Planned |
| P3 | Facial rig and expressions | Planned |
| P4 | Body rig and deformation | Planned |
| P5 | Materials and grooming refinement | Planned |
| P6 | Animation tests | Planned |
| P7 | GLB export and validation | Planned |
| P8 | Three.js viewer | Planned |

## Quick start

Requirements:
- Python 3.10+
- Blender 4.2+ (for the current EEVEE Next preview script)
- Git
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

Build the first character from Blender's bundled Python runtime:

```bash
blender --background --factory-startup --python scripts/build_character.py
```

The default build reads `characters/prototype_001/character.json` and writes a `.blend` file and PNG preview under `outputs/prototype_001/`. Both output folders are ignored by Git.

Optional command-line arguments belong after Blender's separator:

```bash
blender --background --factory-startup --python scripts/build_character.py -- \
  --config characters/prototype_001/character.json \
  --output-dir outputs/prototype_001 \
  --skip-render
```

Blender's `bpy` module is supplied by Blender itself. It is deliberately not installed as a normal pip dependency; pure-Python configuration and tests must remain importable without Blender.

## Project principles

1. Build one excellent, reusable character before attempting short-film automation.
2. Keep the Blender scene as the source of truth.
3. Separate deterministic generation from rendering and web presentation.
4. Validate assets at geometry, rig, export, and visual levels.
5. Prefer small, testable modules over a monolithic generation script.
6. Treat automated technical checks and artistic approval as separate gates.

## License

No open-source license has been selected yet. Until one is added, the repository is public for inspection but standard copyright restrictions apply.
