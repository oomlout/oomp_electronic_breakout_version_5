# Lessons from the two primary-agent pilots

The pilots are real examples in `source_file`, not templates whose hardware
facts may be transferred to another board.

## Adafruit ADXL345, product 1231, current STEMMA QT carrier

Research record:
`source_file/electronic_breakout_sensor_motion_accelerometer_adxl345_stemma_qt_adafruit_1231/working.yaml`

- Exact current CAD filename is `ADXL345 STEMMA QT.brd`. The hardware repository
  also includes old boards with similar filenames. Its README still describes
  nine header contacts and two holes; the selected QT CAD has **ten** header
  contacts and **four** mounting holes. The product page confirms four holes.
- The two four-contact QT connectors add eight physical cable contacts. Total
  exposed contacts are therefore **18**, on **nine** CAD nets. Extra ground
  contacts are not independent signals. Mechanical JST anchor pads are excluded.
- Selected CAD outline is **25.4 x 17.78 mm**. It does not establish PCB
  thickness, full assembly height or insertion clearance. The original catalogue
  ID has no dimensions token and stays unchanged.
- Although the product is ADXL345, the named current CAD file gives U1 the value
  `ADXL343`. This remains an explicit chip-identity conflict. Geometry can be
  attributed to the selected carrier, but the file is not proof of the fitted
  IC in a shipped unit.
- The pinout guide adds the alternate address **0x1D** to default **0x53** and
  warns that not all SPI pins are 5 V safe. A broad product-page logic-level
  statement must not become a guarantee for every signal.
- The linked chip datasheet is a **40-page ADXL345 Rev. E PDF**, not a board
  schematic. Its 14 package leads are separate from the carrier contact count.
- Navigation heading "Programming and Calibration" links to `/programming`.
  Guessing `/programming-and-calibration` produced an empty page shell. Follow
  actual links and verify downloaded page content.

## SparkFun BME280, SEN-15440, Qwiic carrier

Research record:
`source_file/electronic_breakout_sensor_environmental_temperature_humidity_pressure_bme280_qwiic_sparkfun_sen_15440/working.yaml`

- This is the Qwiic SEN-15440 carrier, not the earlier SEN-13676 board and not
  an Adafruit BME280. Exact CAD outline is **25.4 x 25.4 mm**.
- The selected board has **three** mounting holes, six header contacts, and
  two four-contact Qwiic connectors: **14** physical contacts on **six** nets.
  Do not infer a fourth hole from a square outline or count jumper pads as pins.
- The product page claims 5 V tolerant I2C; the guide and archived schematic
  show supply-referenced/direct bus connections for 3.3 V use. The record keeps
  both claims, marks the conflict unresolved, and uses the guide/schematic
  restriction in its electrical notes.
- The chip's advertised 3.4 MHz I2C capability is stored as a **chip** limit,
  not a certified maximum for the complete carrier/cable/host system.
- The board-file commit did not contain the assumed schematic filename. That
  download returned 404. Following the actual current schematic link succeeded;
  the failed attempt and the separate source/hash remain recorded. Do not assume
  board/schematic histories match just because the filenames look related.
- The linked chip datasheet is a **55-page BME280 revision 1.6 PDF**. The
  carrier schematic is a separate PDF with a different resource kind.
- The guide's Python library uses I2C; the Arduino library also covers SPI.
  Generic product-page MicroPython/CircuitPython labels are not sufficient to
  assert tested support for every Python platform.

## Lessons applied to the worker

1. Choose a carrier revision before counting pins or importing dimensions.
2. Count physical header/cable contacts and distinct nets separately.
3. Keep chip limits/package pins separate from board dimensions and contacts.
4. Archive the exact response bytes with hashes; verify PDF identity and page
   count, and retain failures instead of claiming every link was downloaded.
5. Make conflicts visible. Unknowns are null with specific gaps, not guesses.
6. Preserve catalogue IDs while the research file becomes more complete.
7. Save each board and update the queue before starting the next one.
8. Explicitly select connector kinds and mechanical pad exclusions; the pilots'
   JST anchor names are conventions, not a rule for every footprint. Review
   mounting packages outside the extractor's named-hole heuristics.
9. Validate evidence metadata and completed factual sections. A source reference
   must resolve, and a downloaded datasheet item must match the real local PDF.
   Failed HTML validation or output collisions must not leave a stranded raw
   file that prevents a later clean retry.

An independent read-only review reproduced the two CAD results and spot-checked
the chip identities, pull-ups, addresses and voltage conflicts against the saved
sources. The review informed the helper regression tests. This validates the
pilot examples and workflow; the lower-power model's first completed board still
deserves a semantic spot-check before relying on its whole batch.
