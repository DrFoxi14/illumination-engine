# Architecture

## 1. System boundary

Illumination Engine is a hybrid procedural character framework with one authoritative 3D authoring system and one presentation system.

- **Blender** owns editable source geometry, rigging, material networks, simulation, scene assembly, and final-quality rendering.
- **Python** owns deterministic configuration, orchestration, validation, and Blender automation through `bpy`.
- **External base assets** may provide animation-friendly topology and a humanoid armature. They are referenced by local path and are not committed to the source repository.
- **glTF/GLB** is the exchange boundary for features supported by the exporter and target viewer.
- **Three.js / React Three Fiber** loads future exported assets for interactive inspection. It does not author or silently modify the Blender source.

The viewer is intentionally downstream from Blender. This prevents two competing definitions of the character.

## 2. Character data flow

1. A versioned JSON character specification is loaded and validated by the pure-Python core.
2. Blender imports a user-supplied, license-compatible rigged base mesh.
3. The importer identifies the body mesh and armature, with optional explicit object-name overrides.
4. Normalized region rules define fitted garment areas independently of the asset's absolute height.
5. Blender duplicates body topology to create fitted clothing, preserving the source vertex groups and armature modifier.
6. Grooming and footwear modules add editable blockout geometry.
7. Blender creates silhouette and color preview renders and saves the editable `.blend` source.
8. Future stages add facial deformation, animation validation, GLB export, and the Three.js viewer.

## 3. Runtime separation

The Python package must remain importable without Blender. Modules that need `bpy`, `bmesh`, or `mathutils` live behind a Blender-specific runtime boundary and only run inside Blender's bundled Python runtime.

CI tests the pure-Python configuration, normalized garment-region rules, and Python syntax. CI does not download third-party models or run Blender renders.

## 4. Asset interchange

GLB is the planned web-delivery format. The intended contract includes:
- Meshes and supported material properties.
- Skeletal skinning and animation clips.
- Morph targets for facial expressions when correctly exported.
- Asset metadata, stable identifiers, and export-version information.

Not every Blender feature maps perfectly to glTF. Hair curves, procedural nodes, cloth or particle simulations, advanced shaders, and Cycles-specific effects may require baking, conversion, simplified web representations, or omission from the preview asset. The Blender source remains authoritative.

## 5. Quality gates

- **Unit:** configuration validation, normalized garment selectors, and pure functions.
- **Integration:** Blender import, body identification, topology garment construction, rig checks, and export/import checks.
- **Visual:** repeatable front/side/three-quarter silhouette renders plus a color preview and human review of silhouette, garment fit, face, materials, and hair.

A green test suite proves technical invariants, not that a character has studio-level artistic quality. P1 cannot be accepted without local Blender renders and visual review.

## 6. Performance strategy

Start with the supplied animation-friendly base topology. Keep clothing selectors simple and deterministic. Increase geometry density, grooming complexity, simulation quality, render samples, and output resolution only after the silhouette and base proportions are approved. Keep preview settings separate from final-render settings.

## 7. Repository boundaries

- `engine/`: Python package.
- `characters/`: declarative, versioned character specifications.
- `viewer/`: web presentation client, added in a later milestone.
- `scripts/`: local build, validation, and render commands.
- `tests/`: tests that should run without Blender wherever possible.
- `.github/workflows/`: CI automation.
- `docs/asset-sources.md`: third-party asset provenance and license notes.

Downloaded source meshes, generated renders, and temporary build output are not source files and are excluded from Git.
