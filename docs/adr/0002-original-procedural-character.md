# ADR 0002: Original procedural character geometry

- **Status:** Accepted
- **Date:** 2026-10-30
- **Supersedes:** The external base-mesh approach used during the first P1 iteration.

## Context

Prototype 001 targets an original stylized cinematic character. A generic, externally supplied game-ready humanoid base mesh does not provide the intended character design or the distinctive head, facial proportions, silhouette, and hair shapes required by the art direction.

## Decision

Generate the character's body, head, face, hair, clothing, and footwear from original parametric geometry in Blender using this repository's Python modules.

The generator will use:
- Profile lofts for the head, torso, and garment volumes.
- Tapered swept meshes for limbs, fingers, facial contours, and hair clumps.
- Dedicated facial meshes for eyes, eyelids, brows, nose, lips, and ears.
- Explicitly art-directed proportions, palette, hairstyle, and outfit parameters.

No third-party character mesh is required or imported by P1.

## Consequences

Positive:
- The silhouette and head shape are directly controlled by the project.
- The project is not constrained by a generic base mesh or its art direction.
- All geometry is generated and editable in Blender.
- Character parameters can be tested and revised deterministically.

Trade-offs:
- Procedural geometry alone does not guarantee film-quality character appeal.
- The initial generated parts are not yet a unified production retopology.
- Facial/body rigging, deformation, and visual refinement require separate milestones.
- Local Blender renders and artistic review are mandatory.

## Validation

P1 is accepted only after the character is generated in Blender and reviewed from front, side, and three-quarter views, plus close-ups of the face and hair.
