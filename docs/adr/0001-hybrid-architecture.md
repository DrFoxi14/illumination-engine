# ADR 0001: Blender-authoritative hybrid architecture

- **Status:** Accepted
- **Date:** 2026-10-30
- **Decision owners:** Project maintainers

## Context

The project needs both high-quality desktop production features and an interactive way to inspect exported characters. Implementing character authoring independently in two different 3D systems would create duplicated logic and drift.

## Decision

Use Blender as the sole authoritative authoring and final-rendering environment. Use Python and Blender's `bpy` API for deterministic generation. Export supported runtime assets through glTF/GLB. Use Three.js with React Three Fiber as a downstream viewer.

## Consequences

Positive:
- One authoritative source project per character.
- Access to Blender modeling, rigging, materials, simulations, and Cycles rendering.
- Browser-based inspection without requiring Blender on the viewer machine.
- Pure-Python configuration and validation can run in ordinary CI.

Trade-offs:
- glTF cannot represent every Blender feature without conversion or baking.
- Web materials and lighting may differ from Cycles.
- Some procedural grooming and simulation require simplified or baked preview assets.
- Blender-dependent integration and visual tests need a suitable Blender runtime.

## Follow-up

Define a versioned export manifest and automated GLB validation when the character exporter is implemented.
