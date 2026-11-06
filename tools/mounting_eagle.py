"""Deterministic EAGLE mechanical extraction with explicit hole selection.

Layer 20 defines the PCB bounds. All drilled package pads are candidates, not
automatically mounting holes. Unsupported outlines fail instead of guessing.
"""

import math
import re
import xml.etree.ElementTree as ET


def wire_points(wire):
    x1, y1, x2, y2 = [float(wire.get(k)) for k in ("x1", "y1", "x2", "y2")]
    points = [(x1, y1), (x2, y2)]
    sweep = math.radians(float(wire.get("curve", 0)))
    if abs(sweep) < 1e-10:
        return points
    if abs(sweep) >= 2 * math.pi or math.hypot(x2-x1, y2-y1) < 1e-10:
        raise ValueError("Unsupported degenerate outline arc")
    factor = 1 / (2 * math.tan(sweep / 2))
    cx, cy = (x1+x2)/2 - (y2-y1)*factor, (y1+y2)/2 + (x2-x1)*factor
    radius, start = math.hypot(x1-cx, y1-cy), math.atan2(y1-cy, x1-cx)
    for angle in (0, math.pi/2, math.pi, 3*math.pi/2):
        travelled = ((angle-start) if sweep > 0 else (start-angle)) % (2*math.pi)
        if travelled <= abs(sweep) + 1e-9:
            points.append((cx+radius*math.cos(angle), cy+radius*math.sin(angle)))
    return points


def inspect(path, quarter_turn=0):
    if quarter_turn not in (0, 1, 2, 3):
        raise ValueError("quarter_turn is counterclockwise 0, 1, 2 or 3")
    board = ET.parse(path).find(".//board")
    if board is None:
        raise ValueError("Not an XML EAGLE board")
    plain = board.find("plain")
    if plain is None:
        raise ValueError("No board outline")
    points = []
    for item in plain:
        if item.get("layer") != "20":
            continue
        if item.tag == "wire":
            points.extend(wire_points(item))
        elif item.tag == "circle":
            x, y, r = [float(item.get(k)) for k in ("x", "y", "radius")]
            points.extend([(x-r, y-r), (x+r, y+r)])
        else:
            raise ValueError(f"Unsupported layer-20 {item.tag}; use a reviewed drawing")
    if not points:
        raise ValueError("No plain layer-20 outline; footprint-defined outline needs review")
    xmin, xmax = min(p[0] for p in points), max(p[0] for p in points)
    ymin, ymax = min(p[1] for p in points), max(p[1] for p in points)
    cx, cy = (xmin+xmax)/2, (ymin+ymax)/2

    def centre(x, y):
        x, y = x-cx, y-cy
        for _ in range(quarter_turn):
            x, y = -y, x
        return round(x, 6), round(y, 6)

    candidates = []

    def add(id, x, y, drill, plated, package):
        x, y = centre(x, y)
        candidates.append(dict(id=id, x_mm=x, y_mm=y, diameter_mm=float(drill),
                               plated=plated, package=package))

    for index, hole in enumerate(plain.findall("hole"), 1):
        add(f"plain:{index}", float(hole.get("x")), float(hole.get("y")),
            hole.get("drill"), False, "plain")
    packages = {(lib.get("name"), pkg.get("name")): pkg
                for lib in board.findall("libraries/library") for pkg in lib.findall("packages/package")}
    for element in board.findall("elements/element"):
        package = packages[(element.get("library"), element.get("package"))]
        if any(p.get("layer") == "20" for p in package):
            raise ValueError("Footprint contains layer-20 geometry; verify board outline manually")
        rotation = element.get("rot", "R0")
        match = re.fullmatch(r"S?M?R(-?[\d.]+)", rotation)
        if not match:
            raise ValueError("Unsupported component rotation: " + rotation)
        angle = math.radians(float(match.group(1)))
        for index, hole in enumerate(package.findall("hole") + package.findall("pad"), 1):
            if not hole.get("drill"):
                continue
            x, y = float(hole.get("x", 0)), float(hole.get("y", 0))
            if "M" in rotation:
                x = -x
            x, y = x*math.cos(angle)-y*math.sin(angle), x*math.sin(angle)+y*math.cos(angle)
            x, y = x+float(element.get("x")), y+float(element.get("y"))
            suffix = "pad:" + hole.get("name") if hole.tag == "pad" else "hole:" + str(index)
            add(element.get("name") + ":" + suffix, x, y, hole.get("drill"),
                hole.tag == "pad", element.get("package"))
    size = [round(xmax-xmin, 6), round(ymax-ymin, 6)]
    if quarter_turn % 2:
        size.reverse()
    return dict(board_size=size, native_centre_mm=[cx, cy], quarter_turn=quarter_turn,
                candidates=candidates, outline_points=[list(centre(x, y)) for x, y in points])


def select(path, ids, quarter_turn=0):
    data = inspect(path, quarter_turn)
    by_id = {h["id"]: h for h in data["candidates"]}
    if len(ids) != len(set(ids)) or set(ids) - by_id.keys():
        raise ValueError("Duplicate or unknown selected mounting-hole ID")
    data["mounting_holes"] = [by_id[id] for id in ids]
    return data
