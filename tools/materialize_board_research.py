"""One-time migration of reviewed research to verbose editable family modules.

The populate modules are the authority after migration. This script is retained
as an audit trail; do not rerun it over subsequent manual catalogue edits.
"""

import copy
import hashlib
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

import yaml

from extract_board_cad import eagle, kicad

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research" / "microcontrollers"
LAB = Path(r"C:\od\OneDrive\docs\oobb_electronic_microcontroller_web_based_lab")


def literal(value, indent=0):
    space = " " * indent
    if isinstance(value, dict):
        if not value:
            return "{}"
        lines = ["{"]
        for key, item in value.items():
            lines.append(" " * (indent + 4) + repr(key) + ": " + literal(item, indent + 4) + ",")
        lines.append(space + "}")
        return "\n".join(lines)
    if isinstance(value, list):
        if not value:
            return "[]"
        lines = ["["]
        for item in value:
            lines.append(" " * (indent + 4) + literal(item, indent + 4) + ",")
        lines.append(space + "]")
        return "\n".join(lines)
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    return repr(value)


def identifier(option):
    return "_".join(str(option.get(f"taxonomy_{number}", "")) for number in range(1, 16) if option.get(f"taxonomy_{number}"))


def legacy_identifier(seed):
    fields = ["electronic", "breakout", seed["type_1"], seed["type_2"], seed["type_3"]]
    if seed.get("type_4"):
        fields.append(seed["type_4"])
    fields.extend([seed["breakout_description"], seed["manufacturer"], seed["part_number"]])
    return "_".join(fields)


def source(**kwargs):
    result = {
        "id": kwargs["id"],
        "url": kwargs["url"],
        "title": kwargs.get("title", kwargs["id"]),
        "accessed": "2026-10-22",
        "scope": kwargs["scope"],
    }
    path = kwargs.get("path")
    if path:
        destination = kwargs["folder"] / "reference" / path.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)
        result["local_file"] = "reference/" + path.name
        result["sha256"] = hashlib.sha256(destination.read_bytes()).hexdigest()
    return result


def family(seed):
    for name in ("rp2040", "rp2350", "esp32_c3", "esp32_c6", "esp32_s2", "esp32_s3", "esp32_h2"):
        if seed["type_2"].startswith(name):
            return name
    return "esp32"


def base(seed):
    option = copy.deepcopy(seed)
    option["schema_version"] = 1
    option["item_kind"] = "breakout"
    option["name_readable"] = seed["manufacturer"].replace("_", " ").title() + " " + seed["part_number"].replace("_", " ")
    names = {
        "esp32_devkit_v1_30_pin": "DOIT ESP32 DevKit V1 (30 contacts)",
        "esp32_devkitc_32e": "Espressif ESP32 DevKitC-32E V4",
        "nodemcu_32s": "Generic NodeMCU-32S (Ai-Thinker reference pinout)",
        "esp32_s3_devkitc_1_n8r8": "Espressif ESP32-S3 DevKitC-1 N8R8 v1.1",
        "esp32_c3_devkitm_1": "Espressif ESP32-C3 DevKitM-1 (30 contacts)",
        "esp32_c3_devkitc_02": "Espressif ESP32-C3 DevKitC-02",
        "esp32_c6_devkitc_1_n8": "Espressif ESP32-C6 DevKitC-1 N8 (32 contacts)",
        "esp32_c6_devkitm_1_n4": "Espressif ESP32-C6 DevKitM-1 N4",
        "esp32_s2_devkitc_1": "Espressif ESP32-S2 DevKitC-1 (module variant unresolved)",
        "esp32_c3_supermini": "Generic ESP32-C3 SuperMini (carrier revision unknown)",
        "esp32_s3_supermini": "Tenstar ESP32-S3 SuperMini (pinout unverified)",
        "esp32_c6_supermini": "Tenstar ESP32-C6 SuperMini (pinout unverified)",
        "esp32_h2_supermini": "Tenstar ESP32-H2 SuperMini (pinout unverified)",
        "xiao_esp32c3": "Seeed Studio XIAO ESP32-C3",
        "xiao_esp32s3": "Seeed Studio XIAO ESP32-S3 (base board)",
        "xiao_esp32c6": "Seeed Studio XIAO ESP32-C6",
        "5405": "Adafruit QT Py ESP32-C3 (5405)",
        "qt_py_esp32_s3": "Adafruit QT Py ESP32-S3 (memory SKU unresolved)",
        "lolin_s2_mini": "LOLIN S2 Mini",
        "lolin_c3_mini": "LOLIN C3 Mini v2.1",
        "lolin_s3_mini": "LOLIN S3 Mini v1.0",
        "lolin_d32": "LOLIN D32 v1.0",
        "lolin_d32_pro": "LOLIN D32 Pro v2.0",
        "esp32_cam": "Ai-Thinker ESP32-CAM (V1.6 schematic reference)",
        "esp32_pico_kit_v4": "Espressif ESP32-PICO-KIT v4 (40 PCB contacts)",
        "3405": "Adafruit HUZZAH32 ESP32 Feather (3405)",
        "5477": "Adafruit ESP32-S3 Feather 4MB Flash / 2MB PSRAM (5477)",
        "esp32_d1_r32": "Generic ESP32 D1 R32 (SDK aliases)",
        "stamp_c3u": "M5Stack Stamp-C3U",
    }
    option["name_readable"] = names.get(seed["part_number"], option["name_readable"])
    for number in range(1, 16):
        option[f"taxonomy_{number}"] = ""
    fields = ["electronic", "breakout", seed["type_1"], seed["type_2"], seed["type_3"]]
    if seed.get("type_4"):
        fields.append(seed["type_4"])
    fields.append(seed["breakout_description"])
    for number, value in enumerate(fields, 1):
        option[f"taxonomy_{number}"] = value
    option["taxonomy_14"] = seed["manufacturer"]
    option["taxonomy_15"] = seed["part_number"]
    option["form_factor"] = seed["type_3"]
    option["chip"] = {
        "family": family(seed),
        "part_number": seed["type_2"],
        "identity_scope": "catalogue_chip_or_module_label",
        "oomp_id": None,
        "silicon_revision": None,
    }
    option["dimensions_mm"] = {
        "width": seed["breakout_pcb_width"],
        "height": seed["breakout_pcb_height"],
        "pcb_thickness": None,
        "assembled_height": None,
        "scope": "nominal_catalogue_outline_not_measured",
        "source_id": "original_catalogue",
        "status": "unverified",
    }
    option["coordinate_system"] = {
        "units": "mm",
        "origin": "centre_of_pcb_outline",
        "view": "top_with_usb_at_positive_y",
        "x_positive": "right",
        "y_positive": "towards_usb",
    }
    option["assembly"] = {"headers": "unspecified", "header_pitch_mm": None}
    option["electrical"] = {"logic_voltage_v": 3.3, "gpio_5v_tolerant": False, "usb_connector": None, "source_id": "chip_datasheet"}
    option["memory"] = {"external_flash_bytes": None, "psram_bytes": None}
    option["mounting_holes"] = []
    option["mounting_hole_details"] = []
    option["mounting_hole_candidates"] = []
    option["mounting_hole_status"] = "not_verified"
    option["pins"] = {}
    option["connectors"] = {}
    option["onboard_gpio_connections"] = []
    option["sources"] = []
    option["sources"].append({
        "id": "original_catalogue",
        "url": None,
        "title": "Original populate entries in this repository",
        "local_file": None,
        "scope": "Nominal dimensions and identity; not manufacturer verification",
        "accessed": "2026-10-22",
    })
    option["sources"].append(source(id="chip_datasheet", url="https://www.espressif.com/sites/default/files/documentation/" + family(seed).replace("_", "-") + "_datasheet_en.pdf", scope="GPIO capabilities, electrical limits and strapping; not carrier geometry"))
    option["notes"] = []
    option["data_gaps"] = []
    option["data_gaps"].append("Assembled component keepouts and USB insertion/cable envelopes have not been captured.")
    option["pinout_scope"] = "Expansion connectors and explicitly listed test pads; USB socket contacts excluded."
    return option


def pin(**kwargs):
    result = {
        "connector": kwargs["connector"],
        "number": str(kwargs["number"]),
        "name": kwargs["name"],
        "gpio": kwargs.get("gpio"),
        "adc_channel": None,
        "chip_pin_number": None,
        "x_mm": kwargs.get("x_mm"),
        "y_mm": kwargs.get("y_mm"),
        "source_id": kwargs.get("source_id", "board_guide"),
        "functions": kwargs.get("functions", []),
    }
    return result


def add_rows(option, rows, source_id="board_guide"):
    for connector, names in rows.items():
        option["connectors"][connector] = {"contact_count": len(names), "pitch_mm": 2.54, "source_id": source_id, "coordinate_status": "not_transcribed"}
        for number, name in enumerate(names, 1):
            match = re.search(r"(?:GPIO|IO)(\d+)", name)
            gpio = int(match.group(1)) if match else None
            option["pins"][connector + "_" + str(number)] = pin(connector=connector, number=number, name=name, gpio=gpio, source_id=source_id)


def add_manufacturer_references(option, key):
    page = json.loads((RESEARCH / (key + ".json")).read_text(encoding="utf-8"))
    folder = ROOT / "source_file" / identifier(option)
    option["sources"].append(source(id="board_guide", url=page["url"], title=key + " manufacturer guide", scope="Board identity, connector pinout and documented functions"))
    for label, tokens in (("mechanical", ("dimension",)), ("schematic", ("schematic",))):
        for link in page["links"]:
            if any(token in link["title"].lower() for token in tokens) and link["url"].endswith(".pdf"):
                path = RESEARCH / key / link["url"].split("/")[-1].replace("%20", " ").replace("&", "_")
                if path.exists():
                    option["sources"].append(source(id=label, url=link["url"], title=link["title"], scope="Manufacturer " + label + " for the stated revision", path=path, folder=folder))
                    break
    return page


def build_espressif(option, key):
    page = add_manufacturer_references(option, key)
    tables = []
    for table in page["tables"]:
        if table and table[0][0] == "No." and len(table[0]) == 4:
            tables.append(table)
    connector_names = ["J2", "J3"] if key in ("esp32-devkitc", "esp32-pico-kit") else ["J1", "J3"]
    geometry = {
        "esp32-devkitc": (27.94, 48.26, 25.4, 1.27, 6.04),
        "esp32-c3-devkitc-02": (25.4, 38.91, 22.86, None, None),
        "esp32-c3-devkitm-1": (25.4, 38.91, 22.86, None, None),
        "esp32-s2-devkitc-1": (25.4, 62.74, 22.86, 1.27, None),
        "esp32-s3-devkitc-1": (25.4, 62.74, 22.86, 1.27, None),
        "esp32-c6-devkitc-1": (25.4, 51.8, 22.86, 1.27, 6.35),
        "esp32-c6-devkitm-1": (25.4, 48.26, 22.86, 1.27, 5.37),
    }
    if key in geometry:
        width, height, spacing, top_offset, antenna = geometry[key]
        option["dimensions_mm"].update(width=width, height=height, scope="carrier_pcb_excludes_module_antenna_and_usb_overhang", source_id="mechanical", status="manufacturer_drawing")
        option["dimensions_mm"]["module_antenna_overhang_positive_y"] = antenna
    else:
        spacing = top_offset = None
        option["data_gaps"].append("PICO-KIT carrier outline and row centres require mechanical transcription; existing dimensions remain nominal.")
    for index, table in enumerate(tables):
        connector = connector_names[index]
        option["connectors"][connector] = {"contact_count": len(table) - 1, "pitch_mm": 2.54, "row_spacing_mm": spacing, "source_id": "board_guide"}
        for row in table[1:]:
            number, name, kind, functions = row
            name = re.sub(r"\s*\[.*?\]", "", name).strip()
            functions = re.sub(r"\s*\[.*?\]", "", functions).strip()
            match = re.search(r"GPIO(\d+)", functions)
            gpio = int(match.group(1)) if match else None
            item = pin(connector=connector, number=number, name=name, gpio=gpio, functions=[part.strip() for part in functions.split(",")])
            item["manufacturer_pin_type"] = kind
            if top_offset is not None:
                # Board guide numbers from antenna end; rotate 180 degrees to USB-up.
                item["x_mm"] = round(spacing / 2 * (1 if index == 0 else -1), 5)
                item["y_mm"] = round(-option["dimensions_mm"]["height"] / 2 + top_offset + (int(number) - 1) * 2.54, 5)
                item["position_source_id"] = "mechanical"
            option["pins"][connector + "_" + number] = item
    option["coordinate_system"]["view"] = "top_with_usb_at_positive_y"
    option["mounting_hole_status"] = "none_shown_in_manufacturer_drawing" if key in geometry else "not_verified"
    option["electrical"]["usb_connector"] = "dual_usb_c" if "c6" in key else "dual_micro_usb_b" if any(part in key for part in ("s2", "s3")) else "micro_usb_b"
    option["assembly"]["headers"] = "with_headers"
    option["assembly"]["header_pitch_mm"] = 2.54
    option["notes"].append("Physical header contacts include supply, ground and reserved contacts; contact count is not GPIO count.")
    if "c3" in key:
        option["memory"]["external_flash_bytes"] = 4194304
        option["onboard_gpio_connections"].append({"gpio": 8, "function": "addressable_rgb_led", "source_id": "board_guide"})
        option["data_gaps"].append("C3 header absolute Y offset not dimensioned in the captured drawing; pad centres remain null.")
    if "c6" in key:
        option["memory"]["external_flash_bytes"] = 8388608 if "devkitc" in key else 4194304
        option["onboard_gpio_connections"].append({"gpio": 8, "function": "addressable_rgb_led", "source_id": "board_guide"})
    if "s3" in key:
        option["memory"].update(external_flash_bytes=8388608, psram_bytes=8388608)
        option["notes"].append("N8R8 octal PSRAM occupies GPIO35/36/37; these header positions are not usable GPIOs on this variant.")
        option["onboard_gpio_connections"].append({"gpio": 38, "function": "rgb_led_on_revision_1_1", "source_id": "board_guide"})
        option["notes"].append("Revision 1.0 uses GPIO48 for RGB LED; captured geometry and guide are revision 1.1.")
    if "s2" in key:
        option["notes"].append("Original catalogue said WROOM; manufacturer guide identifies SOLO/SOLO-2 modules. Installed memory/module variant must be checked.")
        option["onboard_gpio_connections"].append({"gpio": 18, "function": "addressable_rgb_led", "source_id": "board_guide"})
    if key == "esp32-pico-kit":
        option["memory"]["external_flash_bytes"] = 4194304
        option["assembly"]["normally_fitted_header_contacts"] = 34
        option["assembly"]["total_header_pad_count"] = 40


def build_adafruit(option, key):
    add_manufacturer_references(option, key)
    path = next((RESEARCH / key).glob("*.brd"))
    extracted = eagle(path=path)
    folder = ROOT / "source_file" / identifier(option)
    downloads = json.loads((RESEARCH / "downloads.json").read_text())
    for extension, source_id in ((".brd", "cad"), (".sch", "cad_schematic")):
        asset = path.with_suffix(extension)
        url = next(item["url"] for item in downloads if item["local_file"] == asset.relative_to(RESEARCH).as_posix())
        option["sources"].append(source(id=source_id, url=url, scope="Manufacturer CAD; see revision and product applicability notes", path=asset, folder=folder))
    option["dimensions_mm"].update(width=extracted["width"], height=extracted["height"], source_id="cad", status="manufacturer_cad", scope="pcb_outline_excludes_usb_overhang")
    mapping = extracted["gpio_by_net"]
    if key == "qtpy_c3":
        mapping["TX"] = 21
    if key == "qtpy_s3":
        mapping.update(RX=16, SDA1=41, SCL1=40)
    if key == "feather_s3":
        mapping["TXD0"] = 43
    for pad in extracted["pins"]:
        name = pad["name"]
        gpio = mapping.get(name)
        if name in ("GND", "3.3V", "VBAT", "VBUS", "VSENSOR", "+5V", "NC", "EN", "RESET"):
            gpio = None
        pad["gpio"] = gpio
        pad["adc_channel"] = None
        pad["chip_pin_number"] = None
        pad["functions"] = [name]
        option["pins"][pad["connector"] + "_" + pad["number"]] = pad
    option["mounting_hole_details"] = extracted["holes"]
    option["mounting_hole_status"] = "manufacturer_cad" if extracted["holes"] else "none_in_manufacturer_cad"
    option["electrical"]["usb_connector"] = "micro_usb_b" if key == "huzzah32" else "usb_c"
    option["assembly"].update(headers="without_headers", header_pitch_mm=2.54)
    if key == "feather_s3":
        # The public Eagle repository is the 8 MB SKU, not PID 5477.
        option["mounting_hole_candidates"] = option["mounting_hole_details"]
        option["mounting_hole_details"] = []
        option["mounting_hole_status"] = "related_variant_cad_only"
        for item in option["mounting_hole_candidates"]:
            item["status"] = "related_8mb_sku_requires_confirmation_for_5477"
        for item in option["pins"].values():
            item["position_status"] = "related_8mb_sku_requires_confirmation_for_5477"
            item["reference_position_mm"] = [item["x_mm"], item["y_mm"]]
            item["x_mm"] = None
            item["y_mm"] = None
        option["dimensions_mm"].update(width=22.7, height=52.3, assembled_height=7.2, scope="overall_product_dimensions_including_components", source_id="product", status="manufacturer_product_not_pcb_outline")
        option["sources"].append(source(id="product", url="https://www.adafruit.com/product/5477", scope="Exact SKU, 4 MB flash / 2 MB PSRAM and overall product dimensions"))
        option["memory"].update(external_flash_bytes=4194304, psram_bytes=2097152)
        option["data_gaps"].append("Public CAD is 8MB/no-PSRAM SKU. PID5477 pad positions, mounting holes and PCB outline require confirmation; related coordinates retained separately.")
    if key == "qtpy_c3":
        option["memory"]["external_flash_bytes"] = 4194304
    if key == "qtpy_s3":
        option["data_gaps"].append("Catalogue lacks a numeric QT Py S3 SKU; flash/PSRAM configuration must be selected before flashing.")
    if key == "huzzah32":
        option["memory"]["external_flash_bytes"] = 4194304
    for net, gpio in mapping.items():
        if net in ("NEOPIX", "NEOPIX_PWR", "BOOT", "BOOT0", "I2C_PWR"):
            option["onboard_gpio_connections"].append({"gpio": gpio, "function": net.lower(), "source_id": "cad_schematic"})


def build_xiao(option, key):
    page = add_manufacturer_references(option, key)
    table = next(table for table in page["tables"] if table and table[0][0] == "XIAO Pin")
    for row in table[1:]:
        if not re.fullmatch(r"D\d+", row[0]):
            continue
        gpio = int(re.search(r"GPIO(\d+)", row[2]).group(1))
        item = pin(connector="expansion", number=row[0], name=row[0], gpio=gpio, functions=[row[1]] + [part.strip() for part in row[3].split(",") if part.strip()])
        option["pins"]["expansion_" + row[0]] = item
    for name in ("5V", "GND", "3V3"):
        option["pins"]["expansion_" + name] = pin(connector="expansion", number=name, name=name)
    option["dimensions_mm"].update(width=17.8, height=21, source_id="board_guide", scope="manufacturer_nominal_pcb_outline", status="manufacturer_nominal")
    option["connectors"]["expansion"] = {"contact_count": 14, "pitch_mm": 2.54, "source_id": "board_guide"}
    option["electrical"]["usb_connector"] = "usb_c"
    option["assembly"].update(headers="without_headers", header_pitch_mm=2.54)
    option["memory"]["external_flash_bytes"] = 4194304 if key == "xiao_c3" else 8388608 if key == "xiao_s3" else 4194304
    if key == "xiao_s3":
        option["memory"]["psram_bytes"] = 8388608
        option["data_gaps"].append("Manufacturer base-S3 archive currently contains a Sense v1.5 PCB. It is not used as the base board's exact geometry.")
    else:
        archive = next(path for path in (RESEARCH / key).glob("*.zip") if "KiCad" in path.name or "SCH_PCB" in path.name)
        with zipfile.ZipFile(archive) as bundle:
            filename = next(name for name in bundle.namelist() if name.endswith(".kicad_pcb"))
            cad_path = RESEARCH / key / "board.kicad_pcb"
            cad_path.write_bytes(bundle.read(filename))
        geometry = kicad(path=cad_path)
        folder = ROOT / "source_file" / identifier(option)
        archive_record = next(item for item in json.loads((RESEARCH / "downloads.json").read_text()) if item["local_file"] == archive.relative_to(RESEARCH).as_posix())
        option["sources"].append(source(id="cad", url=archive_record["url"], scope="Board KiCad extracted from manufacturer archive", path=cad_path, folder=folder))
        # Match CAD nets to manufacturer D labels; preserve each physical pad.
        by_gpio = {item["gpio"]: item for item in option["pins"].values() if item["gpio"] is not None}
        located = {}
        for pad in geometry["pins"]:
            pad["name"] = pad["name"].replace("{slash}", "/")
            match = re.search(r"(?:GPIO|IO)(\d+)", pad["name"])
            gpio = int(match.group(1)) if match else None
            if gpio is None:
                d_match = re.search(r"D(\d+)", pad["name"])
                if d_match and "expansion_D" + d_match.group(1) in option["pins"]:
                    gpio = option["pins"]["expansion_D" + d_match.group(1)]["gpio"]
            pad["gpio"] = gpio
            pad["adc_channel"] = None
            pad["chip_pin_number"] = None
            pad["functions"] = [pad["name"]]
            pad["aliases"] = []
            if gpio in by_gpio:
                pad["aliases"].append(by_gpio[gpio]["name"])
                pad["functions"].extend(by_gpio[gpio]["functions"])
                pad["net_name"] = pad["name"]
                pad["name"] = by_gpio[gpio]["name"]
            elif pad["name"] == "BOOT":
                pad["gpio"] = 9
            located[pad["connector"] + "_" + pad["number"]] = pad
        option["pins"] = located
        option["dimensions_mm"].update(width=geometry["width"], height=geometry["height"], source_id="cad", scope="pcb_outline_excludes_usb_overhang", status="manufacturer_cad")
        option["mounting_hole_details"] = geometry["holes"]
        option["mounting_hole_status"] = "none_in_manufacturer_cad" if not geometry["holes"] else "manufacturer_cad"
    option["data_gaps"].append("Only source-confirmed pad centres are positioned; no shared-XIAO outline pin-position inference is applied.")


def build_wemos(option, key):
    add_manufacturer_references(option, key)
    maps = {
        "c3_mini": {"J2": ["EN", "IO3", "IO2", "IO1", "IO0", "IO4", "IO5", "3V3"], "J3": ["IO21", "IO20", "IO10", "IO8", "IO7", "IO6", "GND", "VBUS"]},
        "s2_mini": {"J2": ["EN", "IO3", "IO5", "IO7", "IO9", "IO11", "IO12", "3V3"], "J5": ["IO1", "IO2", "IO4", "IO6", "IO8", "IO10", "IO13", "IO14"], "J4": ["IO40", "IO38", "IO36", "IO34", "IO21", "IO17", "GND", "IO15"], "J3": ["IO39", "IO37", "IO35", "IO33", "IO18", "IO16", "GND", "VBUS"]},
        "s3_mini": {"J2": ["EN", "IO2", "IO4", "IO12", "IO13", "IO11", "IO10", "3V3"], "J5": ["IO1", "IO3", "IO5", "IO6", "IO7", "IO8", "IO9", "IO14"], "J4": ["IO33", "IO37", "IO38", "IO34", "IO21", "IO17", "GND", "IO15"], "J3": ["IO43", "IO44", "IO36", "IO35", "IO18", "IO16", "GND", "VBUS"]},
        "d32": {"JP1": ["3V3", "RESET", "IO36", "IO39", "IO34", "IO32", "IO33", "IO25", "IO26", "IO27", "IO14", "IO12", "IO13", "EN", "VBUS", "VBAT"], "JP2": ["GND", "IO23", "IO22", "IO1", "IO3", "IO21", "IO19", "IO18", "IO5", "IO17", "IO16", "IO4", "IO0", "IO2", "IO15", "GND"]},
        "d32_pro": {"JP1": ["3V3", "RESET", "IO36", "IO39", "IO34", "IO32", "IO33", "IO25", "IO26", "IO27", "IO14", "IO12", "IO13", "EN", "VBUS", "VBAT"], "JP2": ["GND", "IO23", "IO22", "IO1", "IO3", "IO21", "IO19", "IO18", "IO5", "NC", "NC", "IO4", "IO0", "IO2", "IO15", "GND"]},
    }
    add_rows(option, maps[key], "schematic")
    width, height = (25.4, 57) if key == "d32" else (25.4, 65) if key == "d32_pro" else (25.4, 34.3)
    option["dimensions_mm"].update(width=width, height=height, source_id="mechanical", status="manufacturer_drawing", scope="pcb_outline_excludes_usb_overhang")
    option["electrical"]["usb_connector"] = "micro_usb_b" if key.startswith("d32") else "usb_c"
    option["assembly"]["header_pitch_mm"] = 2.54
    option["mounting_hole_status"] = "partially_dimensioned_in_manufacturer_drawing"
    for x in (-10.7, 10.7) if key.startswith("d32") else (-10.2, 10.2):
        option["mounting_hole_candidates"].append({"x_mm": x, "y_mm": None, "diameter_mm": 2.1 if key.startswith("d32") else 2, "source_id": "mechanical", "status": "x_and_diameter_only_y_not_dimensioned"})
    option["data_gaps"].append("Mounting-hole X centres and diameters are dimensioned; Y centres are not. Partial holes are not passed to SCAD or drawn as located holes.")
    option["data_gaps"].append("Header numbers and signals are transcribed from schematic; absolute pad centres remain null pending CAD or a dimensioned pin drawing.")
    option["memory"]["external_flash_bytes"] = 4194304 if key != "d32_pro" else None
    if key == "d32_pro":
        option["notes"].append("Manufacturer page disagrees on PSRAM capacity and lists 4MB/16MB flash variants. Memory is deliberately unspecified.")
        add_rows(option, {"P3_i2c": ["3V3", "GND", "IO22", "IO21"], "P4_tft": ["VBAT", "IO32", "IO23", "IO18", "IO14", "IO27", "IO33", "IO19", "IO12", "GND"]}, "schematic")
    if key in ("s2_mini", "s3_mini"):
        option["memory"]["psram_bytes"] = 2097152
    if key == "s2_mini":
        option["memory"]["psram_bytes"] = None
        option["data_gaps"].append("Current product text names FN4R2 with PSRAM; captured V1 schematic names S2FH4. PSRAM size is left unknown for this unsuffixed catalogue board.")
    if key == "c3_mini":
        option["onboard_gpio_connections"].append({"gpio": 7, "function": "rgb_led_revision_2_1", "source_id": "schematic"})
    if key == "s2_mini":
        option["onboard_gpio_connections"].append({"gpio": 15, "function": "led", "source_id": "schematic"})
    if key == "s3_mini":
        option["onboard_gpio_connections"].append({"gpio": 47, "function": "rgb_led", "source_id": "board_guide"})
    if key.startswith("d32"):
        option["onboard_gpio_connections"].append({"gpio": 5, "function": "led", "source_id": "board_guide"})


def build_extra(option):
    part = option["part_number"]
    folder = ROOT / "source_file" / identifier(option)
    if part == "esp32_c3_supermini":
        option["sources"].append(source(id="board_guide", url="https://nuttx.apache.org/docs/latest/platforms/risc-v/esp32c3/boards/esp32c3-supermini/index.html", scope="Primary NuttX SuperMini support documentation; header GPIO inventory, USB, boot and LED; vendor revisions vary"))
        for name in ["GPIO" + str(number) for number in list(range(11)) + [20, 21]] + ["3V3", "GND", "5V"]:
            match = re.search(r"GPIO(\d+)", name)
            item = pin(connector="silkscreen", number=name, name=name, gpio=int(match.group(1)) if match else None)
            option["pins"][name] = item
        option["electrical"]["usb_connector"] = "usb_c_native_serial_jtag"
        option["onboard_gpio_connections"].append({"gpio": 8, "function": "typical_active_low_led_verify_revision", "source_id": "board_guide"})
        option["onboard_gpio_connections"].append({"gpio": 9, "function": "boot_button", "source_id": "board_guide"})
        option["data_gaps"].append("Generic SuperMini revision and FN4 silicon suffix not verified. Pin numbers are silkscreen names, not an invented physical order; pad coordinates remain null.")
    elif part == "esp32_devkit_v1_30_pin":
        url = "https://embedded-systems-design.github.io/overview-of-the-esp32-devkit-doit-v1/SchematicsforESP32.pdf"
        option["sources"].append(source(id="board_guide", url=url, title="DOIT V0 schematic, manufacturer drawing mirrored by Zephyr reference", scope="DOIT schematic 2x15 signal inventory; not carrier dimensions", path=RESEARCH / "doit_schematic.pdf", folder=folder))
        add_rows(option, {"left_reference": ["EN", "GPIO36", "GPIO39", "GPIO34", "GPIO35", "GPIO32", "GPIO33", "GPIO25", "GPIO26", "GPIO27", "GPIO14", "GPIO12", "GPIO13", "GND", "VIN"], "right_reference": ["GPIO23", "GPIO22", "GPIO1", "GPIO3", "GPIO21", "GPIO19", "GPIO18", "GPIO5", "GPIO17", "GPIO16", "GPIO4", "GPIO2", "GPIO15", "GND", "3V3"]})
        option["electrical"]["usb_connector"] = "micro_usb_b_uart_bridge"
        option["data_gaps"].append("2x15 header inventory is documented; clone PCB dimensions, row spacing, numbering/orientation and mounting holes require confirmation.")
    elif part == "nodemcu_32s":
        option["sources"].append(source(id="board_guide", url="https://en.ai-thinker.com/Uploads/file/20190715/20190715150654_18687.pdf", scope="Ai-Thinker NodeMCU-32S V1 pinout; generic carrier revision not established", path=RESEARCH / "nodemcu32s.pdf", folder=folder))
        names = ["3V3", "EN", "GPIO36", "GPIO39", "GPIO34", "GPIO35", "GPIO32", "GPIO33", "GPIO25", "GPIO26", "GPIO27", "GPIO14", "GPIO12", "GND", "GPIO13", "GPIO9", "GPIO10", "GPIO11", "5V", "GPIO6", "GPIO7", "GPIO8", "GPIO15", "GPIO2", "GPIO0", "GPIO4", "GPIO16", "GPIO17", "GPIO5", "GPIO18", "GPIO19", "GND", "GPIO21", "GPIO3", "GPIO1", "GPIO22", "GPIO23", "GND"]
        add_rows(option, {"expansion": names})
        option["data_gaps"].append("Manufacturer V1 reference has different nominal dimensions from the generic entry. Its pinout is a reference requiring carrier match; dimensions and coordinates remain unverified.")
        option["electrical"]["usb_connector"] = "micro_usb_b_uart_bridge"
    elif part == "esp32_d1_r32":
        option["sources"].append(source(id="board_guide", url="https://raw.githubusercontent.com/espressif/arduino-esp32/master/variants/d1_uno32/pins_arduino.h", scope="Primary Espressif Arduino D1 UNO32 software aliases; not a mechanical header drawing", path=RESEARCH / "d1_uno32.h", folder=folder))
        text = (RESEARCH / "d1_uno32.h").read_text()
        for name, number in re.findall(r"static const uint8_t ([A-Z][A-Z0-9_]*) = (\d+);", text):
            if name == "LED_BUILTIN":
                continue
            item = pin(connector="software_alias", number=name, name=name, gpio=int(number), functions=[name])
            item["contact_scope"] = "software_alias_not_unique_physical_pad"
            option["pins"][name] = item
        option["data_gaps"].append("UNO outline does not establish electrical shield compatibility. Power/ICSP headers, mounting holes and physical contact order are not verified; pins are SDK aliases only.")
    elif part == "esp32_cam":
        option["sources"].append(source(id="board_guide", url="https://raw.githubusercontent.com/espressif/arduino-esp32/master/libraries/ESP32/examples/Camera/CameraWebServer/camera_pins.h", scope="Primary Espressif AI_THINKER camera assignments, not expansion-header geometry", path=RESEARCH / "camera_pins.h", folder=folder))
        text = (RESEARCH / "camera_pins.h").read_text().split("CAMERA_MODEL_AI_THINKER")[1].split("#elif")[0]
        for name, number in re.findall(r"#define ([A-Z0-9_]+)_GPIO_NUM\s+(-?\d+)", text):
            if int(number) < 0:
                continue
            option["onboard_gpio_connections"].append({"gpio": int(number), "function": "camera_" + name.lower(), "source_id": "board_guide"})
        option["sources"].append(source(id="schematic", url="https://raw.githubusercontent.com/SeeedDocument/forum_doc/master/reg/ESP32_CAM_V1.6.pdf", scope="Original ESP32_CAM V1.6 schematic archived by Seeed; 2x8 headers, SD and PSRAM wiring", path=RESEARCH / "esp32_cam_schematic.pdf", folder=folder))
        add_rows(option, {"P1": ["GND", "GPIO1", "GPIO3", "GND", "GPIO0", "GPIO16", "VCC_SELECTED", "3V3"], "P2": ["GPIO4", "GPIO2", "GPIO14", "GPIO15", "GND", "GPIO13", "GPIO12", "5V"]}, "schematic")
        for gpio in (2, 4, 12, 13, 14, 15):
            option["onboard_gpio_connections"].append({"gpio": gpio, "function": "micro_sd_slot", "source_id": "schematic"})
        option["onboard_gpio_connections"].append({"gpio": 16, "function": "psram_chip_select_do_not_drive", "source_id": "schematic"})
        option["data_gaps"].append("Ai-Thinker legacy URLs redirect to its home page. Archived V1.6 schematic is the pin reference; exact clone revision, pad coordinates and outline still need confirmation.")
        option["coordinate_system"]["view"] = "top_no_usb_socket_orientation_requires_board_drawing"
    elif part == "stamp_c3u":
        add_manufacturer_references(option, "stamp_c3u")
        for source_id, name, url in (("pinmap", "pinmap.jpg", "https://m5stack-doc.oss-cn-shenzhen.aliyuncs.com/525/C122-B_PinMap_01.jpg"), ("mechanical", "dimensions.webp", "https://static-cdn.m5stack.com/resource/docs/products/core/stamp_c3u/stamp_c3%26c3u_size_01.webp"), ("schematic", "schematic.webp", "https://static-cdn.m5stack.com/resource/docs/products/core/stamp_c3u/stamp_c3u_sch_01.webp")):
            option["sources"].append(source(id=source_id, url=url, scope="Manufacturer Stamp-C3U " + source_id, path=RESEARCH / "stamp_c3u" / name, folder=folder))
        add_rows(option, {"left_in_vendor_drawing": ["GPIO3", "GPIO4", "GPIO5", "GPIO6", "GPIO7", "GPIO8", "GPIO10", "5V", "GND", "5V", "GPIO1", "GPIO0"], "right_in_vendor_drawing": ["3V3", "GPIO21", "GPIO20", "EN", "GPIO9", "GND", "GPIO18", "GPIO19", "5V", "GND"]}, "pinmap")
        option["dimensions_mm"].update(width=20, height=34, pcb_thickness=1, assembled_height=4.6, source_id="mechanical", scope="dimensioned_board_and_assembled_thickness", status="manufacturer_drawing")
        option["mounting_hole_details"].append({"x_mm": 0, "y_mm": -2, "diameter_mm": 2.1, "source_id": "mechanical", "derivation": "Centred X; hole 19 mm from USB-end edge, 34 mm board; rotate drawing to USB-up."})
        option["mounting_hole_status"] = "manufacturer_dimensioned_drawing"
        option["electrical"]["usb_connector"] = "usb_c_native_serial_jtag"
        option["onboard_gpio_connections"].append({"gpio": 2, "function": "sk6812_rgb_led", "source_id": "schematic"})
        option["onboard_gpio_connections"].append({"gpio": 9, "function": "boot_button", "source_id": "schematic"})
        option["memory"]["external_flash_bytes"] = 4194304
        option["notes"].append("Manufacturer specification text incorrectly lists G22. The pinmap and C3 schematic show G20/G21, which are used here.")
        option["data_gaps"].append("Pad X centres are not dimensioned; positions remain null. Row names refer to the USB-down manufacturer illustration, not the normalized coordinate view.")
    else:
        if part == "esp32_h2_supermini":
            option["sources"].append(source(id="board_guide", url="https://docs.zephyrproject.org/latest/boards/others/esp32h2_supermini/doc/index.html", scope="Primary Zephyr target documentation; does not establish Tenstar header geometry"))
        if part == "esp32_c6_supermini":
            option["sources"].append(source(id="related_variant", url="https://raw.githubusercontent.com/espressif/arduino-esp32/master/variants/makergo_c6_supermini/pins_arduino.h", scope="Related MakerGO C6 SuperMini has 25 pads, not proof of the Tenstar 20-contact board pinout"))
        option["data_gaps"].append("No revision-specific primary Tenstar header drawing was established. Header GPIO assignments, pad centres and hole locations remain unknown; related SuperMini variants are not substituted.")


def enrich(option):
    family_name = option["chip"].get("family", option["chip"]["part_number"])
    if family_name == "rp2350a":
        family_name = "rp2350"
    option["chip"]["family"] = family_name
    resources = {
        "rp2040": (2, 133, 16, 2, 2, 2, 8),
        "rp2350": (2, 150, 24, 2, 2, 2, 12),
        "esp32": (2, 240, 16, 2, None, 3, 0),
        "esp32_c3": (1, 160, 6, 1, 1, 2, 0),
        "esp32_s2": (1, 240, 8, 2, 2, 2, 0),
        "esp32_s3": (2, 240, 8, 2, 2, 3, 0),
        "esp32_c6": (1, 160, 6, 1, 1, 2, 0),
        "esp32_h2": (1, 96, 6, 2, 1, 2, 0),
    }
    core_count, clock, pwm, i2c, spi, uart, pio = resources[family_name]
    option["chip_resources"] = {
        "cpu_core_count": core_count,
        "clock_max_mhz": clock,
        "pwm_channels": pwm,
        "hardware_i2c_controllers": i2c,
        "general_purpose_spi_controllers": spi,
        "hardware_uart_controllers": uart,
        "pio_state_machines": pio,
        "scope": "silicon resources; board routing and firmware may reduce availability",
        "source_id": "chip_datasheet",
    }
    option["lab_support"] = {
        "status": "catalogue_reference_only",
        "automatic_firmware_enable": False,
        "requires_reviewed_board_profile": True,
        "gpio_matrix_routing": family_name.startswith("esp32"),
    }
    option["pinout_status"] = "not_established" if not option["pins"] else "documented_contact_inventory"
    if option["part_number"] == "esp32_d1_r32":
        option["pinout_status"] = "software_aliases_only"
    if any(pin.get("gpio") is not None and pin.get("chip_pin_number") is None for pin in option["pins"].values()):
        option["data_gaps"].append("Chip package/module pad numbers are not fully transcribed; null chip_pin_number values must not be replaced with carrier-header numbers.")
    option["mounting_holes"] = []
    for hole in option["mounting_hole_details"]:
        option["mounting_holes"].append([hole["x_mm"], hole["y_mm"]])
    if option["mounting_holes"]:
        option["mounting_hole_radius_name"] = "m2"
    option["breakout_pcb_width"] = option["dimensions_mm"]["width"]
    option["breakout_pcb_height"] = option["dimensions_mm"]["height"]
    option["electrical"]["gpio_5v_tolerant"] = False
    option["svg_details"] = {"svg_name": "microcontroller", "stylesheet": "microcontroller", "width": option["breakout_pcb_width"], "height": option["breakout_pcb_height"]}
    for key, item in option["pins"].items():
        gpio = item.get("gpio")
        name = item["name"]
        item.setdefault("functions", [])
        item.setdefault("restrictions", [])
        item.setdefault("aliases", [])
        item.setdefault("surface", "unspecified")
        if gpio is not None:
            item["type"] = "gpio"
        elif name in ("GND", "AGND", "G"):
            item["type"] = "ground"
        elif name in ("NC", "N/C"):
            item["type"] = "not_connected"
        elif name in ("EN", "3V3_EN", "RESET", "RST", "RUN", "CHIP_PU"):
            item["type"] = "control"
        elif "VREF" in name.upper():
            item["type"] = "analog_reference"
        elif name in ("SWDIO", "SWCLK", "SWD", "SWC"):
            item["type"] = "debug"
        elif name in ("D+", "D-", "USB_D+", "USB_D-"):
            item["type"] = "usb_data"
        elif any(token in name.upper() for token in ("3V3", "3.3V", "VBUS", "VBAT", "5V", "VSYS", "VSENSOR", "VCC", "VUSB", "VIN")):
            item["type"] = "power"
        else:
            item["type"] = "control"
        item["direction"] = "bidirectional" if gpio is not None else "not_applicable"
        item["capabilities"] = []
        item["signal_types"] = []
        item["available_for_general_io"] = gpio is not None
        item["adc_channel"] = None
        item["adc_unit"] = None
        if gpio is None:
            item["functions"].append(name)
            continue
        item["capabilities"].extend(["gpio", "digital_input", "digital_output", "pwm"])
        item["signal_types"].append("digital")
        item["logic_voltage_v"] = 3.3
        item["input_only"] = False
        if family_name.startswith("esp32"):
            item["routable_peripherals"] = ["uart", "spi", "i2c", "i2s", "rmt", "pwm"]
        if family_name in ("rp2040", "rp2350"):
            if 26 <= gpio <= 29:
                item["adc_channel"] = gpio - 26
                item["adc_unit"] = 0
            item["functions"].extend([f"PWM{gpio // 2 % 8}{'A' if gpio % 2 == 0 else 'B'}", "PIO"])
            uart_index = gpio % 4
            item["functions"].append(f"UART{(gpio + 4) // 8 % 2}_{['TX', 'RX', 'CTS', 'RTS'][uart_index]}")
            item["functions"].append(f"I2C{gpio // 2 % 2}_{'SDA' if gpio % 2 == 0 else 'SCL'}")
            item["functions"].append(f"SPI{gpio // 8 % 2}_{['RX', 'CSn', 'SCK', 'TX'][gpio % 4]}")
            item["function_mapping_source_id"] = "chip_datasheet"
        elif family_name == "esp32":
            adc1 = {36: 0, 37: 1, 38: 2, 39: 3, 32: 4, 33: 5, 34: 6, 35: 7}
            adc2 = {4: 0, 0: 1, 2: 2, 15: 3, 13: 4, 12: 5, 14: 6, 27: 7, 25: 8, 26: 9}
            if gpio in adc1:
                item["adc_unit"], item["adc_channel"] = 1, adc1[gpio]
            if gpio in adc2:
                item["adc_unit"], item["adc_channel"] = 2, adc2[gpio]
                item["restrictions"].append("ADC2 conflicts with Wi-Fi on classic ESP32.")
            if gpio >= 34:
                item["input_only"] = True
                item["direction"] = "input"
                item["capabilities"].remove("digital_output")
                item["capabilities"].remove("pwm")
                item["restrictions"].append("Input only; no internal pull-up or pull-down.")
                item["routable_peripherals"] = ["gpio_matrix_inputs_only"]
            if gpio in (25, 26):
                item["capabilities"].append("analog_output")
                item["functions"].append("DAC" + str(gpio - 24))
            if gpio in range(6, 12):
                item["available_for_general_io"] = False
                item["restrictions"].append("Connected to flash; do not use as application GPIO.")
            if gpio in (0, 2, 5, 12, 15):
                item["restrictions"].append("Boot strapping pin; external levels affect startup.")
        elif family_name == "esp32_c3":
            if gpio <= 4:
                item["adc_unit"], item["adc_channel"] = 1, gpio
            elif gpio == 5:
                item["adc_unit"], item["adc_channel"] = 2, 0
                item["restrictions"].append("ADC2 is not supported by ESP-IDF oneshot/continuous drivers on C3; exclude from lab analog controls.")
            if gpio in (2, 8, 9):
                item["restrictions"].append("Boot strapping pin; verify external levels at reset.")
        elif family_name in ("esp32_s2", "esp32_s3"):
            if 1 <= gpio <= 10:
                item["adc_unit"], item["adc_channel"] = 1, gpio - 1
            elif 11 <= gpio <= 20:
                item["adc_unit"], item["adc_channel"] = 2, gpio - 11
            if family_name == "esp32_s2" and gpio in (17, 18):
                item["capabilities"].append("analog_output")
                item["functions"].append("DAC" + str(gpio - 16))
            if family_name == "esp32_s2" and gpio == 46:
                item["input_only"] = True
                item["direction"] = "input"
                item["capabilities"].remove("digital_output")
                item["capabilities"].remove("pwm")
                item["routable_peripherals"] = ["gpio_matrix_inputs_only"]
            if gpio in ((0, 45, 46) if family_name == "esp32_s2" else (0, 3, 45, 46)):
                item["restrictions"].append("Boot strapping pin; external levels affect startup.")
            if option["part_number"] == "esp32_s3_devkitc_1_n8r8" and gpio in (35, 36, 37):
                item["available_for_general_io"] = False
                item["restrictions"].append("Reserved for octal PSRAM on N8R8 module.")
        elif family_name == "esp32_c6":
            if 0 <= gpio <= 6:
                item["adc_unit"], item["adc_channel"] = 1, gpio
            if gpio in (4, 5, 8, 9, 15):
                item["restrictions"].append("Boot strapping pin; external levels affect startup.")
        elif family_name == "esp32_h2":
            if 1 <= gpio <= 5:
                item["adc_unit"], item["adc_channel"] = 1, gpio - 1
            if gpio in (8, 9, 25):
                item["restrictions"].append("Strapping pin; check chip datasheet and board revision.")
        if item["adc_channel"] is not None:
            item["capabilities"].append("analog_input")
            item["signal_types"].append("analog")
        usb_pins = {"esp32_c3": (18, 19), "esp32_s2": (19, 20), "esp32_s3": (19, 20), "esp32_c6": (12, 13), "esp32_h2": (26, 27)}
        if family_name in usb_pins and gpio in usb_pins[family_name]:
            item["restrictions"].append("USB D-/D+ function: GPIO use can disconnect native USB; check board routing.")
            item["functions"].append("USB_D-" if gpio == usb_pins[family_name][0] else "USB_D+")
        if option["part_number"] == "esp32_cam" and gpio == 16:
            item["available_for_general_io"] = False
            item["restrictions"].append("Connected to PSRAM chip select on V1.6; not free GPIO.")
        for connection in option.get("onboard_gpio_connections", []):
            if connection["gpio"] == gpio:
                if connection.get("function"):
                    item["restrictions"].append("Shared onboard net: " + connection["function"])
                elif connection.get("net_name"):
                    item["aliases"].append(connection["net_name"])
        item["lab_analog_eligible"] = item["adc_channel"] is not None and item["available_for_general_io"] and not (family_name == "esp32_c3" and item["adc_unit"] == 2)
        item["capability_source_id"] = "chip_datasheet"
        item["functions"] = list(dict.fromkeys(item["functions"]))
    option["gpio_summary"] = {
        "exposed": sorted(set(item["gpio"] for item in option["pins"].values() if item.get("gpio") is not None)),
        "general_io_candidates": sorted(set(item["gpio"] for item in option["pins"].values() if item.get("available_for_general_io"))),
        "analog_candidates": sorted(set(item["gpio"] for item in option["pins"].values() if item.get("lab_analog_eligible"))),
        "automatic_firmware_enable": False,
    }
    option["default_interfaces"] = {}
    interface_names = {"i2c": ["SDA", "SCL"], "spi": ["SCK", "MOSI", "MISO"], "uart": ["TX", "RX"]}
    for interface_name, names in interface_names.items():
        signals = {}
        for item in option["pins"].values():
            if item.get("gpio") is not None:
                for signal_name in names:
                    if signal_name == item["name"] or signal_name in item["functions"] or signal_name in item["aliases"]:
                        signals[signal_name.lower() + "_gpio"] = item["gpio"]
        if len(signals) == len(names):
            option["default_interfaces"][interface_name] = signals
    option["data_gaps"] = list(dict.fromkeys(option["data_gaps"]))


def main(**kwargs):
    seeds = json.loads((RESEARCH / "original_catalogue.json").read_text())
    boards = []
    for path in sorted((LAB / "source_file").glob("*/definition.yaml")):
        option = yaml.safe_load(path.read_text(encoding="utf-8"))
        if option["item_kind"] != "breakout":
            continue
        destination = ROOT / "source_file" / path.parent.name
        destination.mkdir(parents=True, exist_ok=True)
        for item in path.parent.iterdir():
            if item.is_dir() and item.name == "reference":
                shutil.copytree(item, destination / item.name, dirs_exist_ok=True)
        option["definition_import"] = {"project": LAB.name, "path": path.relative_to(LAB).as_posix(), "date": "2026-10-22", "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        option["type_1"] = "microcontroller"
        option["type_2"] = option["chip"]["part_number"]
        option["type_3"] = option["form_factor"]
        if option["type_2"].startswith("rp"):
            option["chip"]["family"] = "rp2040" if option["type_2"] == "rp2040" else "rp2350"
        else:
            option["is_device_specific_reference"] = True
            option["name_readable"] += " (observed AZ silicon; carrier unverified)"
        option["mounting_hole_status"] = "documented" if option["mounting_holes"] else "none_shown_in_captured_manufacturer_sources"
        option["mounting_hole_candidates"] = []
        if option["type_2"].startswith("rp"):
            option["sources"].append(source(id="chip_datasheet", url="https://datasheets.raspberrypi.com/" + option["chip"]["family"] + "/" + option["chip"]["family"] + "-datasheet.pdf", scope="GPIO mux, PWM, ADC and electrical characteristics"))
        option.setdefault("electrical", {})
        option.setdefault("onboard_gpio_connections", [])
        option["legacy_ids"] = []
        for seed in seeds:
            if option["type_2"].startswith("rp") and (seed["part_number"] == option["part_number"] or seed["part_number"] == "18288" and option["part_number"] == "dev_18288"):
                option["legacy_ids"].append(legacy_identifier(seed))
        enrich(option)
        boards.append(option)
    espressif = {"esp32_devkitc_32e": "esp32-devkitc", "esp32_c3_devkitm_1": "esp32-c3-devkitm-1", "esp32_c3_devkitc_02": "esp32-c3-devkitc-02", "esp32_s2_devkitc_1": "esp32-s2-devkitc-1", "esp32_s3_devkitc_1_n8r8": "esp32-s3-devkitc-1", "esp32_c6_devkitc_1_n8": "esp32-c6-devkitc-1", "esp32_c6_devkitm_1_n4": "esp32-c6-devkitm-1", "esp32_pico_kit_v4": "esp32-pico-kit"}
    adafruit = {"5405": "qtpy_c3", "qt_py_esp32_s3": "qtpy_s3", "3405": "huzzah32", "5477": "feather_s3"}
    xiao = {"xiao_esp32c3": "xiao_c3", "xiao_esp32s3": "xiao_s3", "xiao_esp32c6": "xiao_c6"}
    wemos = {"lolin_c3_mini": "c3_mini", "lolin_s2_mini": "s2_mini", "lolin_s3_mini": "s3_mini", "lolin_d32": "d32", "lolin_d32_pro": "d32_pro"}
    for seed in seeds:
        if seed["type_2"].startswith("rp"):
            continue
        option = base(seed)
        part = seed["part_number"]
        if part in espressif:
            build_espressif(option, espressif[part])
        elif part in adafruit:
            build_adafruit(option, adafruit[part])
        elif part in xiao:
            build_xiao(option, xiao[part])
        elif part in wemos:
            build_wemos(option, wemos[part])
        else:
            build_extra(option)
        enrich(option)
        boards.append(option)
    families = {}
    for option in boards:
        name = option["chip"]["family"]
        families.setdefault(name, []).append(option)
    for name, options in families.items():
        text = '"""' + name.upper() + ' board definitions. Edit these verbose dictionaries directly."""\n\n\n'
        text += 'def main(**kwargs):\n    options = []\n\n'
        for option in options:
            text += "    # " + option["name_readable"] + "\n"
            text += "    option = " + literal(option, 4) + "\n"
            text += "    options.append(option)\n\n"
        text += "    return options\n"
        chips = []
        for path in sorted((LAB / "source_file").glob("*/definition.yaml")):
            chip = yaml.safe_load(path.read_text(encoding="utf-8"))
            if chip["item_kind"] != "chip":
                continue
            chip_family = "esp32_c3" if chip["part_number"].startswith("esp32_c3") else "rp2040" if chip["part_number"] == "rp2040" else "rp2350"
            if chip_family != name:
                continue
            destination = ROOT / "source_file" / path.parent.name
            destination.mkdir(parents=True, exist_ok=True)
            if (path.parent / "reference").exists():
                shutil.copytree(path.parent / "reference", destination / "reference", dirs_exist_ok=True)
            chips.append(chip)
        text += "\n\ndef get_chips(**kwargs):\n    options = []\n\n"
        for chip in chips:
            text += "    option = " + literal(chip, 4) + "\n"
            text += "    options.append(option)\n\n"
        text += "    return options\n"
        (ROOT / ("working_oomp_populate_microcontroller_" + name + ".py")).write_text(text, encoding="utf-8")
    print("Materialized", len(boards), "boards in", len(families), "families")


if __name__ == "__main__":
    main()
