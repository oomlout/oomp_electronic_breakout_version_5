import copy
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

import yaml

import microcontroller_catalogue as catalogue
import working_oomp_populate
import working_svg
import svg_help
from tools.export_microcontroller_catalogue import export, get_chips

ROOT = Path(__file__).resolve().parents[1]


class MicrocontrollerCatalogueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.boards = catalogue.main()

    def board(self, part, chip=None):
        matches = []
        for board in self.boards:
            if board["part_number"] == part and (chip is None or board["chip"]["part_number"] == chip):
                matches.append(board)
        self.assertEqual(len(matches), 1, part)
        return matches[0]

    def test_all_original_entries_survive_and_imports_are_separate(self):
        seeds = json.loads((ROOT / "research/microcontrollers/original_catalogue.json").read_text())
        for seed in seeds:
            matches = [board for board in self.boards if board["part_number"] == seed["part_number"] or any(legacy.endswith("_" + seed["manufacturer"] + "_" + seed["part_number"]) for legacy in board.get("legacy_ids", []))]
            self.assertTrue(matches, seed["part_number"])
        self.assertEqual(len(self.boards), 48)
        self.assertEqual(len(get_chips()), 6)
        self.assertEqual(sum(board["part_number"] == "rp2350_zero" for board in self.boards), 1)
        self.assertTrue(self.board("esp32_c3_supermini", "esp32_c3_az")["is_device_specific_reference"])

    def test_population_preserves_fixed_taxonomy_and_assembly_variants(self):
        with patch.object(working_oomp_populate, "write_extras") as writer:
            working_oomp_populate.main()
        written = writer.call_args.args[0]
        expected = {catalogue.get_identifier(option=board) for board in self.boards}
        actual = {catalogue.get_identifier(option=board) for board in written if board.get("type_1") == "microcontroller"}
        self.assertEqual(actual, expected)
        pico_h = self.board("pico_h")
        self.assertEqual(pico_h["taxonomy_7"], "with_headers")
        self.assertEqual(pico_h["taxonomy_8"], pico_h["breakout_description"])

    def test_pico_orientation_mounting_and_pin_functions(self):
        board = self.board("pico")
        self.assertEqual(board["mounting_holes"], [[-5.7, -23.5], [-5.7, 23.5], [5.7, -23.5], [5.7, 23.5]])
        first = board["pins"]["expansion_1"]
        self.assertEqual((first["gpio"], first["x_mm"], first["y_mm"]), (0, -8.89, 24.13))
        gpio8 = next(pin for pin in board["pins"].values() if pin.get("gpio") == 8)
        gpio12 = next(pin for pin in board["pins"].values() if pin.get("gpio") == 12)
        self.assertIn("UART1_TX", gpio8["functions"])
        self.assertIn("UART0_TX", gpio12["functions"])
        self.assertEqual(board["pins"]["expansion_37"]["type"], "control")
        self.assertEqual(board["pins"]["expansion_35"]["type"], "analog_reference")

    def test_espressif_corrected_contact_counts_and_carrier_outlines(self):
        c3 = self.board("esp32_c3_devkitm_1")
        self.assertEqual(len(c3["pins"]), 30)
        self.assertEqual((c3["breakout_pcb_width"], c3["breakout_pcb_height"]), (25.4, 38.91))
        self.assertTrue(all(pin["x_mm"] is None for pin in c3["pins"].values()))
        c6 = self.board("esp32_c6_devkitc_1_n8")
        self.assertEqual(len(c6["pins"]), 32)
        self.assertEqual(c6["breakout_pcb_height"], 51.8)
        self.assertEqual(c6["dimensions_mm"]["module_antenna_overhang_positive_y"], 6.35)
        self.assertEqual(sum(pin["type"] == "not_connected" for pin in c6["pins"].values()), 2)
        pico_kit = self.board("esp32_pico_kit_v4")
        self.assertEqual(len(pico_kit["pins"]), 40)
        self.assertEqual(pico_kit["assembly"]["normally_fitted_header_contacts"], 34)

    def test_classic_input_only_flash_and_psram_restrictions(self):
        board = self.board("esp32_devkitc_32e")
        pin = next(pin for pin in board["pins"].values() if pin.get("gpio") == 34)
        self.assertTrue(pin["input_only"])
        self.assertNotIn("digital_output", pin["capabilities"])
        self.assertNotIn("pwm", pin["capabilities"])
        self.assertTrue(set(range(6, 12)).isdisjoint(board["gpio_summary"]["general_io_candidates"]))
        s3 = self.board("esp32_s3_devkitc_1_n8r8")
        for gpio in (35, 36, 37):
            pin = next(pin for pin in s3["pins"].values() if pin.get("gpio") == gpio)
            self.assertFalse(pin["available_for_general_io"])
            self.assertNotIn(gpio, s3["gpio_summary"]["general_io_candidates"])
        cam = self.board("esp32_cam")
        self.assertEqual(len(cam["pins"]), 16)
        self.assertNotIn(16, cam["gpio_summary"]["general_io_candidates"])

    def test_c3_adc2_stays_digital_but_not_lab_analog(self):
        board = self.board("5405")
        pin = next(pin for pin in board["pins"].values() if pin.get("gpio") == 5)
        self.assertEqual((pin["adc_unit"], pin["adc_channel"]), (2, 0))
        self.assertIn("digital_output", pin["capabilities"])
        self.assertFalse(pin["lab_analog_eligible"])
        self.assertNotIn(5, board["gpio_summary"]["analog_candidates"])

    def test_related_variants_and_partial_holes_do_not_become_geometry(self):
        board = self.board("5477")
        self.assertEqual(board["memory"]["external_flash_bytes"], 4194304)
        self.assertEqual(board["memory"]["psram_bytes"], 2097152)
        self.assertFalse(board["mounting_holes"])
        self.assertEqual(len(board["mounting_hole_candidates"]), 4)
        self.assertTrue(all(pin["x_mm"] is None for pin in board["pins"].values()))
        for part in ("lolin_d32", "lolin_d32_pro", "lolin_c3_mini", "lolin_s2_mini", "lolin_s3_mini"):
            board = self.board(part)
            self.assertFalse(board["mounting_holes"])
            self.assertTrue(all(hole["y_mm"] is None for hole in board["mounting_hole_candidates"]))
        stamp = self.board("stamp_c3u")
        self.assertEqual(stamp["mounting_holes"], [[0, -2]])
        self.assertEqual(stamp["mounting_hole_details"][0]["diameter_mm"], 2.1)
        self.assertNotIn(22, stamp["gpio_summary"]["exposed"])
        self.assertIn(20, stamp["gpio_summary"]["exposed"])

    def test_every_positioned_pad_fits_its_pcb_envelope(self):
        for board in self.boards:
            for key, pin in board["pins"].items():
                if pin["x_mm"] is None:
                    continue
                with self.subTest(board=board["part_number"], pin=key):
                    self.assertLessEqual(abs(pin["x_mm"]), board["breakout_pcb_width"] / 2 + 1)
                    self.assertLessEqual(abs(pin["y_mm"]), board["breakout_pcb_height"] / 2 + 1)

    def test_reference_files_are_local_and_match_checksums(self):
        for option in self.boards + get_chips():
            folder = ROOT / "source_file" / catalogue.get_identifier(option=option)
            for source in option["sources"]:
                if source.get("local_file"):
                    path = (folder / source["local_file"]).resolve()
                    self.assertTrue(path.is_relative_to(folder.resolve()))
                    self.assertTrue(path.is_file(), str(path))
                    if source.get("sha256"):
                        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), source["sha256"])

    def test_svg_hits_exactly_match_positioned_pads(self):
        for board in self.boards:
            root = ET.fromstring(working_svg.microcontroller_svg(board=board))
            targets = [element for element in root.iter() if element.get("data-pin")]
            expected = {key for key, pin in board["pins"].items() if pin["x_mm"] is not None}
            self.assertEqual({element.get("data-pin") for element in targets}, expected)
            self.assertEqual(len(targets), len(expected))
            self.assertEqual(len({element.get("id") for element in targets}), len(targets))

    def test_schema_rejects_dangerous_mapping_mutations(self):
        board = copy.deepcopy(self.board("esp32_devkitc_32e"))
        pin = next(pin for pin in board["pins"].values() if pin.get("gpio") == 34)
        pin["capabilities"].append("digital_output")
        with self.assertRaisesRegex(ValueError, "Input-only"):
            catalogue.validate(option=board)

    def test_pico_defaults_include_primary_and_secondary_peripherals(self):
        for part in ("pico", "pico_h", "pico_w", "pico_wh", "pico_2", "pico_2_w"):
            defaults = self.board(part)["default_interfaces"]
            self.assertEqual((defaults["uart"]["tx_gpio"], defaults["uart"]["rx_gpio"]), (0, 1))
            self.assertEqual((defaults["i2c"]["sda_gpio"], defaults["i2c"]["scl_gpio"]), (4, 5))
            self.assertEqual([defaults["spi"][s + "_gpio"] for s in ("sck", "mosi", "miso", "ss")], [18, 19, 16, 17])
            self.assertEqual(defaults["uart_secondary"]["api"], "Serial2")
            self.assertEqual(defaults["i2c_secondary"]["sda_gpio"], 26)
            self.assertEqual(defaults["spi_secondary"]["sck_gpio"], 14)

    def test_board_labels_framework_objects_and_secondary_connectors(self):
        qtpy = self.board("4900")["default_interfaces"]
        self.assertEqual((qtpy["uart"]["api"], qtpy["uart"]["tx_gpio"], qtpy["uart"]["rx_gpio"]), ("Serial2", 20, 5))
        self.assertEqual((qtpy["uart_secondary"]["api"], qtpy["uart_secondary"]["tx_gpio"], qtpy["uart_secondary"]["rx_gpio"]), ("Serial1", 28, 29))
        self.assertEqual((qtpy["i2c_secondary"]["sda_gpio"], qtpy["i2c_secondary"]["scl_gpio"]), (22, 23))
        xiao = self.board("102010550")["default_interfaces"]
        self.assertEqual((xiao["i2c"]["api"], xiao["i2c"]["sda_gpio"]), ("Wire", 16))
        self.assertEqual((xiao["i2c_secondary"]["api"], xiao["i2c_secondary"]["sda_gpio"]), ("Wire1", 6))
        s3 = self.board("qt_py_esp32_s3")["default_interfaces"]
        self.assertEqual((s3["i2c_secondary"]["sda_gpio"], s3["i2c_secondary"]["scl_gpio"]), (41, 40))

    def test_esp_variant_overrides_and_uart_alias_scope(self):
        self.assertEqual(self.board("lolin_d32")["default_interfaces"]["spi"]["ss_gpio"], 5)
        self.assertEqual(self.board("lolin_d32_pro")["default_interfaces"]["spi"]["ss_gpio"], 4)
        feather = self.board("3405")["default_interfaces"]["uart"]
        self.assertEqual((feather["tx_gpio"], feather["rx_gpio"]), (17, 16))
        self.assertEqual(feather["basis"], "framework_pin_aliases")
        self.assertIsNone(feather["api"])
        self.assertIsNone(feather["peripheral"])
        devkit = self.board("esp32_c6_devkitc_1_n8")["default_interfaces"]["i2c"]
        xiao = self.board("xiao_esp32c6")["default_interfaces"]["i2c"]
        self.assertEqual((devkit["sda_gpio"], devkit["scl_gpio"]), (23, 22))
        self.assertEqual((xiao["sda_gpio"], xiao["scl_gpio"]), (22, 23))
        self.assertEqual(devkit["variant_scope"], "generic_target_selection")

    def test_unavailable_defaults_and_software_aliases_are_explicit(self):
        for protocol in ("i2c", "spi"):
            interface = self.board("esp32_cam")["default_interfaces"][protocol]
            self.assertTrue(all(value == "not_in_pinout" for value in interface["signal_status"].values()))
            self.assertTrue(all(not pins for pins in interface["pin_keys"].values()))
        qtpy = self.board("4900")["default_interfaces"]["spi"]
        self.assertIsNone(qtpy["ss_gpio"])
        self.assertEqual(qtpy["signal_status"]["ss"], "not_defined")
        feather = self.board("4884")["default_interfaces"]["spi"]
        self.assertEqual(feather["ss_gpio"], 17)
        self.assertEqual(feather["signal_status"]["ss"], "not_in_pinout")
        d1 = self.board("esp32_d1_r32")["default_interfaces"]["i2c"]
        self.assertEqual(set(d1["signal_status"].values()), {"software_alias_only"})

    def test_unverified_carriers_do_not_inherit_soc_defaults(self):
        for part in ("esp32_s3_supermini", "esp32_c6_supermini", "esp32_h2_supermini"):
            board = self.board(part)
            self.assertEqual(set(board["default_interfaces"]), {"uart", "i2c", "spi"})
            for interface in board["default_interfaces"].values():
                self.assertEqual(interface["status"], "unverified")
                self.assertFalse(interface["source_ids"])
                self.assertTrue(all(value is None for key, value in interface.items() if key.endswith("_gpio")))

    def test_rp_defaults_agree_with_silicon_mux_and_pad_roles(self):
        # Independently cross-check the new defaults against the earlier datasheet mux data.
        for board in self.boards:
            if not board["chip"]["family"].startswith("rp"):
                continue
            for name, interface in board["default_interfaces"].items():
                for signal, pins in interface["pin_keys"].items():
                    suffix = {"miso": "RX", "mosi": "TX", "ss": "CSn"}.get(signal, signal.upper())
                    function = interface["peripheral"].upper() + "_" + suffix
                    for pin in pins:
                        with self.subTest(board=board["part_number"], interface=name, pin=pin):
                            self.assertIn(function, board["pins"][pin]["functions"])
                            self.assertIn({"interface": name, "signal": signal}, board["pins"][pin]["default_interface_roles"])

    def test_default_interface_validator_rejects_broken_consumer_links(self):
        mutations = [
            lambda b: b["default_interfaces"]["i2c"].update(sda_gpio=0),
            lambda b: b["default_interfaces"]["i2c"]["pin_keys"].update(sda=["missing_contact"]),
            lambda b: b["default_interfaces"]["i2c"]["signal_status"].update(sda="not_in_pinout"),
            lambda b: b["default_interfaces"]["i2c"].update(source_ids=["missing_source"]),
            lambda b: b["default_interfaces"]["i2c"].update(status="unverified"),
            lambda b: b["pins"]["expansion_1"].update(default_interface_roles=[]),
        ]
        for mutation in mutations:
            board = copy.deepcopy(self.board("pico"))
            mutation(board)
            with self.assertRaises(ValueError):
                catalogue.validate(option=board)

    def test_normal_svg_pipeline_preserves_web_metadata(self):
        board = copy.deepcopy(self.board("pico"))
        board["id"] = catalogue.get_identifier(option=board)
        board["kwargs"] = {
            "save_type": "all",
            "stylesheet": "microcontroller",
            "oomp_mode": "project",
        }
        previous = Path.cwd()
        with tempfile.TemporaryDirectory() as directory:
            try:
                os.chdir(directory)
                with patch.object(svg_help.svg_a4, "make_a4_sheet"):
                    svg_help.make_svg_generic(board)
                root = ET.parse(Path("parts") / board["id"] / "working_svg.svg").getroot()
                self.assertEqual(sum(element.get("data-pin") is not None for element in root.iter()), 40)
            finally:
                os.chdir(previous)

    def test_portable_export_matches_authoritative_python(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest = export(destination=directory)
            self.assertEqual(manifest["board_count"], len(self.boards))
            ids = {entry["id"] for entry in manifest["boards"]}
            for legacy, target in manifest["legacy_id_aliases"].items():
                self.assertTrue(legacy not in ids or legacy == target)
            for board in self.boards:
                folder = Path(directory) / "source_file" / catalogue.get_identifier(option=board)
                self.assertEqual(yaml.safe_load((folder / "definition.yaml").read_text(encoding="utf-8")), board)
                self.assertTrue((folder / "working_svg.svg").is_file())


if __name__ == "__main__":
    unittest.main()
