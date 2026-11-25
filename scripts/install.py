#!/usr/bin/env python3
"""Install the core skills and, optionally, a named family of upstream skills."""
import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1], help=argparse.SUPPRESS)
    parser.add_argument('--optional', nargs='?', const='all', help='install all optional skills or one family')
    args = parser.parse_args()
    root = args.root.resolve()
    manifest = json.loads((root / 'kstack.json').read_text())
    optional = manifest.get('optional', [])
    families = {s['family'] for s in optional}
    if args.optional and args.optional != 'all' and args.optional not in families:
        parser.error('unknown optional family: ' + args.optional)
    selected = [s for s in optional if args.optional and (args.optional == 'all' or s['family'] == args.optional)]
    target = Path.home() / '.agents' / 'skills'
    target.mkdir(parents=True, exist_ok=True)
    installed = 0
    skipped = 0
    for source in sorted((root / 'skills').iterdir()):
        if (source / 'SKILL.md').is_file():
            destination = target / source.name
            if not destination.exists() and not destination.is_symlink():
                shutil.copytree(source, destination)
                installed += 1
            else:
                skipped += 1
    with tempfile.TemporaryDirectory(prefix='kstack-optional-') as temp:
        repos = {}
        for skill in selected:
            key = (skill['source'], skill['commit'])
            if key not in repos:
                path = Path(temp) / str(len(repos))
                source = skill['source']
                if not source.startswith('/'):
                    source = 'https://github.com/' + source + '.git'
                subprocess.run(['git', 'clone', '-q', '--no-checkout', source, str(path)], check=True)
                subprocess.run(['git', '-C', str(path), 'checkout', '-q', '--detach', skill['commit']], check=True)
                repos[key] = path
            source = repos[key] / skill['path']
            if not (source / 'SKILL.md').is_file():
                raise SystemExit('Missing upstream skill: ' + skill['name'])
            destination = target / skill['name']
            if not destination.exists() and not destination.is_symlink():
                shutil.copytree(source, destination)
                installed += 1
            else:
                skipped += 1
    print(f'Installed {installed} skills to {target}. Preserved {skipped} existing folders.')


if __name__ == '__main__':
    main()
