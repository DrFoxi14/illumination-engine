# Character System Contract

## First target: Prototype 001

The first character is an original stylized cinematic character. It is a technical prototype, not a recreation of an existing film character.

The first deliverable is a reusable editable Blender character with:
- A coherent, readable silhouette and intentional proportions.
- Deliberate facial geometry and expressive eyes.
- A facial rig with a small, composable expression set.
- A body rig with clean deformation at tested joints.
- A material and grooming setup that can be rendered predictably.
- A documented GLB export for the web viewer.

## Configuration

Character specifications are versioned JSON documents stored under `characters/<character_id>/character.json`.

Version 1 currently defines:
- `schema_version`: configuration contract version.
- `character_id`: stable lowercase identifier.
- `display_name`: human-readable name.
- `visual_style`: currently `stylized_cinematic`.
- `proportions.head_to_body_ratio`: normalized high-level blockout control.
- `proportions.eye_scale`: relative eye-size control.
- `features.facial_rig`, `features.body_rig`, and `features.grooming`: requested feature switches.

These values are semantic controls, not direct Blender dimensions. Character-generation modules will interpret them consistently and document the mapping.

## Facial system

The intended facial architecture combines:
- Dedicated eye geometry with controllable gaze.
- Shape keys for broad facial deformation.
- Bone controls where they provide better animator ergonomics.
- Corrective shapes for deformations that cannot be represented cleanly by a single control.
- A composable expression layer rather than one mutually exclusive shape per emotion.

The initial expression set will be selected after the first face blockout and will be tested for combinations, not just isolated poses.

## Body system

The body rig will be introduced after the primary mesh and silhouette are stable. The acceptance checks will cover:
- Neutral rest pose and consistent scale.
- Joint naming and hierarchy.
- Skin-weight coverage.
- Shoulder, elbow, wrist, hip, knee, and ankle deformation.
- Repeatable walk-cycle preview only after the rig passes static checks.

## Grooming and materials

Grooming should be selected for the character's design: curves, clumps, cards, or a deliberately sculpted silhouette may be more appropriate than dense strand simulation. The choice must account for render quality, editability, simulation cost, and GLB preview limitations.

Material look-development will be measured in Blender final renders. The web viewer will use compatible approximations rather than promising pixel-identical output.

## Acceptance philosophy

Technical completeness and artistic approval are separate gates. A character is not accepted until the rig and export tests pass and its silhouette, face, materials, and test poses have been reviewed visually.
