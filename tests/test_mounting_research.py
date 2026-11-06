import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

import oobb

from mounting_geometry import standard_holder
from tools import mounting_eagle as eagle
from tools import mounting_research as research
from working_oomp_populate_mounting import apply_mounting
import working_scad_mounting_plate_default as plate


BOARD = '''<eagle><drawing><board><plain>
<wire x1="0" y1="0" x2="20" y2="0" layer="20"/>
<wire x1="20" y1="0" x2="20" y2="10" layer="20"/>
<wire x1="20" y1="10" x2="0" y2="10" layer="20"/>
<wire x1="0" y1="10" x2="0" y2="0" layer="20"/>
</plain><libraries><library name="lib"><packages><package name="mount">
<hole x="2" y="1" drill="2.5"/>
</package><package name="header"><pad name="1" x="0" y="0" drill="1"/>
</package></packages></library></libraries><elements>
<element name="H1" library="lib" package="mount" x="14" y="6" rot="MR90"/>
<element name="J1" library="lib" package="header" x="3" y="3"/>
</elements></board></drawing></eagle>'''


class GeometryTests(unittest.TestCase):
    def test_drill_sizes_select_clearance_screws_and_actual_positions(self):
        holes = [dict(x_mm=-6, y_mm=3, diameter_mm=2.5),
                 dict(x_mm=5, y_mm=-3, diameter_mm=3.302)]
        geometry = standard_holder([20, 12], holes)
        self.assertEqual(geometry["mounting_hole_radius_names"], ["m2", "m3"])
        calls = []
        with patch.object(oobb, "append_full", side_effect=lambda thing, **kw: calls.append(kw)):
            plate.get_base({}, board_size=[20, 12], mounting_holes=holes, pos=[10, 20, 0])
        cuts = [c for c in calls if c["shape"] == "oobb_screw_countersunk"]
        self.assertEqual([c["radius_name"] for c in cuts], ["m2", "m3"])
        self.assertEqual([c["pos"] for c in cuts], [[4, 23, 0], [15, 17, 0]])
        self.assertEqual(holes[0]["x_mm"], -6)

    def test_bad_or_unknown_geometry_rejected(self):
        cases = [([0, 10], []), ([float("nan"), 10], []), ([10, 10], None),
                 ([10, 10], [dict(x_mm=5, y_mm=0, diameter_mm=3)]),
                 ([10, 10], [dict(x_mm=0, y_mm=0, diameter_mm=1)]),
                 ([10, 10], [dict(x_mm=0, y_mm=0, diameter_mm=2.5)] * 2)]
        for size, holes in cases:
            with self.subTest(size=size, holes=holes), self.assertRaises(ValueError):
                standard_holder(size, holes)
        self.assertEqual(standard_holder([10, 10], [])["mounting_holes"], [])

    def test_arc_extrema_and_mirrored_rotated_packages(self):
        wire = ET.fromstring('<wire x1="-1" y1="0" x2="1" y2="0" curve="180"/>')
        points = eagle.wire_points(wire)
        self.assertAlmostEqual(min(y for x, y in points), -1)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "board.brd"
            path.write_text(BOARD)
            data = eagle.select(path, ["H1:hole:1"], 1)
            # local (2,1) -> mirror (-2,1) -> R90 (-1,-2)
            # placement (13,4), centre (10,5) -> (3,-1) -> CCW (-y,x)=(1,3)
            self.assertEqual(data["board_size"], [10, 20])
            hole = data["mounting_holes"][0]
            self.assertEqual((hole["x_mm"], hole["y_mm"]), (1, 3))
            self.assertEqual(len(data["candidates"]), 2)
            with self.assertRaises(ValueError):
                eagle.select(path, ["missing"])


class ResearchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.part_id = next(iter(research.boards()))
        base, record = research.seed(self.part_id, self.root)
        (base / "board.brd").write_text(BOARD)
        (base / "identity.html").write_text("Manufacturer exact board revision 1")
        research.register(self.part_id, "board.brd", "https://maker.example/board.brd", "cad",
                          "manufacturer_cad", "revision 1 layer 20", self.root)
        research.register(self.part_id, "identity.html", "https://maker.example/product", "product",
                          "manufacturer_product", "revision 1 identity", self.root)
        research.extract(self.part_id, "cad", ["H1:hole:1"], root=self.root)
        self.base, record = research.load(self.part_id, self.root)
        record.update(status="verified", board_revision="v1", reviewed_by="test",
                      identity_source_ids=["product", "cad"], identity_evidence="Product links exact v1 CAD")
        record["review"] = {key: True for key in research.CHECKS}
        research.save(self.base, record)

    def test_promotion_idempotence_replay_and_identity_preservation(self):
        value = research.promote(self.part_id, self.root)
        generated = self.root / "working_oomp_populate_mounting_data.py"
        before = generated.read_bytes()
        research.promote(self.part_id, self.root)
        self.assertEqual(before, generated.read_bytes())
        board = copy.deepcopy(research.boards()[self.part_id])
        original_taxonomy = {k: v for k, v in board.items() if k.startswith("taxonomy_")}
        apply_mounting([board], {self.part_id: value})
        self.assertEqual(original_taxonomy, {k: v for k, v in board.items() if k.startswith("taxonomy_")})
        self.assertEqual(len(board["oobb_details"]), 3)
        self.assertEqual(board["mounting_holes"], [[3, -1]])
        self.assertEqual(board["mounting_hole_details"][0]["source_id"], "mounting_cad")
        self.assertIn("mounting_cad", {s["id"] for s in board["sources"]})
        _, record = research.load(self.part_id, self.root)
        record["mounting_holes"][0]["x_mm"] = 2
        research.save(self.base, record)
        with self.assertRaisesRegex(ValueError, "disagree"):
            research.validate(self.part_id, self.root)

    def test_tampered_evidence_and_unreviewed_records_rejected(self):
        _, record = research.load(self.part_id, self.root)
        record["review"]["identity"] = False
        research.save(self.base, record)
        with self.assertRaisesRegex(ValueError, "semantic"):
            research.validate(self.part_id, self.root)
        record["review"]["identity"] = True
        research.save(self.base, record)
        (self.base / "identity.html").write_text("Changed")
        with self.assertRaisesRegex(ValueError, "hash"):
            research.validate(self.part_id, self.root)

    def test_no_holes_does_not_schedule_a_holder(self):
        (self.base / "board.brd").write_text(BOARD.replace(
            '<element name="H1" library="lib" package="mount" x="14" y="6" rot="MR90"/>', ''))
        research.register(self.part_id, "board.brd", "https://maker.example/board.brd", "cad",
                          "manufacturer_cad", "revision without mounting holes", self.root)
        research.extract(self.part_id, "cad", [], root=self.root)
        _, record = research.load(self.part_id, self.root)
        record["status"] = "no_holes"
        record["review"] = {key: True for key in research.CHECKS}
        research.save(self.base, record)
        value = research.promote(self.part_id, self.root)
        board = copy.deepcopy(research.boards()[self.part_id])
        apply_mounting([board], {self.part_id: value})
        self.assertEqual(board["oobb_details"], [])
        self.assertFalse(board["mounting_geometry_ready"])

    def test_paths_cannot_escape_evidence_folder(self):
        for relative in ("../x", "C:/x", "reference\\x"):
            with self.assertRaises(ValueError):
                research.local(self.base, relative)

    def test_superseded_holders_are_preserved_but_not_left_as_current(self):
        part = self.root / "parts" / self.part_id
        part.mkdir(parents=True)
        for name in ("3dpr.stl", "working_oobb.stl", "working.yaml", "image.jpg"):
            (part/name).write_text(name)
        moved = research.archive_superseded(self.part_id, no_holes=True, root=self.root)
        self.assertEqual(len(moved), 2)
        self.assertFalse((part/"3dpr.stl").exists())
        self.assertTrue((part/"working.yaml").exists())
        self.assertTrue((part/"image.jpg").exists())
        self.assertTrue(all((self.root/p).is_file() for p in moved))

    def test_interrupted_build_resumes_and_artifact_tampering_is_detected(self):
        value = research.promote(self.part_id, self.root)
        status = lambda: next(r["status"] for r in research.queue(self.root) if r["part_id"] == self.part_id)
        self.assertEqual(status(), "awaiting_generation")
        output = self.root / "parts" / self.part_id / "3dpr.scad"
        output.parent.mkdir(parents=True)
        output.write_text("cube(1);")
        content = output.read_bytes()
        receipt = dict(record_sha256=value["record_sha256"], artifacts=[dict(
            path=output.relative_to(self.root).as_posix(), bytes=len(content),
            sha256=hashlib.sha256(content).hexdigest())])
        (self.base/"mounting_build.json").write_text(json.dumps(receipt))
        self.assertEqual(status(), "promoted")
        research.verify_build(self.part_id, self.root)
        output.write_text("cube(2);")
        with self.assertRaisesRegex(ValueError, "artifact changed"):
            research.verify_build(self.part_id, self.root)
        output.unlink()
        self.assertEqual(status(), "awaiting_generation")


if __name__ == "__main__":
    unittest.main()
