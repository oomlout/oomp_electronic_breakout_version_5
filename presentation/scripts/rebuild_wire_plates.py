"""Rebuild tracked wire-holder plates from their saved CAD parameters, not board research."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import yaml
import trimesh
import oobb
import working_scad_mounting_plate_oobb as plate


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--part', help='Limit to one exact catalogue directory name')
    parser.add_argument('--openscad', default=os.environ.get('OPENSCAD_EXE', r'C:\Program Files\OpenSCAD (Nightly)\openscad.com'))
    args = parser.parse_args()
    os.chdir(ROOT)
    files = subprocess.check_output(['git', 'ls-files', 'parts/*/working_oobb_thing.yaml'], text=True).splitlines()
    if args.part:
        files = [p for p in files if Path(p).parent.name == args.part]
    if not files:
        raise ValueError('No tracked wire-holder CAD records match')
    cache = ROOT / 'presentation/.cache/wire-plates'
    cache.mkdir(parents=True, exist_ok=True)
    reports = []
    for name in files:
        source = ROOT / name
        folder = source.parent
        data = yaml.safe_load(source.read_text(encoding='utf-8'))
        thing = copy.deepcopy(data['thing'])
        for key in ('components', 'components_objects', 'components_string'):
            thing[key] = []
        plate.get_base(thing, **copy.deepcopy(data['kwargs']))
        scad = folder / 'working_oobb.scad'
        old_mesh = trimesh.load_mesh(folder / 'working_oobb.stl')
        before = dict(stl_sha256=digest(folder / 'working_oobb.stl'), scad_sha256=digest(scad),
                      volume_mm3=float(old_mesh.volume), dimensions_mm=old_mesh.extents.tolist())
        # Emit to a temporary location first. No background OpenSCAD processes.
        scratch = cache / 'working.scad'
        oobb.opsc_make_object(str(scratch), thing['components'], mode='3dpr', save_type='none', overwrite=True)
        key = digest(scratch)
        compiled = cache / (key + '.stl')
        if not compiled.exists():
            result = subprocess.run([args.openscad, '-o', str(compiled), str(scratch)], capture_output=True, text=True)
            if result.returncode:
                raise RuntimeError(result.stderr)
        mesh = trimesh.load_mesh(compiled)
        if not mesh.is_watertight or mesh.volume <= 0:
            raise ValueError(f'Invalid mesh: {folder.name}')
        if any(abs(a - b) > .001 for a, b in zip(mesh.extents[:2], old_mesh.extents[:2])):
            raise ValueError(f'Unexpected footprint change: {folder.name}')
        if mesh.volume > old_mesh.volume + .01:
            raise ValueError(f'Unexpected material added: {folder.name}')
        # The adapter adds only negative holes. Retain the board standoffs.
        assert not any('oobb_nut' == c.get('shape') for c in thing['components_objects'])
        data['thing'] = thing
        shutil.copyfile(scratch, scad)
        shutil.copyfile(compiled, folder / 'working_oobb.stl')
        source.write_text(yaml.dump(data), encoding='utf-8', newline='\n')
        reports.append(dict(folder=folder.relative_to(ROOT).as_posix(), before=before,
                            after=dict(stl_sha256=digest(folder / 'working_oobb.stl'),
                                       volume_mm3=float(mesh.volume), dimensions_mm=mesh.extents.tolist())))
        print(f'Built {folder.name}', flush=True)
    report = cache / ('example-audit.json' if args.part else 'rebuild-audit.json')
    report.write_text(json.dumps(reports, indent=2) + '\n', encoding='utf-8')
    print(f'Built {len(reports)} wire-holder plates. Audit: {report}')


if __name__ == '__main__':
    main()
