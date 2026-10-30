# Illumination Engine

A procedural 3D character and animation framework with a Blender production core and a Three.js inspection viewer.

> **Project status:** Foundation (P0). The repository currently defines the architecture and development contracts. Character generation has not been implemented yet.
>
> **Art direction:** original, expressive, stylized cinematic characters. The project is independent and is not affiliated with or endorsed by Illumination, Universal, or any film studio.

## Architecture

- **Blender** is the authoritative source for character geometry, rigging, materials, simulation, and final rendering.
- **Python** drives deterministic scene and character generation through Blender's `bpy` API.
- **glTF/GLB** is the interchange format for supported meshes, materials, skinning, morph targets, and animation clips.
- **Three.js / React Three Fiber** provides an interactive web viewer. It is a preview and inspection layer, not a second authoring engine.
- **pytest and GitHub Actions** validate the Python foundation and future integration contracts.

See [docs/architecture.md](docs/architecture.md), [docs/character-system.md](docs/character-system.md), and [docs/development.md](docs/development.md).

## Repository layout

```text
engine/                 Python package and deterministic core
characters/             Declarative character specifications
viewer/                 Three.js / React Three Fiber viewer (planned)
scripts/                Local command-line entry points (planned)
tests/                  Automated tests
docs/                   Architecture and development decisions
.github/workflows/      Continuous integration
```

## Development status

| Milestone | Scope | Status |
|---|---|---|
| P0 | Repository foundation, configuration contract, documentation, CI | In progress |
| P1 | Character geometry and blockout | Planned |
| P2 | Facial geometry and eye system | Planned |
| P3 | Facial rig and expressions | Planned |
| P4 | Body rig | Planned |
| P5 | Materials and grooming | Planned |
| P6 | Animation tests | Planned |
| P7 | GLB export and validation | Planned |
| P8 | Three.js viewer | Planned |

## Quick start

Requirements:
- Python 3.10+
- Git
- Blender installed separately for future scene-generation commands
- Node.js for the future web viewer

Set up the Python development environment:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
pytest
ruff check .
```

Blender is intentionally not installed as a normal project dependency. The engine will run inside Blender's bundled Python environment when it needs `bpy`; the pure-Python core and tests must remain importable without Blender.

## Project principles

1. Build one excellent, reusable character before attempting short-film automation.
2. Keep the Blender scene as the source of truth.
3. Separate deterministic generation from rendering and web presentation.
4. Validate generated assets at geometry, rig, export, and visual levels.
5. Prefer small, testable modules over a monolithic generation script.

## License

No open-source license has been selected yet. Until one is added, the repository is public for inspection but standard copyright restrictions apply.
