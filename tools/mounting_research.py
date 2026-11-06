"""One-board mechanical research, validation and promotion. See MOUNTING_RESEARCH.md."""

import argparse
import ast
import contextlib
import copy
from datetime import datetime, timezone
import hashlib
from functools import lru_cache
import json
from pathlib import Path
import pprint
import re
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from mounting_geometry import standard_holder
from tools.mounting_eagle import inspect, select

CHECKS = ("identity", "outline", "hole_selection", "coordinate_frame", "conflicts_resolved")


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@lru_cache(maxsize=1)
def boards():
    from working_oomp_populate import get_options
    from working_oomp_populate_mounting import identifier
    return {identifier(b): b for b in get_options(apply_mounting=False)}


def folder(part_id, root=ROOT):
    if not re.fullmatch(r"[a-z0-9_]+", part_id) or part_id not in boards():
        raise ValueError("Use an exact current catalogue board ID")
    return Path(root) / "source_file" / part_id


def local(base, relative):
    if not relative or Path(relative).is_absolute() or "\\" in relative:
        raise ValueError("Evidence paths must be relative forward-slash paths")
    result = (base / relative).resolve()
    if not result.is_relative_to(base.resolve()):
        raise ValueError("Evidence path escapes board folder")
    if not result.exists():
        raise FileNotFoundError(f"Evidence not found: {result}. --file is relative to source_file/<ID>/, not the repository.")
    return result


def atomic(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(text, encoding="utf-8")
    temp.replace(path)


def save(base, record):
    record["updated_at"] = now()
    atomic(base / "mounting.yaml", yaml.safe_dump(record, sort_keys=False, allow_unicode=True))


def seed(part_id, root=ROOT):
    base = folder(part_id, root)
    if (base / "mounting.yaml").exists():
        return load(part_id, root)
    board = boards()[part_id]
    record = dict(schema_version=1, part_id=part_id, status="in_progress",
                  board_revision=None, identity_evidence=None, board_size=None,
                  mounting_holes=None,
                  coordinate_system=dict(units="mm", origin="pcb_bounding_box_centre",
                                         view="top", x_positive="right", y_positive="up"),
                  method=None, geometry_source_id=None, derivation=None,
                  review={key: False for key in CHECKS}, reviewed_by=None,
                  sources=[], attempts=[], conflicts=[], notes=[],
                  fit_status="generic_holder_not_physical_fit_tested")
    save(base, record)
    context = {key: board.get(key) for key in
               ("name_readable", "manufacturer", "part_number", "webpage", "sources",
                "dimensions_mm", "coordinate_system", "mounting_hole_details")}
    atomic(base / "mounting_context.json", json.dumps(context, indent=2))
    return base, record


def load(part_id, root=ROOT):
    base = folder(part_id, root)
    record = yaml.safe_load((base / "mounting.yaml").read_text(encoding="utf-8"))
    if not isinstance(record, dict) or record.get("part_id") != part_id:
        raise ValueError("Record identity mismatch")
    return base, record


def register(part_id, relative, url, source_id, kind, locator, root=ROOT):
    base, record = seed(part_id, root)
    content = local(base, relative).read_bytes()
    if not content or not re.match(r"https?://", url):
        raise ValueError("Need non-empty evidence and its original HTTP(S) URL")
    source = dict(id=source_id, local_file=relative, url=url, kind=kind, locator=locator,
                  registered_at=now(), bytes=len(content), sha256=hashlib.sha256(content).hexdigest())
    # Registration verifies existing bytes; it does not pretend they were fetched today.
    record["sources"] = [s for s in record["sources"] if s["id"] != source_id] + [source]
    save(base, record)
    return source


def extract(part_id, source_id, ids, quarter_turn=0, root=ROOT):
    base, record = load(part_id, root)
    source = next(s for s in record["sources"] if s["id"] == source_id)
    data = select(local(base, source["local_file"]), ids, quarter_turn)
    record.update(board_size=data["board_size"],
                  mounting_holes=[dict(h, source_id=source_id) for h in data["mounting_holes"]],
                  method="eagle", geometry_source_id=source_id,
                  extraction=dict(selected_ids=ids, quarter_turn=quarter_turn,
                                  native_centre_mm=data["native_centre_mm"]),
                  derivation="EAGLE layer-20 bounds; explicit package/plain drills; centred then rotated CCW.")
    record["status"] = "in_progress"
    record["review"] = {key: False for key in CHECKS}
    save(base, record)
    atomic(base / "mounting_candidates.json", json.dumps(data, indent=2))
    return record


def validate(part_id, root=ROOT):
    base, record = load(part_id, root)
    if record.get("schema_version") != 1 or record.get("status") not in ("verified", "no_holes"):
        raise ValueError("Only verified/no_holes records can be promoted")
    for key in ("board_revision", "identity_evidence", "derivation", "reviewed_by"):
        if not isinstance(record.get(key), str) or not record[key].strip():
            raise ValueError("Missing review field: " + key)
    if any(record.get("review", {}).get(k) is not True for k in CHECKS):
        raise ValueError("Complete every semantic review check")
    if record.get("conflicts"):
        raise ValueError("Unresolved mechanical conflicts must be escalated")
    expected_frame = dict(units="mm", origin="pcb_bounding_box_centre", view="top",
                          x_positive="right", y_positive="up")
    if record.get("coordinate_system") != expected_frame:
        raise ValueError("Mounting coordinates must use the documented top/centre/mm frame")
    sources = record.get("sources", [])
    by_id = {s["id"]: s for s in sources}
    if len(by_id) != len(sources) or not sources:
        raise ValueError("Missing or duplicate sources")
    for source in sources:
        if not source.get("locator") or not re.match(r"https?://", source.get("url", "")):
            raise ValueError("Each source needs URL and exact page/CAD locator")
        content = local(base, source["local_file"]).read_bytes()
        if len(content) != source["bytes"] or hashlib.sha256(content).hexdigest() != source["sha256"]:
            raise ValueError("Evidence hash/size mismatch: " + source["id"])
    geometry_source = record.get("geometry_source_id")
    if geometry_source not in by_id or not record.get("identity_source_ids") or not set(record["identity_source_ids"]) <= by_id.keys():
        raise ValueError("Geometry and identity must reference registered sources")
    standard_holder(record["board_size"], record["mounting_holes"])
    if (record["status"] == "no_holes") != (len(record["mounting_holes"]) == 0):
        raise ValueError("No-hole status must agree with the explicit pattern")
    for hole in record["mounting_holes"]:
        if hole.get("source_id") not in by_id:
            raise ValueError("Every hole needs a registered source")
    if record.get("method") == "eagle":
        extraction = record["extraction"]
        actual = select(local(base, by_id[geometry_source]["local_file"]),
                        extraction["selected_ids"], extraction["quarter_turn"])
        if actual["board_size"] != record["board_size"]:
            raise ValueError("Board dimensions disagree with archived CAD")
        expected = [dict(h, source_id=geometry_source) for h in actual["mounting_holes"]]
        if expected != record["mounting_holes"]:
            raise ValueError("Mounting holes disagree with archived CAD")
    elif record.get("method") != "dimensioned_drawing":
        raise ValueError("Use eagle or dimensioned_drawing; photos/estimates cannot be promoted")
    return record


def promoted_records(root=ROOT):
    path = Path(root) / "working_oomp_populate_mounting_data.py"
    if not path.exists():
        return {}
    tree = ast.parse(path.read_text(encoding="utf-8"))
    assignment = next(n for n in tree.body if isinstance(n, ast.Assign)
                      and any(isinstance(t, ast.Name) and t.id == "BOARD_MOUNTING" for t in n.targets))
    return ast.literal_eval(assignment.value)


def promotion_value(record):
    return {k: copy.deepcopy(record[k]) for k in
            ("status", "board_size", "mounting_holes", "coordinate_system", "board_revision",
             "sources", "fit_status", "derivation", "reviewed_by", "identity_evidence")}


def promote(part_id, root=ROOT):
    record = validate(part_id, root)
    records = promoted_records(root)
    value = promotion_value(record)
    value["research_file"] = f"source_file/{part_id}/mounting.yaml"
    value["record_sha256"] = hashlib.sha256((folder(part_id, root)/"mounting.yaml").read_bytes()).hexdigest()
    records[part_id] = value
    text = ('"""Generated by tools/mounting_research.py promote; do not edit by hand."""\n\n'
            + "BOARD_MOUNTING = " + pprint.pformat(records, sort_dicts=True, width=110) + "\n")
    atomic(Path(root) / "working_oomp_populate_mounting_data.py", text)
    return value


def queue(root=ROOT):
    promoted = promoted_records(root)
    rows = []
    for part_id, board in boards().items():
        path = folder(part_id, root) / "mounting.yaml"
        status = "pending"
        if path.exists():
            record = yaml.safe_load(path.read_text(encoding="utf-8"))
            status = record.get("status", "needs_review")
            if part_id in promoted:
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                status = "promoted" if promoted[part_id].get("record_sha256") == digest else "stale_promotion"
                if status == "promoted":
                    receipt_path = path.with_name("mounting_build.json")
                    receipt = json.loads(receipt_path.read_text()) if receipt_path.exists() else {}
                    if receipt.get("record_sha256") != digest or any(
                            not (Path(root)/a["path"]).is_file() for a in receipt.get("artifacts", [])):
                        status = "awaiting_generation"
        rows.append(dict(part_id=part_id, status=status, name=board.get("name_readable", part_id)))
    return rows


def preview(part_id, root=ROOT):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, Rectangle
    base, record = load(part_id, root)
    geometry = standard_holder(record["board_size"], record["mounting_holes"])
    width, height = record["board_size"]
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.add_patch(Rectangle((-width/2, -height/2), width, height, fill=False))
    for hole, screw in zip(record["mounting_holes"], geometry["mounting_hole_radius_names"]):
        x, y, d = [hole[k] for k in ("x_mm", "y_mm", "diameter_mm")]
        ax.add_patch(Circle((x, y), d/2, fill=False, color="tab:blue"))
        ax.annotate(f'{hole.get("id", "hole")}\n({x:g}, {y:g}) D{d:g} / {screw}',
                    (x, y), xytext=(0, 12), textcoords="offset points", ha="center", fontsize=7,
                    parse_math=False)
    ax.axhline(0, color="gray", lw=.5)
    ax.axvline(0, color="gray", lw=.5)
    ax.set(xlim=(-width/2-8, width/2+8), ylim=(-height/2-8, height/2+8),
           xlabel="X mm (right)", ylabel="Y mm (up)", aspect="equal",
           title=f"Top view: {width:g} x {height:g} mm\nPCB bounding box and selected mounting drills")
    fig.tight_layout()
    path = base / "mounting_preview.png"
    fig.savefig(path, dpi=160)
    with matplotlib.rc_context({"svg.hashsalt": part_id}):
        fig.savefig(base / "mounting_preview.svg", metadata={"Date": None})
    plt.close(fig)
    return str(path)


def archive_superseded(part_id, no_holes=False, root=ROOT):
    """Keep old generated holders reviewable without offering them as current builds."""
    import tempfile
    base = (Path(root) / "parts" / part_id).resolve()
    if not base.is_relative_to((Path(root)/"parts").resolve()):
        raise ValueError("Part path escapes parts directory")
    names = ["working_oobb" + ext for ext in (".scad", ".stl", ".png", ".yaml", "_thing.yaml")]
    if no_holes:
        names += ["3dpr" + ext for ext in (".scad", ".stl", ".png")]
    paths = [base/name for name in names if (base/name).is_file()]
    if not paths:
        return []
    archive = base / "mounting_superseded"
    archive.mkdir(parents=True, exist_ok=True)
    destination = Path(tempfile.mkdtemp(prefix="previous_", dir=archive))
    moved = []
    for path in paths:
        if path.is_symlink():
            raise ValueError("Refusing to archive a symlink artifact")
        target = destination / path.name
        path.rename(target)
        moved.append(target.relative_to(Path(root).resolve()).as_posix())
    return moved


def generate(part_id, render_stl=False):
    """Run the real populate -> parts -> standard plate pipeline for exactly one board."""
    with contextlib.chdir(ROOT):
        return _generate(part_id, render_stl)


def _generate(part_id, render_stl):
    from working_oomp_populate_mounting import apply_mounting
    from oomp_populate_helper import write_extras
    import working_oomp
    import working_scad
    import scad_help
    validate(part_id)
    record = promoted_records().get(part_id)
    digest = hashlib.sha256((folder(part_id)/"mounting.yaml").read_bytes()).hexdigest()
    if not record or record.get("record_sha256") != digest:
        raise ValueError("Promote the current validated record before generating")
    option = copy.deepcopy(boards()[part_id])
    apply_mounting([option], {part_id: record})
    write_extras([option])
    working_oomp.main(part_ids=[part_id])
    archived = archive_superseded(part_id, no_holes=not record["mounting_holes"])
    def receipt(artifacts, mesh_check=None):
        data = dict(record_sha256=digest, generated_at=now(),
                    physical_fit_tested=False, artifacts=artifacts, superseded_artifacts=archived,
                    mesh_check=mesh_check)
        atomic(folder(part_id)/"mounting_build.json", json.dumps(data, indent=2))
    if not record["mounting_holes"]:
        receipt([])
        return "Confirmed no holes; no screw holder generated"
    parts = working_scad.get_parts(dict(modes=["3dpr"], save_type="none", overwrite=True), "project")
    selected = [p for p in parts if p.get("id") == part_id and p["oobb_name"] == "mounting_plate_default"]
    if len(selected) != 1:
        raise ValueError("Expected one populated standard holder")
    scad_help.make_scad_generic(selected[0])
    path = ROOT / "parts" / part_id / "3dpr.scad"
    if not path.is_file():
        raise ValueError("SCAD pipeline produced no output")
    mesh_check = None
    if render_stl:
        import subprocess
        import trimesh
        temporary_stl = path.with_name("3dpr.mounting_tmp.stl")
        try:
            result = subprocess.run(["openscad", "-o", str(temporary_stl), str(path)],
                                    capture_output=True, text=True, timeout=180)
            if result.returncode or "ERROR:" in result.stderr or not temporary_stl.is_file():
                raise ValueError("OpenSCAD failed: " + result.stderr[-2000:])
            mesh = trimesh.load(temporary_stl, force="mesh")
            if not mesh.is_watertight or mesh.body_count != 1 or mesh.volume <= 0:
                raise ValueError("Holder STL is not one positive-volume watertight solid; needs review")
            mesh_check = dict(watertight=True, bodies=1, volume_mm3=float(mesh.volume),
                              bounds_mm=mesh.bounds.tolist())
            temporary_stl.replace(path.with_suffix(".stl"))
        finally:
            temporary_stl.unlink(missing_ok=True)
    paths = [path] + ([path.with_suffix(".stl")] if render_stl else [])
    receipt([dict(path=p.relative_to(ROOT).as_posix(), bytes=p.stat().st_size,
                  sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in paths], mesh_check)
    return str(path)


def verify_build(part_id, root=ROOT):
    record = validate(part_id, root)
    base = folder(part_id, root)
    digest = hashlib.sha256((base/"mounting.yaml").read_bytes()).hexdigest()
    promoted = promoted_records(root).get(part_id, {})
    receipt = json.loads((base/"mounting_build.json").read_text())
    if promoted.get("record_sha256") != digest or receipt.get("record_sha256") != digest:
        raise ValueError("Stale promotion or generation receipt")
    artifacts = receipt["artifacts"]
    if record["mounting_holes"] and not artifacts:
        raise ValueError("Holder has no generated artifacts")
    for artifact in artifacts:
        path = local(Path(root), artifact["path"])
        content = path.read_bytes()
        if len(content) != artifact["bytes"] or hashlib.sha256(content).hexdigest() != artifact["sha256"]:
            raise ValueError("Generated artifact changed: " + artifact["path"])
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("queue")
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--status", default="actionable")
    for name in ("seed", "validate", "promote", "preview", "generate", "verify-build"):
        p = sub.add_parser(name)
        p.add_argument("part_id")
        if name == "generate":
            p.add_argument("--stl", action="store_true")
    p = sub.add_parser("register")
    p.add_argument("part_id")
    for flag in ("file", "url", "source-id", "kind", "locator"):
        p.add_argument("--" + flag, required=True)
    p = sub.add_parser("inspect-eagle")
    p.add_argument("path", type=Path)
    p.add_argument("--quarter-turn", type=int, default=0)
    p.add_argument("--all-drills", action="store_true")
    p = sub.add_parser("eagle")
    p.add_argument("part_id")
    p.add_argument("--source-id", required=True)
    p.add_argument("--holes", required=True, help="Comma-separated explicit candidate IDs; empty for no holes")
    p.add_argument("--quarter-turn", type=int, default=0)
    args = parser.parse_args()
    if args.command == "queue":
        rows = queue()
        actionable = {"pending", "in_progress", "verified", "no_holes", "stale_promotion", "awaiting_generation"}
        selected = [r for r in rows if args.status == "all" or r["status"] == args.status
                    or (args.status == "actionable" and r["status"] in actionable)]
        selected.sort(key=lambda r: r["status"] == "pending")
        print(json.dumps({"counts": {s: sum(r["status"] == s for r in rows) for s in sorted({r["status"] for r in rows})},
                          "boards": selected[:args.limit]}, indent=2))
    elif args.command == "seed":
        print(seed(args.part_id)[0] / "mounting.yaml")
    elif args.command == "register":
        print(json.dumps(register(args.part_id, args.file, args.url, args.source_id, args.kind, args.locator), indent=2))
    elif args.command == "inspect-eagle":
        data = inspect(args.path, args.quarter_turn)
        data.pop("outline_points")
        data["total_drilled_candidates"] = len(data["candidates"])
        if not args.all_drills:
            data["candidates"] = [h for h in data["candidates"] if h["diameter_mm"] >= 1.8]
        print(json.dumps(data, indent=2))
    elif args.command == "eagle":
        record = extract(args.part_id, args.source_id, [s for s in args.holes.split(",") if s], args.quarter_turn)
        print(json.dumps({k: record[k] for k in ("board_size", "mounting_holes", "status")}, indent=2))
    elif args.command == "validate":
        validate(args.part_id)
        print("Validated " + args.part_id)
    elif args.command == "promote":
        promote(args.part_id)
        print("Promoted " + args.part_id)
    elif args.command == "preview":
        print(preview(args.part_id))
    elif args.command == "generate":
        print(generate(args.part_id, args.stl))
    elif args.command == "verify-build":
        print(json.dumps(verify_build(args.part_id), indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, StopIteration, FileNotFoundError) as exc:
        raise SystemExit("Mounting research: " + str(exc))
