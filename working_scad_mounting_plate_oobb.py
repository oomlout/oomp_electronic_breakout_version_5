"""PCB mounting plate with grid-aligned 3 x 3 OOBB wire-holder adapters."""

import copy

import oobb
import scad_help
import working_scad_mounting_plate_default
from mounting_geometry import normalize_kwargs


def get_adapter_positions(width, height):
    """Return (x, y, rotated) placements on the host's M6 grid.

    Centre on the short axis (positive half-step for even grids). Place a
    single holder at the positive end of the long axis, or one at each end
    for six or more units. Outer hole rows align with the perimeter grid.
    """
    spacing = oobb.gv("osp")
    x = 0 if width % 2 else spacing / 2
    y = 0 if height % 2 else spacing / 2
    if width >= height:
        offset = (width - 3) * spacing / 2
        positions = [(offset, y, False)]
        if width >= 6:
            positions.insert(0, (-offset, y, False))
        return positions
    offset = (height - 3) * spacing / 2
    positions = [(x, offset, True)]
    if height >= 6:
        positions.insert(0, (x, -offset, True))
    return positions


def get_base(thing, **kwargs):
    kwargs = normalize_kwargs(kwargs)
    pos = kwargs.get("pos", [0, 0, 0])
    depth = kwargs.get("depth", 3)
    base_kwargs = copy.deepcopy(kwargs)
    base_kwargs["mounting_lift"] = kwargs.get("mounting_lift", 3) + 3
    base_kwargs["prepare_print"] = False
    base_kwargs["wire_adapter"] = True
    working_scad_mounting_plate_default.get_base(thing, **base_kwargs)

    width, height = working_scad_mounting_plate_default.get_plate_dimensions(**kwargs)
    for x, y, rotated in get_adapter_positions(width, height):
        adapter_pos = [pos[0] + x, pos[1] + y, pos[2]]
        add_adapter(
            thing, adapter_pos, depth, rotated,
            shift_wire_hole_x=kwargs.get("shift_wire_hole_x", 0),
            shift_wire_hole_y=kwargs.get("shift_wire_hole_y", 0),
        )

    if kwargs.get("prepare_print", False):
        scad_help.prepare_base_for_print(thing, pos, **kwargs)


def add_adapter(thing, pos, depth, rotated=False,
                shift_wire_hole_x=0, shift_wire_hole_y=0):
    # Cable opening through the plate.
    oobb.append_full(
        thing, type="negative", shape="oobb_hole", radius=6,
        depth=depth + 1,
        # Shift the opening in plate X/Y coordinates, keeping the screw grid fixed.
        pos=[pos[0] + shift_wire_hole_x, pos[1] + shift_wire_hole_y, pos[2] - 1],
    )

    # Side M3 holes lie halfway between the M6 holes of the wire holder:
    # (+/-7.5, +/-15), rotated a quarter turn for a portrait host plate.
    spacing = oobb.gv("osp")
    offsets = [(x, y) for x in (-spacing / 2, spacing / 2)
               for y in (-spacing, spacing)]
    for offset_x, offset_y in offsets:
        if rotated:
            offset_x, offset_y = -offset_y, offset_x
        x = pos[0] + offset_x
        y = pos[1] + offset_y
        oobb.append_full(
            thing, type="negative", shape="oobb_hole", radius_name="m3",
            # Preserve the original cutter reach where a PCB post overlaps.
            depth=depth + 5, pos=[x, y, pos[2] - 1],
        )
