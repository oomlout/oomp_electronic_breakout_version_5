# Per-part research schema, version 1

Use `python tools/i2c_part_research.py seed --part-id <id>` to get the complete
starting shape. Do not delete fields to hide gaps. `null` means unknown; `0`
means verified zero. All lengths are millimetres and I2C addresses are integer
seven-bit values, not eight-bit read/write addresses.

## Identity and status

- `research_schema_version: 1`
- `part_id`, `name_readable`, `manufacturer`, `part_number`,
  `manufacturer_part_number`, `catalogue_definition` retain the exact catalogue
  identity. `manufacturer` is the board maker, not necessarily the IC maker.
- `taxonomy` contains the original 15 slots. Do not shift empty slots or alter
  any value. Manufacturer is `taxonomy_14`; normalized vendor part number is
  `taxonomy_15`. `part_id` is not recomputed from researched dimensions.
- `default_website` contains `url`, `source_id`, `local_file`. Normally these are
  the official product URL, `product_page`, and `website.html`.
- `research` contains `status`, timestamps, `reviewed_by`, and `attempts`.
  Successful pass states are `complete` and `complete_with_gaps`. Other worker
  states are `in_progress` and `partial`; the queue uses `pending` when no file
  exists. `attempts` retains failed URLs, source IDs, reasons and timestamps.
- `board_revision` records the selected carrier name/revision, `status`,
  `source_ids` and notes. A CAD part value is not proof of a fitted production IC.

## Measurements, contacts and electrical fields

- `dimensions_mm`: `width`, `height`, `pcb_thickness`, `assembled_height`,
  `scope`, `status`, `source_ids`. Use `scope: carrier_pcb_outline` for verified
  carrier dimensions. Optional `product_dimensions_mm` or `chip.package` must
  have their own scope and evidence rather than overwriting the PCB dimensions.
- `coordinate_system`: units, origin, view, orientation, status. With the helper,
  the origin is the Dimension-layer bounding-box centre and the orientation is
  native Eagle axes, top view. No implicit USB direction.
- `mounting_holes`: objects with `id`, `x_mm`, `y_mm`, `diameter_mm`, `plated` and
  `source_id`; unknown locations stay unresolved rather than entering this list.
  Qualify an empty list using `mounting_hole_status`.
- `connectors`: keyed by actual reference (`JP1`, `J2`, etc.), with `kind`
  (`header` or `cable_connector`), `cad_package`/description, `contacts` (keys in
  `pins`) and source evidence. It is also acceptable to use a clearly described
  unnumbered header group when only a guide is available.
- `pins`: keyed by physical connector/pad identity. Each entry has `connector`,
  `number` (string or null), `name`, `net_name` where available, `aliases`,
  `signal_type`, `direction`, `kind`, `x_mm`, `y_mm`, `source_id`/`source_ids`,
  and notes. Unknown XY must be null as a pair. A CAD-derived net name must be
  marked as such if the silkscreen label has not been checked.
- `pin_count`: `header_contacts`, `cable_connector_contacts`,
  `total_exposed_contacts`, `unique_nets`, `scope`, `status`, `source_ids`.
  `total_exposed_contacts` equals the number of `pins` entries. Duplicate nets on
  multiple contacts still count as separate physical contacts. If net identity
  is incomplete, leave `unique_nets: null` rather than counting labels as nets.
- `pin_names`: sorted unique `name` values from `pins`. This is a convenience
  inventory, not an independent count of GPIOs.
- `electrical.board_supply`: nominal values, min/max only if established,
  status, source IDs and notes. `supported_nominal_v: [3.3, 5.0]` does not assert
  an independently established continuous min/max range.
- `electrical.chip_supply`: optional separate chip limits with explicit scope.
- `electrical.logic_levels`: status, restrictions/notes and source IDs.
- `electrical.pullups`: signal lists, resistance in ohms when known, rail,
  reference/designator, disconnect method and source IDs.
- `electrical.extra_signals`: IRQ, RESET, CS, XSHUT, etc. Include relevant
  restrictions in the pin entries or electrical notes.
- `i2c`: `default_address_7bit`, `documented_addresses_7bit`, address selection,
  `maximum_clock_hz`, clock stretching, status and source IDs. Optional
  `chip_maximum_clock_hz` must stay distinct from a verified board/host maximum.

## Chip, software and extra resources

- `chip`: maker, part number, identity status, optional package/pin count,
  conflicting CAD part value and source IDs.
- `datasheets`: `status` (`not_searched`, `downloaded`, `not_found`,
  `download_failed`), `items`, notes. Each downloaded item identifies the chip,
  `source_id`, `local_file`, URL, SHA-256, page count and revision if found.
  The referenced source must be `kind: chip_datasheet` and an actual PDF.
- `software`: list of named library/driver entries with `framework`, official
  URL, optional docs/example/installation/dependencies, `tested: false` unless
  actually tested, source IDs and interface/platform caveats.
- `extra_resources`: named/kinded links and local files for guides, CAD,
  schematics, drawings, Fritzing, hardware repositories and licenses. Reference
  a source ID when the resource has been archived. Never invent a local filename
  for a link-only resource.
- `conflicts`: topic, conflicting claims with their source IDs, resolution text
  and status. Preserve an unresolved conflict even when a conservative working
  constraint is adopted.
- `data_gaps`: precise, useful missing facts and unresolved questions. Include
  missing pinouts, thickness, complete assembly envelopes, unavailable
  datasheets or ambiguous chip identity instead of generic "needs research".

## Evidence manifest

`sources` is a list maintained by `capture`, with this shape:

```yaml
- id: cad_board
  kind: cad_board
  requested_url: https://official-or-linked-host/exact-resource
  url: https://final-download-url/exact-resource
  retrieved_at: ISO-8601 UTC timestamp
  content_type: response content type
  acquisition: http_response_bytes_after_browser_discovery
  discovered_from: hardware_repository
  local_file: reference/carrier.brd
  bytes: 123456
  sha256: actual-64-character-file-hash
  derivatives:
    - kind: cad_summary
      generator: tools/i2c_eagle.py
      local_file: reference/cad_summary.yaml
      bytes: 12345
      sha256: actual-64-character-file-hash
```

HTML sources also have a title, snapshot-scope note and hashed `text` and `links`
derivatives. Optional PDF text extraction is a `pdf_text` derivative. Do not
replace the original PDF with its extracted text. Use
`tools.i2c_part_research.file_details(path, folder)` to get real paths, byte
counts and hashes for a new derivative, then save the record. All files and
relative paths must stay inside this part's folder; do not reference another
part's files as if they were local.

Every `source_id`/`source_ids` reference must resolve to this manifest. A source
being downloaded does not prove every claim on it is current or accurate.
Important facts should include useful locators in notes (guide heading, CAD
connector/pad, or PDF page), especially when explaining conflicts.

## Completion check

`python tools/i2c_part_research.py validate --part-id <id>` checks identity,
unchanged taxonomy, archived default website/text, local paths, file hashes and
sizes, evidence references, contact counts, addresses and actual PDF datasheets.
It rejects unknown research states, missing source URLs/timestamps, missing
evidence on completed factual sections, and datasheet item paths/hashes/page
counts that differ from their archived source. Explicitly unverified sections
can remain unknown; do not remove fields or provenance to avoid a check.
It cannot prove a physical fact or recognize every stale/wrong revision. The
worker must inspect those semantics before marking the research pass complete.
