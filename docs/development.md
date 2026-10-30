# Development Guide

## Requirements

- Python 3.10 or newer for the pure-Python package and CI.
- Git.
- Blender installed separately for future geometry and scene-generation milestones.
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
python -m compileall -q engine tests
```

## Running Blender later

When Blender automation is introduced, use Blender in background mode with a script entry point. The exact executable path is machine-specific; it should be configured locally, not committed.

Example pattern (after the corresponding script exists):

```bash
blender --background --factory-startup --python scripts/build_character.py
```

The command above is a future usage pattern. The build script is not part of P0 yet.

## CI policy

GitHub Actions runs pure-Python linting, compilation, and unit tests. Blender integration tests will be added only after the Blender runtime adapter exists. GPU rendering and artistic visual review remain local or on a dedicated render runner.

## Generated files

Keep renders, temporary exports, caches, and local environments out of version control. Commit source specifications, scripts, tests, documentation, and intentionally curated assets only.

## Contribution discipline

- Keep modules focused and typed where practical.
- Validate input at system boundaries.
- Do not import `bpy` from pure-Python core modules.
- Add tests with each new deterministic behavior.
- Document Blender-specific behavior and version assumptions.
- Never mark a visual-quality milestone complete solely because CI is green.
