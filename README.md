# Illumination Engine

An original procedural 3D character framework. Blender is the authoring and rendering engine; Python builds editable geometry; a Three.js viewer will later provide web-based inspection.

> **Project status:** P1 is in progress. The character is generated from custom geometry. No downloaded humanoid base mesh or third-party character asset is required.
>
> **Art direction:** original, expressive, stylized cinematic characters using broad family-animation design principles. This independent project is not affiliated with or endorsed by Illumination, Universal, or any film studio.

## Architecture

- **Blender** owns editable geometry, materials, rigging, simulation, scene assembly, and final rendering.
- **Python** builds custom parametric surfaces and orchestrates character creation through Blender's `bpy` API.
- **Character geometry** is generated from lofts, parallel-transport sweeps, facial components, and sculptural hair clumps.
- **Hair silhouette** keeps the long mass behind the shoulders, with shorter face-framing locks so the outfit remains readable from the front.
- **Unified skin** joins the custom head, torso, neck, limbs, hands, and feet, then voxel-remeshes them into one watertight anatomical surface.
- **glTF/GLB** will be the interchange format for supported meshes, materials, skinning, morph targets, and animation clips.
- **Three.js / React Three Fiber** will be a downstream viewer, not a second authoring engine.
- **pytest and GitHub Actions** validate pure-Python contracts, while a separate Blender job builds the scene and renders CPU-only silhouette reviews.

## Repository layout

```text
engine/
  core/                 Blender-independent configuration and validation
  blender/
    geometry.py         Parametric lofts, sweeps, ellipsoids, materials
    body.py             Custom torso, limbs, hands, and feet
    head.py             Custom head and jaw profile
    face.py             Eyes, eyelids, brows, nose, mouth, ears
    hair.py             Tapered volumetric hair clumps
    outfit.py           Custom top, shorts, socks, and slippers
    skin.py             Unified anatomical mesh and voxel remesh
    validation.py       Manifold, geometry, and required-object checks
    character_builder.py Scene assembly, camera, lights, render passes
characters/             Versioned declarative character specifications
scripts/                Blender CLI entry points
viewer/                 Three.js / React Three Fiber viewer (planned)
tests/                  Automated Python tests
docs/                   Architecture and development decisions
.github/workflows/      Python CI and headless Blender scene validation
```

## Development status

| Milestone | Scope | Status |
|---|---|---|
| P0 | Repository foundation, configuration contract, documentation, CI | Implemented |
| P1 | Original procedural character blockout and Blender scene validation | In progress; visual approval required |
| P2 | Facial topology refinement, eyelid geometry, expression shape keys | Planned |
| P3 | Body rig, weights, corrective deformation | Planned |
| P4 | Hair refinement, materials, grooming | Planned |
| P5 | Animation tests and posing | Planned |
| P6 | GLB export and validation | Planned |
| P7 | Three.js viewer | Planned |

## Requirements

- Python 3.10+
- Blender 4.5 LTS recommended (the CI scene build is pinned to Blender 4.5.15)
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

Build Prototype 001 with a full local preview:

```bash
blender --background --factory-startup --python-exit-code 1 \
  --python scripts/build_character.py
```

For a CPU-only geometry check with front, side, and three-quarter silhouette renders:

```bash
blender --background --factory-startup --python-exit-code 1 \
  --python scripts/build_character.py -- \
  --output-dir outputs/validation \
  --silhouette-only
```


For a shaded CPU Cycles color preview:

```bash
blender --background --factory-startup --python-exit-code 1 \\
  --python scripts/build_character.py -- \\
  --output-dir outputs/color \\
  --color-only \\
  --preview-engine cycles \\
  --preview-samples 16
```

To construct and validate the scene without rendering:

```bash
blender --background --factory-startup --python-exit-code 1 \
  --python scripts/build_character.py -- \
  --output-dir outputs/validation \
  --skip-render
```

The builder generates the body, head, face, hair, outfit, and studio scene directly in Blender. It writes an editable `.blend` file and a `validation_report.json`; render modes also write the corresponding preview images under the chosen output directory.

No Quaternius, MakeHuman, MPFB, downloaded character mesh, or third-party character asset is used by P1.

## Current P1 boundaries

P1 is a custom procedural blockout, not a finished feature-film character. The anatomical parts are now joined into one watertight remeshed skin surface, but this is not final animation topology. The face does not yet have production edge flow around the eyelids and mouth. Facial and body rigs, shape keys, skin weights, cloth simulation, advanced groom simulation, selfie posing, GLB export, and the web viewer remain later milestones.

The Blender integration workflow verifies the generated scene's required objects and closed mesh invariants, then produces CPU-only silhouette renders. It also attempts a low-sample Cycles CPU color preview as a best-effort visual artifact. This proves the scene can be constructed and rendered in Blender; it does not certify artistic quality. P1 still requires visual review and refinement of the face, silhouette, hair, clothing, and intersections.

## Project principles

1. Design the character's silhouette and face before adding micro-detail.
2. Build the geometry ourselves; do not substitute a generic game-ready base mesh.
3. Keep Blender as the source of truth.
4. Separate deterministic generation from rendering and web presentation.
5. Validate code, geometry, deformation, and artistic quality as separate gates.
6. Never claim studio-quality output from a technically successful script alone.

## License

No open-source license has yet been selected for this repository. Until one is added, standard copyright restrictions apply to original project code.
