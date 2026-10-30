# Stylized Character Production Research

This document records the production workflow references used to shape P1. It does not import, redistribute, or depend on third-party character models.

## Blender Studio — Stylized Character Workflow

Reference: https://studio.blender.org/training/stylized-character-workflow/

The Blender Studio course page describes a film-character workflow built around:
1. Defining design goals and gathering visual references.
2. Sculpting the head and exploring head-design variations.
3. Sculpting body proportions, hands, feet, and clothing.
4. Testing expressions before committing to final facial topology.
5. Retopologizing the face and body with articulation in mind.
6. Refining hair and clothing topology.
7. Developing materials, lighting, turntables, and presentation renders.

The page lists dedicated chapters for head sculpting, body/outfit sculpting, expression tests, clean facial retopology, hair retopology, clothing retopology, shading, and final presentation. This is the process-level reference for how Illumination Engine separates design, geometry, expression, topology, and look development.

No Rain/Snow .blend files or character assets from that course are included in this repository.

## Implications for Illumination Engine

Code is useful for repeatable structure and controllable parameters, but it cannot decide by itself whether the character has appeal. The generator therefore creates an editable first pass and exposes parameters for head profile, proportions, eye scale, hair clumps, and palette.

The P1 review gate must include:
- Front, side, and three-quarter silhouette checks.
- Close-up inspection of eye placement, eyelid arcs, brow shape, nose, and mouth.
- Hair silhouette and intersections around shoulders.
- Clothing silhouette and intersections with body geometry.
- A proportion and expression review before adding fine detail.

After the design is accepted, facial retopology, shape keys, rigging, and deformation tests become separate technical tasks.

## Blender Python API

Reference: https://docs.blender.org/api/blender_python_api/

The generator uses Blender's mesh data, modifiers, curves, materials, and scene APIs. Blender remains the authoring environment and final-rendering source of truth.
