import copy
import opsvg
import yaml
import os
import svg_help
import svg_styles
import json
import re
import textwrap
import xml.etree.ElementTree as ET
import working_svg_microcontroller_styles
from working_svg_coordinate import get_coordinate_diagram

# Register in process so the normal svg_help / per-part stylesheet path uses
# the same named sheet as the standalone catalogue exporter.
svg_styles.STYLESHEETS["microcontroller"] = working_svg_microcontroller_styles.get_stylesheet()


def get_microcontroller(thing, **kwargs):
    """Draw only documented pad/hole centres; show unlocated pins separately.

    Geometry uses the existing opsvg Y-up millimetre pipeline and named styles.
    Component packages and connector envelopes are not invented for decoration.
    """
    board = kwargs.get("board", thing)
    thing["styles"] = svg_styles.merge(
        svg_styles.get_stylesheet(kwargs.get("stylesheet", "microcontroller")),
        kwargs.get("part_styles", {}),
    )
    width = board["dimensions_mm"]["width"]
    height = board["dimensions_mm"]["height"]
    title_lines = textwrap.wrap(board["name_readable"], width=55)
    # Explicit canvas bounds include externally anchored labels. The generic
    # pipeline's text estimate is intentionally not used as a clipping box.
    longest_label = 0
    unlocated_count = 0
    for pin in board["pins"].values():
        longest_label = max(longest_label, len(pin["name"]) + 6)
        if pin["x_mm"] is None:
            unlocated_count += 1
    left = -max(50, width / 2 + longest_label * 0.9 + 8)
    right = max(50, width / 2 + longest_label * 0.9 + 8)
    if unlocated_count:
        right = max(right, width / 2 + 28 + longest_label * 1.1 + 24)
    top = height / 2 + 13 + (len(title_lines) - 1) * 3
    bottom = min(-height / 2 - 20, height / 2 - unlocated_count * 2.8 - 13)
    opsvg.se(thing, shape="rect", size=[right - left, top - bottom, 0], pos=[(right + left) / 2, (top + bottom) / 2, 0], color="#ffffff", stroke="none", stroke_width=0)
    opsvg.se(thing, shape="rect", style="board", size=[width, height, 0], pos=[0, 0, 0])
    for index, line in enumerate(title_lines):
        opsvg.se(thing, shape="text", style="label.title", text=line, pos=[0, height / 2 + 8 + (len(title_lines) - index - 1) * 3, 0])
    view = board["coordinate_system"].get("view") or ""
    orientation = "+Y towards USB" if "usb" in view and "no_usb" not in view else "orientation not established"
    scope = "nominal envelope" if board["dimensions_mm"].get("status") == "unverified" else "envelope"
    opsvg.se(thing, shape="text", style="label.detail", text=f"{width:g} x {height:g} mm {scope} | top view | {orientation}", pos=[0, height / 2 + 4, 0])
    for hole in board["mounting_hole_details"]:
        opsvg.se(thing, shape="circle", style="hole", r=hole["diameter_mm"] / 2, pos=[hole["x_mm"], hole["y_mm"], 0], css_class="mounting-hole")
    labels = set()
    unlocated = []
    for key, pin in board["pins"].items():
        if pin["x_mm"] is None:
            unlocated.append((key, pin))
            continue
        style = "pad"
        if pin["type"] == "ground":
            style = "pad.ground"
        elif pin["type"] == "power":
            style = "pad.power"
        elif "analog_input" in pin["capabilities"]:
            style = "pad.analog"
        if pin.get("gpio") is not None and not pin.get("available_for_general_io"):
            style = "pad.reserved"
        token = re.sub(r"[^a-zA-Z0-9_-]", "_", key)
        radius = min(0.85, max(0.35, pin.get("drill_mm") or 0.65))
        opsvg.se(thing, shape="circle", style=style, r=radius, pos=[pin["x_mm"], pin["y_mm"], 0], css_class="pin-target pin-id-" + token)
        # Castellations and drilled pads can share a net and a row. Keep one
        # label for that row while retaining every physical pad as a target.
        side = -1 if pin["x_mm"] < 0 else 1
        label_key = (pin["name"], side, round(pin["y_mm"], 1))
        if pin["connector"] == "bottom":
            text = "GP" + str(pin["gpio"]) if pin.get("gpio") is not None else pin["name"]
            opsvg.se(thing, shape="text", style="label", text=text, halign="left", rot=[0, 0, -60], pos=[pin["x_mm"], -height / 2 - 2.2, 0])
            continue
        connector = board.get("connectors", {}).get(pin["connector"], {})
        footprint = connector.get("cad_footprint", "").upper()
        if footprint:
            label_connector = "1X" in footprint or "HALF-HOLE" in footprint
        else:
            label_connector = not pin["connector"].startswith("TP")
        if label_connector and label_key not in labels and abs(pin["x_mm"]) >= width * 0.28:
            labels.add(label_key)
            text = pin["name"]
            if pin.get("gpio") is not None and str(pin["gpio"]) not in text:
                text += "/GP" + str(pin["gpio"])
            opsvg.se(thing, shape="text", style="label", text=text, halign="right" if side < 0 else "left", pos=[side * (width / 2 + 2), pin["y_mm"], 0])
    if unlocated:
        # Separate textual inventory. These rows are never drawn as pads and
        # are never offered as spatial SVG hit targets.
        x = width / 2 + 28
        opsvg.se(thing, shape="text", style="label.detail", text="UNLOCATED CONTACTS / NOT TO SCALE", halign="left", pos=[x, height / 2 + 2, 0])
        for index, (key, pin) in enumerate(unlocated):
            text = pin["connector"] + ":" + str(pin["number"]) + " " + pin["name"]
            if pin.get("gpio") is not None:
                text += " / GP" + str(pin["gpio"])
            opsvg.se(thing, shape="text", style="label.detail", text=text, halign="left", pos=[x, height / 2 - 2 - index * 2.8, 0])
    footer_y = min(-height / 2 - 12, height / 2 - len(unlocated) * 2.8 - 5)
    status = board["dimensions_mm"].get("status", "imported manufacturer evidence")
    opsvg.se(thing, shape="text", style="label.detail", text="Outline: " + status.replace("_", " ") + " | holes: " + board["mounting_hole_status"].replace("_", " "), pos=[0, footer_y, 0])
    if not board["pins"]:
        opsvg.se(thing, shape="text", style="label.board", text="PINOUT UNVERIFIED", pos=[0, -4, 0])


def microcontroller_svg(**kwargs):
    """Return an accessible SVG with physical-pad identifiers and metadata."""
    board = kwargs["board"]
    thing = {"svg_components": []}
    get_microcontroller(thing, board=board, part_styles=kwargs.get("part_styles", {}), stylesheet=kwargs.get("stylesheet", "microcontroller"))
    xml = opsvg.opsvg_get_svg(thing["svg_components"], padding=4)
    namespace = "http://www.w3.org/2000/svg"
    ET.register_namespace("", namespace)
    root = ET.fromstring(xml)
    root.set("role", "img")
    root.set("aria-label", board["name_readable"] + " pinout and mechanical reference")
    title = ET.SubElement(root, "{" + namespace + "}title")
    title.text = board["name_readable"]
    metadata = ET.SubElement(root, "{" + namespace + "}metadata")
    metadata.text = json.dumps({
        "coordinate_system": board["coordinate_system"],
        "dimensions_mm": board["dimensions_mm"],
        "data_gaps": board["data_gaps"],
        "sources": board["sources"],
    }, ensure_ascii=False)
    by_token = {}
    for key, pin in board["pins"].items():
        by_token["pin-id-" + re.sub(r"[^a-zA-Z0-9_-]", "_", key)] = (key, pin)
    for element in list(root):
        classes = element.get("class", "").split()
        for token in classes:
            if token not in by_token:
                continue
            key, pin = by_token[token]
            element.set("id", "pin-" + token[7:])
            element.set("data-pin", key)
            element.set("data-pin-type", pin["type"])
            element.set("data-capabilities", " ".join(pin["capabilities"]))
            element.set("data-signal-types", " ".join(pin["signal_types"]))
            element.set("data-x-mm", str(pin["x_mm"]))
            element.set("data-y-mm", str(pin["y_mm"]))
            element.set("data-source-id", pin["source_id"])
            element.set("aria-label", key + ": " + pin["name"])
            if pin.get("gpio") is not None:
                element.set("data-gpio", str(pin["gpio"]))
                element.set("data-available-for-general-io", str(pin["available_for_general_io"]).lower())
            if pin.get("adc_channel") is not None:
                element.set("data-adc-channel", str(pin["adc_channel"]))
                element.set("data-adc-unit", str(pin["adc_unit"]))
            tooltip = ET.SubElement(element, "{" + namespace + "}title")
            tooltip.text = key + ": " + pin["name"] + " | " + ", ".join(pin["functions"] + pin["restrictions"])
    return ET.tostring(root, encoding="unicode") + "\n"


def main(**kwargs):
    return make_svg(**kwargs)

def make_svg(**kwargs):
    typ = svg_help.get_typ(**kwargs)
    oomp_mode = "project"
    #oomp_mode = "oobb"
    filt = ""
    build_variables = svg_help.get_build_variables(typ, filter=filt)
    if True:
        for key in ("filter", "save_type", "navigation", "overwrite"):
            kwargs.setdefault(key, build_variables[key])
        kwargs["oomp_mode"] = oomp_mode
    parts = get_parts(kwargs, oomp_mode)

    kwargs["parts"] = parts

    results = svg_help.make_parts(**kwargs)

    if kwargs["navigation"]:
        oobb_style = False
        sort = svg_help.get_navigation_sort(oobb_style=oobb_style)
        svg_help.generate_navigation(sort=sort)
    return results


def get_parts(kwargs, oomp_mode):
    parts = []

    #load parts from parts/folder/working.yaml
    parts_directory = os.path.join(os.path.dirname(__file__), "parts")
    if not os.path.isdir(parts_directory):
        return parts

    selected = kwargs.get("part_ids")
    selected = None if selected is None else ({selected} if isinstance(selected, str) else set(selected))
    found = set()
    for folder in sorted(os.listdir(parts_directory)):
        if selected is not None and folder not in selected:
            continue
        folder_path = os.path.join(parts_directory, folder)
        if not os.path.isdir(folder_path):
            continue

        working_yaml_path = os.path.join(folder_path, "working.yaml")
        if not os.path.isfile(working_yaml_path):
            continue

        with open(working_yaml_path, "r", encoding="utf-8") as infile:
            loaded_part = yaml.safe_load(infile)

        if not isinstance(loaded_part, dict):
            continue

        for part in svg_help.expand_svg_jobs(loaded_part, kwargs):
            if oomp_mode == "oobb":
                part["kwargs"]["oomp_size"] = part["oobb_name"]
            parts.append(part)
            found.add(folder)
    if selected is not None and selected - found:
        raise ValueError("No matching SVG jobs for: " + ", ".join(sorted(selected - found)))
    return parts


def get_base(thing, **kwargs):

    prepare_print = kwargs.get("prepare_print", False)
    width = kwargs.get("width", 1)
    height = kwargs.get("height", 1)
    depth = kwargs.get("depth", 3)
    rot = kwargs.get("rot", [0,0,0])
    pos = kwargs.get("pos", [0,0,0])
    extra = kwargs.get("extra", "")



    #add plate
    if True:
        p3 = copy.deepcopy(kwargs)
        p3["shape"] = f"oobb_plate"
        p3["depth"] = depth
        #p3["m"] = "#"
        pos1 = copy.deepcopy(pos)
        p3["pos"] = pos1
        opsvg.se(thing,**p3)

    #add holes
    if True:
        p3 = copy.deepcopy(kwargs)
        p3["shape"] = f"oobb_holes"
        p3["depth"] = depth
        p3["radius_name"] = "m6"
        #p3["m"] = "#"
        pos1 = copy.deepcopy(pos)
        p3["pos"] = pos1
        opsvg.se(thing,**p3)

    #add text
    if True:
        p3 = copy.deepcopy(kwargs)
        p3["shape"] = f"text"
        p3["text"] = "Base Plate"
        p3["size"] = 10.0
        p3["font"] = "sans-serif"
        p3["halign"] = "left"
        p3["valign"] = "center"
        p3["color"] = "#000000"
        #p3["m"] = "#"
        pos1 = copy.deepcopy(pos)
        p3["pos"] = pos1
        opsvg.se(thing,**p3)

    if prepare_print:
        svg_help.prepare_base_for_print(thing, pos, **kwargs)


def get_fill_in_the_blanks(thing, **kwargs):
    svg_help.get_fill_in_the_blanks(thing, **kwargs)


def get_a4_sheet(thing, **kwargs):
    svg_help.get_a4_sheet(thing, **kwargs)


def get_label_76x50(thing, **kwargs):
    svg_help.get_label_76x50(thing, **kwargs)


def _default_label_boxes():
    """Default 3 × 4 grid matching the Project Bolt tin insert photo.

    Top row is 0.5 units tall (narrow label strip);
    the three lower rows are each 1.0 units tall.
    Total: 3 wide × 3.5 high = 12 boxes.
    """
    boxes = []
    n = 1
    layout = [
        (0.0, 0.5),   # top narrow row
        (0.5, 1.0),
        (1.5, 1.0),
        (2.5, 1.0),
    ]
    for (row_y, row_h) in layout:
        for col in range(3):
            boxes.append({
                "x": float(col),
                "y": row_y,
                "w": 1.0,
                "h": row_h,
                "name": f"box_{n}",
            })
            n += 1
    return boxes


def get_internal_label_sheet(thing, **kwargs):
    """Proportional grid label sheet for tin inserts.

    No dark background — boxes sit directly on the card, separated by the
    card's own fill showing through the gap.  Corner radii are computed per
    corner so junctions and card edges look geometrically correct:

      r_inner  = gap_mm / 2   — inner corners: arc exactly fills the gap void
      r_outer  = card_r - card_margin_mm  — outer corners: parallel to card edge

    Parameters
    ----------
    unit_mm        : float  — physical size of one grid unit in mm   (default 42.0)
    grid_w         : float  — grid width in units                    (default 3.0)
    grid_h         : float  — grid height in units                   (default 3.5)
    card_margin_mm : float  — card fill visible around the grid      (default 2.0)
                              unit_mm=42, grid_w=3, margin=2 → card_w=130 mm
    card_r         : float  — card corner radius in mm               (default 8.0)
    gap_frac       : float  — gap between boxes as fraction of unit_mm (default 0.07)
    boxes          : list   — list of box dicts.  Each dict may contain:
                               x, y        — top-left position in units (required)
                               w, h        — size in units              (required)
                               name        — identifier string          (default "box_N")
                               text        — display text               (defaults to name)
                               style       — box fill style             (default "plate.cell")
                               text_style      — text style             (default "label")
                               text_size       — font size override mm  (default from style)
                               halign          — text alignment         (default "center";
                                                 auto "left" when lined)
                               valign          — vertical alignment     (default "center";
                                                 auto "top" when lined)
                               lined           — fill box with ruled    (default False)
                                                 lines for handwriting
                               line_spacing_mm — spacing between lines  (default 6.0 mm)
                               (any extra keys are preserved and ignored)
    stylesheet     : str    — stylesheet name                        (default "project_bolt")
    """
    prepare_print  = kwargs.get("prepare_print", False)
    pos            = kwargs.get("pos", [0, 0, 0])
    unit_mm        = float(kwargs.get("unit_mm",         42.0))
    grid_w         = float(kwargs.get("grid_w",           3.0))
    grid_h         = float(kwargs.get("grid_h",           3.5))
    card_margin_mm = float(kwargs.get("card_margin_mm",   2.0))
    card_r         = float(kwargs.get("card_r",           8.0))
    gap_frac       = float(kwargs.get("gap_frac",         0.07))
    boxes          = kwargs.get("boxes", _default_label_boxes())

    # ── Derived dimensions ────────────────────────────────────────────────────
    sheet_w  = grid_w * unit_mm                       # 126.0 mm
    sheet_h  = grid_h * unit_mm                       # 147.0 mm
    card_w   = sheet_w + 2 * card_margin_mm           # 130.0 mm
    card_h   = sheet_h + 2 * card_margin_mm           # 151.0 mm
    gap_mm   = gap_frac * unit_mm                     #   2.94 mm

    # Corner radius rules:
    #   inner: arc radius = gap/2 → arc exactly reaches the gap centreline,
    #          filling the void where four box corners meet
    #   outer: parallel to the card's own rounded corner
    r_inner  = gap_mm / 2
    r_outer  = max(card_r - card_margin_mm, 0.0)

    _EPS = 1e-3   # tolerance for edge-touching checks

    def _radii(bx, by, bw, bh):
        """Return (r_tl, r_tr, r_br, r_bl) for a box at grid position (bx,by)."""
        at_left   = bx              < _EPS
        at_top    = by              < _EPS
        at_right  = (bx + bw - grid_w) > -_EPS
        at_bottom = (by + bh - grid_h) > -_EPS
        tl = r_outer if (at_left  and at_top)    else r_inner
        tr = r_outer if (at_right and at_top)    else r_inner
        br = r_outer if (at_right and at_bottom) else r_inner
        bl = r_outer if (at_left  and at_bottom) else r_inner
        return tl, tr, br, bl

    # ── Stylesheet ────────────────────────────────────────────────────────────
    if "styles" not in thing or not thing.get("styles"):
        sheet_name = kwargs.get("stylesheet", "project_bolt")
        thing["styles"] = svg_styles.get_stylesheet(sheet_name)

    # ── Card fill (drawn first — border comes last) ───────────────────────────
    pos1 = copy.deepcopy(pos)
    opsvg.se(thing, shape="rounded_rectangle", style="plate",
             size=[card_w, card_h, 0], r=card_r, pos=pos1,
             stroke="none", stroke_width=0)

    # ── Boxes ─────────────────────────────────────────────────────────────────
    # Box centre in Y-up coords (origin = card centre = sheet centre):
    #   cx = -sheet_w/2 + unit_mm*(bx + bw/2)
    #   cy =  sheet_h/2 - unit_mm*(by + bh/2)
    # gap_mm cancels in the centre calculation; only affects w_mm / h_mm.
    for i, box in enumerate(boxes):
        bx         = float(box.get("x", 0))
        by         = float(box.get("y", 0))
        bw         = float(box.get("w", 1))
        bh         = float(box.get("h", 1))
        name       = box.get("name",       f"box_{i + 1}")
        text       = box.get("text",       name)
        box_style  = box.get("style",      "plate.cell")
        txt_style  = box.get("text_style", "label")
        txt_size   = box.get("text_size",  None)
        lined      = bool(box.get("lined", False))
        line_spc   = float(box.get("line_spacing_mm", 6.0))

        # lined boxes default to top-left anchored text; explicit values win
        halign = box.get("halign", "left"   if lined else "center")
        valign = box.get("valign", "top"    if lined else "center")

        w_mm = bw * unit_mm - gap_mm
        h_mm = bh * unit_mm - gap_mm
        cx   = -sheet_w / 2 + unit_mm * (bx + bw / 2)
        cy   =  sheet_h / 2 - unit_mm * (by + bh / 2)

        tl, tr, br, bl = _radii(bx, by, bw, bh)

        pos1    = copy.deepcopy(pos)
        pos1[0] += cx
        pos1[1] += cy

        # 1. Box fill
        opsvg.se(thing, shape="rrect_corners", style=box_style,
                 size=[w_mm, h_mm, 0],
                 r_tl=tl, r_tr=tr, r_br=br, r_bl=bl,
                 pos=pos1)

        # 2. Ruled lines (drawn before text so text sits on top)
        if lined:
            pad_x      = gap_mm * 1.5          # horizontal inset
            pad_y      = gap_mm                # top / bottom inset
            rule_w     = w_mm - 2 * pad_x
            rule_thick = 0.35
            y_from_top = pad_y + line_spc * 0.65   # first line
            while y_from_top + rule_thick / 2 < h_mm - pad_y:
                # Y-up offset from box centre: positive = up
                line_dy = h_mm / 2 - y_from_top
                lpos    = copy.deepcopy(pos)
                lpos[0] += cx
                lpos[1] += cy + line_dy
                opsvg.se(thing, shape="rect", style="rule",
                         size=[rule_w, rule_thick, 0], pos=lpos)
                y_from_top += line_spc

        # 3. Text — anchor point offset so halign/valign align to box edge
        padding = gap_mm
        off_x = {"left":  -(w_mm / 2 - padding),
                 "right":  (w_mm / 2 - padding),
                 "center": 0.0}.get(halign, 0.0)
        off_y = {"top":    (h_mm / 2 - padding),    # Y-up: positive = up
                 "bottom": -(h_mm / 2 - padding),
                 "center": 0.0}.get(valign, 0.0)

        txt_pos    = copy.deepcopy(pos)
        txt_pos[0] += cx + off_x
        txt_pos[1] += cy + off_y

        txt_kwargs = dict(halign=halign, valign=valign)
        if txt_size is not None:
            txt_kwargs["size"] = txt_size
        opsvg.se(thing, shape="text", style=txt_style,
                 text=text, pos=txt_pos, **txt_kwargs)

    # ── Card border (drawn last — on top of everything) ───────────────────────
    pos1 = copy.deepcopy(pos)
    opsvg.se(thing, shape="rounded_rectangle", style="plate.outline",
             size=[card_w, card_h, 0], r=card_r, pos=pos1)

    if prepare_print:
        svg_help.prepare_base_for_print(thing, pos, **kwargs)


if __name__ == '__main__':
    kwargs = {}
    main(**kwargs)
