"""Seed, archive and validate per-board I2C research without changing catalogue IDs.

Use the in-app browser to discover/read a resource first. `capture` only saves a
previously inspected public URL; it is not an alternative to a denied browser
operation. Examples and the detailed workflow live in research/i2c_breakouts/.
"""

import argparse
import copy
from datetime import datetime, timezone
import hashlib
import io
import json
import math
from pathlib import Path
import re
import sys
from urllib.parse import urljoin, urlparse

import requests
import yaml
from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import working_oomp_populate_i2c as catalogue

READY_STATES = {"complete", "complete_with_gaps"}
RESEARCH_STATES = READY_STATES | {"in_progress", "partial"}


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def boards():
    return {catalogue.get_identifier(board): board for board in catalogue.main()
            if "i2c" in board["interfaces"]}


def part_folder(part_id, root=ROOT):
    if part_id not in boards():
        raise ValueError("Not a catalogue I2C peripheral ID: " + part_id)
    base = (Path(root) / "source_file").resolve()
    folder = (base / part_id).resolve()
    if not folder.is_relative_to(base):
        raise ValueError("Part directory escapes source_file")
    return folder


def local_path(folder, relative):
    relative = str(relative)
    if not relative or Path(relative).is_absolute() or "\\" in relative:
        raise ValueError("Use a non-empty, relative forward-slash resource path")
    path = (folder / relative).resolve()
    if not path.is_relative_to(folder.resolve()):
        raise ValueError("Resource path escapes part directory")
    return path


def atomic_write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(data)
    temporary.replace(path)


def save_record(folder, data):
    atomic_write(folder / "working.yaml", yaml.safe_dump(
        data, sort_keys=False, allow_unicode=True, width=100).encode("utf-8"))


def load_record(part_id, root=ROOT):
    folder = part_folder(part_id, root)
    data = yaml.safe_load((folder / "working.yaml").read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("part_id") != part_id:
        raise ValueError("Research file has wrong identity")
    return folder, data


def seed(part_id, root=ROOT):
    folder = part_folder(part_id, root)
    if (folder / "working.yaml").exists():
        load_record(part_id, root)
        return folder
    board = copy.deepcopy(boards()[part_id])
    data = {
        "research_schema_version": 1,
        "part_id": part_id,
        "name_readable": board["name_readable"],
        "manufacturer": board["manufacturer"],
        "part_number": board["part_number"],
        "manufacturer_part_number": board["manufacturer_part_number"],
        "catalogue_definition": "working_oomp_populate_i2c.py",
        "taxonomy": {f"taxonomy_{i}": board[f"taxonomy_{i}"] for i in range(1, 16)},
        "default_website": {"url": board["webpage"], "source_id": "product_page",
                            "local_file": "website.html"},
        "research": {"status": "in_progress", "started_at": utc_now(),
                     "updated_at": utc_now(), "reviewed_by": None, "attempts": []},
        "board_revision": {"name": None, "status": "unverified", "source_ids": [],
                           "notes": "Match the selected carrier, not an older board in the same repository."},
        "description": board["description"],
        "interfaces": board["interfaces"],
        "dimensions_mm": {"width": None, "height": None, "pcb_thickness": None,
                          "assembled_height": None, "scope": "carrier_pcb_outline",
                          "status": "unverified", "source_ids": []},
        "coordinate_system": {"units": "mm", "origin": None, "view": None,
                              "orientation": None, "status": "unverified"},
        "mounting_holes": [],
        "mounting_hole_status": "unverified",
        "connectors": {},
        "pins": {},
        "pin_count": {"header_contacts": None, "cable_connector_contacts": None,
                      "total_exposed_contacts": None, "unique_nets": None,
                      "scope": "physical_connector_contacts_not_chip_package_pins",
                      "status": "unverified", "source_ids": []},
        "pin_names": [],
        "electrical": {"board_supply": {"min_v": None, "max_v": None, "nominal_v": None,
                                         "status": "unverified", "source_ids": []},
                       "logic_levels": {"status": "unverified", "notes": [], "source_ids": []},
                       "pullups": [], "extra_signals": [], "source_ids": []},
        "i2c": {"default_address_7bit": None, "documented_addresses_7bit": [],
                "address_selection": None, "maximum_clock_hz": None,
                "clock_stretching": "unverified", "status": "unverified", "source_ids": []},
        "chip": {"manufacturer": None, "part_number": None, "source_ids": []},
        "datasheets": {"status": "not_searched", "items": [], "notes": []},
        "software": [],
        "extra_resources": [],
        "sources": [],
        "conflicts": [],
        "data_gaps": ["Research not yet completed; catalogue guesses must not be treated as verified evidence."],
    }
    save_record(folder, data)
    return folder


def file_details(path, folder):
    content = path.read_bytes()
    return content_details(path, content, folder)


def content_details(path, content, folder):
    return {"local_file": path.relative_to(folder).as_posix(), "bytes": len(content),
            "sha256": hashlib.sha256(content).hexdigest()}


def capture(part_id, source_id, url, kind, filename, *, discovered_from=None, root=ROOT):
    """Download exact bytes and a searchable derivative; never overwrite prior evidence."""
    if not re.fullmatch(r"[a-z][a-z0-9_]*", source_id):
        raise ValueError("Source IDs must be lowercase identifier strings")
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Only public HTTPS resource URLs are supported")
    if parsed.hostname.lower().endswith("aliexpress.com"):
        raise ValueError("AliExpress research remains outside this catalogue task")
    seed(part_id, root)
    folder, record = load_record(part_id, root)
    if discovered_from and discovered_from not in {s["id"] for s in record["sources"]}:
        raise ValueError("Unknown discovery source: " + discovered_from)
    path = local_path(folder, filename)
    for source in record["sources"]:
        if source["id"] == source_id:
            if source["requested_url"] != url or source["local_file"] != filename:
                raise ValueError("Source ID already belongs to different evidence")
            for item in [source] + source.get("derivatives", []):
                saved = local_path(folder, item["local_file"])
                if not saved.is_file() or file_details(saved, folder)["sha256"] != item["sha256"]:
                    raise ValueError("Existing evidence is missing or has changed")
            return source
    if path.exists() or any(s["local_file"] == filename for s in record["sources"]):
        raise ValueError("Refusing to overwrite an existing evidence file: " + filename)
    written = []
    try:
        response = requests.get(url, timeout=(10, 45), headers={"User-Agent": "OOMP-board-research/1.0"})
        response.raise_for_status()
        content = response.content
        if len(content) > 25 * 1024 * 1024 or not content:
            raise ValueError("Resource is empty or exceeds the 25 MiB per-file limit")
        pdf_page_count = None
        if kind in {"chip_datasheet", "schematic_pdf"}:
            if not content.lstrip().startswith(b"%PDF-"):
                raise ValueError("Expected a PDF, received other content (possibly an error page)")
            from pypdf import PdfReader
            pdf_page_count = len(PdfReader(io.BytesIO(content)).pages)
            if not pdf_page_count:
                raise ValueError("PDF has no pages")
        if kind in {"cad_board", "cad_schematic"}:
            import xml.etree.ElementTree as ET
            if ET.fromstring(content).tag != "eagle":
                raise ValueError("Expected an Eagle XML file")
        outputs = [(path, content)]
        source = {"id": source_id, "kind": kind, "requested_url": url,
                  "url": response.url, "retrieved_at": utc_now(),
                  "content_type": response.headers.get("Content-Type", ""),
                  "acquisition": "http_response_bytes_after_browser_discovery",
                  "discovered_from": discovered_from, **content_details(path, content, folder), "derivatives": []}
        if pdf_page_count is not None:
            source["pdf_page_count"] = pdf_page_count
        if filename.endswith(".html"):
            soup = BeautifulSoup(content, "html.parser")
            if not soup.find("html") or not soup.find("title"):
                raise ValueError("Expected a full HTML page with a title")
            source["title"] = soup.title.get_text(" ", strip=True)
            links = [{"title": a.get_text(" ", strip=True), "url": urljoin(response.url, a["href"])}
                     for a in soup.find_all("a", href=True)
                     if urljoin(response.url, a["href"]).startswith(("https://", "http://"))]
            for tag in soup(["script", "style", "noscript"]):
                tag.decompose()
            body = soup.find("main") or soup.body or soup
            text_path = path.with_suffix(".txt")
            links_path = path.with_suffix(".links.json")
            text_bytes = body.get_text("\n", strip=True).encode("utf-8")
            links_bytes = (json.dumps(links, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
            outputs.extend([(text_path, text_bytes), (links_path, links_bytes)])
            source["derivatives"] = [dict(kind="text", **content_details(text_path, text_bytes, folder)),
                                     dict(kind="links", **content_details(links_path, links_bytes, folder))]
            source["snapshot_scope"] = "HTML response, extracted text and links; remote assets are not bundled"
        # Validate all responses and output paths before committing any evidence.
        for destination, _ in outputs:
            if destination.exists():
                raise ValueError("Refusing to overwrite an existing evidence file or derivative")
        for destination, payload in outputs:
            atomic_write(destination, payload)
            written.append(destination)
        record["sources"].append(source)
        record["research"]["updated_at"] = utc_now()
        save_record(folder, record)
        return source
    except Exception as error:
        for destination in written:
            destination.unlink(missing_ok=True)
        record["sources"] = [s for s in record["sources"] if s["id"] != source_id]
        record["research"]["attempts"].append({"url": url, "source_id": source_id,
                                              "at": utc_now(), "outcome": "failed",
                                              "reason": str(error)})
        save_record(folder, record)
        raise


def validate(part_id, root=ROOT):
    folder, record = load_record(part_id, root)
    errors = []
    board = boards()[part_id]
    status = record.get("research", {}).get("status")
    if status not in RESEARCH_STATES:
        errors.append("Unknown research status: " + str(status))
    if record.get("research_schema_version") != 1:
        errors.append("Unsupported research schema")
    if (record.get("manufacturer"), record.get("part_number")) != (board["manufacturer"], board["part_number"]):
        errors.append("Manufacturer/part identity changed")
    expected_taxonomy = {f"taxonomy_{i}": board[f"taxonomy_{i}"] for i in range(1, 16)}
    if record.get("taxonomy") != expected_taxonomy:
        errors.append("Taxonomy identity changed; research must not rename catalogue IDs")
    source_ids = [source["id"] for source in record.get("sources", [])]
    if len(source_ids) != len(set(source_ids)):
        errors.append("Duplicate source IDs")
    for source in record.get("sources", []):
        for key in ("kind", "requested_url", "url", "retrieved_at", "content_type", "acquisition"):
            if not source.get(key):
                errors.append("Missing source metadata: " + source["id"] + "." + key)
        for key in ("requested_url", "url"):
            parsed = urlparse(source.get(key, ""))
            if parsed.scheme not in {"https", "http"} or not parsed.hostname:
                errors.append("Invalid source URL: " + source["id"] + "." + key)
        try:
            retrieved = datetime.fromisoformat(source.get("retrieved_at", ""))
            if retrieved.tzinfo is None:
                raise ValueError("missing timezone")
        except (ValueError, TypeError):
            errors.append("Invalid source retrieval timestamp: " + source["id"])
        if source.get("discovered_from") is not None and source["discovered_from"] not in source_ids:
            errors.append("Unknown source discovery reference: " + source["discovered_from"])
        for item in [source] + source.get("derivatives", []):
            try:
                path = local_path(folder, item["local_file"])
                if not path.is_file() or file_details(path, folder) != {k: item[k] for k in ("local_file", "bytes", "sha256")}:
                    errors.append("Missing or changed evidence: " + item["local_file"])
            except (ValueError, KeyError) as error:
                errors.append(str(error))
    def walk(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if key == "source_ids" and (not isinstance(child, list) or not set(child) <= set(source_ids)):
                    errors.append("Unknown source_ids reference: " + str(child))
                elif key == "source_id" and child is not None and child not in source_ids:
                    errors.append("Unknown source_id reference: " + str(child))
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)
    walk(record)
    website = record.get("default_website", {})
    default_source = next((s for s in record.get("sources", []) if s["id"] == website.get("source_id")), None)
    if not default_source or default_source["local_file"] != website.get("local_file"):
        errors.append("Default website has not been archived")
    if default_source and website.get("url") not in {default_source.get("requested_url"), default_source.get("url")}:
        errors.append("Default website URL differs from its archived source")
    if default_source and not any(d["kind"] == "text" for d in default_source.get("derivatives", [])):
        errors.append("Default website needs a searchable text snapshot")
    pins = record.get("pins", {})
    counts = record.get("pin_count", {})
    if counts.get("total_exposed_contacts") is not None and counts["total_exposed_contacts"] != len(pins):
        errors.append("Total physical contact count differs from pin records")
    contact_keys = [(pin.get("connector"), str(pin.get("number")) if pin.get("number") is not None else key)
                    for key, pin in pins.items()]
    if len(contact_keys) != len(set(contact_keys)):
        errors.append("Duplicate physical connector/pad identities")
    names = sorted({pin.get("name") for pin in pins.values() if pin.get("name")})
    if record.get("pin_names") != names:
        errors.append("pin_names must equal the sorted unique pin names")
    for pin in pins.values():
        if not pin.get("connector") or not pin.get("name") or not (pin.get("source_id") or pin.get("source_ids")):
            errors.append("Each pin needs connector identity, name and evidence")
        if (pin.get("x_mm") is None) != (pin.get("y_mm") is None):
            errors.append("Pin XY coordinates must be provided together")
    for key in ("width", "height", "pcb_thickness", "assembled_height"):
        value = record.get("dimensions_mm", {}).get(key)
        if value is not None:
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
                errors.append("Invalid millimetre dimension: " + key)
            if not record["dimensions_mm"].get("source_ids"):
                errors.append("Known dimensions need source_ids")
    for kind, key in (("header", "header_contacts"), ("cable_connector", "cable_connector_contacts")):
        value = counts.get(key)
        if value is not None and value != sum(pin.get("kind") == kind for pin in pins.values()):
            errors.append("Contact category count differs from pin records: " + key)
    if counts.get("unique_nets") is not None and counts["unique_nets"] != len({p.get("net_name") for p in pins.values() if p.get("net_name")}):
        errors.append("Unique-net count differs from documented CAD net names")
    for name, connector in record.get("connectors", {}).items():
        if any(key not in pins or pins[key].get("connector") != name for key in connector.get("contacts", [])):
            errors.append("Connector contact list refers to wrong or missing pins: " + name)
    default = record.get("i2c", {}).get("default_address_7bit")
    addresses = record.get("i2c", {}).get("documented_addresses_7bit", [])
    if any(type(address) is not int or not 0x08 <= address <= 0x77 for address in addresses):
        errors.append("Addresses must be non-reserved seven-bit integers")
    if default is not None and default not in addresses:
        errors.append("Default address is not included in documented addresses")
    datasheets = record.get("datasheets", {})
    if datasheets.get("status") == "downloaded":
        if not datasheets.get("items"):
            errors.append("Downloaded datasheets need at least one file")
        for item in datasheets.get("items", []):
            source = next((s for s in record.get("sources", []) if s["id"] == item.get("source_id")), None)
            if not source or source["kind"] != "chip_datasheet":
                errors.append("Datasheet entry must reference a chip_datasheet source")
            else:
                for key in ("local_file", "sha256"):
                    if item.get(key) != source.get(key):
                        errors.append("Datasheet item differs from its source: " + key)
                if item.get("url") not in {source.get("requested_url"), source.get("url")}:
                    errors.append("Datasheet URL differs from its source")
                try:
                    from pypdf import PdfReader
                    pdf_path = local_path(folder, source["local_file"])
                    if not pdf_path.read_bytes().lstrip().startswith(b"%PDF-"):
                        raise ValueError("Not a PDF")
                    pages = len(PdfReader(pdf_path).pages)
                    if not pages or item.get("page_count") != pages:
                        errors.append("Datasheet page count differs from parsed PDF")
                except (OSError, ValueError) as error:
                    errors.append("Invalid chip datasheet: " + str(error))
    if status in READY_STATES:
        for key in ("board_revision", "dimensions_mm", "pin_count", "electrical", "chip", "software", "conflicts", "data_gaps"):
            if key not in record:
                errors.append("Missing required research section: " + key)
        if datasheets.get("status") not in {"downloaded", "not_found", "download_failed"}:
            errors.append("Datasheet search has not been resolved")
        if not pins and not any("pin" in gap.lower() for gap in record.get("data_gaps", [])):
            errors.append("Missing pinout needs an explicit evidence gap")
        def require_evidence(value, location):
            if not (value.get("source_id") or value.get("source_ids")):
                errors.append("Completed factual section needs evidence: " + location)

        # Unknown sections can remain explicitly unverified. Known claims need
        # their own evidence rather than relying on an unrelated source list.
        for key in ("board_revision", "pin_count", "chip", "i2c"):
            value = record.get(key, {})
            if value.get("status") not in {"unverified", "unknown"} or any(
                    value.get(k) is not None for k in ("manufacturer", "part_number", "default_address_7bit")):
                require_evidence(value, key)
        electrical = record.get("electrical", {})
        if electrical.get("extra_signals"):
            require_evidence(electrical, "electrical.extra_signals")
        for key in ("board_supply", "chip_supply", "logic_levels"):
            value = electrical.get(key, {})
            if value and (value.get("status") not in {"unverified", "unknown"} or any(
                    value.get(k) is not None for k in ("min_v", "max_v", "nominal_v"))):
                require_evidence(value, "electrical." + key)
        for key, values in (("electrical.pullups", electrical.get("pullups", [])),
                            ("software", record.get("software", [])),
                            ("mounting_holes", record.get("mounting_holes", [])),
                            ("connectors", record.get("connectors", {}).values())):
            for value in values:
                require_evidence(value, key)
    return errors


def queue(root=ROOT):
    items = []
    for part_id, board in boards().items():
        path = part_folder(part_id, root) / "working.yaml"
        status = "pending"
        if path.is_file():
            status = yaml.safe_load(path.read_text(encoding="utf-8")).get("research", {}).get("status", "in_progress")
        items.append({"part_id": part_id, "name": board["name_readable"], "status": status,
                      "default_website": board["webpage"], "research_file": f"source_file/{part_id}/working.yaml"})
    return {"schema_version": 1, "scope": "28 catalogue I2C peripherals; excludes analog ADXL335 and AliExpress", "parts": items}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    list_parser = commands.add_parser("queue")
    list_parser.add_argument("--write", action="store_true")
    seed_parser = commands.add_parser("seed")
    seed_parser.add_argument("--part-id", required=True)
    capture_parser = commands.add_parser("capture")
    for flag in ("part-id", "source-id", "url", "kind", "filename"):
        capture_parser.add_argument("--" + flag, required=True)
    capture_parser.add_argument("--discovered-from")
    validate_parser = commands.add_parser("validate")
    validate_parser.add_argument("--part-id")
    args = parser.parse_args()
    if args.command == "queue":
        text = yaml.safe_dump(queue(), sort_keys=False, allow_unicode=True)
        if args.write:
            destination = ROOT / "research/i2c_breakouts/research_queue.yaml"
            atomic_write(destination, text.encode("utf-8"))
            print(destination)
        else:
            print(text)
    elif args.command == "seed":
        print(seed(args.part_id))
    elif args.command == "capture":
        print(json.dumps(capture(args.part_id, args.source_id, args.url, args.kind, args.filename,
                                 discovered_from=args.discovered_from), indent=2))
    elif args.command == "validate":
        ids = [args.part_id] if args.part_id else [p for p in boards() if (part_folder(p) / "working.yaml").is_file()]
        errors = []
        for part_id in ids:
            found = validate(part_id)
            errors.extend((part_id, error) for error in found)
        for part_id, error in errors:
            print(part_id + ": " + error)
        print(f"Validated {len(ids)} research records; {len(errors)} errors")
        return 1 if errors else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
