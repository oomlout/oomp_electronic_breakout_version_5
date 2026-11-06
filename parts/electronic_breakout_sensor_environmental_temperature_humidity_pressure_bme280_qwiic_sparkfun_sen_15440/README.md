<!-- oobb-presentation:start -->
# SparkFun Qwiic BME280

AI-generated images and instructions. Errors possible.

![AI-generated CAD render of SparkFun Qwiic BME280 default mounting plate](presentation/images/3dpr.png)

Mounting plates for the listed board. Board not shown.

## Parts

One board and one plate. Choose a plate variant.

| Part | Type | Specification | Qty | MD5 alpha |
| --- | --- | --- | ---: | --- |
| [Default plate](3dpr.stl) | Printed | 59 × 58.98 × 6 mm | 1 | — |
| [SparkFun Qwiic BME280](working.yaml) | Hardware | 25.4 × 25.4 mm; bme280 | 1 | [1l2i6](working.yaml) |

## Installation

1. Download and print the default mounting plate STL.
2. The plate uses 3 board fixing locations, sized for M3 screws. The PCB drill diameters are listed below.
3. Check screw length, screw-head clearance and underside component clearance against the physical board before fastening; physical fit has not been tested.

## Files

[Catalogue record](working.yaml) · [Render sources](presentation/manifest.json) · [Mounting evidence](../../source_file/electronic_breakout_sensor_environmental_temperature_humidity_pressure_bme280_qwiic_sparkfun_sen_15440/mounting.yaml) · [SCAD](3dpr.scad) · [Hole coordinates](mounting.csv)
<!-- oobb-presentation:end -->

<!-- mounting-review:start -->
## Mounting pattern

25.4 × 25.4 mm PCB bounding box. Coordinates are millimetres, top view, with the origin at the PCB centre, +X right and +Y up.

![Mounting coordinates](mounting.png)

| Mount | X mm | Y mm | PCB drill mm | Holder screw |
| --- | ---: | ---: | ---: | --- |
| `H4:hole:1` | 10.16 | 10.16 | 3.302 | M3 |
| `H2:hole:1` | -10.16 | 10.16 | 3.302 | M3 |
| `H1:hole:1` | 10.16 | -10.16 | 3.302 | M3 |

The generic holder has a 3 mm plate and 3 mm board lift. Screw sizes are the holder's design choice, not a manufacturer hardware recommendation.

[Vector drawing](mounting.svg) · [Coordinate CSV](mounting.csv) · [Evidence and revision](../../source_file/electronic_breakout_sensor_environmental_temperature_humidity_pressure_bme280_qwiic_sparkfun_sen_15440/mounting.yaml) · [Build checks](../../source_file/electronic_breakout_sensor_environmental_temperature_humidity_pressure_bme280_qwiic_sparkfun_sen_15440/mounting_build.json)
<!-- mounting-review:end -->
