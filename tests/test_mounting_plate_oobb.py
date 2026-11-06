import copy
import unittest
from unittest.mock import patch

import oobb
import working_scad_mounting_plate_default as default_plate
import working_scad_mounting_plate_oobb as wire_plate


class AdapterLayoutTests(unittest.TestCase):
    def test_odd_even_alignment_and_two_end_threshold(self):
        cases = {
            (3, 3): [(0, 0, False)],
            (5, 5): [(15, 0, False)],
            (4, 5): [(7.5, 15, True)],
            (5, 4): [(15, 7.5, False)],
            (4, 4): [(7.5, 7.5, False)],
            (6, 5): [(-22.5, 0, False), (22.5, 0, False)],
            (5, 6): [(0, -22.5, True), (0, 22.5, True)],
            (7, 4): [(-30, 7.5, False), (30, 7.5, False)],
            (4, 7): [(7.5, -30, True), (7.5, 30, True)],
            (6, 6): [(-22.5, 7.5, False), (22.5, 7.5, False)],
        }
        for (width, height), expected in cases.items():
            with self.subTest(width=width, height=height):
                positions = wire_plate.get_adapter_positions(width, height)
                self.assertEqual(positions, expected)
                for x, y, _ in positions:
                    # Holder centre and its 15 mm grid must coincide with the
                    # host grid, and the full 44 mm holder must fit its plate.
                    self.assertEqual((x + (width - 1) * 7.5) % 15, 0)
                    self.assertEqual((y + (height - 1) * 7.5) % 15, 0)
                    self.assertLessEqual(abs(x) + 22, (width * 15 - 1) / 2)
                    self.assertLessEqual(abs(y) + 22, (height * 15 - 1) / 2)

    def test_opening_and_plain_through_holes_match_wire_holder(self):
        for rotated in (False, True):
            with self.subTest(rotated=rotated):
                calls = []
                def record(thing, **kwargs):
                    calls.append(copy.deepcopy(kwargs))
                with patch.object(oobb, "append_full", side_effect=record):
                    wire_plate.add_adapter({}, [10, 20, 5], 4, rotated)
                opening = calls[0]
                self.assertEqual(opening["radius"] * 2, 12)
                # Aperture exits at the plate top; screw holes cross both faces.
                self.assertEqual(opening["pos"][2] + opening["depth"], 9)
                holes = [c for c in calls if c.get("radius_name") == "m3"]
                actual = {(c["pos"][0] - 10, c["pos"][1] - 20) for c in holes}
                expected = ({(-15, -7.5), (-15, 7.5), (15, -7.5), (15, 7.5)}
                            if rotated else
                            {(-7.5, -15), (-7.5, 15), (7.5, -15), (7.5, 15)})
                self.assertEqual(actual, expected)
                self.assertEqual(len(holes), 4)
                self.assertTrue(all(c["type"] == "negative" for c in calls))
                self.assertTrue(all(c["shape"] == "oobb_hole" for c in calls))
                self.assertTrue(all(c["depth"] == 9 for c in holes))
                self.assertTrue(all(c["pos"][2] < 5 and c["pos"][2] + c["depth"] > 9 for c in holes))

    def test_relay_uses_actual_plate_dimensions_and_retains_extra_lift(self):
        kwargs = dict(breakout_pcb_width=49, breakout_pcb_height=38,
                      mounting_holes=[[22, 16.5]], pos=[0, 0, 0])
        self.assertEqual(default_plate.get_plate_dimensions(**kwargs), (6, 5))
        original = copy.deepcopy(kwargs)
        calls = []
        with patch.object(oobb, "append_full", side_effect=lambda thing, **kw: calls.append(kw)):
            wire_plate.get_base({"components": []}, **kwargs)
        self.assertEqual(kwargs, original)
        openings = [c for c in calls if c["shape"] == "oobb_hole" and "radius" in c]
        self.assertEqual([c["pos"][:2] for c in openings], [[-22.5, 0], [22.5, 0]])
        self.assertFalse(any(c["shape"] == "oobb_nut" for c in calls))
        self.assertEqual(sum(c["shape"] == "oobb_hole" and c.get("radius_name") == "m3" and c["depth"] == 8 for c in calls), 8)
        standoff = next(c for c in calls if c["shape"] == "oobb_cylinder")
        self.assertEqual(standoff["depth"], 6)

    def test_power_adapter_reaches_edge_on_even_short_axis(self):
        import working_oomp_populate_power

        power = working_oomp_populate_power.main()[0]
        # M6 head clearance increases the unpadded plate to 6 x 4 units.
        power["breakout_pcb_width_extra"] = 0
        power["breakout_pcb_height_extra"] = 0
        power["shift_wire_hole_x"] = 0
        power["shift_wire_hole_y"] = 0
        width, height = default_plate.get_plate_dimensions(**power)
        self.assertEqual((width, height), (6, 4))
        calls = []
        with patch.object(oobb, "append_full", side_effect=lambda thing, **kw: calls.append(kw)):
            wire_plate.get_base({"components": []}, **power)
        openings = [c for c in calls if c["shape"] == "oobb_hole" and "radius" in c]
        self.assertEqual([c["pos"][:2] for c in openings], [[-22.5, 7.5], [22.5, 7.5]])
        # The holder's positive outer M6 row coincides with the host edge.
        self.assertEqual(openings[-1]["pos"][0] + 15, (width - 1) * 7.5)
        self.assertFalse(any(c["shape"] == "oobb_nut" for c in calls))
        self.assertEqual(sum(c["shape"] == "oobb_hole" and c.get("radius_name") == "m3" and c["depth"] == 8 for c in calls), 8)


if __name__ == "__main__":
    unittest.main()
