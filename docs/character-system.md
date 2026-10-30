# Character System Contract

## First target: Prototype 001

Prototype 001 is an original stylized cinematic character informed by the broad visual cues in the user-provided reference: long straight warm-blonde/light-brown hair with a side part, a dark navy short-sleeved top, light-grey shorts, light socks, and soft house slippers. The initial presentation includes a handheld phone in a mirror-selfie pose.

The reference image itself is not copied into the public repository. Only a concise, non-identifying art-direction specification is stored.

The reference does not clearly reveal the subject's facial features because the phone obscures much of the face. The prototype therefore uses an original, friendly stylized face. Its iris color is a design placeholder, not a claim about the reference subject.

## Current implementation boundary

P1 introduces a deterministic Blender geometry blockout:
- Head and torso volumes.
- Stylized limb and clothing volumes.
- Large readable eyes, brows, nose, and a simple smile line.
- Long hair silhouette and a small number of groom curves.
- Shoes/slippers, socks, and a phone prop.
- A simple preview camera, studio floor, and three-point lighting setup.

P1 does **not** implement a production-ready character:
- No facial or body armature is bound yet.
- No skin weights or corrective shapes exist yet.
- The expression features in the JSON are desired capabilities, not a claim that the facial rig is implemented.
- Hair curves are silhouette/groom guides, not strand-level simulated hair.
- The selfie pose is a static presentation pose, not a motion-captured or physically simulated pose.
- The preview renderer is a fast Blender preview; final look-development is a later milestone.

## Configuration

Character specifications are versioned JSON documents stored under `characters/<character_id>/character.json`.

Schema version 2 defines:
- `schema_version`: configuration contract version.
- `character_id`: stable lowercase identifier.
- `display_name`: human-readable name.
- `visual_style`: currently `stylized_cinematic`.
- `proportions.head_to_body_ratio`: high-level head scale control.
- `proportions.eye_scale`: relative eye-size control.
- `features.facial_rig`, `features.body_rig`, and `features.grooming`: requested future feature switches.
- `hair`: supported hair silhouette, part direction, base color, and highlight color.
- `face`: skin and iris palette. Iris color is a placeholder where the reference does not show the eyes.
- `outfit`: colors for the top, shorts, socks, slippers, and soles.
- `pose`: initial presentation pose and phone visibility.

Colors must be six-digit hexadecimal sRGB values. Proportion values are validated before Blender is invoked.

## Geometry and materials

The first blockout uses readable forms with clear silhouette separation. Geometry should remain editable and named by semantic part. Materials use a small, explicit palette so the character can be revised without changing geometry code.

The first pass intentionally favors an expressive readable face and recognizable hair/clothing silhouette over dense micro-detail. Topology refinement, facial loops, cloth construction, and advanced grooming are later tasks.

## Facial system

The planned facial architecture combines:
- Dedicated eye geometry with controllable gaze.
- Shape keys for broad facial deformation.
- Bone controls where they provide better animator ergonomics.
- Corrective shapes for deformations that cannot be represented cleanly by a single control.
- A composable expression layer rather than one mutually exclusive shape per emotion.

The initial expression set will be selected after the first face blockout and tested in combinations.

## Body system

The body rig will be introduced after the primary mesh and silhouette are stable. Acceptance checks will cover:
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
