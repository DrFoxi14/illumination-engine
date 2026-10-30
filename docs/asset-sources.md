# Asset Sources and Licensing

## Quaternius — Universal Base Characters

Official source: https://quaternius.com/packs/universalbasecharacters.html

The project uses the free Standard pack as an optional external input for Prototype 001. The pack page describes six male/female base characters in superhero, regular, and teen proportions, animation-friendly topology, a humanoid rig, and multiple hairstyle assets. The pack is released under CC0 1.0 and may be used in personal, educational, and commercial projects.

The source mesh is downloaded by the developer and kept outside this repository. Do not commit the downloaded archive or extracted binary assets here. This keeps the repository small and makes the provenance of the external input explicit.

The current build expects one rigged female full-body glTF or GLB file. The importer chooses the largest suitable mesh and the armature with the most bones by default. Exact object-name overrides are available if a particular asset variant needs them.

## Body-topology clothing workflow reference

Research reference: https://github.com/ChilyerStudiosLLC/blender-character-pipeline

That public MIT-licensed project documents a useful fitted-garment pattern: duplicate a rigged body mesh, retain faces in a clothing region, smooth the cut boundary, remove small islands, and add thickness. This repository implements its own smaller version of the technique; the reference is credited as a workflow design source, not vendored code.

## MPFB / MakeHuman alternative

MPFB is a free and open-source Blender human generator with parametric body controls, automatic rigging, procedural skin and eye materials, and a supporting asset library. Its source code is GPL-3.0-or-later, while the project's core assets are listed as CC0. It is not currently a dependency of Illumination Engine. It remains an alternative for future configurable human-base generation.

Official pages:
- https://extensions.blender.org/add-ons/mpfb/
- https://www.makehumancommunity.org/about/license.html

## Original project code

No open-source license has yet been selected for Illumination Engine itself. Until a license is added, the repository's original code is public for inspection but remains under standard copyright restrictions. Third-party asset licenses do not automatically license this repository's code.
