"""One-time, offline enrichment from reviewed Arduino source snapshots.

The family dictionaries remain the editable authority. This audit script refuses
to overwrite already-enriched records; it is not part of the normal export.
"""

import ast
import copy
import hashlib
import importlib
import json
from pathlib import Path
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
RESEARCH = ROOT / "research/microcontrollers/interface_defaults"

RP_VARIANTS = {
    "4884": "adafruit_feather", "pico": "rpipico", "pico_h": "rpipico",
    "pico_w": "rpipicow", "pico_wh": "rpipicow",
    "pico_2": "rpipico2", "pico_2_with_headers": "rpipico2",
    "pico_2_w": "rpipico2w", "pico_2_w_with_headers": "rpipico2w",
    "dev_18288": "sparkfun_promicrorp2040", "4900": "adafruit_qtpy",
    "102010428": "seeed_xiao_rp2040", "102010550": "seeed_xiao_rp2350",
    "rp2040_zero": "waveshare_rp2040_zero", "rp2040_zero_m": "waveshare_rp2040_zero",
    "rp2350_zero": "waveshare_rp2350_zero", "rp2350_zero_m": "waveshare_rp2350_zero",
    "6000": "adafruit_feather_rp2350_hstx",
}
ESP_VARIANTS = {
    "esp32_devkit_v1_30_pin": "doitESP32devkitV1", "esp32_devkitc_32e": "esp32",
    "nodemcu_32s": "nodemcu-32s", "lolin_d32": "d32", "lolin_d32_pro": "d32_pro",
    "esp32_cam": "esp32", "esp32_pico_kit_v4": "pico32", "3405": "feather_esp32",
    "esp32_d1_r32": "d1_uno32", "esp32_c3_supermini": "esp32c3",
    "esp32_c3_devkitm_1": "esp32c3", "esp32_c3_devkitc_02": "esp32c3",
    "xiao_esp32c3": "XIAO_ESP32C3", "5405": "adafruit_qtpy_esp32c3",
    "lolin_c3_mini": "lolin_c3_mini", "stamp_c3u": "esp32c3",
    "esp32_s2_devkitc_1": "esp32s2", "lolin_s2_mini": "lolin_s2_mini",
    "esp32_s3_devkitc_1_n8r8": "esp32s3", "xiao_esp32s3": "XIAO_ESP32S3",
    "qt_py_esp32_s3": "adafruit_qtpy_esp32s3_n4r2", "lolin_s3_mini": "lolin_s3_mini",
    "5477": "adafruit_feather_esp32s3", "esp32_c6_devkitc_1_n8": "esp32c6",
    "esp32_c6_devkitm_1_n4": "esp32c6", "xiao_esp32c6": "XIAO_ESP32C6",
}
SIGNALS = {"uart": ["tx", "rx"], "i2c": ["sda", "scl"], "spi": ["sck", "mosi", "miso", "ss"]}


def literal(value, indent=0):
    if isinstance(value, (dict, list)):
        opening, closing = ("{", "}") if isinstance(value, dict) else ("[", "]")
        if not value:
            return opening + closing
        items = value.items() if isinstance(value, dict) else enumerate(value)
        rows = [opening]
        for key, item in items:
            prefix = repr(key) + ": " if isinstance(value, dict) else ""
            rows.append(" " * (indent + 4) + prefix + literal(item, indent + 4) + ",")
        return "\n".join(rows + [" " * indent + closing])
    return json.dumps(value, ensure_ascii=False) if isinstance(value, str) else repr(value)


def enrich(board):
    if "interface_defaults_version" in board:
        raise ValueError("Already enriched; edit family dictionaries directly")
    part = board["part_number"]
    key = "rp" if board["chip"]["family"].startswith("rp") else "esp32"
    variant = (RP_VARIANTS if key == "rp" else ESP_VARIANTS).get(part)
    defaults = {}
    for pin in board["pins"].values():
        pin["default_interface_roles"] = []
    board["interface_defaults_version"] = 1
    board["default_interfaces"] = defaults
    if variant is None:
        assert not board["pins"], part
        for protocol, signals in SIGNALS.items():
            defaults[protocol] = {
                "protocol": protocol, "status": "unverified", "basis": "unknown",
                "framework": None, "variant": None, "variant_scope": "unverified_carrier",
                "api": None, "peripheral": None, "source_ids": [],
                **{signal + "_gpio": None for signal in signals},
                "pin_keys": {signal: [] for signal in signals},
                "signal_status": {signal: "unverified" for signal in signals},
                "notes": ["Revision-specific carrier pinout is unverified. Do not substitute a similarly named board or generic SoC default."],
            }
        return

    index = json.loads((RESEARCH / (key + "_index.json")).read_text())
    sources = []

    def evidence(filename, upstream, source_id, scope):
        path = RESEARCH / filename
        relative = "reference/interface_defaults/" + filename
        identifier = "_".join(board["taxonomy_" + str(n)] for n in range(1, 16) if board["taxonomy_" + str(n)])
        target = ROOT / "source_file" / identifier / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        content = path.read_text()
        extra = {}
        if upstream == "boards.txt":
            # Keep portable evidence small while retaining exact selection lines.
            lines = content.splitlines()
            prefixes = [line.split(".build.variant=")[0] for line in lines if line.endswith(".build.variant=" + variant)]
            content = "\n".join(line for line in lines if any(line.startswith(p + ".name=") or line.startswith(p + ".build.variant=") for p in prefixes)) + "\n"
            target.write_text(content, encoding="utf-8")
            extra = {"content_scope": "excerpt_of_board_names_and_variant_selections", "source_document_sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        else:
            shutil.copy2(path, target)
        board["sources"].append({
            "id": source_id, "url": f"https://raw.githubusercontent.com/{index['repo']}/{index['revision']}/{upstream}",
            "revision": index["revision"], "retrieved_date": "2026-10-23", "scope": scope,
            "local_file": relative, "sha256": hashlib.sha256(target.read_bytes()).hexdigest(), **extra,
        })
        sources.append(source_id)
        return path.read_text()

    text = evidence(key + "_" + variant + ".h", f"variants/{variant}/pins_arduino.h", "interface_variant", "Arduino variant pin assignments; not a physical header drawing")
    if variant in ("d32", "d32_pro"):
        text += evidence("esp32_d32_core.h", "variants/d32/d32_core.h", "interface_variant_base", "Included common LOLIN D32 pin aliases")
    if part == "qt_py_esp32_s3":
        evidence("esp32_adafruit_qtpy_esp32s3_nopsram.h", "variants/adafruit_qtpy_esp32s3_nopsram/pins_arduino.h", "interface_variant_other_sku", "Both published QT Py S3 memory variants have identical bus pin aliases")
    evidence(key + "_boards.txt", "boards.txt", "interface_board_selection", "Framework board names and variant selection; generic selections remain explicitly scoped")
    runtime_sources = {}
    for protocol, filename, upstream in (
        ("uart", "SerialUART.cpp" if key == "rp" else "HardwareSerial.cpp", "cores/rp2040/SerialUART.cpp" if key == "rp" else "cores/esp32/HardwareSerial.cpp"),
        ("i2c", "Wire.cpp", "libraries/Wire/src/Wire.cpp"),
        ("spi", "SPI.cpp", "libraries/SPI/src/SPI.cpp"),
    ):
        source_id = "interface_runtime_" + protocol
        evidence(key + "_" + filename, upstream, source_id, "Framework API construction/default behavior; USB Serial is separate from UART pin aliases")
        runtime_sources[protocol] = source_id
    variant_sources = [s for s in sources if not s.startswith("interface_runtime_")]

    def number(symbol):
        expression = (r"#define\s+" + re.escape(symbol) + r"\s+\(?([0-9]+)u?\)?" if key == "rp"
                      else r"\b" + re.escape(symbol) + r"\s*=\s*([0-9]+)\s*;")
        match = re.search(expression, text)
        if not match:
            raise ValueError("Missing reviewed symbol " + symbol)
        value = int(match[1])
        return None if key == "rp" and value == 31 else value

    def add(name, protocol, values, api, peripheral=None, notes=None):
        scope = "board_variant"
        if key == "esp32" and variant in ("esp32", "esp32c3", "esp32s2", "esp32s3", "esp32c6"):
            scope = "generic_target_selection"
        entry = {
            "protocol": protocol, "status": "documented",
            "basis": "framework_pin_aliases" if key == "esp32" and protocol == "uart" else "framework_defaults",
            "framework": "arduino-pico" if key == "rp" else "arduino-esp32",
            "variant": variant, "variant_scope": scope, "api": api, "peripheral": peripheral,
            "source_ids": variant_sources + [runtime_sources[protocol]],
            **{signal + "_gpio": value for signal, value in values.items()},
            "pin_keys": {}, "signal_status": {}, "notes": list(notes or []),
        }
        if scope == "generic_target_selection":
            entry["notes"].append("Defaults apply when selecting this generic Arduino target; they do not establish a carrier-specific hardware convention.")
        if protocol == "uart":
            entry["notes"].append("UART GPIOs are distinct from USB CDC/USB Serial. The meaning of Serial depends on the core and USB build settings.")
            if key == "esp32":
                entry["notes"].append("TX/RX are board variant aliases. Pass the GPIOs explicitly to the selected HardwareSerial instance; no-argument pin selection can use SoC UART defaults instead.")
        if protocol == "spi":
            entry["notes"].append("ss is the framework chip-select alias/default, not an automatically asserted CS. Select and drive CS as required by the peripheral and library.")
        if part == "esp32_cam" and protocol in ("i2c", "spi"):
            entry["notes"].append("These generic defaults are not broken out on the ESP32-CAM headers; camera/SD routing requires an explicit application-specific choice.")
        if part == "lolin_d32_pro" and protocol == "spi":
            entry["notes"].append("SS expands to TF_CS (GPIO4), shared with the onboard microSD slot; the included base header's SS=5 is overridden.")
        for signal, value in values.items():
            pins = [p for p, data in board["pins"].items() if value is not None and data.get("gpio") == value]
            entry["pin_keys"][signal] = pins
            status = "mapped" if pins else "not_in_pinout"
            if value is None:
                status = "not_defined"
            elif pins and all(board["pins"][p].get("contact_scope") == "software_alias_not_unique_physical_pad" for p in pins):
                status = "software_alias_only"
            entry["signal_status"][signal] = status
            for pin in pins:
                board["pins"][pin]["default_interface_roles"].append({"interface": name, "signal": signal})
        defaults[name] = entry

    if key == "rp":
        for index_number in range(2):
            suffix = "" if index_number == 0 else "_secondary"
            serial_number = index_number + 1
            uart = {s: number(f"PIN_SERIAL{serial_number}_{s.upper()}") for s in SIGNALS["uart"]}
            # Preserve the existing board-labelled TX/RX convention on QT Py.
            uart_name = "uart" + suffix
            if part == "4900":
                uart_name = "uart" if serial_number == 2 else "uart_secondary"
            if any(v is not None for v in uart.values()):
                note = ["On QT Py RP2040, labelled TX/RX use Serial2; Serial1 uses the A1/A0 pads."] if part == "4900" else []
                add(uart_name, "uart", uart, f"Serial{serial_number}", f"uart{index_number}", note)
            wire = {s: number(f"PIN_WIRE{index_number}_{s.upper()}") for s in SIGNALS["i2c"]}
            if any(v is not None for v in wire.values()):
                device = re.search(r"#define\s+__WIRE" + str(index_number) + r"_DEVICE\s+\(?(i2c[01])", text)
                add("i2c" + suffix, "i2c", wire, "Wire" + ("1" if index_number else ""), device[1] if device else f"i2c{index_number}")
            spi = {s: number(f"PIN_SPI{index_number}_{s.upper()}") for s in SIGNALS["spi"]}
            if any(v is not None for v in spi.values()):
                add("spi" + suffix, "spi", spi, "SPI" + ("1" if index_number else ""), f"spi{index_number}")
    else:
        for protocol, signals in SIGNALS.items():
            values = {s: number(s.upper()) for s in signals}
            if variant == "d32_pro" and protocol == "spi":
                values["ss"] = 4  # pins_arduino.h: #define SS TF_CS; #define TF_CS 4
            add(protocol, protocol, values, {"uart": None, "i2c": "Wire", "spi": "SPI"}[protocol])
        if part == "qt_py_esp32_s3":
            add("i2c_secondary", "i2c", {"sda": number("SDA1"), "scl": number("SCL1")}, "Wire1", notes=["Separate STEMMA QT connector bus."])
    assert set(SIGNALS).issubset(defaults), part


def main():
    # Replace only the relevant dictionary fields, preserving unrelated edits.
    plans = []
    for path in sorted(ROOT.glob("working_oomp_populate_microcontroller_*.py")):
        text = path.read_text(encoding="utf-8")
        tree = ast.parse(text)
        function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")
        nodes = [n.value for n in function.body if isinstance(n, ast.Assign) and isinstance(n.value, ast.Dict) and any(isinstance(t, ast.Name) and t.id == "option" for t in n.targets)]
        module = importlib.import_module(path.stem)
        boards = module.main()
        assert len(boards) == len(nodes)
        if any("interface_defaults_version" in b for b in boards):
            raise ValueError("Already enriched; edit family dictionaries directly")
        plans.append((path, text, nodes, boards))
    for path, text, nodes, boards in plans:
        lines = text.splitlines(keepends=True)
        edits = []
        for node, original in zip(nodes, boards):
            board = copy.deepcopy(original)
            enrich(board)
            fields = {ast.literal_eval(k): v for k, v in zip(node.keys, node.values)}
            for field in ("default_interfaces", "sources", "pins"):
                value_node = fields[field]
                # UTF-8 byte offsets are used by AST; all field prefixes are ASCII.
                start = sum(len(s) for s in lines[:value_node.lineno - 1]) + value_node.col_offset
                end = sum(len(s) for s in lines[:value_node.end_lineno - 1]) + value_node.end_col_offset
                edits.append((start, end, literal(board[field], 8)))
            insertion = sum(len(s) for s in lines[:node.end_lineno - 1])
            edits.append((insertion, insertion, "        'interface_defaults_version': 1,\n"))
        for start, end, replacement in sorted(edits, reverse=True):
            text = text[:start] + replacement + text[end:]
        path.write_text(text, encoding="utf-8")
    print("Enriched", sum(len(p[3]) for p in plans), "boards")


if __name__ == "__main__":
    if sys.argv[1:] != ["--apply-once"]:
        raise SystemExit("One-time audit tool only; use --apply-once on an unenriched catalogue")
    main()
