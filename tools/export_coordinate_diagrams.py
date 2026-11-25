"""Generate three A4 demos through populate -> working_oomp -> working_svg.

python tools/export_coordinate_diagrams.py
python tools/export_coordinate_diagrams.py --stylesheet coordinate_monochrome
python tools/export_coordinate_diagrams.py --part-id <exact_id> --svg-only
"""

import argparse
import contextlib
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import working_oomp
import working_oomp_populate
import working_svg
from working_oomp_populate_coordinate import DEMO_IDS, drawing_geometry


def export(part_ids=None, *, stylesheet="coordinate", pdf=True, output=None):
    selected = DEMO_IDS if part_ids is None else list(dict.fromkeys(part_ids))
    if not selected:
        raise ValueError("Select at least one part")
    output = Path(output or ROOT / "output/pdf/coordinate_diagrams").resolve()
    # Validate the complete selection before materialising any records.
    options = working_oomp_populate.get_options(coordinate_diagrams=True, part_ids=selected)
    from oomp_populate_helper import build_oomp_id
    by_id = {build_oomp_id(option): option for option in options}
    for part_id in selected:
        if part_id not in by_id:
            raise ValueError("Unknown populate part ID: " + part_id)
        drawing_geometry(by_id[part_id])
    with contextlib.chdir(ROOT):
        working_oomp_populate.main(part_ids=selected, coordinate_diagrams=True,
                                   coordinate_stylesheet=stylesheet)
        working_oomp.main(part_ids=selected)
        drawings = working_svg.main(part_ids=selected, drawing="coordinate_diagram",
                                    stylesheet=stylesheet, export_pdf=pdf, navigation=False)
    output.mkdir(parents=True, exist_ok=True)
    by_id = {drawing["id"]: drawing for drawing in drawings}
    manifest = []
    for index, part_id in enumerate(selected, 1):
        drawing = by_id[part_id]
        slug = f"{index:02d}_" + drawing.get("manufacturer", "board") + "_" + drawing.get("part_number", "reference")
        files = {}
        for kind, source in drawing["drawing_files"].items():
            destination = output / (slug + "." + kind)
            shutil.copyfile(ROOT / source, destination)
            files[kind] = destination.name
        manifest.append(dict(id=part_id, name=drawing.get("name_readable"), files=files,
                             scale=drawing["coordinate_drawing"]["scale"], stylesheet=stylesheet))
    if pdf:
        from pypdf import PdfReader, PdfWriter
        writer = PdfWriter()
        for entry in manifest:
            reader = PdfReader(output / entry["files"]["pdf"])
            if len(reader.pages) != 1:
                raise ValueError("Expected one A4 page per coordinate sheet")
            page = reader.pages[0]
            if abs(float(page.mediabox.width) - 210 / 25.4 * 72) > 0.1 or abs(float(page.mediabox.height) - 297 / 25.4 * 72) > 0.1:
                raise ValueError("PDF export is not A4")
            writer.append(reader)
        writer.add_metadata({"/Title": "OOMLOUT - coordinate drawing demos", "/Author": "OOMLOUT"})
        with (output / "coordinate_demos.pdf").open("wb") as stream:
            writer.write(stream)
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--part-id", action="append", dest="part_ids", help="Exact part ID; repeat to select several. Default: three demos.")
    parser.add_argument("--stylesheet", choices=["coordinate", "coordinate_monochrome"], default="coordinate")
    parser.add_argument("--svg-only", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = export(args.part_ids, stylesheet=args.stylesheet, pdf=not args.svg_only, output=args.output)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
