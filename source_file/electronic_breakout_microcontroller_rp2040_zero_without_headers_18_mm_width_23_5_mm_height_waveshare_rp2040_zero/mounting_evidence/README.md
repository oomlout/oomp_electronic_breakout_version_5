# Waveshare RP2040-Zero mounting evidence

- Official product page: https://www.waveshare.com/wiki/RP2040-Zero
- STEP download: https://files.waveshare.com/upload/f/f7/RP2040_Zero_stp.zip
- Mechanical drawing: https://www.waveshare.net/w/upload/thumb/2/2e/RP2040-Zero-3.jpg/800px-RP2040-Zero-3.jpg
- STEP ZIP acquired 2026-11-06; local registered ZIP SHA-256 is recorded in mounting.yaml. ZIP contains `RP2040_Zero.stp`; STEP header calls the assembly `RP2040_ZERO_ASM`, dated 2022-01-08. Product page supplies the model but states no PCB revision number.
- STEP review: first solid is the bare PCB. Its bounds are X -0.0601036317 to 17.9600170327 mm, Y 0.0901532305 to 23.6100287848 mm, Z -1.0928398848 to 0.0013993448 mm. The STEP top view has positive Y toward USB. Centred mapping is x=X-8.9499567005, y=Y-11.8500910076, with no rotation/reflection.
- All 33 unique cylindrical features in the PCB solid were reviewed: 23 Ø0.9 mm edge castellated pads, 8 Ø0.5 mm USB-C connector shell/anchor holes, and 2 Ø0.762 mm USB-C signal-pin holes. The manufacturer dimension image identifies the edge-pad layout. No board mounting feature appears in the complete PCB solid.
- `review_step_top.png` was generated from the official STEP PCB solid as a top-view audit aid. Orange rings mark all cylindrical drill/pad feature locations.
