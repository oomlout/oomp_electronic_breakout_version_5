"""Check saved layouts and actual STL cross-sections at every M6 station."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import trimesh
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import mounting_layouts
from mounting_geometry import normalize_kwargs


def main():
    paths = subprocess.check_output(['git', '-C', str(ROOT), 'ls-tree', '-r', '--name-only', 'HEAD', 'parts'], text=True).splitlines()
    count = stations = trimmed = footprint_retained = 0
    meshes = {}
    records = []
    for name in paths:
        if not name.endswith('/working.yaml'):
            continue
        folder = (ROOT/name).parent
        source = folder/'mounting_variants.json'
        if not source.exists():
            continue
        variants = json.loads(source.read_text())['variants']
        full = {}
        for v in variants:
            params = yaml.safe_load((folder/('thing.yaml' if v['family']=='Standard' else 'working_oobb_thing.yaml')).read_text())['kwargs']
            params = normalize_kwargs(params)
            mounting_layouts.audit(v['geometry'], params)
            stl = folder/v['source']
            digest = hashlib.sha256(stl.read_bytes()).hexdigest()
            if digest not in meshes:
                mesh = trimesh.load_mesh(stl)
                assert mesh.is_watertight and mesh.volume > 0, stl
                z = float(params.get('pos', [0,0,0])[2]) + float(params.get('depth',3))/2
                section = trimesh.intersections.mesh_plane(mesh, [0,0,1], [0,0,z])[:,:,:2]
                meshes[digest] = (mesh, section)
            mesh, section = meshes[digest]
            for point in v['geometry']['m6_centres_mm']:
                centre = np.array(point) + np.array(params.get('pos',[0,0,0])[:2])
                # Rays from each hole centre must meet the bore wall at r=3.25.
                # Intersect 24 radial rays with every segment of the STL slice.
                a, delta = section[:,0]-centre, section[:,1]-section[:,0]
                for angle in np.arange(24)*np.pi/12:
                    ray = np.array([np.cos(angle), np.sin(angle)])
                    cross = ray[0]*delta[:,1]-ray[1]*delta[:,0]
                    valid = np.abs(cross)>1e-9
                    t = np.divide(a[:,0]*delta[:,1]-a[:,1]*delta[:,0],cross,out=np.full(len(a),np.inf),where=valid)
                    u = np.divide(a[:,0]*ray[1]-a[:,1]*ray[0],cross,out=np.full(len(a),np.inf),where=valid)
                    hits = t[valid & (t>1e-6) & (u>=-1e-7) & (u<=1+1e-7)]
                    assert len(hits) and 3.22 <= hits.min() <= 3.26, (stl,point,angle,hits.min() if len(hits) else None)
                stations += 1
            if v['layout']=='full_wrap':
                full[v['family']] = mesh.extents
            else:
                assert np.all(mesh.extents <= full[v['family']]+.03), stl
                if np.prod(mesh.extents[:2]) < np.prod(full[v['family']][:2])-.1:
                    trimmed += 1
                else:
                    footprint_retained += 1
            count += 1
        records.append(folder.name)
    result = dict(records=len(records), variants=count, unique_meshes=len(meshes), m6_stations=stations,
                  trimmed_variants=trimmed, attachment_footprint_retained=footprint_retained,
                  hole_diameter_mm=6.5, head_nut_clearance_diameter_mm=13,
                  result='Watertight positive-volume meshes; 24 radial STL-section measurements per M6 bore; PCB/post clearance; compact footprints no larger than full wrap.')
    (ROOT/'presentation/mounting-layout-audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__': main()
