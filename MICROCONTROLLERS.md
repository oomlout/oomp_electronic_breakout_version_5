# Microcontroller board catalogue

The editable authority is now the eight `working_oomp_populate_microcontroller_<family>.py` files: RP2040, RP2350, classic ESP32, ESP32-C3, ESP32-S2, ESP32-S3, ESP32-C6 and ESP32-H2. Each board is an explicit, verbose multiline dictionary followed by `options.append(option)`. No compressed pin tables, runtime research, or dependency on the lab project's location is needed to load them. The RP and C3 files also expose `get_chips(**kwargs)` for imported package definitions.

`working_oomp_populate_microcontroller.py` remains the public populate entry point. `microcontroller_catalogue.py` assembles and validates the family data and supplies the mounting-plate output details. The top-level population script preserves these definitions' taxonomy instead of rebuilding it and losing assembly variants.

Research snapshot: **22 October 2026**. The catalogue contains **48 board records and six chip/package references**. This includes the original 46 distinct board entries, the lab's headered RP2350-Zero variant, and its separately identified C3 AZ device reference. The original file accidentally appended RP2350-Zero twice; the duplicate was removed. The attached C3 AZ observation is kept separate from the original generic C3 FN4 entry because an observed chip revision is not evidence that every similarly named carrier uses that silicon.

The lab project's populate script loads `source_file/*/definition.yaml` through `working_source.py`; those authoritative files and their CAD/drawing assets were imported. Import paths, dates and SHA-256 hashes are recorded in `definition_import`. The lab project itself was not edited. Its data changed during this research; the hashes identify the specific imported snapshots.

## Generated handoff

Run from this repository, or invoke the script by absolute path:

```powershell
python tools/export_microcontroller_catalogue.py
python tools/export_microcontroller_catalogue.py --destination C:\path\to\handoff
python -m unittest discover -s tests -v
```

The exporter requires the existing shared `opsvg`/`svg_styles` environment and PyYAML. Loading the family dictionaries themselves requires only Python's standard library.

- [Coverage and remaining evidence gaps](catalogue/microcontrollers/coverage.md): a row for every board, with links to its YAML and SVG.
- [Manifest](catalogue/microcontrollers/manifest.json): canonical IDs, legacy ID aliases, relative artifact paths, contact/GPIO counts and geometry coverage.
- [Complete JSON catalogue](catalogue/microcontrollers/catalogue.json): boards plus chip definitions for a web build to ingest directly.
- `source_file/<id>/definition.yaml`: generated definition, retaining the human-editable Python as its authority here.
- `source_file/<id>/reference/`: manufacturer CAD, drawings and schematics used by that definition, with source URLs and checksums.
- `source_file/<id>/working_svg.svg`: a generated, accessible drawing with machine-readable physical-pad attributes.

Do not rerun `tools/materialize_board_research.py` after making manual family-file edits. It is the one-time import/research audit trail, not the normal build. The collector and CAD extraction tools are also research tools, not catalogue runtime dependencies. Additional research-only packages are `requests`, `beautifulsoup4`, `html5lib`, `sexpdata`, and `ezdxf` if DXFs are examined.

## Mechanical and electrical contract

Coordinates are **millimetres, centred on the carrier PCB, viewed from above, with USB towards +Y**. Exceptions, such as ESP32-CAM having no USB socket, are explicit in `coordinate_system`. SVG screen coordinates are transformed by the existing Y-up `opsvg` pipeline; `data-x-mm` and `data-y-mm` preserve the original mechanical coordinates.

`dimensions_mm.scope`, `status`, and `source_id` explain whether dimensions are a verified carrier outline, a nominal catalogue value or overall product dimensions. Module antenna overhang is separate from carrier height where the drawing provides it. An SVG rectangle represents the board's bounding envelope, not a CNC-ready traced perimeter. Connector keepouts, insertion clearance, underside components and complete assembly envelopes are not inferred from a product photograph.

`mounting_hole_details` contains located holes with diameter and source. `mounting_holes` is the derived `[x, y]` list used by existing mounting-plate code. `mounting_hole_candidates` contains incomplete measurements or related-variant evidence; these never enter that manufacturing list. An empty list is qualified by `mounting_hole_status`: it can mean no holes in CAD, no holes shown in a drawing, or simply unverified. It does not automatically mean that a board has no holes. The M2 mounting-plate default is a fixture choice; the measured board hole diameter remains separate.

Each `pins` entry identifies a **physical connector and pad number**, its source name, optional GPIO and chip package pin, ADC unit/channel, functions, aliases, direction, capabilities, restrictions and optional XY coordinates. CAD can include distinct castellations and plated holes on the same signal; multiple contact records do not mean additional independent GPIOs. SDK-only D1 R32 entries explicitly identify themselves as software aliases rather than verified physical contacts. Connector numbering follows each cited source; a descriptive reference-row name does not invent PCB silkscreen numbering.

GPIO signal types, ADC capability and output capability are separate. Classic ESP32 GPIO34–39 are input-only. Flash and board-specific PSRAM contacts are excluded from `general_io_candidates`. Native USB pins carry a routing restriction. Boot straps and onboard loads are documented. C3 GPIO5 retains its ADC2 silicon mapping but is excluded from `lab_analog_eligible` because the normal ESP-IDF C3 ADC2 drivers are unsupported; see [Espressif's ADC limitations](https://docs.espressif.com/projects/esp-idf/en/latest/esp32c3/api-reference/peripherals/adc/adc_oneshot.html).

`chip_resources` describes silicon resources, not a promise that the board exposes every peripheral. ESP32 `routable_peripherals` describes GPIO matrix possibilities, not a fixed bus pin assignment. `default_interfaces` now records sourced, framework-scoped UART, I2C and SPI assignments and explicit unknowns for every board; see the consumer contract below. `gpio_summary` deduplicates GPIO numbers. Every record requires a reviewed lab profile before firmware enablement; the catalogue does not flash devices or infer firmware support from a common footprint.

## Default interface data

Interface research updated **23 October 2026**. All **48** boards contain `interface_defaults_version: 1` and explicit `default_interfaces.uart`, `.i2c` and `.spi` entries. **45** boards have documented assignments; the three unresolved Tenstar S3/C6/H2 SuperMini carriers have `status: unverified` and null GPIOs. The [interface coverage table](catalogue/microcontrollers/interfaces.md) lists every board. The same fields are exported in each `source_file/<id>/definition.yaml` and in `catalogue/microcontrollers/catalogue.json`.

Defaults are scoped to pinned [Arduino-Pico source](https://github.com/earlephilhower/arduino-pico/tree/d087696645b98dce8a3df92c0afff40a3745d295/variants) or [Arduino-ESP32 source](https://github.com/espressif/arduino-esp32/tree/6b41cf6f6f272538ee91746f26c5068e2ca692e4/variants). They are not universal MicroPython, CircuitPython, ESP-IDF or Pico SDK defaults. No network access or Arduino installation is needed to load the catalogue. Each documented entry links through `source_ids` to commit-pinned URLs, local reference copies, SHA-256 hashes and a retrieval date. Board-selection evidence contains explicitly labelled excerpts; full snapshots and the one-time enrichment script are retained in `research/microcontrollers/interface_defaults/` and `tools/research_interface_defaults.py`. Do not rerun the research script over later edits; normal regeneration uses the exporter.

Each interface contains these fields:

| Field | Meaning |
| --- | --- |
| `protocol` | `uart`, `i2c` or `spi`. Secondary entries use the same protocol and keys such as `i2c_secondary`. |
| `status` | `documented` means the cited framework defines the assignment. `unverified` means the carrier/default mapping remains unknown. Neither means electrically available for every application. |
| `basis` | `framework_defaults`, `framework_pin_aliases` or `unknown`. ESP32 UART `TX`/`RX` constants are aliases: firmware should pass these pins explicitly to its chosen HardwareSerial instance. |
| `framework`, `variant`, `variant_scope` | Identifies the exact software selection. `generic_target_selection` applies only when that generic Arduino target is selected; it is not evidence of a carrier-specific convention. |
| `api`, `peripheral` | The Arduino object and silicon controller where established, for example `Wire` and `i2c1`. Null means unspecified, not peripheral zero. ESP32 UART deliberately specifies neither an API instance nor a controller. |
| `tx_gpio`, `rx_gpio` | UART signals from the board's perspective: connect TX to the other device's RX. |
| `sda_gpio`, `scl_gpio` | I2C data and clock. |
| `sck_gpio`, `mosi_gpio`, `miso_gpio`, `ss_gpio` | SPI controller clock, output, input and chip-select alias. `ss` is optional and does not imply automatic assertion by a library. |
| `pin_keys` | Maps each signal name to **all** matching keys in the board's `pins` dictionary. Separate header, castellated and connector contacts may share a GPIO. |
| `signal_status` | Per-signal mapping status, as described below. |
| `source_ids`, `notes` | Evidence and limitations specific to this interface. |

Every pin also has `default_interface_roles`, a list of `{interface, signal}` references back to these entries. An empty list means no recorded default role, not a lack of alternate peripheral capability. Existing `functions`, aliases, ADC, PWM and GPIO-matrix capability fields are preserved. Multiple default roles on one GPIO show shared assignments, not permission to use the interfaces simultaneously.

`signal_status` distinguishes these cases:

- `mapped`: matching contact records exist. Inspect their `restrictions`, `available_for_general_io`, direction, contact scope and geometry before choosing a contact. The status does not upgrade the original contact evidence or imply a main-header position.
- `software_alias_only`: only SDK aliases exist; no physical pad identity was established.
- `not_in_pinout`: the framework names a GPIO but the catalogue has no matching contact. The numeric GPIO remains available for auditing; programs must not treat it as an exposed pad.
- `not_defined`: no usable default is defined. GPIO is null; framework sentinel values such as RP GPIO31 are not exported as real assignments.
- `unverified`: neither a verified assignment nor its contact mapping is available. GPIO is null.

The UART entries describe physical UART signals, separate from USB CDC and USB Serial/JTAG. `Serial` can refer to USB depending on framework and build settings. QT Py RP2040 retains its labelled TX20/RX5 pair under `uart`, with `api: Serial2`; `uart_secondary` describes `Serial1` on A1/A0 (GPIO28/29). XIAO RP2350's `Wire` defaults use GPIO16/17 on underside pads, while `Wire1` uses GPIO6/7 on the side contacts. QT Py boards also record separate STEMMA QT buses where defined. LOLIN D32 Pro's `SS` override selects GPIO4, shared with onboard microSD. ESP32-CAM's generic I2C/SPI values are explicitly marked `not_in_pinout`.

Programs can look up assignments without parsing pin labels or board names:

```python
import json
from pathlib import Path

catalogue = json.loads(Path("catalogue/microcontrollers/catalogue.json").read_text())
board = next(b for b in catalogue["boards"] if b["part_number"] == "pico")
assert board["interface_defaults_version"] == 1
bus = board["default_interfaces"]["i2c"]
assert bus["status"] == "documented"
assert all(bus["signal_status"][signal] == "mapped" for signal in ("sda", "scl"))
print(bus["framework"], bus["variant"], bus["api"])  # arduino-pico rpipico Wire
print(bus["sda_gpio"], bus["scl_gpio"])             # 4, 5
contacts = [board["pins"][key] for key in bus["pin_keys"]["sda"]]
```

The catalogue validator checks mandatory interface coverage, source references, per-signal statuses, GPIO/contact joins and reciprocal pin roles. Tests also cross-check RP defaults against the separately sourced silicon mux functions. The normal export regenerates definitions, JSON, the manifest and the interface coverage table together.

## SVG integration

All board drawing code is in `working_svg.get_microcontroller()` and `working_svg.microcontroller_svg()`. The named stylesheet lives in `working_svg_microcontroller_styles.py`, uses `svg_styles` inheritance and permits per-part overrides. Analog, power, ground and reserved pads have distinct styles.

Every located contact has `data-pin`, `data-pin-type`, `data-capabilities`, `data-signal-types`, `data-x-mm`, `data-y-mm`, and `data-source-id`; GPIO/ADC contacts add their corresponding identifiers and availability. Its title includes functions and restrictions. Unknown pad positions appear in a separate textual inventory and have no spatial hit target. The lab can join a hit target's `data-pin` directly to the definition's `pins` key.

Pad markers use schematic sizes; they do not imply undocumented drill or copper diameters. Located mounting-hole circles use their measured diameters. Internal connector/test pads retain their metadata and tooltips while row labels are limited to main headers to keep dense boards readable. The eight contact sheets in `catalogue/microcontrollers/review/` were rendered and visually inspected.

## Lab migration boundaries

The lab now imports complete source folders from this repository during make-all, using its editable `config/oomp_sources.yaml` OOMP ID/wildcard list. Hardware edits belong in the family dictionaries here; run `python tools/export_microcontroller_catalogue.py` to refresh the exported definitions before rebuilding the lab. The lab's former population modules have been retired. Its eight LED component definitions remain local.

The follow-up migration checked all 25 shared lab definitions (19 board variants and six chips) for missing fields and list entries. The enriched catalogue already retained the hardware details and GPIO capability tags. Three missing reviewed `lab.yaml` profiles were copied alongside their definitions: Raspberry Pi Pico, RP2040-Zero and the observed C3 AZ SuperMini. These profiles survive catalogue exports and are copied recursively by the lab importer. Paths and SHA-256 hashes are recorded in [the migration audit](catalogue/microcontrollers/lab_migration.json). Keep profile changes here so subsequent imports retain them.

The imported RP and observed C3 AZ entries preserve the lab's source taxonomy and package links. Legacy ID aliases retain the original catalogue identities. Existing generated `parts_source`/`parts` folders are not migrated or deleted by this work; use the manifest as the current export inventory.

The additional ESP32 entries retain their existing catalogue IDs, including historical dimensions or contact counts in those IDs. Corrected dimensions and contact records are in the structured fields. **These additional entries are catalogue data, not drop-in validated lab source records:** the current lab validator requires fixed assembly taxonomy and fully populated chip package references, and its runtime currently supports RP2040/C3 profiles. Most new ESP32 variants still need a package/module catalogue link, taxonomy migration and a reviewed runtime profile. Copying the JSON/SVG data for browsing does not require enabling a new firmware target. A future importer should use the explicit `chip.family`, dimensions, pins, restrictions and source evidence rather than parsing IDs.

Three Tenstar S3/C6/H2 SuperMini carrier pinouts remain unknown: no revision-specific primary header drawing was established. Related MakerGO/Zephyr definitions are cited only within their actual scope. Adafruit PID5477's public CAD repository describes an 8 MB/no-PSRAM sibling; its related pad and hole geometry is retained as reference evidence and not presented as verified geometry for the 4 MB/2 MB SKU. LOLIN holes retain their documented X centres and diameters with null Y where the drawing does not dimension Y. Every remaining gap is listed per board in the coverage report.
