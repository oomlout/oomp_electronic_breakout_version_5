"""Refresh full-wrap legacy previews and existing tracked navigation copies."""
from pathlib import Path
import shutil
import subprocess
import yaml

ROOT = Path(__file__).resolve().parents[2]


def main():
    paths = subprocess.check_output(['git', '-C', str(ROOT), 'ls-tree', '-r', '--name-only', 'HEAD'], text=True).splitlines()
    tracked = set(paths)
    parts = {}
    previews = copies = 0
    seen = set()
    for name in paths:
        if not name.startswith('parts/') or not name.endswith('/working.yaml'):
            continue
        folder = (ROOT / name).parent
        if not (folder / 'mounting_variants.json').exists():
            continue
        parts[yaml.safe_load((ROOT/name).read_text(encoding='utf-8'))['id']] = folder
        for stem in ('3dpr', 'working_oobb'):
            image = folder / 'presentation/images' / (stem + '.png')
            if image.exists():
                shutil.copyfile(image, folder / (stem + '.png'))
                previews += 1
    for name in paths:
        if not name.startswith('navigation_oobb/') or not name.endswith(('/working.yaml', '/working_oobb.yaml')):
            continue
        target = (ROOT/name).parent
        if target in seen:
            continue
        seen.add(target)
        record = yaml.safe_load((ROOT/name).read_text(encoding='utf-8'))
        source = parts.get(record['id'])
        if source is None:
            continue
        for filename in ('3dpr.scad', '3dpr.stl', '3dpr.png', 'thing.yaml',
                         'working_oobb.scad', 'working_oobb.stl', 'working_oobb.png', 'working_oobb_thing.yaml'):
            destination = target / filename
            if destination.relative_to(ROOT).as_posix() in tracked and (source/filename).exists():
                shutil.copyfile(source/filename, destination)
                copies += 1
    print(f'Updated {previews} legacy previews and {copies} tracked navigation files.')


if __name__ == '__main__':
    main()
