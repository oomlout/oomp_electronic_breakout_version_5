"""Opt-in A4 coordinate drawings from promoted, independently scoped geometry."""

import copy

from mounting_geometry import standard_holder


DEMO_IDS = [
    "electronic_breakout_microcontroller_rp2040_feather_without_headers_22_86_mm_width_50_8_mm_height_adafruit_4884",
    "electronic_breakout_sensor_motion_accelerometer_adxl345_stemma_qt_adafruit_1231",
    "electronic_breakout_sensor_environmental_temperature_humidity_pressure_bme280_qwiic_sparkfun_sen_15440",
]


def drawing_geometry(board):
    """Never mix mounting research with a possibly different pinout frame."""
    record = board.get("mounting_research")
    if not record or record.get("status") != "verified":
        raise ValueError("Coordinate drawings require verified mounting_research")
    frame = record.get("coordinate_system", {})
    expected = dict(origin="pcb_bounding_box_centre", units="mm", view="top",
                    x_positive="right", y_positive="up")
    if any(frame.get(key) != value for key, value in expected.items()):
        raise ValueError("Coordinate drawings require a centred, top-view, X-right/Y-up mm frame")
    geometry = standard_holder(record["board_size"], record["mounting_holes"])
    holes = sorted(geometry["mounting_hole_details"], key=lambda h: (-h["y_mm"], h["x_mm"]))
    if len(holes) > 6:
        raise ValueError("This A4 template supports up to six mounting holes")
    for index, hole in enumerate(holes, 1):
        hole["label"] = f"H{index}"
    return dict(width=geometry["breakout_pcb_width"], height=geometry["breakout_pcb_height"],
                holes=holes, coordinate_system=copy.deepcopy(frame),
                sources=copy.deepcopy(record.get("sources", [])), status=record["status"])


def apply_coordinate_drawings(options, *, stylesheet="coordinate"):
    for option in options:
        if not option.get("mounting_research"):
            continue
        drawing_geometry(option)
        details = copy.deepcopy(option.get("svg_details", []))
        if isinstance(details, dict):
            details = [details]
        if not any(d.get("svg_name") == "coordinate_diagram" for d in details):
            details.append(dict(svg_name="coordinate_diagram", stylesheet=stylesheet,
                                svg_output="working_coordinate_diagram", export_pdf=True))
        option["svg_details"] = details
    return options
