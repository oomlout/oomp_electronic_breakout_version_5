import contextlib
import copy
import hashlib
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

import yaml

from oomp_populate_helper import build_oomp_id
import working_oomp
import working_oomp_populate
import working_oomp_populate_i2c as catalogue


ROOT = Path(__file__).resolve().parents[1]


class I2CBreakoutTests(unittest.TestCase):
    def test_every_named_manufacturer_board_in_the_report_is_imported(self):
        # Independent coverage oracle: the approved report, including the analog
        # exception. AliExpress queue rows have no manufacturer part identity.
        report = (ROOT / "research/i2c_breakouts/proposal_2026_10_23.md").read_text(encoding="utf-8")
        expected = set(re.findall(
            r"^\| \[(?:SparkFun|Adafruit)[^\n]+?\| `(sparkfun|adafruit)` \| `([^`]+)` \|",
            report, re.MULTILINE,
        ))
        self.assertEqual(len(expected), 29)
        boards = catalogue.main()
        self.assertEqual({(b["manufacturer"], b["part_number"]) for b in boards}, expected)
        self.assertEqual(len(boards), len(expected))

    def test_fixed_taxonomy_survives_the_normal_population_pipeline(self):
        boards = catalogue.main()
        with patch.object(working_oomp_populate, "write_extras") as writer:
            working_oomp_populate.main()
        actual = {b["part_number"]: b for b in writer.call_args.args[0]
                  if b.get("catalogue") == "i2c_breakouts"}
        self.assertEqual(len(actual), 29)
        for board in boards:
            built = actual[board["part_number"]]
            for index in range(1, 16):
                self.assertEqual(built[f"taxonomy_{index}"], board[f"taxonomy_{index}"])
            self.assertEqual(build_oomp_id(built), catalogue.get_identifier(board))
            if built.get("mounting_geometry_ready"):
                self.assertEqual([d["oobb_name"] for d in built["oobb_details"]], ["mounting_plate_default"] * 3)
                self.assertTrue(built["mounting_research"]["sources"])
            else:
                self.assertEqual(built["oobb_details"], [])
        fram = actual["1895"]
        self.assertEqual(fram["taxonomy_6"], "")
        self.assertEqual(fram["taxonomy_7"], "header_breakout")
        self.assertEqual((fram["taxonomy_14"], fram["taxonomy_15"]), ("adafruit", "1895"))

    def test_analog_exception_and_unverified_geometry_are_not_fabricated(self):
        boards = catalogue.main()
        self.assertEqual(sum("i2c" in b["interfaces"] for b in boards), 28)
        analog = next(b for b in boards if b["part_number"] == "163")
        self.assertEqual(analog["interfaces"], ["analog"])
        self.assertIsNone(analog["i2c"])
        for board in boards:
            self.assertFalse(board["geometry_ready"])
            self.assertEqual(board["mounting_holes"], [])
            self.assertEqual(board["mounting_hole_status"], "unverified")
            if board["dimensions_mm"]["width"] is None:
                self.assertEqual(board["taxonomy_8"], "")
                self.assertIsNone(board["breakout_pcb_width"])
            if "product_dimensions_mm" in board and board["part_number"] != "938":
                # A product bounding box must not be promoted to a PCB outline.
                self.assertIsNone(board["breakout_pcb_width"])

    def test_validation_rejects_shifted_taxonomy_and_eight_bit_addresses(self):
        board = catalogue.main()[0]
        shifted = copy.deepcopy(board)
        shifted["taxonomy_14"] = ""
        with self.assertRaisesRegex(ValueError, "slots 14/15"):
            catalogue.validate([shifted])
        invalid_address = copy.deepcopy(board)
        invalid_address["i2c"]["documented_addresses_7bit"] = [0xee]
        with self.assertRaisesRegex(ValueError, "seven-bit"):
            catalogue.validate([invalid_address])
        with self.assertRaisesRegex(ValueError, "Duplicate board"):
            catalogue.validate([board, copy.deepcopy(board)])

    def test_targeted_source_to_parts_generation_is_complete_and_repeatable(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            # An unrelated malformed source catches accidental whole-repo loads.
            unrelated = root / "parts_source/unrelated/working.yaml"
            unrelated.parent.mkdir(parents=True)
            unrelated.write_text("[invalid yaml", encoding="utf-8")
            existing = root / "parts/unrelated/working.yaml"
            existing.parent.mkdir(parents=True)
            existing.write_text("preserve this record\n", encoding="utf-8")
            original = hashlib.sha256(existing.read_bytes()).hexdigest()
            identifiers = catalogue.populate(generate_parts=True, destination=root)
            self.assertEqual(len(identifiers), 29)
            self.assertEqual(len(set(identifiers)), 29)
            first_pass = {}
            for identifier in identifiers:
                source = root / "parts_source" / identifier / "working.yaml"
                generated = root / "parts" / identifier / "working.yaml"
                source_data = yaml.safe_load(source.read_text(encoding="utf-8"))
                generated_data = yaml.safe_load(generated.read_text(encoding="utf-8"))
                self.assertEqual(build_oomp_id(source_data), identifier)
                self.assertEqual(generated_data["id"], identifier)
                self.assertEqual(generated_data["sources"], source_data["sources"])
                self.assertEqual(generated_data["i2c"], source_data["i2c"])
                self.assertEqual(generated_data["taxonomy_14"], source_data["manufacturer"])
                self.assertEqual(generated_data["taxonomy_15"], source_data["part_number"])
                self.assertNotIn("part_ids", generated_data)
                first_pass[identifier] = generated_data
            self.assertEqual(catalogue.populate(generate_parts=True, destination=root), identifiers)
            for identifier, expected in first_pass.items():
                generated = root / "parts" / identifier / "working.yaml"
                self.assertEqual(yaml.safe_load(generated.read_text(encoding="utf-8")), expected)
            self.assertEqual(hashlib.sha256(existing.read_bytes()).hexdigest(), original)

    def test_targeted_loader_reports_missing_records(self):
        with tempfile.TemporaryDirectory() as temp, contextlib.chdir(temp):
            with self.assertRaisesRegex(FileNotFoundError, "Missing parts_source"):
                working_oomp.main(part_ids=["missing"])
            Path("parts_source/missing").mkdir()
            with self.assertRaisesRegex(FileNotFoundError, "Missing working.yaml"):
                working_oomp.main(part_ids=["missing"])


if __name__ == "__main__":
    unittest.main()
