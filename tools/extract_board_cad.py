"""Research-only extraction of connector pads from manufacturer CAD.

Outputs are reviewed and materialized in the family populate files. Neither
this module nor CAD parser packages are needed to load the final catalogue.
"""

import math
import re
import xml.etree.ElementTree as ET

import sexpdata


def rotate(**kwargs):
    x, y = kwargs["point"]
    angle = math.radians(kwargs.get("angle", 0))
    return (x * math.cos(angle) - y * math.sin(angle),
            x * math.sin(angle) + y * math.cos(angle))


def eagle(**kwargs):
    root = ET.parse(kwargs["path"])
    board = root.find(".//board")
    coordinates = []
    for wire in board.findall("plain/wire"):
        if wire.get("layer") == "20":
            coordinates.append((float(wire.get("x1")), float(wire.get("y1"))))
            coordinates.append((float(wire.get("x2")), float(wire.get("y2"))))
    x_min = min(point[0] for point in coordinates)
    x_max = max(point[0] for point in coordinates)
    y_min = min(point[1] for point in coordinates)
    y_max = max(point[1] for point in coordinates)
    centre = ((x_min + x_max) / 2, (y_min + y_max) / 2)
    landscape = x_max - x_min > y_max - y_min

    def transform(x, y):
        x -= centre[0]
        y -= centre[1]
        # Feather USB is at the left of its native Eagle drawing.
        return (y, -x) if landscape else (x, y)

    packages = {}
    for library in board.findall("libraries/library"):
        for package in library.findall("packages/package"):
            packages[(library.get("name"), package.get("name"))] = package
    signals = {}
    for signal in board.findall("signals/signal"):
        for contact in signal.findall("contactref"):
            signals[(contact.get("element"), contact.get("pad"))] = signal.get("name")
    pads = []
    holes = []
    for hole in board.findall("plain/hole"):
        x, y = transform(float(hole.get("x")), float(hole.get("y")))
        holes.append({"x_mm": round(x, 5), "y_mm": round(y, 5), "diameter_mm": float(hole.get("drill")), "source_id": "cad"})
    for element in board.findall("elements/element"):
        name = element.get("name")
        package = packages[(element.get("library"), element.get("package"))]
        rotation = element.get("rot", "R0")
        angle = float(re.search(r"R([\d.]+)", rotation).group(1))
        def place(pad):
            x = float(pad.get("x", 0))
            y = float(pad.get("y", 0))
            if "M" in rotation:
                x = -x
            x, y = rotate(point=(x, y), angle=angle)
            return transform(x + float(element.get("x")), y + float(element.get("y")))
        for hole in package.findall("hole") if "MOUNT" in element.get("package").upper() else []:
            x, y = place(hole)
            holes.append({"x_mm": round(x, 5), "y_mm": round(y, 5), "diameter_mm": float(hole.get("drill")), "source_id": "cad"})
        if "MOUNT" in element.get("package").upper():
            for pad in package.findall("pad"):
                x, y = place(pad)
                holes.append({"x_mm": round(x, 5), "y_mm": round(y, 5), "diameter_mm": float(pad.get("drill")), "source_id": "cad"})
        is_connector = element.get("package").startswith(("1X", "2X", "JST")) or name.startswith("TP")
        if not is_connector:
            continue
        for pad in list(package.findall("pad")) + list(package.findall("smd")):
            if not pad.get("name") or pad.get("name").startswith(("M", "NC")):
                continue
            x, y = place(pad)
            pads.append({
                "connector": name,
                "number": pad.get("name"),
                "name": signals.get((name, pad.get("name")), "NC"),
                "x_mm": round(x, 5),
                "y_mm": round(y, 5),
                "drill_mm": float(pad.get("drill")) if pad.get("drill") else None,
                "pad_kind": "through_hole" if pad.tag == "pad" else "surface_pad",
                "surface": "bottom" if "M" in rotation else "top",
                "source_id": "cad",
            })
    gpio_by_net = {}
    schematic = kwargs["path"].with_suffix(".sch")
    if schematic.exists():
        sch = ET.parse(schematic)
        mcu_parts = set()
        for part in sch.findall(".//schematic/parts/part"):
            if "ESP32" in part.get("deviceset", ""):
                mcu_parts.add(part.get("name"))
        for net in sch.findall(".//schematic/sheets/sheet/nets/net"):
            for pinref in net.findall("segment/pinref"):
                if pinref.get("part") not in mcu_parts:
                    continue
                match = re.search(r"(?:GPIO|IO)(\d+)", pinref.get("pin", ""))
                if match:
                    gpio_by_net[net.get("name")] = int(match.group(1))
    return {
        "width": round(y_max - y_min if landscape else x_max - x_min, 5),
        "height": round(x_max - x_min if landscape else y_max - y_min, 5),
        "pins": pads,
        "holes": holes,
        "gpio_by_net": gpio_by_net,
    }


def child(node, tag, default=None):
    for item in node:
        if isinstance(item, list) and item and str(item[0]) == tag:
            return item[1:]
    return default


def children(node, tag):
    return [item for item in node if isinstance(item, list) and item and str(item[0]) == tag]


def kicad(**kwargs):
    root = sexpdata.loads(kwargs["path"].read_text(encoding="utf-8"))
    edge_points = []
    for tag in ("gr_line", "gr_arc", "gr_rect"):
        for item in children(root, tag):
            if child(item, "layer") != ["Edge.Cuts"]:
                continue
            for key in ("start", "end", "mid"):
                point = child(item, key)
                if point:
                    edge_points.append(point[:2])
    # Some Seeed projects put the entire exterior inside the castellated
    # module footprint; root Edge.Cuts then contains only internal slots.
    for footprint in children(root, "footprint"):
        position = child(footprint, "at", [0, 0, 0])
        angle = -position[2] if len(position) > 2 else 0
        for tag in ("fp_line", "fp_arc", "fp_rect"):
            for item in children(footprint, tag):
                if child(item, "layer") != ["Edge.Cuts"]:
                    continue
                for key in ("start", "end", "mid"):
                    point = child(item, key)
                    if point:
                        x, y = rotate(point=point[:2], angle=angle)
                        edge_points.append((x + position[0], y + position[1]))
    x_min = min(point[0] for point in edge_points)
    x_max = max(point[0] for point in edge_points)
    y_min = min(point[1] for point in edge_points)
    y_max = max(point[1] for point in edge_points)
    centre = ((x_min + x_max) / 2, (y_min + y_max) / 2)
    orientation = 0
    for footprint in children(root, "footprint"):
        if "USB" not in str(footprint[1]).upper():
            continue
        position = child(footprint, "at", [0, 0])
        dx, dy = position[0] - centre[0], centre[1] - position[1]
        if abs(dx) > abs(dy):
            orientation = 90 if dx > 0 else -90
        elif dy < 0:
            orientation = 180
        break
    pads = []
    holes = []
    for footprint in children(root, "footprint"):
        properties = {}
        for item in children(footprint, "property"):
            properties[str(item[1])] = item[2]
        name = properties.get("Reference", "")
        position = child(footprint, "at")
        if not position:
            continue
        angle = -position[2] if len(position) > 2 else 0
        usb = "USB" in str(footprint[1]).upper()
        is_connector = name.startswith(("J", "TP")) or "HALF-HOLE" in str(footprint[1]).upper()
        for pad in children(footprint, "pad"):
            location = child(pad, "at", [0, 0])
            x, y = rotate(point=location[:2], angle=angle)
            x += position[0] - centre[0]
            y = centre[1] - position[1] - y
            x, y = rotate(point=(x, y), angle=orientation)
            drill = child(pad, "drill")
            if str(pad[2]) == "np_thru_hole" and drill and isinstance(drill[0], (int, float)) and drill[0] >= 1.8 and not usb:
                holes.append({"x_mm": round(x, 5), "y_mm": round(y, 5), "diameter_mm": drill[0], "source_id": "cad"})
            if not is_connector or usb or str(pad[1]) == "":
                continue
            net = child(pad, "net", [None, "NC"])
            pads.append({
                "connector": name,
                "number": str(pad[1]),
                "name": str(net[-1]).split("/")[-1],
                "x_mm": round(x, 5),
                "y_mm": round(y, 5),
                "drill_mm": drill[0] if drill and isinstance(drill[0], (int, float)) else None,
                "pad_kind": "through_hole" if str(pad[2]) == "thru_hole" else "surface_pad",
                "surface": "bottom" if child(footprint, "layer") == ["B.Cu"] else "top",
                "source_id": "cad",
            })
    unique = {}
    for pad in pads:
        key = (pad["connector"], pad["number"])
        if key not in unique or pad["pad_kind"] == "through_hole":
            unique[key] = pad
    width = y_max - y_min if orientation in (-90, 90) else x_max - x_min
    height = x_max - x_min if orientation in (-90, 90) else y_max - y_min
    return {"width": round(width, 5), "height": round(height, 5), "pins": list(unique.values()), "holes": holes}
