"""Apply promoted mechanical research without changing a catalogue identity."""

import copy
from mounting_geometry import standard_holder
from working_oomp_populate_mounting_data import BOARD_MOUNTING


def identifier(option):
    return "_".join(str(option.get(f"taxonomy_{i}", "")) for i in range(1, 16)
                    if option.get(f"taxonomy_{i}"))


def apply_mounting(options, records=None):
    records = BOARD_MOUNTING if records is None else records
    for option in options:
        record = records.get(identifier(option))
        if record is None:
            continue
        geometry = standard_holder(record["board_size"], record["mounting_holes"])
        # Promoted geometry has its own evidence namespace; a legacy "cad"
        # source may describe a different revision or coordinate frame.
        for hole in geometry["mounting_hole_details"]:
            if "source_id" in hole:
                hole["source_id"] = "mounting_" + hole["source_id"]
        mounting_sources = [dict(copy.deepcopy(s), id="mounting_" + s["id"])
                            for s in record["sources"]]
        new_ids = {s["id"] for s in mounting_sources}
        option["sources"] = [s for s in option.get("sources", []) if s["id"] not in new_ids] + mounting_sources
        option.update(copy.deepcopy(geometry))
        option["mounting_research"] = copy.deepcopy(record)
        option["mounting_hole_status"] = record["status"]
        # Existing pin coordinates retain their own frame; the new frame is
        # explicitly scoped to mounting geometry and does not rotate pinouts.
        option["mounting_coordinate_system"] = copy.deepcopy(record["coordinate_system"])
        option["mounting_geometry_ready"] = bool(record["mounting_holes"])
        option["oobb_details"] = []
        if record["mounting_holes"]:
            option["oobb_details"] = [dict(copy.deepcopy(geometry),
                                          oobb_name="mounting_plate_default")]
        # Wire-holder adapters need a separate collision review, not automatic promotion.
    from mounting_variants import apply_variants
    apply_variants(options)
    return options
