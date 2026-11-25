# Mounting source acquisition notes

Acquired 2026-11-06 using Python requests with a 20 second timeout.

- `reference/board.brd`: pre-archived manufacturer EAGLE board file; verified byte-for-byte SHA-256 against the pinned raw URL at commit `619b543b7f2c7f0dbd7fd5cbe14f768b8b75cced` (SHA-256 `37043a6cc669c9ba29413a4c00e33724d1de67b6b3cc9f2759a8b3d5101437e2`). The repository has a single commit for this board file, `Adding board files.` (2021-04-20), tying the carrier CAD to the QT Py RP2040 launch/product repository.
- `repository_readme.md`: pinned repository README; product page link explicitly identifies product 4900 and repository description identifies the repo as QT Py RP2040 PCB files.
- `product_4900.html`: official Adafruit product page and product ID 4900; establishes named product identity.

The CAD EAGLE XML is complete and parses as board outline plus 34 drilled copper/USB component candidates. The full drill list was reviewed: JP1/JP3 comprise castellated signal pads, X2 includes USB-C shell anchor holes and shell pads. No intended board mounting holes appear in the carrier CAD. The default >=1.8 mm drill inspection has no candidates.
