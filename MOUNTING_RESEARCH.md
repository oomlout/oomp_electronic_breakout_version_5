# Board mounting research

The reusable agent is `.codex/agents/board-mounting-researcher.toml`, pinned to
`gpt-6-luna` with high reasoning. It works on **one exact catalogue board per
invocation**. A coordinator starts the next worker after the previous finishes;
this keeps context small and avoids concurrent edits to the generated module.

## Start in a new window

Open this repository and paste:

```text
Read MOUNTING_RESEARCH.md. Work through the remaining mounting-research queue.
Delegate each board, one at a time, to board_mounting_researcher (gpt-6-luna,
high reasoning). Give each worker exactly one actionable current catalogue ID.
Wait for it to finish; run verify-build for its board to check the saved evidence
and generated artifact hashes,
then start a fresh worker for the next board. Preserve existing work and IDs.
Use the helper's queue and per-board records as checkpoints. Skip blocked or
needs_review boards after recording the reason and continue with pending boards.
Do not infer missing geometry or ask me about routine choices. Keep going until
the actionable queue is exhausted, then report promoted/no-hole/blocked counts and
the precise cases needing review. Do not commit or push.
```

If the role is not available after opening the new window, spawn a `default`
agent with model `gpt-6-luna`, reasoning `high`, fresh context, and instruct it
to read the TOML's developer instructions plus this file. Do not silently
substitute a model. The pilots use this fallback because a role created during
an existing conversation is not in that conversation's initial role list.

## One-board checklist

1. Run `python tools/mounting_research.py queue --limit 5`. Use the assigned exact
   ID or the first actionable ID. This resumes in_progress/verified/no_holes/
   stale_promotion/awaiting_generation work before pending boards. `queue --status all --limit 200`
   shows all states. needs_review and blocked require deliberate reassignment.
2. Run `python tools/mounting_research.py seed ID`. Read that board's
   `mounting_context.json` and existing `source_file/ID/working.yaml` if present.
   Do not overwrite the existing research. New work goes in `mounting.yaml`.
3. Establish the exact carrier/product/revision using official product pages,
   manufacturer-linked hardware repositories and CAD filenames. Browse those
   sources; do not trust a search snippet or another board's name. Prefer a
   commit-pinned CAD URL. Reuse archived raw files after checking their identity.
   Save new evidence below `source_file/ID/mounting_evidence/` with its URL and
   actual acquisition date in notes. Use requests with a timeout for permitted
   public downloads; never bypass a browser denial. A successful HTTP response
   alone is not evidence: verify actual XML/PDF/page content and exact revision.
4. Register each existing/downloaded file, including identity evidence:

   **`--file` is relative to `source_file/ID/`, not to the repository.** For
   `source_file/ID/reference/board.brd`, pass `reference/board.brd`.

   ```powershell
   python tools/mounting_research.py register ID --file reference/board.brd --url 'https://raw.githubusercontent.com/MAKER/REPO/COMMIT/board.brd' --source-id cad --kind manufacturer_cad --locator 'Exact filename, revision, layer 20 and named mounting features'
   python tools/mounting_research.py register ID --file website.html --url 'https://MANUFACTURER/product/NUMBER' --source-id product --kind manufacturer_product --locator 'Product identity and carrier revision section'
   ```

   `register` hashes the local bytes and records registration time, not a
   fabricated download time. Preserve the original URL/date when reusing files.
5. For XML EAGLE, run:

   ```powershell
   python tools/mounting_research.py inspect-eagle source_file/ID/reference/board.brd
   python tools/mounting_research.py inspect-eagle source_file/ID/reference/board.brd --all-drills
   python tools/mounting_research.py eagle ID --source-id cad --holes 'H1:hole:1,H2:hole:1' --quarter-turn 0
   ```

   The short inspection lists drills >=1.8 mm; the full one lists all candidates.
   Inspect every relevant footprint/feature. Selection is explicit, never based
   solely on diameter or footprint naming. Plain holes and plated mounting pads
   are both possible; header drills, USB tabs and tooling holes may be unsuitable.
   `--holes ''` is an explicit no-hole candidate requiring full evidence review.
   Use Python `extract(ID, 'cad', [], 0)` if your shell drops empty arguments.
   EAGLE names containing `$` require **single-quoted PowerShell arguments**.
6. The CAD helper handles native mm, plain board outlines including wire arcs,
   centred coordinates and mirrored/rotated packages. Quarter turns are CCW:
   1 maps `(x,y)` to `(-y,x)`, with width and height swapped. Use 0 unless evidence
   or matching an existing board orientation requires rotation. It rejects
   footprint-defined or unsupported outlines instead of silently shrinking them.
   For KiCad, binary EAGLE, slots, unusual outlines or ambiguous revisions, use
   an exact dimensioned manufacturer drawing or mark needs_review. Do not use
   the older connector extractor as an automatic mounting authority.
7. Drawing fallback: set method `dimensioned_drawing`; fill board_size and each
   `{id, x_mm, y_mm, diameter_mm, source_id}`. Set geometry_source_id, cite the
   drawing page/figure/revision in the registered locator, and show every formula
   in derivation. For a bottom-left origin: `x = X - width/2`, `y = Y - height/2`.
   Convert inches by 25.4. Top-left drawing Y must be inverted. Do not measure
   pixels from perspective product photos. No drawing means unknown, not zero.
8. Review and fill `mounting.yaml`:
   - board_revision: exact carrier/version, including any limitations.
   - identity_source_ids: registered sources linking the exact product to CAD.
   - identity_evidence: concise explanation of that link, including filename.
   - reviewed_by: `gpt-6-luna`; all five review booleans true only after checking.
   - coordinate_system: keep the seeded canonical five fields unchanged. Put
     transform explanations in derivation/extraction, not extra frame keys.
   - For method eagle, retain the helper's complete mounting_holes dictionaries,
     including id/plated/package/source_id. Do not replace them with shortened
     hand-written copies; validation compares them with fresh CAD extraction.
   - conflicts: unresolved **mechanical** conflicts; move resolved explanations
     and unrelated electrical/chip-label conflicts into notes without erasing them.
   - status: `verified` with holes, `no_holes` with proven empty pattern;
   otherwise leave `in_progress` while working, or use `needs_review`/`blocked`
   when returning an unresolved case. Record attempted sources and gaps.
   - fit_status stays `generic_holder_not_physical_fit_tested`.
9. Run `preview ID` and visually inspect `mounting_preview.png`. Check top view,
   asymmetric placement, extent, diameters, hole count and screw choice against
   the raw CAD or dimensioned drawing. The preview is a bounding box, not a
   traced physical outline or proof of underside clearance.
10. Run `validate ID`, then `promote ID`, then `generate ID --stl`, then
    `verify-build ID` (all with
    `python tools/mounting_research.py`). These target only this board. Re-run
    promotion after any record edit. Report the outcome and stop this worker.

After three failed source avenues, save partial findings and attempts, flag the
precise review need and return. The coordinator moves on. Never solve uncertain
geometry by guessing. Do not rewrite helpers to force a board to pass.

## Standard holder and populate integration

```python
from mounting_geometry import standard_holder
geometry = standard_holder([25.4, 17.78], [
    {"x_mm": -10.16, "y_mm": 6.35, "diameter_mm": 2.5},
    # Include every actual hole, even asymmetric patterns.
])
# Or directly:
# working_scad_mounting_plate_default.get_base(
#     thing, board_size=[25.4, 17.78], mounting_holes=[...])
```

The only required geometry is board size and hole pattern **including drill
diameters**. Screw selection is a project design policy: largest supported
M2/M2.5/M3 screw with at least 0.2 mm diametral clearance. It is not a manufacturer
fastener recommendation. Unsupported small drills fail for custom review.
Existing width/height/XY-only callers retain their old screw settings.
Default plate thickness and board lift remain 3 mm. Underside components, pins,
cable access, screw heads and printed tolerances still need a physical fit review.

Promotion writes an explicit Python dictionary in
`working_oomp_populate_mounting_data.py`. Normal `working_oomp_populate.main()` and
the I2C `populate()` entry point apply it through
`working_oomp_populate_mounting.py`. Raw family definitions and IDs stay stable.
It supplies the standard holder only; the OOBB wire adapter needs a separate
collision review. Existing electrical pin coordinates keep their original frame;
mounting geometry has its own `mounting_coordinate_system`.
Confirmed no-hole boards receive no screw holder. Unknown boards are not promoted.

`generate ID --stl` runs the real source writer, targeted parts loader and SCAD
renderer, then OpenSCAD. STL output must be one positive-volume watertight solid
before it replaces the prior output. This uses the existing local OOMP/OOBB
Python libraries, PyYAML, matplotlib, trimesh and OpenSCAD on PATH.
Outputs are `parts/ID/3dpr.scad` and `.stl`. For no-hole
boards it writes metadata and reports that no screw holder was generated.
Old standard output for a confirmed no-hole board, and old OOBB wire-adapter
output replaced by this standard-only workflow, are retained under that part's
`mounting_superseded/` directory instead of left as current manufacturing files.
Queue state is derived from records, promoted record hashes and the
`mounting_build.json` generation receipt; no second queue file needs to be
synchronised. `stale_promotion` means the record changed after promotion and must
be reviewed/validated again. `awaiting_generation` resumes a board promoted before
an interruption or build failure. A successful generation receipt records hashes
of the generated artifacts and never claims a physical fit test.

## Why this workflow

Small, fresh, one-board tasks, explicit outputs and deterministic checks follow
the [official custom-agent guidance](https://learn.chatgpt.com/docs/agent-configuration/subagents).
EAGLE outline layers and mechanical/electrical drills are distinct in
[Autodesk's layer documentation](https://www.autodesk.com/products/fusion-360/blog/every-layer-explained-autodesk-eagle/).
The extractor follows the coordinates, rotation and drill fields documented by
[KiCad's EAGLE importer reference](https://dev-docs.kicad.org/en/import-formats/eagle/).
Human/model review is still required to identify which features serve as board
mounts and whether a CAD revision belongs to the named product.

See [the actual two-board Luna pilot report](research/mounting/PILOT_REPORT.md)
for results, remaining limitations and workflow corrections.

## Full pilot build and visual review

Run `python tools/build_mounting_pilots.py` to rebuild both pilots from their
validated records through populate, SCAD, watertight STL checks, coordinate
PNG/SVG/CSV, Blender angled/top-view sheets and linked part READMEs. The shared
OOBB presentation script is used from the sibling repository; pass
`--presenter PATH` if it lives elsewhere. `--readme-only` reuses the current
validated meshes and cached presentation images.

Open [the two-pilot review page](research/mounting/REVIEW.md) to inspect the
results. [full_build.json](research/mounting/full_build.json) records hashes of
the displayed files. Source evidence and hashed pilot outputs use `-text` Git
attributes so line-ending conversion cannot invalidate their receipts.
