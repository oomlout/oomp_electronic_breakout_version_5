Acquisition and review notes

- 2026-11-06: downloaded official WEMOS product documentation page https://www.wemos.cc/en/latest/d32/d32_pro.html to product_d32_pro.html using requests with a 20-second timeout. The page identifies the D32 Pro, states board size 65 × 25.4 mm, and links Dimension V2.0.0 and Schematic V2.0.0.
- Reused archived official Dimension V2.0.0 PDF at ../reference/dim_d32_pro_v2.0.0.pdf after matching SHA-256 to the seeded context: 332a0ba3f8324d181a7fb768e8727c4eb3b228e0e01113efbed599dc1817e10c. Visual review shows the 25.40 × 65.00 mm board and two circles, with a 21.40 mm horizontal centre spacing and 2.10 mm top-edge-to-hole-centre dimension. It provides no drill diameter callout.
- Reused archived official Schematic V2.0.0 PDF after matching SHA-256 to the seeded context: 54cc89a4df45f76c847cae09e2acac86a95891a89c85421a8f146bca91cb3f60. Schematic evidence establishes revision but does not specify mechanical drill size.
- Reviewed official WEMOS product page links for revision and searched WEMOS/GitHub for an exact D32 Pro v2.0.0 board CAD source; no manufacturer CAD source was located in this review.
- Geometry is held for review because the manufacturer drawing's two visible circles have no explicit drill diameter. Do not infer diameter from rendered circle pixels.
