# M6 mounting layouts

AI-generated images and instructions. Errors possible.

## Geometry

| Layout | OOBB mounting edges | Outline |
| --- | --- | --- |
| Full wrap | All four | Full rectangle |
| Two short sides | Opposing short edges | Trim unused long-edge margins |
| One long side | Positive long edge | Trim the other margins |

Apply all three layouts to each available standard and wire-holder plate. Determine short and long edges from PCB dimensions. For square boards, short edges are ±Y and the single long edge is +X. Landscape boards use ±X and +Y respectively.

- M6 bore: Ø6.5 mm through the plate.
- M6 grid: 15 mm pitch. Retain optional empty M3 half-grid holes.
- Head/nut space: Ø13 mm clear of the PCB outline and printed support posts.
- Outer M6 centres: 7 mm from the plate edge.
- Trimmed margins: retain the PCB outline plus 3 mm, support-post radius plus 1.5 mm, at least two tangential grid stations and each 44 mm wire-holder attachment footprint.
- Preserve PCB post positions, fastening holes, cable openings and plain M3 adapter holes. Do not restore raised hex-pocket collars.

The Ø13 mm envelope is clear space for a head or nut above the plate, not a nut-sized through-hole or captive pocket. Small wire-holder variants may retain the full outline where their attachment footprint requires it. Comparison views fit each part independently; use the printed dimensions to compare size.

## Hardware evidence

Reviewed 2026-11-06:

- [Accu M6 DIN 933 hex bolt](https://www.accu.co.uk/full-thread-hexagon-bolts/18865-SEBF-M6-10-A2): 10 mm spanner size.
- [HPC DIN 934 hex nut dimensions](https://shop.hpceurope.com/pdf/gbPDFauto/SHN.pdf): M6, 10 mm across flats.
- A regular 10 mm across-flats hexagon spans approximately 11.55 mm across corners. Ø13 mm is the selected design allowance, not a quoted standard tolerance.
- OOBB's `radius_m6` for `3dpr` is 3.25 mm. Actual STL cross-sections are checked independently of manifest labels.

Bolt length and quantity depend on the mating assembly. Do not invent a hardware code or add unreviewed screws to the parts list. Board codes link to their exact catalogue records.

## Build

From the repository root:

```bat
python presentation/scripts/build_mounting_variants.py
oobb-present --all
python presentation/scripts/sync_mounting_previews.py
python presentation/scripts/audit_mounting_variants.py
python C:\gh\oomlout_oobb_version_5\presentation\scripts\verify_catalogue.py .
```

Use `--part <folder-id>` on the CAD command for one example, then run `oobb-present` in that part folder. Add the OOBB base folder to PATH for the batch command.

`mounting_layouts.py` plans bounds and hole positions. The CAD builder reads saved `thing.yaml` and `working_oobb_thing.yaml`, writes six or three STL/SCAD pairs and `mounting_variants.json`. Full-wrap filenames retain existing links. Cache keys deduplicate identical SCAD. The mesh audit measures 24 radial intersections per M6 bore and checks watertightness, volume, clearance and compact bounds.

The base catalogue tool reads the variant manifest and produces individual sheets, family comparison images and one linked parts table. Its cache includes mesh and renderer hashes. The sync script updates existing tracked navigation copies from canonical part folders. Compact downloads remain in canonical folders.

Keep public copy short: one AI notice, one clearance line, Parts, Installation and Files. Keep calculations here. Do not infer board compatibility from its envelope or add fastening instructions without reviewed mounting data.
