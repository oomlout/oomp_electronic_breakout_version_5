# I2C part researcher: operating instructions

This is the detailed runbook for `i2c_part_researcher`. It is deliberately explicit
so a smaller model can complete one contained board at a time with little prior
conversation context. Use it with [RESEARCH_SCHEMA.md](RESEARCH_SCHEMA.md) and
[PILOT_LESSONS.md](PILOT_LESSONS.md).

## Objective and scope

Create a useful, auditable research folder for every **existing I2C peripheral**:

```text
source_file/<EXACT_PART_ID>/
  working.yaml                      collected facts and evidence manifest
  website.html                      exact HTTP copy of the default website
  website.txt                       searchable extracted text
  website.links.json                link inventory from that saved response
  reference/
    guide_pinouts.html              relevant guide pages, with text/link derivatives
    chip_datasheet.pdf              actual chip datasheet if available
    carrier.brd                     exact matching CAD, if available
    carrier.sch                     matching schematic, if available
    cad_summary.yaml                optional derived geometry/contact inventory
```

Filenames below `reference/` can be more descriptive than the example. Never use
`downloads/`: this repository ignores directories with that name. Save source
files as evidence, not as executable programs to run. Do not execute anything
obtained from a research website.

The queue consists of **28 boards** from `working_oomp_populate_i2c.py`. It excludes
the analog-only Adafruit ADXL335, all microcontroller boards, and AliExpress.
Two reviewed pilots are already finished. Do not redo completed pilots just to
make them resemble a new board. All remaining work is one board per iteration.

The authoritative catalogue remains the populate Python. This research pass
writes `source_file/<id>/working.yaml`, not `definition.yaml`, `parts_source` or
`parts`. It does not regenerate the catalogue or change IDs. Keep the existing
taxonomy values even when the new research resolves previously unknown size.
The user requires manufacturer at slot 14 and part number at slot 15.

## Start a run

Work from the repository root (`C:\gh\oomp_electronic_breakout_version_5` on the
current machine). Commands also resolve their own import/root paths.

```powershell
python tools/i2c_part_research.py queue
```

Read one queue entry and copy its complete `part_id` exactly. Do not reconstruct
the ID from a product name. Prefer a pending entry; resume a partial/in-progress
entry if assigned. Completed means the research pass was finished, not that all
engineering facts are known or the hardware was tested.

```powershell
python tools/i2c_part_research.py seed --part-id EXACT_PART_ID
```

The seed helper creates a research record without inventing data and preserves
an existing working.yaml. Read it before editing. Its original catalogue
identity is useful context, but the initial claims are research leads, not new
independent evidence.

## Inspect and archive the default website

1. Open the queue's `default_website` in the **in-app browser**, following that
   tool's initialization/documentation rules. Verify the manufacturer, product
   number and carrier variant in the visible page. A search-result snippet alone
   is insufficient. Use the official product page as the default when it works.
2. If the page redirects, record the final URL. If the product page is gone,
   look for an official guide for the **same** board. Keep the original attempted
   URL and explain why the replacement is the default. A similar board is not a
   replacement evidence source for physical details.
3. Save the allowed public URL with the archive helper:

```powershell
python tools/i2c_part_research.py capture --part-id EXACT_PART_ID --source-id product_page --kind product_page --url "EXACT_PUBLIC_URL" --filename website.html
```

4. Read the resulting `website.txt`. Confirm it contains the expected board and
   useful product content, not an access-denied, challenge, empty-shell or login
   page. The helper saves response HTML plus extracted text/links; it does not
   bundle remote images, CSS or JavaScript. Describe that scope truthfully.
5. `capture` records the requested/final URLs, timestamp, byte count and SHA-256
   in working.yaml. It does not overwrite existing evidence. A repeated matching
   call verifies its cached files instead of downloading again. Use a new source
   ID/filename for a genuinely different revision; retain old evidence.

If browser policy blocks the site, do not invoke requests/curl/another browser as
a way around that denial. Record the block and continue useful work on allowed
sources/other boards. Do not change settings. If a normal allowed download fails,
make at most one reasonable alternate attempt from a link on an official page;
record the failure and move on if it still fails. Never spend the entire batch
on one unavailable asset.

## Follow documentation, pinouts and downloads

Prefer links actually present in the product page or its official guide. Inspect
the guide in the browser. Adafruit usually places datasheet/CAD links in
**Downloads** and signals in **Pinouts**. SparkFun usually has **Hardware
Overview**, **Resources** and a **single-page** guide. Read the actual navigation
links; do not guess a route from a heading. One pilot's visible heading
"Programming and Calibration" linked to `/programming`, not the guessed URL.

Archive relevant pages under `reference/`:

```powershell
python tools/i2c_part_research.py capture --part-id EXACT_PART_ID --source-id guide_pinouts --kind guide --url "DISCOVERED_GUIDE_URL" --filename reference/guide_pinouts.html --discovered-from product_page
```

Use short, unique source IDs (`guide_hardware`, `guide_downloads`,
`hardware_repository`, `cad_board`, `cad_schematic`, `chip_datasheet`). Every
`--discovered-from` must refer to a source already saved in the same record.

## Collect the requested facts

Fill these independently, with explicit units and evidence:

- **Identity:** readable name, board maker, manufacturer SKU, exact carrier and
  assembly/revision. Distinguish the board maker from the sensor IC maker.
- **Size:** PCB width/height, thickness if given, assembly height if given,
  mounting holes and connector/overhang notes. Keep chip package size, PCB size,
  glass/screen size and overall product bounding box separate. If two dimensions
  are shown without orientation, state the source order or leave orientation
  unresolved. Do not copy dimensions from another vendor's carrier.
- **Physical contacts:** actual header/connector references and pad numbers,
  their printed labels or CAD net names, alternate names, signal roles and
  direction where documented. A named-but-unnumbered header contact can have
  `number: null`; do not invent PCB numbering. Unknown XY stays null.
- **Counts:** header contacts, cable-connector contacts, total exposed contacts,
  and unique documented nets. A four-pin connector duplicated twice adds eight
  physical contacts, not eight independent signals. Count the chip's package
  leads separately under `chip`, if useful. Do not count mounting holes,
  mechanical connector anchors, test fixtures or solder-configuration jumpers
  as ordinary header/cable contacts.
- **I2C:** default and alternate **seven-bit integer** addresses, selection
  method, required reset/jumper operations, pull-up rails/values/disconnect
  method, and extra pins. Store chip maximum bus speed separately from an
  established whole-carrier/host/cable maximum. A null value is preferable to
  an unverified guess. Record clock-stretching or repeated-start requirements
  if documented; do not assume their absence.
- **Electrical:** board power inputs versus regulated outputs, nominal/range
  evidence, logic-level restrictions, extra outputs, load supply if applicable,
  and chip supply limits in their own scope. A 5 V VIN does not establish that
  every signal pin accepts 5 V.
- **Software:** official Arduino/Python/CircuitPython libraries and guides,
  documentation and example URLs, package/library names, installation guidance
  and dependencies where found. Distinguish supported interfaces: a chip that
  supports SPI can have a Python driver supporting only I2C. Set `tested: false`
  unless this run actually performs a relevant test; no firmware flashing is
  part of this task.
- **Extra resources:** schematics, matching CAD, drawings, Fritzing files,
  tutorials, hardware repository and license links/copies when available.
- **Conflicts/gaps:** keep conflicting claims with their source IDs and explain
  what remains unresolved. Do not silently discard an inconvenient source or
  convert unknowns to zero.

## Download the chip datasheet

Follow the datasheet link from the vendor guide/product or the actual chip
manufacturer. Confirm its title is the chip in question. A carrier schematic,
brief marketing sheet or HTML webpage is not automatically the chip datasheet.

```powershell
python tools/i2c_part_research.py capture --part-id EXACT_PART_ID --source-id chip_datasheet --kind chip_datasheet --url "DISCOVERED_PDF_URL" --filename reference/chip_datasheet.pdf --discovered-from guide_downloads
```

The helper checks the PDF signature and parses a nonempty page tree. Read the
saved PDF and verify the chip
title and useful page count. Record document revision/date when shown, and use
PDF page numbers for technical locators. Store the file path and source ID in
`datasheets.items`. If extraction is garbled or the fact depends on a diagram,
render and inspect that page using the PDF workflow. For Unicode text on Windows
use UTF-8 file output or `sys.stdout.reconfigure(encoding='utf-8')`; do not lose
the research run to a console encoding error.

If unavailable, keep the known URL and actual failure in `research.attempts` and
set `datasheets.status` to `download_failed` or `not_found`, with a precise note.
Do not fabricate a PDF or mark it downloaded because a link exists.

## Optional CAD extraction

Use CAD only after matching the **exact carrier**, not merely its chip. Repository
roots and READMEs often describe old revisions. Prefer immutable commit URLs for
the actual `.brd`/`.sch` file when the file page provides them; archive the exact
bytes and hashes in all cases. A `.sch` can have a different filename/history
from the matching `.brd`; do not assume a valid board commit contains the same
schematic pathname. Retain an unsuccessful attempt before following the actual
current schematic link.

Archive Eagle XML as `--kind cad_board` or `--kind cad_schematic`. The capture
helper checks that the response is Eagle XML. For KiCad or another format, use
an appropriate kind and inspect that format; do not label it Eagle.

Inspect element/package names and choose **actual external connector
references**. Then use the generic extractor:

```powershell
python tools/i2c_eagle.py source_file/EXACT_PART_ID/reference/carrier.brd --connectors JP1,JP2,CONN3,CONN4 --connector-kinds JP1=header,JP2=header,CONN3=cable_connector,CONN4=cable_connector --exclude-pads CONN3:MT1,CONN3:MT2,CONN4:MT1,CONN4:MT2 --output source_file/EXACT_PART_ID/reference/cad_summary.yaml
```

The example connector names and excluded pad names belong to one pilot and must
not be copied blindly. Specify a kind for every selected connector and explicitly
list each mechanical pad to exclude after reviewing the footprint. An `NC` or
`MT` name by itself is not proof of a mechanical anchor; unused electrical
contacts still count as contacts. If no anchors need exclusion, omit that flag.
The extractor retains native Eagle orientation, centres coordinates on the
outline bounding box, handles curved outline bounds, excludes only your reviewed
pad pairs, and reports its selected contacts/mounting packages. Mounting-hole
discovery covers plain holes and packages named MOUNT/STAND-OFF; manually inspect
the other packages and compare the whole board so differently named holes are
not missed. Review its
output before merging those fields into working.yaml. Register the summary as a
hashed derivative of the `cad_board` source using `file_details` from the helper.
The examples show the exact manifest shape.

Do **not** reuse `tools/extract_board_cad.py`'s microcontroller-specific rotation
rule for these peripherals; it assumes a USB orientation. Do not fabricate
components/pins from a photograph or infer a fourth hole from a square board.
Source a CAD pin's `net_name` separately from a guide label; `SDA/SDIO` in CAD can
have a user-facing `name: SDA` and aliases without losing the original net.

## Finish one record and continue

1. Read the working.yaml again as a coherent record. Verify requested/default
   URLs, revision, source references, sizes/units, counts and signal names.
2. Set `research.status` to `complete` if the requested research is resolved,
   or `complete_with_gaps` for a completed pass with specifically documented
   unknowns. Use `partial` when an access/download problem prevented a useful
   pass. These states describe research, not manufacturing or hardware testing.
   Leave `reviewed_by: null` for the later reviewer; never attribute your work
   to the pilot reviewer. Update timestamps.
3. Run the validator and fix actual errors:

```powershell
python tools/i2c_part_research.py validate --part-id EXACT_PART_ID
python tools/i2c_part_research.py queue --write
```

4. Read the next queue entry and repeat. Save progress after each board. Avoid
   broad source refetches or whole-catalogue generation. One parent/worker should
   own queue updates; do not run concurrent writers on a single working.yaml.
5. At batch completion, validate all created research records and summarize
   completed/partial/pending counts, acquired datasheets, important conflicts and
   specific items needing a higher-capability review. Include paths rather than
   pasting entire archived pages into the chat.
