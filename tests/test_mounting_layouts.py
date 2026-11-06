import unittest
from mounting_layouts import plan, LAYOUTS


class LayoutTests(unittest.TestCase):
    def test_portrait_compact_variants_keep_board_and_fastener_space(self):
        layouts = {v: plan(breakout_pcb_width=21, breakout_pcb_height=51, mounting_layout=v) for v in LAYOUTS}
        self.assertEqual(layouts['short_sides']['edges'], ['bottom', 'top'])
        self.assertEqual(layouts['long_side']['edges'], ['right'])
        areas = {v: (p['bounds_mm'][1]-p['bounds_mm'][0])*(p['bounds_mm'][3]-p['bounds_mm'][2]) for v,p in layouts.items()}
        self.assertLess(areas['short_sides'], areas['full_wrap'])
        self.assertLess(areas['long_side'], areas['full_wrap'])
        for p in layouts.values():
            self.assertGreaterEqual(len(p['m6_centres_mm']), 2)
            for x,y in p['m6_centres_mm']:
                self.assertTrue(abs(x)>=10.5+6.5 or abs(y)>=25.5+6.5)

    def test_landscape_rotates_selected_edges(self):
        self.assertEqual(plan(breakout_pcb_width=51,breakout_pcb_height=21,mounting_layout='short_sides')['edges'], ['left','right'])
        self.assertEqual(plan(breakout_pcb_width=51,breakout_pcb_height=21,mounting_layout='long_side')['edges'], ['top'])

    def test_tight_board_and_posts_push_the_grid_out(self):
        p=plan(breakout_pcb_width=18,breakout_pcb_height=22.5)
        self.assertEqual(p['grid_units'][0],4)  # Old 3-unit plate left only 6 mm.
        p=plan(board_size=[30,50],mounting_holes=[dict(x_mm=13,y_mm=20,diameter_mm=3.2)])
        for x,y in p['m6_centres_mm']:
            self.assertGreaterEqual(((x-13)**2+(y-20)**2)**.5, 6.5+3.75)

    def test_wire_attachment_footprints_survive_trim(self):
        for variant in LAYOUTS:
            p=plan(breakout_pcb_width=21,breakout_pcb_height=51,mounting_layout=variant,wire_adapter=True)
            left,right,bottom,top=p['bounds_mm']
            for x,y,_ in p['adapter_positions']:
                self.assertLessEqual(left,x-22)
                self.assertGreaterEqual(right,x+22)
                self.assertLessEqual(bottom,y-22)
                self.assertGreaterEqual(top,y+22)


if __name__ == '__main__': unittest.main()
