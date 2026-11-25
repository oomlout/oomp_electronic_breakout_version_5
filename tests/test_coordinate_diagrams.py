import copy
import contextlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

import yaml

import svg_help
import working_oomp_populate
import working_svg
from working_oomp_populate_coordinate import DEMO_IDS, apply_coordinate_drawings, drawing_geometry
from working_oomp_populate_mounting import identifier
from working_svg_coordinate import coordinate_svg, get_coordinate_diagram, choose_scale


class CoordinateDrawingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.boards = {identifier(b): b for b in working_oomp_populate.get_options()}

    def board(self, index=0):
        board = copy.deepcopy(self.boards[DEMO_IDS[index]])
        board["id"] = DEMO_IDS[index]
        return board

    def test_paper_size_and_true_geometry_survive_the_svg_transform(self):
        for index in range(3):
            board = self.board(index)
            original = copy.deepcopy(board)
            thing = copy.deepcopy(board)
            get_coordinate_diagram(thing, board=board)
            root = ET.fromstring(coordinate_svg(thing))
            self.assertEqual(root.get("viewBox"), "0 0 210.0000 297.0000")
            self.assertEqual(root.get("width"), "210.0000mm")
            self.assertEqual(root.get("height"), "297.0000mm")
            metadata = json.loads(root.find("{*}metadata").text)
            self.assertEqual(metadata["outline_scope"], "pcb_bounding_box")
            holes = root.findall(".//{*}circle[@data-diameter-mm]")
            self.assertEqual(len(holes), len(original["mounting_research"]["mounting_holes"]))
            scale = metadata["scale"]
            for circle in holes:
                self.assertAlmostEqual(float(circle.get("cx")), 105 + float(circle.get("data-x-mm")) * scale, places=3)
                self.assertAlmostEqual(float(circle.get("cy")), 135 - float(circle.get("data-y-mm")) * scale, places=3)
                self.assertAlmostEqual(float(circle.get("r")), float(circle.get("data-diameter-mm")) * scale / 2, places=3)
            self.assertEqual(board, original)

    def test_asymmetric_pattern_does_not_invent_a_fourth_hole(self):
        geometry = drawing_geometry(self.board(2))
        self.assertEqual(len(geometry["holes"]), 3)
        self.assertNotIn((-10.16, -10.16), [(h["x_mm"], h["y_mm"]) for h in geometry["holes"]])

    def test_missing_or_different_frames_are_rejected(self):
        board = self.board()
        board["mounting_research"]["coordinate_system"]["origin"] = "lower_left"
        with self.assertRaisesRegex(ValueError, "centred"):
            drawing_geometry(board)
        board.pop("mounting_research")
        with self.assertRaisesRegex(ValueError, "verified"):
            drawing_geometry(board)
        for scale in (0, -1, float("nan"), 20):
            with self.assertRaises(ValueError):
                choose_scale(25.4, 25.4, scale)

    def test_mounting_frame_does_not_use_pinout_or_holder_overrides(self):
        board = self.board()
        expected = drawing_geometry(board)
        board["mounting_hole_details"] = []
        board["breakout_pcb_width"] = 999
        board["pins"] = {"wrong_frame": {"x_mm": 900, "y_mm": 900}}
        self.assertEqual(drawing_geometry(board), expected)

    def test_population_is_opt_in_and_preserves_existing_drawing(self):
        board = self.board()
        original = copy.deepcopy(board["svg_details"])
        apply_coordinate_drawings([board])
        apply_coordinate_drawings([board])
        self.assertEqual(board["svg_details"][0], original)
        self.assertEqual(len(board["svg_details"]), 2)
        self.assertIsInstance(self.boards[DEMO_IDS[0]]["svg_details"], dict)

    def test_selection_dry_run_and_styles_do_not_write_or_lose_jobs(self):
        board = self.board()
        apply_coordinate_drawings([board])
        board["svg_details"][1]["styles"] = {"board": {"color": "#ffcc00", "stroke_width": 0.7}}
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            folder = root / "parts" / board["id"]
            folder.mkdir(parents=True)
            source = folder / "working.yaml"
            source.write_text(yaml.safe_dump(board), encoding="utf-8")
            before = source.read_bytes()
            # An unrelated invalid record must never be read during exact selection.
            other = root / "parts" / "unrelated"
            other.mkdir()
            (other / "working.yaml").write_text("[[invalid", encoding="utf-8")
            with patch.object(working_svg, "__file__", str(root / "working_svg.py")):
                jobs = working_svg.get_parts(dict(part_ids=[board["id"]], drawing="coordinate_diagram", save_type="none",
                                                  part_styles={"board": {"color": "#aabbcc"}}), "project")
                self.assertEqual(len(jobs), 1)
                thing = svg_help.make_svg_generic(jobs[0])
                self.assertEqual(thing["styles"]["board"]["color"], "#aabbcc")
                self.assertEqual(thing["styles"]["board"]["stroke_width"], 0.7)
                self.assertEqual(len(jobs[0]["svg_details"]), 2)
                with self.assertRaisesRegex(ValueError, "No matching"):
                    working_svg.get_parts(dict(part_ids=["missing"]), "project")
            self.assertEqual(source.read_bytes(), before)
            self.assertEqual([p.name for p in folder.iterdir()], ["working.yaml"])

    def test_xml_text_escaping_and_monochrome_style(self):
        board = self.board()
        board["name_readable"] = "Board <test> & reference"
        get_coordinate_diagram(board, stylesheet="coordinate_monochrome")
        root = ET.fromstring(coordinate_svg(board))
        self.assertIn("Board <test> & reference", "".join(root.itertext()))
        self.assertEqual(board["styles"]["board"]["stroke"], "#333333")

    def test_both_drawing_streams_write_without_overwriting_configuration(self):
        board = self.board()
        apply_coordinate_drawings([board])
        board["svg_details"][1]["export_pdf"] = False
        board["svg_details"][1]["styles"] = {"board": {"stroke_width": 0.6}}
        original_details = copy.deepcopy(board["svg_details"])
        with tempfile.TemporaryDirectory() as temporary, contextlib.chdir(temporary):
            with patch.object(svg_help.svg_a4, "make_a4_sheet"):
                results = svg_help.make_svg_generic(board)
            self.assertEqual(len(results), 2)
            folder = Path("parts") / board["id"]
            self.assertTrue((folder / "working_svg.svg").is_file())
            self.assertTrue((folder / "working_coordinate_diagram.svg").is_file())
            saved = yaml.safe_load((folder / "working.yaml").read_text(encoding="utf-8"))
            self.assertEqual(saved["svg_details"], original_details)
            self.assertNotIn("_svg_detail", saved)
            self.assertEqual(board["svg_details"], original_details)


if __name__ == "__main__":
    unittest.main()
