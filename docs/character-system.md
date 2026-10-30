# Character System Contract

## First target: Prototype 001

Prototype 001 is an original stylized cinematic character informed by broad, non-identifying visual cues from the user-provided reference: long straight warm-blonde/light-brown hair with a side part, a dark navy short-sleeved top, light-grey shorts, light socks, and soft house slippers.

The reference image itself is not copied into the public repository. Only a concise art-direction specification is stored. The phone obscures much of the face, so the character uses an original, friendly stylized face rather than attempting an exact facial likeness.

The source pose is a mirror selfie. The P1 working mesh remains in the base asset's neutral rigging pose; the phone and selfie pose are postponed until a controlled animation stage.

## P1 implementation

P1 now uses a rigged female humanoid mesh from the externally downloaded Quaternius Universal Base Characters Standard pack. The asset is not bundled in this repository.

Current P1 operations:
- Import a rigged glTF/GLB base mesh.
- Automatically identify the largest suitable mesh and the primary armature, with explicit name overrides available.
- Use the imported body topology as the source for fitted clothing shells.
- Create a navy top, light-grey shorts, and light socks by duplicating the body mesh, selecting normalized face regions, and preserving the copied vertex groups and armature modifier.
- Add a Solidify modifier to the garments for thickness.
- Add a simple long-lock hair blockout if no hair object is present in the imported file.
- Add simple slipper blockout meshes from the imported foot bounds.
- Produce front, side, three-quarter silhouette renders and a color preview.

The clothing selector coordinates are normalized to the body's local bounds. This keeps the cut rules independent from the exact world height of the external base mesh.

## P1 limitations

P1 is not accepted until the external base asset has been tested in Blender and the generated renders have been visually reviewed.

The current code does not yet provide:
- Verified body-part selection for every possible Quaternius asset variant.
- Custom sculpting or production-quality retopology.
- A custom facial rig or an expressive shape-key library.
- Facial deformation or eye-gaze animation.
- Strand-level hair grooming or dynamics.
- Verified clothing deformation during motion.
- A mirror-selfie pose, phone prop, or animation.
- Final Cycles look-development, GLB export, or Three.js viewer.

The imported base rig is preserved, but its deformations are not declared validated until the character has been tested with real motion.

## Configuration

Character specifications are versioned JSON documents stored under `characters/<character_id>/character.json`.

Schema version 2 defines:
- `schema_version`: configuration contract version.
- `character_id`: stable lowercase identifier.
- `display_name`: human-readable name.
- `visual_style`: currently `stylized_cinematic`.
- `proportions.head_to_body_ratio`: high-level proportion intent.
- `proportions.eye_scale`: relative eye-size intent; used by future facial refinement.
- `features.facial_rig`, `features.body_rig`, and `features.grooming`: requested future capabilities.
- `hair`: style, part direction, base color, and highlight color.
- `face`: skin and iris palette. Iris color is a design placeholder because the reference does not reveal the eyes.
- `outfit`: colors for the top, shorts, socks, slippers, and soles.
- `pose`: current working pose. P1 uses a neutral standing pose; the selfie pose is a later animation target.

Colors must be six-digit hexadecimal sRGB values. Proportion values and color fields are validated before Blender is invoked.

## Geometry and garments

The base body is the source surface for fitted garments. A garment is created from a separate copy of the body mesh, then trimmed using a normalized face-region predicate. This preserves matching topology and copied vertex groups. The Solidify modifier adds fabric thickness.

This body-topology approach is suited to close-fitting pieces such as a short-sleeved top, shorts, and socks. It is not the correct method for loose skirts, flowing fabric, jackets with large gaps, or capes; those need separately modeled meshes or cloth workflows.

## Facial system

The planned facial architecture combines:
- Dedicated eye geometry with controllable gaze.
- Shape keys for broad facial deformation.
- Bone controls where they provide better animator ergonomics.
- Corrective shapes for deformations that cannot be represented cleanly by a single control.
- A composable expression layer rather than one mutually exclusive shape per emotion.

The initial expression set will be chosen after the imported face and first preview have been inspected.

## Body system

The external armature is retained. Acceptance checks will cover:
- Neutral rest pose and consistent scale.
- Joint naming and hierarchy.
- Weight coverage.
- Shoulder, elbow, wrist, hip, knee, and ankle deformation.
- Clothing shells following the body without visible clipping.
- One real walk or idle animation before declaring the rig valid.

## Grooming and materials

The current procedural hair consists of editable large curves and a cap mesh. It is a silhouette blockout, not a final groom. A dedicated hairstyle asset or a Blender hair-curves workflow can replace it later.

Material look-development will be measured in Blender renders. The web viewer will use compatible approximations rather than promising pixel-identical output.

## Acceptance philosophy

Technical completeness and artistic approval are separate gates. P1 is not complete until the generated mesh, clothing fit, hair silhouette, and preview renders have been reviewed in Blender.
