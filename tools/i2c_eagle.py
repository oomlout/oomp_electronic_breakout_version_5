"""Extract a reviewed Eagle board's outline, selected connectors and mounting holes.

This utility retains native Eagle orientation and explicitly selected connector
references. It never guesses a USB direction or counts jumpers/chip leads as
external connector contacts. The output remains research evidence, not a change
to a populate definition.
"""

import argparse
import math
from pathlib import Path
import re
import xml.etree.ElementTree as ET

import yaml


def _outline_points(plain):
    points = []
    for wire in plain.findall("wire"):
        if wire.get("layer") != "20":
            continue
        x1, y1, x2, y2 = (float(wire.get(key)) for key in ("x1", "y1", "x2", "y2"))
        points.extend([(x1, y1), (x2, y2)])
        sweep = math.radians(float(wire.get("curve", "0")))
        if abs(sweep) < 1e-10:
            continue
        offset = 0.5 / math.tan(sweep / 2)
        cx = (x1 + x2) / 2 - (y2 - y1) * offset
        cy = (y1 + y2) / 2 + (x2 - x1) * offset
        radius = math.hypot(x1 - cx, y1 - cy)
        start = math.atan2(y1 - cy, x1 - cx)
        for angle in (0, math.pi / 2, math.pi, 3 * math.pi / 2):
            distance = (angle - start) % math.tau if sweep > 0 else (start - angle) % math.tau
            if distance <= abs(sweep) + 1e-9:
                points.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
    for circle in plain.findall("circle"):
        if circle.get("layer") == "20":
            x, y, radius = (float(circle.get(key)) for key in ("x", "y", "radius"))
            points.extend([(x - radius, y - radius), (x + radius, y + radius)])
    if not points:
        raise ValueError("No explicit board Dimension-layer outline found")
    return points


def extract(path, connector_names, source_id="cad_board", *, connector_kinds, excluded_pads=None):
    excluded_pads = set(excluded_pads or [])
    if set(connector_kinds) != set(connector_names) or any(
            kind not in {"header", "cable_connector"} for kind in connector_kinds.values()):
        raise ValueError("Explicit header/cable_connector kind required for every selected connector")
    board = ET.parse(path).find(".//board")
    if board is None:
        raise ValueError("Not an Eagle board")
    points = _outline_points(board.find("plain"))
    xmin, xmax = min(p[0] for p in points), max(p[0] for p in points)
    ymin, ymax = min(p[1] for p in points), max(p[1] for p in points)
    centre = ((xmin + xmax) / 2, (ymin + ymax) / 2)
    packages = {(lib.get("name"), package.get("name")): package
                for lib in board.findall("libraries/library")
                for package in lib.findall("packages/package")}
    nets = {(contact.get("element"), contact.get("pad")): signal.get("name")
            for signal in board.findall("signals/signal")
            for contact in signal.findall("contactref")}
    elements = {element.get("name"): element for element in board.findall("elements/element")}
    if set(connector_names) - set(elements):
        raise ValueError("Unknown selected connector reference")

    def place(element, point):
        x, y = float(point.get("x", "0")), float(point.get("y", "0"))
        rotation = element.get("rot", "R0")
        if "M" in rotation:
            x = -x
        match = re.search(r"R(-?[0-9.]+)", rotation)
        angle = math.radians(float(match.group(1))) if match else 0
        px = x * math.cos(angle) - y * math.sin(angle) + float(element.get("x")) - centre[0]
        py = x * math.sin(angle) + y * math.cos(angle) + float(element.get("y")) - centre[1]
        return round(px, 5), round(py, 5)

    pins, connectors, holes, excluded = {}, {}, [], []
    for hole in board.findall("plain/hole"):
        holes.append({"id": f"plain_hole_{len(holes) + 1}",
                      "x_mm": round(float(hole.get("x")) - centre[0], 5),
                      "y_mm": round(float(hole.get("y")) - centre[1], 5),
                      "diameter_mm": float(hole.get("drill")), "plated": False,
                      "source_id": source_id})
    for name, element in elements.items():
        package_name = element.get("package")
        package = packages[(element.get("library"), package_name)]
        if "MOUNT" in package_name.upper() or "STAND-OFF" in package_name.upper():
            for index, hole in enumerate(package.findall("hole") + package.findall("pad"), 1):
                if hole.get("drill"):
                    x, y = place(element, hole)
                    holes.append({"id": name + ("_" + str(index) if index > 1 else ""),
                                  "x_mm": x, "y_mm": y, "diameter_mm": float(hole.get("drill")),
                                  "plated": hole.tag == "pad", "source_id": source_id})
        if name not in connector_names:
            continue
        kind = connector_kinds[name]
        connectors[name] = {"kind": kind, "cad_package": package_name,
                            "value": element.get("value"), "contacts": [], "source_id": source_id}
        for pad in package.findall("pad") + package.findall("smd"):
            number = pad.get("name")
            if (name, number) in excluded_pads:
                excluded.append({"connector": name, "pad": number,
                                 "reason": "mechanical_anchor_not_a_cable_contact", "source_id": source_id})
                continue
            x, y = place(element, pad)
            key = name + "_" + number
            net_name = nets.get((name, number))
            pins[key] = {"connector": name, "number": number, "name": net_name or "NC",
                         "net_name": net_name, "label_status": "cad_net_name_not_verified_silkscreen",
                         "kind": kind, "x_mm": x, "y_mm": y,
                         "drill_mm": float(pad.get("drill")) if pad.get("drill") else None,
                         "source_id": source_id}
            connectors[name]["contacts"].append(key)
    header_count = sum(pin["kind"] == "header" for pin in pins.values())
    cable_count = sum(pin["kind"] == "cable_connector" for pin in pins.values())
    if excluded_pads != {(pad["connector"], pad["pad"]) for pad in excluded}:
        raise ValueError("An explicit excluded pad does not exist on a selected connector")
    return {
        "dimensions_mm": {"width": round(xmax - xmin, 5), "height": round(ymax - ymin, 5),
                          "pcb_thickness": None, "assembled_height": None, "scope": "carrier_pcb_outline",
                          "status": "documented_cad", "source_ids": [source_id]},
        "coordinate_system": {"units": "mm", "origin": "centre_of_dimension_layer_bounding_box",
                              "view": "top", "orientation": "native_Eagle_axes_no_rotation",
                              "native_centre_mm": list(centre), "status": "documented_cad"},
        "connectors": connectors, "pins": pins,
        "pin_count": {"header_contacts": header_count, "cable_connector_contacts": cable_count,
                      "total_exposed_contacts": len(pins),
                      "unique_nets": len({pin["net_name"] for pin in pins.values() if pin["net_name"]}),
                      "scope": "physical_connector_contacts_not_chip_package_pins",
                      "status": "documented_cad", "source_ids": [source_id]},
        "pin_names": sorted({pin["name"] for pin in pins.values()}),
        "mounting_holes": holes, "mounting_hole_status": "documented_cad",
        "excluded_mechanical_pads": excluded,
        "cad_elements": [{"reference": e.get("name"), "value": e.get("value"), "package": e.get("package")}
                         for e in elements.values()],
        "notes": ["Header pads and cable contacts are counted separately even on shared nets.",
                  "Connector footprint pad centres are not connector envelope/insertion clearances.",
                  "A matching CAD file does not prove the fitted chip variant in every shipped unit."],
        "extraction_review": {"connector_selection": "explicit",
                              "connector_kinds": "explicit",
                              "mechanical_pad_exclusions": "explicit_reviewed_pairs_only",
                              "mounting_holes": "plain holes plus MOUNT/STAND-OFF-named packages; inspect other packages manually"},
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("board", type=Path)
    parser.add_argument("--connectors", required=True, help="Comma-separated reviewed connector references")
    parser.add_argument("--connector-kinds", required=True,
                        help="Comma-separated REF=header or REF=cable_connector entries, one per connector")
    parser.add_argument("--exclude-pads", default="",
                        help="Comma-separated reviewed mechanical anchors REF:PAD; names alone do not prove mechanical function")
    parser.add_argument("--source-id", default="cad_board")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    kinds = dict(item.split("=", 1) for item in args.connector_kinds.split(","))
    exclusions = [tuple(item.split(":", 1)) for item in args.exclude_pads.split(",") if item]
    text = yaml.safe_dump(extract(args.board, args.connectors.split(","), args.source_id,
                                 connector_kinds=kinds, excluded_pads=exclusions), sort_keys=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text)
