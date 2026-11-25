import copy
import json
from pathlib import Path
import tempfile
import tomllib
import unittest
from unittest.mock import patch

from pypdf import PdfReader

from tools import i2c_eagle, i2c_part_research as research


ROOT = Path(__file__).resolve().parents[1]


def part_id(number):
    return next(key for key, board in research.boards().items() if board["part_number"] == number)


class Response:
    def __init__(self, content, url="https://www.adafruit.com/product/1231", content_type="text/html"):
        self.content = content
        self.url = url
        self.headers = {"Content-Type": content_type}

    def raise_for_status(self):
        pass


HTML = b'<html><head><title>ADXL345 test reference</title></head><body><main>ADXL345 product evidence<a href="/guide">Guide</a></main></body></html>'


class ResearchArchiveTests(unittest.TestCase):
    def test_scope_and_seed_preserve_identity_and_manual_research(self):
        self.assertEqual(len(research.boards()), 28)
        self.assertTrue(all("i2c" in board["interfaces"] for board in research.boards().values()))
        identifier = part_id("1231")
        with tempfile.TemporaryDirectory() as temp:
            research.seed(identifier, temp)
            folder, record = research.load_record(identifier, temp)
            self.assertEqual(record["taxonomy"]["taxonomy_14"], "adafruit")
            self.assertEqual(record["taxonomy"]["taxonomy_15"], "1231")
            record["description"] = "Keep my curated research"
            research.save_record(folder, record)
            research.seed(identifier, temp)
            self.assertEqual(research.load_record(identifier, temp)[1]["description"], "Keep my curated research")
            analog = next(board for board in __import__("working_oomp_populate_i2c").main() if board["part_number"] == "163")
            with self.assertRaisesRegex(ValueError, "Not a catalogue I2C"):
                research.seed(__import__("working_oomp_populate_i2c").get_identifier(analog), temp)

    def test_archiving_records_exact_bytes_derivatives_and_reuses_cached_evidence(self):
        identifier = part_id("1231")
        with tempfile.TemporaryDirectory() as temp, patch.object(research.requests, "get", return_value=Response(HTML)) as fetch:
            first = research.capture(identifier, "product_page", "https://www.adafruit.com/product/1231", "product_page", "website.html", root=temp)
            folder, record = research.load_record(identifier, temp)
            self.assertEqual((folder / "website.html").read_bytes(), HTML)
            self.assertIn("ADXL345 product evidence", (folder / "website.txt").read_text())
            links = json.loads((folder / "website.links.json").read_text())
            self.assertEqual(links[0]["url"], "https://www.adafruit.com/guide")
            second = research.capture(identifier, "product_page", "https://www.adafruit.com/product/1231", "product_page", "website.html", root=temp)
            self.assertEqual(first, second)
            self.assertEqual(fetch.call_count, 1)
            self.assertEqual(research.validate(identifier, temp), [])
            (folder / "website.html").write_bytes(b"changed")
            self.assertTrue(any("Missing or changed evidence" in error for error in research.validate(identifier, temp)))
            with self.assertRaisesRegex(ValueError, "missing or has changed"):
                research.capture(identifier, "product_page", "https://www.adafruit.com/product/1231", "product_page", "website.html", root=temp)

    def test_html_disguised_as_pdf_is_logged_without_a_fake_datasheet(self):
        identifier = part_id("1231")
        with tempfile.TemporaryDirectory() as temp, patch.object(research.requests, "get", return_value=Response(HTML)):
            with self.assertRaisesRegex(ValueError, "Expected a PDF"):
                research.capture(identifier, "chip_datasheet", "https://example.com/datasheet.pdf", "chip_datasheet", "reference/chip.pdf", root=temp)
            folder, record = research.load_record(identifier, temp)
            self.assertFalse((folder / "reference/chip.pdf").exists())
            self.assertEqual(record["sources"], [])
            self.assertEqual(record["research"]["attempts"][0]["outcome"], "failed")

    def test_failed_html_validation_or_derivative_collision_leaves_no_raw_orphan(self):
        identifier = part_id("1231")
        with tempfile.TemporaryDirectory() as temp:
            folder = research.seed(identifier, temp)
            with patch.object(research.requests, "get", return_value=Response(b"bad HTML")):
                with self.assertRaisesRegex(ValueError, "full HTML"):
                    research.capture(identifier, "product_page", "https://www.adafruit.com/product/1231", "product_page", "website.html", root=temp)
            self.assertFalse((folder / "website.html").exists())
            (folder / "website.txt").write_text("Preserve existing evidence")
            with patch.object(research.requests, "get", return_value=Response(HTML)):
                with self.assertRaisesRegex(ValueError, "overwrite"):
                    research.capture(identifier, "product_page", "https://www.adafruit.com/product/1231", "product_page", "website.html", root=temp)
            self.assertFalse((folder / "website.html").exists())
            self.assertFalse((folder / "website.links.json").exists())
            self.assertEqual((folder / "website.txt").read_text(), "Preserve existing evidence")
            self.assertEqual(research.load_record(identifier, temp)[1]["sources"], [])

    def test_resource_paths_and_source_identity_cannot_replace_other_files(self):
        identifier = part_id("1231")
        with tempfile.TemporaryDirectory() as temp, patch.object(research.requests, "get", return_value=Response(HTML)):
            folder = research.seed(identifier, temp)
            with self.assertRaisesRegex(ValueError, "escapes part directory"):
                research.capture(identifier, "escape", "https://example.com/", "guide", "../outside.html", root=temp)
            research.capture(identifier, "product_page", "https://www.adafruit.com/product/1231", "product_page", "website.html", root=temp)
            with self.assertRaisesRegex(ValueError, "different evidence"):
                research.capture(identifier, "product_page", "https://example.com/different", "guide", "reference/other.html", root=temp)
            with self.assertRaisesRegex(ValueError, "Unknown discovery source"):
                research.capture(identifier, "guide", "https://example.com/guide", "guide", "reference/guide.html", discovered_from="missing", root=temp)

    def test_validation_rejects_identity_drift_unsourced_measurements_and_contact_errors(self):
        identifier = part_id("1231")
        with tempfile.TemporaryDirectory() as temp, patch.object(research.requests, "get", return_value=Response(HTML)):
            research.capture(identifier, "product_page", "https://www.adafruit.com/product/1231", "product_page", "website.html", root=temp)
            folder, record = research.load_record(identifier, temp)
            record["taxonomy"]["taxonomy_8"] = "guessed_new_size"
            record["dimensions_mm"]["width"] = 25.4
            record["pin_count"]["total_exposed_contacts"] = 12
            record["i2c"]["documented_addresses_7bit"] = [0xa6]
            research.save_record(folder, record)
            errors = "\n".join(research.validate(identifier, temp))
            self.assertIn("Taxonomy identity changed", errors)
            self.assertIn("Known dimensions need source_ids", errors)
            self.assertIn("contact count differs", errors)
            self.assertIn("seven-bit", errors)


class ResearchPilotTests(unittest.TestCase):
    def test_project_agent_config_and_queue_match_the_current_catalogue(self):
        config = tomllib.loads((ROOT / ".codex/agents/i2c-part-researcher.toml").read_text())
        self.assertEqual(config["name"], "i2c_part_researcher")
        self.assertTrue(config["description"])
        self.assertTrue(config["developer_instructions"])
        self.assertNotIn("model", config)
        queue = research.queue()
        self.assertEqual(len(queue["parts"]), 28)
        statuses = {p["part_id"]: p["status"] for p in queue["parts"]}
        self.assertTrue(all(statuses[part_id(number)] in research.READY_STATES for number in ("1231", "sen_15440")))
        self.assertTrue(all(status in research.RESEARCH_STATES | {"pending"} for status in statuses.values()))

    def test_validator_rejects_missing_provenance_datasheet_drift_and_unknown_status(self):
        identifier = part_id("1231")
        folder, original = research.load_record(identifier)
        mutations = []
        changed = copy.deepcopy(original)
        changed["research"]["status"] = "compelete"
        mutations.append((changed, "Unknown research status"))
        changed = copy.deepcopy(original)
        for source in changed["sources"]:
            source.pop("retrieved_at", None)
            source.pop("requested_url", None)
        mutations.append((changed, "Missing source metadata"))
        changed = copy.deepcopy(original)
        changed["datasheets"]["items"][0]["local_file"] = "reference/not_real.pdf"
        changed["datasheets"]["items"][0]["sha256"] = "incorrect"
        mutations.append((changed, "Datasheet item differs"))
        changed = copy.deepcopy(original)
        changed["i2c"].pop("source_ids")
        changed["electrical"]["board_supply"].pop("source_ids")
        mutations.append((changed, "Completed factual section needs evidence"))
        for changed, expected in mutations:
            with patch.object(research, "load_record", return_value=(folder, changed)):
                self.assertTrue(any(expected in error for error in research.validate(identifier)))

    def test_pilot_files_validate_and_datasheets_have_the_correct_titles(self):
        for number, chip, pages in (("1231", "ADXL345", 40), ("sen_15440", "BME280", 55)):
            identifier = part_id(number)
            self.assertEqual(research.validate(identifier), [])
            folder, record = research.load_record(identifier)
            item = record["datasheets"]["items"][0]
            reader = PdfReader(folder / item["local_file"])
            self.assertEqual(len(reader.pages), pages)
            self.assertIn(chip, reader.pages[0].extract_text())
            self.assertTrue(record["conflicts"])
            self.assertFalse(any(item.get("tested") for item in record["software"]))

    def test_cad_extraction_counts_physical_contacts_and_actual_holes(self):
        cases = (("1231", "adxl345_stemma_qt.brd", ["JP1", "JP2", "CONN3", "CONN4"], (25.4, 17.78), (10, 8, 18, 9), 4),
                 ("sen_15440", "qwiic_bme280.brd", ["J1", "J2", "J3", "J4"], (25.4, 25.4), (6, 8, 14, 6), 3))
        for number, filename, connectors, size, counts, holes in cases:
            folder = research.part_folder(part_id(number))
            cable_refs = [name for name in connectors if name.startswith("CONN")] if number == "1231" else ["J1", "J2"]
            kinds = {name: "cable_connector" if name in cable_refs else "header" for name in connectors}
            anchor_names = ("MT1", "MT2") if number == "1231" else ("NC1", "NC2")
            exclusions = [(ref, pad) for ref in cable_refs for pad in anchor_names]
            summary = i2c_eagle.extract(folder / "reference" / filename, connectors,
                                      connector_kinds=kinds, excluded_pads=exclusions)
            self.assertEqual((summary["dimensions_mm"]["width"], summary["dimensions_mm"]["height"]), size)
            self.assertEqual(tuple(summary["pin_count"][k] for k in ("header_contacts", "cable_connector_contacts", "total_exposed_contacts", "unique_nets")), counts)
            self.assertEqual(len(summary["mounting_holes"]), holes)
            self.assertEqual(len(summary["excluded_mechanical_pads"]), 4)
            self.assertFalse(any(p["number"].startswith(("MT", "NC")) for p in summary["pins"].values()))
            unfiltered = i2c_eagle.extract(folder / "reference" / filename, connectors, connector_kinds=kinds)
            self.assertEqual(unfiltered["pin_count"]["total_exposed_contacts"], counts[2] + 4)
            with self.assertRaisesRegex(ValueError, "kind required"):
                i2c_eagle.extract(folder / "reference" / filename, connectors, connector_kinds={})


if __name__ == "__main__":
    unittest.main()
