# Mounting researcher pilots — 2026-11-06

Two fresh subagents actually ran **gpt-6-luna, high reasoning**. Each read the
new agent instructions and completed one board. They used existing archived
manufacturer evidence, independently checked official identity/revision and
commit-pinned CAD, then ran extraction, preview, validation, promotion and the
real populate → parts → SCAD → STL pipeline. No simulated model runs or physical
fit tests are claimed.

| Pilot | PCB size mm | Mounting centres mm, top view, centred | PCB drills | Holder screws |
| --- | --- | --- | --- | --- |
| Adafruit ADXL345 STEMMA QT, 1231 | 25.4 × 17.78 | (−10.16,+6.35), (+10.16,+6.35), (−10.16,−6.35), (+10.16,−6.35) | Four plated 2.5 mm | M2 |
| SparkFun Qwiic BME280, SEN-15440 | 25.4 × 25.4 | (+10.16,+10.16), (−10.16,+10.16), (+10.16,−10.16) | Three unplated 3.302 mm | M3 |

## Sources and decisions

ADXL345: [official product 1231](https://www.adafruit.com/product/1231) and
[exact QT board CAD](https://raw.githubusercontent.com/adafruit/Adafruit_ADXL345_PCB/1e0b3eb6c53d8b8ff424b9be11058d701cb31156/ADXL345%20STEMMA%20QT.brd).
Luna distinguished the current four-hole QT board from the older two-hole README.
It inspected 14 drilled candidates: four mounts and ten header drills. The CAD
U1 value ADXL343 versus product ADXL345 remains an explicit chip-identity limitation
in the record; mechanical dimensions are scoped to the selected QT carrier.

BME280: [official SEN-15440 product](https://www.sparkfun.com/products/15440) and
[exact manufacturer CAD](https://raw.githubusercontent.com/sparkfun/Qwiic_Atmospheric_Sensor_Breakout_BME280/69d2067e2999ea92fe713dfb745f2955c7e2953a/Hardware/Qwiic_Atmospheric_Sensor.brd).
Luna inspected nine drilled candidates: three stand-offs and six header contacts.
It preserved the asymmetric missing fourth mount rather than inventing symmetry.

Both raw CAD hashes matched the archives. Source URLs, exact locators and hashes
are recorded in each board's `source_file/<ID>/mounting.yaml` and the explicit
`working_oomp_populate_mounting_data.py` entries. Existing full research records
and catalogue IDs were retained.

## Verification

- `python -m unittest discover -s tests`: **49 tests passed** after both pilots.
- Python compilation and `git diff --check` passed (Git reported only its normal
  README LF/CRLF conversion notice).
- Both preview images were visually reviewed by Luna and the coordinator.
- Both `verify-build` commands passed; saved evidence and SCAD/STL output hashes
  match their receipts.
- Both STLs are a single watertight, positive-volume solid, 6 mm overall tall.
- Independent STL cross-sections at Z=4 mm contain exactly two concentric contours
  per expected stand-off centre (inner screw bore and outer boss). Both pilots'
  coordinates therefore survive all the way through the real mesh output.
- Effective populate entries have one standard holder each, unchanged IDs and
  resolvable namespaced mounting source references.
- Machine-readable mesh/coordinate checks: [pilot_checks.json](pilot_checks.json).
- Queue at handoff: **2 promoted, 78 pending**.

## Outputs

Each board has `source_file/<ID>/mounting.yaml`, `mounting_candidates.json`,
`mounting_preview.png` and `mounting_build.json`. Generated `parts_source/<ID>/`
and `parts/<ID>/` metadata contain the promoted geometry. Printable files:

- [ADXL345 STL](../../parts/electronic_breakout_sensor_motion_accelerometer_adxl345_stemma_qt_adafruit_1231/3dpr.stl)
- [BME280 STL](../../parts/electronic_breakout_sensor_environmental_temperature_humidity_pressure_bme280_qwiic_sparkfun_sen_15440/3dpr.stl)

## Pilot lessons incorporated

1. The first worker initially supplied repo-relative evidence paths. Instructions
   and missing-file errors now explicitly require paths relative to the board folder.
2. The second added an extra axis_transform frame key and shortened extracted hole
   dictionaries. Validation rejected these changes. Instructions now say to retain
   canonical frame/complete extracted dictionaries and put explanations in derivation.
3. Preview labels containing EAGLE dollar signs now disable mathematical text parsing.
4. Interrupted research/promotion/builds have resumable queue states. Generation
   receipts distinguish promoted data awaiting a build from a completed board.
5. STL output is checked before replacing an earlier STL. Superseded wire-adapter
   outputs and no-hole boards' old standard outputs are archived, not offered as
   current geometry.
6. The pre-existing OOBB import prints `directory does not exist` even in successful
   runs and tests. Exit status, artifacts and validation establish build success.

The tested automated CAD path is XML EAGLE. Other formats can use cited dimensioned
drawings or be left for review. Slots, ambiguous revisions, unsupported small drills,
component interference and unusual outlines need deliberate review. Board lift,
screw-head access, connector clearance and printed tolerances have **not** been
physically tested. The tool checks geometry/evidence and mesh integrity, not those
assembly clearances.

## Full publication build

The follow-up full build generated coordinate PNG/SVG/CSV, Blender angled/top
render sheets, downloadable SCAD/STL files and linked part pages for both pilots.
Start with [the combined visual review](REVIEW.md).

Both pilots were regenerated successfully from a clean snapshot of the files
being published, with **19 scoped tests passing**. This snapshot includes the
mounting workflow and its required I2C/population support; other in-progress
catalogue changes are outside this publication. All evidence and published
artifact hashes survived a Git checkout with Windows line-ending conversion
enabled. The earlier 49-test result covers the larger development workspace.

The full build also checks render/source hash agreement, 1600 × 1000 image
dimensions, identical image copies beside each STL and local README links.
