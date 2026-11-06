"""Standard screw-mounted holder inputs; all coordinates are top-view, centred mm."""

import copy
import math


def number(value, name, positive=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    if positive and value <= 0:
        raise ValueError(f"{name} must be positive")
    return float(value)


def screw_for_drill(diameter):
    """Design policy: largest supported M screw with >=0.2 mm diametral clearance."""
    diameter = number(diameter, "diameter_mm", True)
    for nominal, name in ((3, "m3"), (2.5, "m2_5"), (2, "m2")):
        if diameter + 1e-8 >= nominal + 0.2:
            return name
    raise ValueError("Drill too small for supported M2/M2.5/M3 screws; needs custom holder")


def standard_holder(board_size, mounting_holes):
    """Return renderer kwargs from [width,height] and [{x_mm,y_mm,diameter_mm}].

    Empty is a confirmed no-hole pattern, never an unknown pattern. The result
    describes a generic plate, not validated component/connector clearances.
    """
    if not isinstance(board_size, (list, tuple)) or len(board_size) != 2:
        raise ValueError("board_size must be [width_mm, height_mm]")
    width, height = [number(v, "board_size", True) for v in board_size]
    if not isinstance(mounting_holes, (list, tuple)):
        raise ValueError("mounting_holes must be an explicit list")
    points, details, screws = [], [], []
    for hole in mounting_holes:
        if not isinstance(hole, dict):
            raise ValueError("Each mounting hole needs x_mm, y_mm and diameter_mm")
        x, y = [number(hole[k], k) for k in ("x_mm", "y_mm")]
        diameter = number(hole["diameter_mm"], "diameter_mm", True)
        if abs(x) + diameter / 2 > width / 2 + 1e-6 or abs(y) + diameter / 2 > height / 2 + 1e-6:
            raise ValueError("Mounting drill extends beyond PCB bounding box")
        if any(math.hypot(x - p[0], y - p[1]) < 1e-5 for p in points):
            raise ValueError("Duplicate mounting hole centre")
        points.append([x, y])
        details.append(copy.deepcopy(hole))
        screws.append(screw_for_drill(diameter))
    return dict(breakout_pcb_width=width, breakout_pcb_height=height,
                mounting_holes=points, mounting_hole_details=details,
                mounting_hole_radius_names=screws,
                mounting_hole_radius_name=screws[0] if screws else "m2",
                mounting_lift=3)


def normalize_kwargs(kwargs):
    """Accept the two-input API while retaining existing legacy holder callers."""
    result = copy.deepcopy(kwargs)
    if "board_size" in result:
        geometry = standard_holder(result.pop("board_size"), result["mounting_holes"])
        result.update(geometry)
        result["mounting_lift"] = kwargs.get("mounting_lift", 3)
    return result
