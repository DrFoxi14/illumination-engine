# Illumination Engine

An original procedural 3D character framework. Blender is the authoring and rendering engine; Python builds editable geometry; a Three.js viewer will later provide web-based inspection.

> **Project status:** P1 is in progress. The current direction generates the character's geometry from scratch. No downloaded humanoid base mesh or third-party character asset is required.
>
> **Art direction:** original, expressive, stylized cinematic characters using broad family-animation design principles. This independent project is not affiliated with or endorsed by Illumination, Universal, or any film studio.

## Architecture

- **Blender** owns editable geometry, materials, rigging, simulation, scene assembly, and final rendering.
- **Python** builds custom parametric surfaces and orchestrates character creation through Blender's `bpy` API.
- **Character geometry** is generated from authored profiles, swept surfaces, facial components, and sculptural hair clumps.
- **glTF/GLB** will be the interchange format for supported meshes, materials, skinning, morph targets, and animation clips.
- **Three.js / React Three Fiber** will be a downstream viewer, not a second authoring engine.
- **pytest and GitHub Actions** validate pure-Python contracts and Python source.

## Repository layout

```text
engine/
  core/                 Blender-independent configuration and validation
  blender/
    geometry.py         Parametric lofts, sweeps, ellipsoids, materials
    body.py             Custom torso, limbs, hands, and neck
    head.py             Custom head and jaw profile
    face.py             Eyes, eyelids, brows, nose, mouth, ears
    hair.py             Tapered volumetric hair clumps
    outfit.py           Custom top, shorts, socks, and slippers
    character_builder.py Scene assembly, camera, lights, render passes
characters/             Versioned declarative character specifications
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
| P1 | Original procedural character blockout | In progress; Blender render review required |
| P2 | Facial topology refinement, eyelid geometry, expression shape keys | Planned |
| P3 | Body rig, weights, corrective deformation | Planned |
| P4 | Hair refinement, materials, grooming | Planned |
| P5 | Animation tests and posing | Planned |
| P6 | GLB export and validation | Planned |
| P7 | Three.js viewer | Planned |

## Requirements

- Python 3.10+
- Blender 4.2+
- Git
- Node.js only when the web viewer is introduced

Set up the Blender-independent Python environment:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
pytest
ruff check .
```

Build Prototype 001:

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

The builder generates the body, head, face, hair, outfit, and studio scene directly in Blender. It writes an editable `.blend` file, a color preview, and front/side/three-quarter silhouette images under `outputs/prototype_001/`.

No Quaternius, MakeHuman, MPFB, downloaded character mesh, or third-party character asset is used by P1.

## Current P1 boundaries

P1 is a custom procedural blockout, not a finished feature-film character. The meshes are editable but are not yet a unified production topology. Facial and body rigs, shape keys, skin weights, cloth simulation, advanced groom simulation, selfie posing, GLB export, and the web viewer remain later milestones.

P1 is not accepted until the Blender scene has been rendered locally and the face, silhouette, hair, outfit, and intersections have been visually reviewed and refined.

## Project principles

1. Design the character's silhouette and face before adding micro-detail.
2. Build the geometry ourselves; do not substitute a generic game-ready base mesh.
3. Keep Blender as the source of truth.
4. Separate deterministic generation from rendering and web presentation.
5. Validate code, geometry, deformation, and artistic quality as separate gates.
6. Never claim studio-quality output from a technically successful script alone.

## License

No open-source license has yet been selected for this repository. Until one is added, standard copyright restrictions apply to original project code.
