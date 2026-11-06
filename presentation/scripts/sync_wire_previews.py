"""Refresh legacy wire-plate previews and tracked navigation copies after a rebuild."""
from pathlib import Path
import shutil
import subprocess
import yaml

ROOT = Path(__file__).resolve().parents[2]


def tracked(pattern):
    return subprocess.check_output(['git', '-C', str(ROOT), 'ls-files', pattern], text=True).splitlines()


def main():
    parts = {}
    for name in tracked('parts/*/working_oobb.yaml'):
        source = ROOT / name
        data = yaml.safe_load(source.read_text(encoding='utf-8'))
        folder = source.parent
        parts[data['id']] = folder
        shutil.copyfile(folder / 'presentation/images/working_oobb.png', folder / 'working_oobb.png')
    tracked_paths = set(tracked('navigation_oobb/*'))
    count = 0
    for name in tracked('navigation_oobb/*/working_oobb.yaml'):
        target = ROOT / name
        data = yaml.safe_load(target.read_text(encoding='utf-8'))
        source = parts[data['id']]
        for filename in ('working_oobb.scad', 'working_oobb.stl', 'working_oobb.png', 'working_oobb_thing.yaml'):
            destination = target.parent / filename
            if destination.relative_to(ROOT).as_posix() in tracked_paths:
                shutil.copyfile(source / filename, destination)
                count += 1
    print(f'Updated {len(parts)} legacy previews and {count} tracked navigation files.')


if __name__ == '__main__':
    main()
