"""Shared populate/CAD scheduling and export metadata for mounting plates."""
import copy
import json
import os
from pathlib import Path
import shutil
import subprocess

from mounting_geometry import normalize_kwargs
from mounting_layouts import LABELS, LAYOUTS, plan

FAMILIES = {'mounting_plate_default': ('Standard', '3dpr'),
            'mounting_plate_oobb': ('Wire-holder', 'working_oobb')}
GEOMETRY_KEYS = ('board_size', 'breakout_pcb_width', 'breakout_pcb_height',
                 'mounting_holes', 'mounting_hole_radius_name', 'mounting_hole_radius_names',
                 'mounting_hole_details', 'mounting_lift')


def details_for(record):
    """Expand declared families once; undefined/empty patterns schedule no holder.

    A board with holes and no family declaration gets standard plates. Existing
    wire-holder declarations are retained; research promotion does not add them.
    """
    details = copy.deepcopy(record.get('oobb_details', []))
    if isinstance(details, dict):
        details = [details]
    details = [d for d in details if isinstance(d, dict)] if isinstance(details, list) else []
    other = [d for d in details if d.get('oobb_name') not in FAMILIES]
    seeds = {}
    for d in details:
        family = d.get('oobb_name')
        if family in FAMILIES and (family not in seeds or d.get('mounting_layout', 'full_wrap') == 'full_wrap'):
            seeds[family] = d
    if not seeds and record.get('mounting_holes'):
        seeds['mounting_plate_default'] = dict(oobb_name='mounting_plate_default')
    for family, seed in seeds.items():
        params = copy.deepcopy(seed)
        for key in GEOMETRY_KEYS:
            if key in record:
                params[key] = copy.deepcopy(record[key])
        if not params.get('mounting_holes') or record.get('mounting_geometry_ready') is False:
            continue
        params = normalize_kwargs(params)
        if not all(params.get(k, 0) > 0 for k in ('breakout_pcb_width', 'breakout_pcb_height')):
            raise ValueError('Mounting plates need positive PCB width and height')
        for layout in LAYOUTS:
            item = dict(copy.deepcopy(params), oobb_name=family, mounting_layout=layout)
            stem = FAMILIES[family][1]
            if layout != 'full_wrap':
                stem += '_' + layout
            # Keep the canonical working.yaml / thing.yaml for the standard full wrap.
            item.pop('scad_output', None)
            if stem != '3dpr':
                item['scad_output'] = stem
            plan(**dict(item, wire_adapter=family == 'mounting_plate_oobb'))
            other.append(item)
    return other


def apply_variants(records):
    for record in records:
        record['oobb_details'] = details_for(record)
    return records


def manifest_for(parts):
    variants = []
    for part in parts:
        name = part['oobb_name']
        if name not in FAMILIES:
            continue
        params = part['kwargs']
        family, default_stem = FAMILIES[name]
        layout = params.get('mounting_layout', 'full_wrap')
        variants.append(dict(source=(params.get('scad_output') or default_stem)+'.stl',
                             label=family+' — '+LABELS[layout], family=family, layout=layout,
                             geometry=plan(**dict(params, wire_adapter=name=='mounting_plate_oobb'))))
    return dict(schema=1, variants=variants)


def write_manifests(parts, directory='parts'):
    groups = {}
    for part in parts:
        if part['oobb_name'] in FAMILIES:
            groups.setdefault(part['id'], []).append(part)
    for identifier, group in groups.items():
        path = Path(directory)/identifier/'mounting_variants.json'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(manifest_for(group), indent=2)+'\n', encoding='utf-8')


def export_stls(parts, directory='parts', executable=None):
    """Synchronous OpenSCAD export: failures propagate before presentation runs."""
    import trimesh
    executable = executable or os.environ.get('OPENSCAD_EXE') or shutil.which('openscad')
    if not executable:
        candidate = Path(r'C:\Program Files\OpenSCAD (Nightly)\openscad.com')
        executable = str(candidate) if candidate.is_file() else None
    if not executable:
        raise FileNotFoundError('OpenSCAD not found; set OPENSCAD_EXE')
    results = []
    for part in parts:
        stem = part['kwargs'].get('scad_output') or '3dpr'
        source = Path(directory)/part['id']/(stem+'.scad')
        output = source.with_suffix('.stl')
        temporary = source.with_name(stem+'.building.stl')
        try:
            result = subprocess.run([executable, '-o', str(temporary), str(source)],
                                    capture_output=True, text=True, timeout=180)
            if result.returncode or 'ERROR:' in result.stderr or not temporary.is_file():
                raise RuntimeError('OpenSCAD failed for '+str(source)+': '+result.stderr[-2000:])
            mesh = trimesh.load_mesh(temporary)
            if not mesh.is_watertight or mesh.volume <= 0:
                raise ValueError('Invalid STL: '+str(source))
            temporary.replace(output)
            results.append(dict(source=str(output), watertight=True, bodies=int(mesh.body_count),
                                volume_mm3=float(mesh.volume), bounds_mm=mesh.bounds.tolist()))
        finally:
            temporary.unlink(missing_ok=True)
    return results
