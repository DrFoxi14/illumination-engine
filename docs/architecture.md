# Architecture

## 1. System boundary

Illumination Engine is a hybrid procedural character framework with one authoritative 3D authoring system and one presentation system.

- **Blender** owns editable source geometry, rigging, material networks, simulation, scene assembly, and final-quality rendering.
- **Python** owns deterministic configuration, orchestration, validation, and Blender automation through `bpy`.
- **glTF/GLB** is the exchange boundary for features supported by the exporter and target viewer.
- **Three.js / React Three Fiber** loads exported assets for interactive inspection. It does not author or silently modify the Blender source.

The viewer is intentionally downstream from Blender. This prevents two competing definitions of the character.

## 2. Data flow

1. A versioned JSON character specification is loaded and validated by the pure-Python core.
2. A Blender runtime adapter translates the specification into scene operations.
3. Character modules generate geometry, materials, rigging, and animation data.
4. Blender saves the editable `.blend` source project.
5. An export stage produces GLB and a metadata manifest.
6. The viewer loads the GLB and exposes inspection controls for supported features.
7. Automated tests validate contracts; local visual review evaluates artistic quality.

## 3. Runtime separation

The Python package must remain importable without Blender. Modules that need `bpy` will live behind a Blender-specific runtime boundary and will only be imported or executed inside Blender's bundled Python runtime.

The first milestone establishes pure-Python configuration and tests. It does not install Blender into CI.

## 4. Asset interchange

GLB is the primary web-delivery format. The intended contract includes:

- Meshes and supported material properties.
- Skeletal skinning and animation clips.
- Morph targets for facial expressions when correctly exported.
- Asset metadata, stable identifiers, and export-version information.

Not every Blender feature maps perfectly to glTF. Hair curves, procedural nodes, cloth or particle simulations, advanced shaders, and Cycles-specific effects may require baking, conversion, simplified web representations, or omission from the preview asset. The Blender source remains authoritative.

## 5. Quality gates

- **Unit:** configuration validation and pure functions.
- **Integration:** Blender scene construction, rig checks, and export/import checks, introduced when the Blender runtime adapter exists.
- **Visual:** repeatable preview renders and human review of silhouette, materials, expressions, deformation, and motion.

A green test suite proves technical invariants, not that a character has studio-level artistic quality.

## 6. Performance strategy

Use deterministic low-cost blockouts first. Increase geometry density, grooming complexity, simulation quality, render samples, and output resolution only after the design is approved. Keep preview settings separate from final-render settings.

## 7. Repository boundaries

- `engine/`: Python package.
- `characters/`: declarative, versioned character specifications.
- `viewer/`: web presentation client, added in a later milestone.
- `scripts/`: local build, validation, and render commands.
- `tests/`: tests that should run without Blender wherever possible.
- `.github/workflows/`: CI automation.

Generated renders and temporary build output are not source files and are excluded from Git.
