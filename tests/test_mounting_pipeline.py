import contextlib
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import yaml
import working
import working_oomp_populate
import working_scad
from mounting_variants import apply_variants, details_for


def board():
    return dict(taxonomy_1='electronic', taxonomy_2='breakout', taxonomy_3='pipeline_fixture',
                breakout_pcb_width=30, breakout_pcb_height=50,
                mounting_holes=[[-10,-20],[10,20]], mounting_hole_radius_name='m2',
                oobb_details=[dict(oobb_name='mounting_plate_default'),
                              dict(oobb_name='mounting_plate_oobb', scad_output='working_oobb')])


class PipelineTests(unittest.TestCase):
    def test_six_layouts_are_idempotent_and_do_not_mutate_inputs(self):
        source = board()
        original = copy.deepcopy(source)
        result = details_for(source)
        self.assertEqual(source, original)
        self.assertEqual(len(result), 6)
        source['oobb_details'] = result
        self.assertEqual(details_for(source), result)
        self.assertEqual({d.get('scad_output', '3dpr') for d in result},
                         {'3dpr','3dpr_short_sides','3dpr_long_side','working_oobb',
                          'working_oobb_short_sides','working_oobb_long_side'})

    def test_no_invented_holes_and_direct_hole_definitions_enable_standard_family(self):
        for holes in (None, []):
            value = board()
            value['mounting_holes'] = holes
            value['oobb_details'].append(dict(oobb_name='hole_cover'))
            self.assertEqual(details_for(value), [dict(oobb_name='hole_cover')])
        value = board()
        value.pop('oobb_details')
        self.assertEqual(len(details_for(value)), 3)
        value['mounting_geometry_ready'] = False
        self.assertEqual(details_for(value), [])

    def test_normal_pipeline_exports_six_scads_without_touching_other_records(self):
        selected = 'electronic_breakout_pipeline_fixture'
        other = dict(board(), taxonomy_3='other')
        with tempfile.TemporaryDirectory() as temporary, contextlib.chdir(temporary):
            root = Path(temporary)
            sentinel = root/'parts'/'electronic_breakout_other'/'working.yaml'
            sentinel.parent.mkdir(parents=True)
            sentinel.write_text('id: untouched\n')
            original = sentinel.read_bytes()
            options = apply_variants([board(), other])
            with patch.object(working_oomp_populate, 'get_options', return_value=options):
                working.main(part_ids=[selected], parts_directory=str(root/'parts'),
                             mounting_only=True, navigation=False, run_action=False)
            self.assertEqual(sentinel.read_bytes(), original)
            self.assertFalse((root/'parts_source'/'electronic_breakout_other').exists())
            folder = root/'parts'/selected
            populated = yaml.safe_load((folder/'working.yaml').read_text())
            self.assertEqual(populated['mounting_holes'], [[-10,-20],[10,20]])
            self.assertEqual(len(populated['oobb_details']), 6)
            manifest = json.loads((folder/'mounting_variants.json').read_text())
            self.assertEqual(len(manifest['variants']), 6)
            for variant in manifest['variants']:
                self.assertTrue((folder/Path(variant['source']).with_suffix('.scad')).is_file())
            # A second CAD run must not grow the schedule or overwrite another layout.
            working_scad.main(part_ids=[selected], parts_directory=str(root/'parts'), navigation=False)
            self.assertEqual(json.loads((folder/'mounting_variants.json').read_text()), manifest)

    def test_bad_part_id_fails_before_writes(self):
        with tempfile.TemporaryDirectory() as temporary, contextlib.chdir(temporary):
            with patch.object(working_oomp_populate, 'get_options', return_value=apply_variants([board()])):
                with self.assertRaisesRegex(ValueError, 'Unknown populate'):
                    working_oomp_populate.main(part_ids=['missing'])
            self.assertFalse(Path('parts_source').exists())


if __name__ == '__main__': unittest.main()
