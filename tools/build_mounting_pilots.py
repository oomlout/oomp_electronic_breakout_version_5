"""Build the two mounting pilots, their render sheets and linked review pages.

Uses the shared OOBB presentation builder; does not commit or push.
"""

import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from urllib.parse import unquote, urlsplit

import yaml
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import mounting_research as research
from mounting_geometry import standard_holder

PILOTS = [
    "electronic_breakout_sensor_motion_accelerometer_adxl345_stemma_qt_adafruit_1231",
    "electronic_breakout_sensor_environmental_temperature_humidity_pressure_bme280_qwiic_sparkfun_sen_15440",
]
TITLES = ["Adafruit ADXL345 STEMMA QT", "SparkFun Qwiic BME280"]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def block(path, name, body):
    start, end = f"<!-- {name}:start -->", f"<!-- {name}:end -->"
    content = path.read_text(encoding="utf-8") if path.exists() else ""
    replacement = start + "\n" + body.rstrip() + "\n" + end
    if start in content or end in content:
        if content.count(start) != 1 or content.count(end) != 1 or content.index(start) > content.index(end):
            raise ValueError("Malformed review markers: " + str(path))
        content = content[:content.index(start)] + replacement + content[content.index(end)+len(end):]
    else:
        content = content.rstrip() + "\n\n" + replacement + "\n"
    path.write_text(content, encoding="utf-8")


def check_links(page):
    for target in re.findall(r"\]\(([^)]+)\)", page.read_text(encoding="utf-8")):
        parsed = urlsplit(target)
        if not parsed.scheme and parsed.path:
            path = page.parent / unquote(parsed.path)
            if not path.exists():
                raise ValueError(f"Missing link in {page}: {target}")


def build(presenter, *, render=True):
    if not presenter.is_file():
        raise FileNotFoundError("Shared OOBB presenter missing; pass --presenter PATH")
    results = []
    for part_id, title in zip(PILOTS, TITLES):
        print("Building " + title, flush=True)
        record = research.validate(part_id)
        if render:
            research.generate(part_id, render_stl=True)
            research.preview(part_id)
        receipt = research.verify_build(part_id)
        base = ROOT / "source_file" / part_id
        part = ROOT / "parts" / part_id
        geometry = standard_holder(record["board_size"], record["mounting_holes"])
        for extension in ("png", "svg"):
            shutil.copyfile(base/f"mounting_preview.{extension}", part/f"mounting.{extension}")
        with (part/"mounting.csv").open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(["id", "x_mm", "y_mm", "pcb_drill_diameter_mm", "holder_screw"])
            for h, screw in zip(record["mounting_holes"], geometry["mounting_hole_radius_names"]):
                writer.writerow([h["id"], h["x_mm"], h["y_mm"], h["diameter_mm"], screw])
        config_path = part / "presentation/config.json"
        config = json.loads(config_path.read_text()) if config_path.exists() else {}
        config.update(title=title, sources=[
            {"label": "Mounting evidence", "url": f"../../source_file/{part_id}/mounting.yaml"},
            {"label": "SCAD", "url": "3dpr.scad"},
            {"label": "Hole coordinates", "url": "mounting.csv"},
        ])
        count = len(record["mounting_holes"])
        screws = ", ".join(sorted({s.upper().replace("_", ".") for s in geometry["mounting_hole_radius_names"]}))
        config["installation"] = [
            "Select and print one mounting plate layout.",
            f"The plate uses {count} board fixing locations, sized for {screws} screws. The PCB drill diameters are listed below.",
            "Check screw length, screw-head clearance and underside component clearance against the physical board before fastening; physical fit has not been tested.",
        ]
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
        command = [sys.executable, str(presenter), str(part)]
        if not render:
            command.append("--readme-only")
        subprocess.run(command, cwd=ROOT, check=True)
        w, h = record["board_size"]
        body = (f"## Mounting pattern\n\n{w:g} × {h:g} mm PCB bounding box. "
                "Coordinates are millimetres, top view, with the origin at the PCB centre, +X right and +Y up.\n\n"
                "![Mounting coordinates](mounting.png)\n\n"
                "| Mount | X mm | Y mm | PCB drill mm | Holder screw |\n"
                "| --- | ---: | ---: | ---: | --- |\n")
        for hole, screw in zip(record["mounting_holes"], geometry["mounting_hole_radius_names"]):
            body += f"| `{hole['id']}` | {hole['x_mm']:g} | {hole['y_mm']:g} | {hole['diameter_mm']:g} | {screw.upper().replace('_', '.')} |\n"
        body += ("\nThe generic holder has a 3 mm plate and 3 mm board lift. Screw sizes are "
                 "the holder's design choice, not a manufacturer hardware recommendation.\n\n"
                 "[Vector drawing](mounting.svg) · [Coordinate CSV](mounting.csv) · "
                 f"[Evidence and revision](../../source_file/{part_id}/mounting.yaml) · "
                 f"[Build checks](../../source_file/{part_id}/mounting_build.json)\n")
        block(part/"README.md", "mounting-review", body)
        manifest = json.loads((part/"presentation/manifest.json").read_text())
        if manifest["source_sha256"] != digest(part/"working.yaml"):
            raise ValueError("Stale presentation metadata")
        for variant in manifest["variants"]:
            if variant["sha256"] != digest(part/variant["source"]):
                raise ValueError("Stale rendered mesh")
            with Image.open(part/variant["image"]) as image:
                assert image.size == (1600, 1000)
                image.verify()
            assert digest(part/variant["image"]) == digest(part/(Path(variant['source']).stem+'_presentation.png'))
        check_links(part/"README.md")
        results.append(dict(part_id=part_id, title=title, board_size=record["board_size"],
                            holes=count, mesh_check=receipt["mesh_check"],
                            artifacts={p.relative_to(ROOT).as_posix(): digest(p) for p in [
                                part/"3dpr.scad", part/"3dpr.stl", part/"README.md",
                                part/"mounting.png", part/"mounting.svg", part/"mounting.csv",
                                part/"presentation/images/3dpr.png", part/"presentation/manifest.json"]}))
    review = ROOT / "research/mounting/REVIEW.md"
    body = ("# Review the two mounting pilots\n\n"
            "Both boards have completed source validation, populate generation, SCAD/STL export "
            "and presentation rendering. Both STLs are single watertight solids. Physical fit remains untested.\n\n")
    for result in results:
        folder = "../../parts/" + result["part_id"]
        w, h = result["board_size"]
        body += (f"## {result['title']}\n\n{w:g} × {h:g} mm PCB; {result['holes']} mounting holes.\n\n"
                 f"[Open the part page]({folder}) · [Download STL]({folder}/3dpr.stl) · "
                 f"[Mounting drawing]({folder}/mounting.png)\n\n"
                 f"![{result['title']} holder, angled and top views]({folder}/presentation/images/3dpr.png)\n\n")
    body += ("## Check before accepting\n\nConfirm the selected carrier revision, mounting pattern and "
             "screw choice on each part page. The views show the generated holder without a board or fasteners. "
             "A successful mesh check does not establish connector or underside clearance.\n\n"
             "[Luna research pilot report](PILOT_REPORT.md) · [Full build manifest](full_build.json) · "
             "[Rebuild instructions](../../MOUNTING_RESEARCH.md)\n")
    review.write_text(body, encoding="utf-8")
    manifest_path = ROOT / "research/mounting/full_build.json"
    manifest_path.write_text(json.dumps(dict(pilots=results, result="passed"), indent=2)+"\n", encoding="utf-8")
    check_links(review)
    block(ROOT/"README.md", "mounting-pilots", "## Mounting pilot review\n\n"
          "[Review the ADXL345 and BME280 holders](research/mounting/REVIEW.md): renders, mounting patterns, "
          "printable STLs and source evidence.\n")
    print("Both full pilot builds and link/image/hash checks passed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--presenter", type=Path,
                        default=ROOT.parent/"oomlout_oobb_version_5/presentation/scripts/catalogue.py")
    parser.add_argument("--readme-only", action="store_true")
    args = parser.parse_args()
    build(args.presenter.resolve(), render=not args.readme_only)
