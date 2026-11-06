# Presentation

AI-generated images and instructions. Errors possible.

The part pages show the existing mounting-plate STLs. Each sheet contains an angled view, a top view and the measured mesh envelope. Electronic boards are listed separately in the parts table.

## Rebuild

Install the [OOBB catalogue tools](https://github.com/oomlout/oomlout_oobb_version_5/blob/main/presentation/CATALOGUE.md). Add the OOBB base repository to PATH.

From a part folder:

```bat
oobb-present
```

From this repository root:

```bat
oobb-present --all
```

The batch uses Git-tracked catalogue records. New local records require `--all --include-untracked`. Generated READMEs preserve text outside their marked block. Optional part-level `presentation/config.json` stores reviewed titles, hardware, installation actions and sources.

## Source notes

- `3dpr.stl` is the default mounting plate; `working_oobb.stl` is the OOBB wire-holder mounting plate. The meshes are rendered unchanged.
- Board dimensions and `md5_6_alpha` codes come from each `working.yaml`. Codes link to that record, not to an unverified URL shortener. Printed plate rows link directly to STLs.
- Plate dimensions are measured mesh bounds. The board envelope is separate. Matching envelopes do not establish board fastening compatibility.
- The two plates are alternatives. No wire holder, electronic board or unspecified fastener is added to the renders. Records without CAD get reference pages.
- Public text is the shortened second pass. Full metadata stays in `working.yaml`; render hashes, dimensions and source paths are in each presentation manifest.
- The Pico example uses code `1owcj`, verified against its public GitHub record on 2026-11-06. [Raspberry Pi](https://www.raspberrypi.com/products/raspberry-pi-pico/) confirms its 21 × 51 mm envelope. The legacy record does not specify board mounting holes or fixing hardware.
- Legacy `link_main` fields point at an older repository. Generated pages use relative links to the current catalogue instead.

## Agent handoff

Read [the reusable rules](https://github.com/oomlout/oomlout_oobb_version_5/blob/main/presentation/CATALOGUE.md) before extending the renderer. Source scripts live in the OOBB base repository; do not fork a renderer into every part folder. Cache keys combine the source mesh and renderer hashes. Use `--force` after changes to Blender or its rendering environment.

Only files belonging to this presentation build are included in its sync. Existing uncommitted catalogue research, source generators and new part records are separate work.

## Build review

Built on 2026-11-06 with Python 3.12.2 and Blender 5.2.2 LTS: 67 part pages, 134 image sheets and 18 unique source meshes. The [audit record](qa.json) records library versions and the identical second rebuild. Source hashes, catalogue codes, PNG copies and all relative README links passed the read-only audit.

The synced Pico example was inspected in GitHub at desktop and 420 px widths. Both images loaded at 1600 × 1000; the STL and alpha-code links resolved to the intended files. The review shortened the printed-part names and replaced repeated quantity wording with a single instruction above the table. GitHub scrolls the table horizontally at narrow widths.
