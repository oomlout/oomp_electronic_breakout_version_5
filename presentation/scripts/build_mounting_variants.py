"""Build three M6-clear layouts for every tracked, CAD-bearing catalogue part."""
import argparse
import copy
from concurrent.futures import ThreadPoolExecutor, as_completed
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
import mounting_layouts as layouts
import working_scad_mounting_plate_default as standard
import working_scad_mounting_plate_oobb as wire


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--part')
    parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--openscad',default=os.environ.get('OPENSCAD_EXE',r'C:\Program Files\OpenSCAD (Nightly)\openscad.com'))
    args=parser.parse_args()
    os.chdir(ROOT)
    files=subprocess.check_output(['git','ls-tree','-r','--name-only','HEAD','parts'],text=True).splitlines()
    folders=[ROOT/Path(f).parent for f in files if f.endswith('/working.yaml')]
    if args.part:
        folders=[p for p in folders if p.name==args.part]
        if not folders:
            parser.error('--part must name a committed part folder')
    cache=ROOT/'presentation/.cache/mounting-variants'
    cache.mkdir(parents=True,exist_ok=True)
    jobs={}; prepared=[]
    for folder in folders:
        variants=[]
        for stem, thing_file, module, family in [('3dpr','thing.yaml',standard,'Standard'),('working_oobb','working_oobb_thing.yaml',wire,'Wire-holder')]:
            if not (folder/(stem+'.stl')).exists() or not (folder/thing_file).exists(): continue
            saved=yaml.safe_load((folder/thing_file).read_text(encoding='utf-8'))
            for variant in layouts.LAYOUTS:
                params=copy.deepcopy(saved['kwargs'])
                params['mounting_layout']=variant
                params.pop('wire_adapter',None)
                plan=layouts.plan(**dict(params,wire_adapter=family=='Wire-holder'))
                thing=copy.deepcopy(saved['thing'])
                for key in ('components','components_objects','components_string'): thing[key]=[]
                module.get_base(thing,**params)
                filename=stem if variant=='full_wrap' else stem+'_'+variant
                scratch=cache/'working.scad'
                oobb.opsc_make_object(str(scratch),thing['components'],mode='3dpr',save_type='none',overwrite=True)
                key=sha(scratch)
                scad=cache/(key+'.scad'); stl=cache/(key+'.stl')
                if not scad.exists(): shutil.copyfile(scratch,scad)
                if not stl.exists(): jobs[key]=(scad,stl)
                record=dict(source=filename+'.stl',label=family+' — '+layouts.LABELS[variant],
                            family=family,layout=variant,geometry=plan)
                variants.append(record)
                new_saved=copy.deepcopy(saved);new_saved['thing']=thing
                new_saved['kwargs']=params
                prepared.append((folder,filename,scad,stl,new_saved,thing_file if variant=='full_wrap' else None))
        if variants:
            (cache/(folder.name+'.json')).write_text(json.dumps(dict(schema=1,variants=variants),indent=2)+'\n',encoding='utf-8')
    print(f'Compiling {len(jobs)} unique meshes for {len(prepared)} variants.',flush=True)
    def compile_one(pair):
        scad,stl=pair
        result=subprocess.run([args.openscad,'-o',str(stl),str(scad)],capture_output=True,text=True)
        if result.returncode: raise RuntimeError(result.stderr)
        mesh=trimesh.load_mesh(stl)
        if not mesh.is_watertight or mesh.volume<=0: raise ValueError(f'Invalid mesh: {stl.name}')
        return stl
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures=[pool.submit(compile_one,pair) for pair in jobs.values()]
        for i,f in enumerate(as_completed(futures),1):
            f.result()
            if i%10==0 or i==len(futures): print(f'Compiled {i}/{len(futures)}',flush=True)
    for folder,filename,scad,stl,saved,thing_file in prepared:
        shutil.copyfile(scad,folder/(filename+'.scad'))
        shutil.copyfile(stl,folder/(filename+'.stl'))
        if thing_file:
            (folder/thing_file).write_text(yaml.dump(saved),encoding='utf-8',newline='\n')
    completed=0
    for folder in folders:
        manifest=cache/(folder.name+'.json')
        if manifest.exists():
            shutil.copyfile(manifest,folder/'mounting_variants.json');completed+=1
    print(f'Built {len(prepared)} variants in {completed} part folders.',flush=True)


if __name__=='__main__': main()
