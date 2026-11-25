"""Paper-space A4 coordinate sheets using the shared opsvg primitives.

Only the verified mounting frame is drawn. A rectangle denotes the PCB's
bounding box, not an invented edge contour. Line weights and type stay constant
on paper while board dimensions and holes scale together.
"""

import copy
import html
import json
import math
from pathlib import Path
import shutil
import subprocess
import xml.etree.ElementTree as ET

import opsvg
import svg_styles
import yaml

from working_oomp_populate_coordinate import drawing_geometry

ROOT = Path(__file__).resolve().parent
NS = "http://www.w3.org/2000/svg"


def register_styles():
    base = yaml.safe_load((ROOT / "svg/styles/coordinate.yaml").read_text(encoding="utf-8"))["styles"]
    mono = yaml.safe_load((ROOT / "svg/styles/coordinate_monochrome.yaml").read_text(encoding="utf-8"))["styles"]
    svg_styles.STYLESHEETS["coordinate"] = base
    svg_styles.STYLESHEETS["coordinate_monochrome"] = svg_styles.merge(base, mono)


register_styles()


def number(value):
    return f"{value:.3f}".rstrip("0").rstrip(".") or "0"


def choose_scale(width, height, requested=None):
    maximum = min(120 / width, 78 / height)
    if requested is not None:
        if isinstance(requested, bool) or not isinstance(requested, (int, float)) or not math.isfinite(requested) or requested <= 0:
            raise ValueError("drawing_scale must be a positive finite number")
        if requested > maximum:
            raise ValueError(f"drawing_scale does not fit A4; maximum is {maximum:.3f}")
        return float(requested)
    for scale in (4, 3, 2.5, 2, 1.5, 1, 0.75, 0.5, 0.25):
        if scale <= maximum:
            return scale
    raise ValueError("Board is too large for this A4 template")


def scale_label(scale):
    return f"{number(scale)}:1" if scale >= 1 else f"1:{number(1 / scale)}"


class Sheet:
    """Top-left paper coordinates, converted once to opsvg's Y-up mm."""

    def __init__(self, thing):
        self.thing = thing

    def draw(self, shape, style, x, y, **kwargs):
        opsvg.se(self.thing, shape=shape, style=style, pos=[x, 297 - y, 0],
                 css_class=kwargs.pop("css_class", style.replace(".", "-")), **kwargs)

    def text(self, text, x, y, style="text", **kwargs):
        self.draw("text", style, x, y, text=html.escape(str(text)), **kwargs)

    def line(self, x1, y1, x2, y2, style="rule", **kwargs):
        self.draw("line", style, x1, y1, p1=[0, 0], p2=[x2 - x1, y1 - y2], **kwargs)

    def rect(self, x, y, width, height, style="panel", **kwargs):
        self.draw("rect", style, x + width / 2, y + height / 2, size=[width, height, 0], **kwargs)

    def dimension(self, p1, p2, label, offset, direction, style="dimension"):
        self.draw("dimension_line", style, 0, 0, p1=[p1[0], -p1[1]],
                  p2=[p2[0], -p2[1]], text=html.escape(label), offset=offset, direction=direction)

    def wrapped(self, text, x, y, max_width, style="text.small", leading=4.2, **kwargs):
        # Use font metrics to wrap the installed Arial/Consolas faces, with a
        # conservative width budget also suitable for common SVG fallbacks.
        from reportlab.pdfbase.pdfmetrics import stringWidth
        props = svg_styles.resolve(style, self.thing["styles"])
        size = kwargs.get("size", props.get("size", 3))
        face = "Courier" if "Consolas" in props.get("font", "") else "Helvetica"
        if props.get("font_weight") == "bold":
            face += "-Bold"
        lines, current = [], ""
        for word in str(text).split():
            candidate = (current + " " + word).strip()
            if current and stringWidth(candidate, face, size) > max_width * 0.94:
                lines.append(current)
                current = word
            else:
                current = candidate
        if current:
            lines.append(current)
        for index, line in enumerate(lines):
            self.text(line, x, y + index * leading, style, **kwargs)
        return y + len(lines) * leading


def get_coordinate_diagram(thing, **kwargs):
    board = kwargs.get("board", thing)
    geometry = drawing_geometry(board)
    width, height, holes = geometry["width"], geometry["height"], geometry["holes"]
    scale = choose_scale(width, height, kwargs.get("drawing_scale"))
    sheet_name = kwargs.get("stylesheet", "coordinate")
    thing["styles"] = svg_styles.merge(svg_styles.get_stylesheet("coordinate"),
                                       svg_styles.get_stylesheet(sheet_name))
    thing["styles"] = svg_styles.merge(thing["styles"], kwargs.get("part_styles", {}))
    thing["svg_components"] = []
    thing["coordinate_drawing"] = dict(geometry, scale=scale, stylesheet=sheet_name,
                                       outline_scope="pcb_bounding_box", paper_mm=[210, 297])
    s = Sheet(thing)
    s.rect(0, 0, 210, 297, "paper")
    s.line(14, 12, 32, 12, "accent", stroke_width=1.2)
    s.text("OOMLOUT  /  ELECTRONIC BREAKOUTS", 14, 18, "text.kicker")
    s.text("COORDINATE SHEET", 196, 18, "text.kicker", halign="right")
    title = board.get("name_readable") or board.get("name", "Electronic breakout").replace("_", " ")
    end = s.wrapped(title, 14, 30, 181, "text.title", leading=8)
    if end > 47:
        raise ValueError("Drawing title exceeds the two-line A4 header")
    s.text("Mechanical reference  /  PCB envelope + mounting centres", 14, 46, "text.small")
    s.line(14, 51, 196, 51)
    for x, caption, value in [(14, "ENVELOPE / MM", f"{number(width)} x {number(height)}"),
                              (78, "MOUNTING HOLES", f"{len(holes):02d}"),
                              (126, "DRAWING SCALE", scale_label(scale)),
                              (172, "VIEW", "TOP")]:
        s.text(caption, x, 58, "text.kicker")
        s.text(value, x, 65, "text.value")

    s.rect(14, 75, 182, 119)
    s.text("01 / GEOMETRY", 20, 81, "text.kicker")
    s.text("ALL DIMENSIONS IN mm", 190, 81, "text.kicker", halign="right")
    cx, cy = 105, 135
    left, right = cx - width * scale / 2, cx + width * scale / 2
    top, bottom = cy - height * scale / 2, cy + height * scale / 2

    def point(x, y):
        return cx + x * scale, cy - y * scale

    # Subtle grid at actual 5 mm intervals; no grid scaling of line weights.
    for x in range(math.ceil(-width / 10), math.floor(width / 10) + 1):
        px, _ = point(x * 5, 0)
        s.line(px, top - 3, px, bottom + 3, "grid")
    for y in range(math.ceil(-height / 10), math.floor(height / 10) + 1):
        _, py = point(0, y * 5)
        s.line(left - 3, py, right + 3, py, "grid")
    s.rect(left, top, width * scale, height * scale, "board")
    # Dashed centre lines are explicit line segments for portable SVG/PDF output.
    for x in range(math.floor(left - 4), math.ceil(right + 5), 4):
        s.line(x, cy, min(x + 2, right + 5), cy, "axis")
    for y in range(math.floor(top - 4), math.ceil(bottom + 5), 4):
        s.line(cx, y, cx, min(y + 2, bottom + 5), "axis")
    s.draw("circle", "accent", cx, cy, r=1.1, color="none", stroke=thing["styles"]["accent"]["color"], stroke_width=0.35)
    s.text("0,0", cx + 2.8, cy + 4, "text.mono", size=2.5)
    s.text("+X", right - 2, cy - 2.5, "text.small", halign="right")
    s.text("+Y", cx + 2.5, top - 4, "text.small")

    for hole in holes:
        x, y = point(hole["x_mm"], hole["y_mm"])
        radius = hole["diameter_mm"] * scale / 2
        s.draw("circle", "hole", x, y, r=radius, css_class="mounting-hole " + hole["label"])
        cross = radius + 1.1
        s.line(x - cross, y, x + cross, y, "axis")
        s.line(x, y - cross, x, y + cross, "axis")
        dx = -1 if hole["x_mm"] > 0 else 1
        dy = 1 if hole["y_mm"] > 0 else -1
        bx, by = x + dx * (radius + 4.5), y + dy * (radius + 4.5)
        s.line(x + dx * radius * 0.7, y + dy * radius * 0.7, bx, by, "rule")
        s.draw("circle", "badge", bx, by, r=3)
        s.text(hole["label"], bx, by, "text.badge")

    s.dimension((left, bottom), (right, bottom), number(width), -8, "horizontal")
    s.dimension((left, bottom), (left, top), number(height), -10, "vertical")
    # Extreme centre spans are dimensions between parallel reference lines;
    # absent corner holes are never inferred from an asymmetric pattern.
    if len(holes) > 1:
        xmin, xmax = min(h["x_mm"] for h in holes), max(h["x_mm"] for h in holes)
        ymin, ymax = min(h["y_mm"] for h in holes), max(h["y_mm"] for h in holes)
        if xmax > xmin:
            p1, p2 = point(xmin, ymax), point(xmax, ymax)
            s.dimension(p1, p2, number(xmax - xmin) + " c/c", p1[1] - top + 6, "horizontal", "dimension.pitch")
        if ymax > ymin:
            p1, p2 = point(xmax, ymin), point(xmax, ymax)
            s.dimension(p1, p2, number(ymax - ymin) + " c/c", right - p1[0] + 9, "vertical", "dimension.pitch")

    s.text("02 / MOUNTING COORDINATES", 14, 203, "text.kicker")
    s.text("CENTRE ORIGIN / mm", 112, 203, "text.kicker", halign="right")
    s.rect(14, 208, 98, 7)
    for label, x, align in [("ID", 17, "left"), ("X", 52, "right"), ("Y", 78, "right"), ("DIA", 108, "right")]:
        s.text(label, x, 211.5, "text.kicker", halign=align)
    for index, hole in enumerate(holes):
        y = 219.5 + index * 6.6
        s.text(hole["label"], 17, y, "text.mono")
        for key, x in [("x_mm", 52), ("y_mm", 78), ("diameter_mm", 108)]:
            value = hole[key]
            label = ("+" if value > 0 and key != "diameter_mm" else "") + number(value)
            s.text(label, x, y, "text.mono", halign="right")
        s.line(14, y + 3.3, 112, y + 3.3)
    if not holes:
        s.text("No mounting holes recorded in verified geometry.", 17, 220, "text.small")
    s.text("READING THE DRAWING", 123, 211.5, "text.kicker")
    s.wrapped("Origin at PCB bounding-box centre. +X right; +Y up. Top view in the recorded mounting frame.", 123, 219, 72)
    s.wrapped("Rectangle = PCB envelope. Edge radii, cutouts and components are not represented.", 123, 237, 72)

    # Provenance is embedded in full in the SVG; the paper footnote is compact.
    sources = geometry["sources"]
    cad = next((source for source in sources if "cad" in source.get("kind", "")), sources[0] if sources else {})
    s.line(14, 260, 196, 260)
    source_name = "Manufacturer CAD" if "cad" in cad.get("kind", "") else "Archived mounting evidence"
    s.text("VERIFIED GEOMETRY", 14, 266, "text.kicker")
    s.text(source_name + " / " + board.get("manufacturer_part_number", board.get("part_number", "")), 58, 266, "text.small")
    checksum = cad.get("sha256", "")
    evidence = "CAD SHA256 " + checksum[:20] if checksum else "Source references embedded in the SVG metadata"
    s.text(evidence, 14, 272, "text.small", font="Consolas, monospace", size=2.3)
    s.text("Dimensions govern. Tolerances are not specified.", 14, 278, "text.small")
    # A physical 20 mm paper ruler checks the printer independently of scale.
    for index in range(4):
        s.rect(164 + index * 5, 270, 5, 1.5, "badge" if index % 2 == 0 else "paper")
    s.line(164, 271.5, 184, 271.5)
    s.text("20 mm on paper", 174, 276, "text.small", size=2.2, halign="center")
    s.line(14, 283, 196, 283)
    s.text("A4 / Print at 100% / Do not fit to page", 14, 289, "text.small", size=2.2)
    s.text("OOMLOUT  /  " + board.get("md5_6_alpha", "REFERENCE").upper(), 196, 289, "text.kicker", halign="right", size=2.2)
    return thing


def coordinate_svg(thing):
    ET.register_namespace("", NS)
    root = ET.fromstring(opsvg.opsvg_get_svg(thing["svg_components"], padding=0))
    # The full-page paper primitive fixes the transform. Refuse enlarged pages
    # rather than silently changing the physical scale or cropping geometry.
    if root.get("viewBox") != "0 0 210.0000 297.0000":
        raise ValueError("Coordinate drawing exceeds the A4 canvas")
    root.set("role", "img")
    root.set("aria-labelledby", "drawing-title drawing-description")
    title = ET.Element(f"{{{NS}}}title", {"id": "drawing-title"})
    title.text = thing.get("name_readable", "Electronic breakout") + " coordinate diagram"
    root.insert(0, title)
    description = ET.Element(f"{{{NS}}}desc", {"id": "drawing-description"})
    description.text = "A4 top-view mounting reference. Origin at PCB envelope centre; X right, Y up; coordinates in millimetres."
    root.insert(1, description)
    metadata = ET.SubElement(root, f"{{{NS}}}metadata")
    metadata.text = json.dumps(thing["coordinate_drawing"], ensure_ascii=False)
    by_label = {hole["label"]: hole for hole in thing["coordinate_drawing"]["holes"]}
    for element in root:
        classes = element.get("class", "").split()
        if "mounting-hole" in classes:
            hole = by_label[classes[-1]]
            element.set("id", "mounting-" + hole["label"])
            for key in ("x_mm", "y_mm", "diameter_mm", "id", "source_id"):
                if key in hole:
                    element.set("data-" + key.replace("_", "-"), str(hole[key]))
    return ET.tostring(root, encoding="unicode") + "\n"


def export_pdf(svg_path, pdf_path):
    """Export the same SVG artwork as vector PDF, retaining exact A4 size."""
    executable = shutil.which("inkscape") or shutil.which("inkscape.com")
    if not executable:
        raise RuntimeError("Inkscape is required for coordinate-sheet PDF export; add it to PATH")
    subprocess.run([executable, str(Path(svg_path).resolve()), "--export-area-page",
                    "--export-type=pdf", "--export-filename=" + str(Path(pdf_path).resolve())],
                   check=True, capture_output=True, text=True, timeout=90)


def write_drawing(thing, folder, *, stem="working_coordinate_diagram", pdf=True, overwrite=True):
    if Path(stem).name != stem or "/" in stem or "\\" in stem or stem in ("", ".", ".."):
        raise ValueError("svg_output must be a filename stem without directories")
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    svg_path, pdf_path = folder / (stem + ".svg"), folder / (stem + ".pdf")
    if overwrite or not svg_path.exists():
        svg_path.write_text(coordinate_svg(thing), encoding="utf-8")
    if pdf and (overwrite or not pdf_path.exists()):
        export_pdf(svg_path, pdf_path)
    return {"svg": str(svg_path), **({"pdf": str(pdf_path)} if pdf else {})}
