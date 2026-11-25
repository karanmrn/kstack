#!/usr/bin/env python3
"""Install optional upstream skills from all families or one named family."""
import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from kstack import REDISTRIBUTABLE, UPSTREAM_NOTE, detect_license, license_file, upstream_note


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1], help=argparse.SUPPRESS)
    parser.add_argument('--optional', required=True, nargs='?', const='all', help='install all optional skills or one family')
    args = parser.parse_args()
    root = args.root.resolve()
    manifest = json.loads((root / 'kstack.json').read_text())
    optional = manifest.get('optional', [])
    families = {s['family'] for s in optional}
    if args.optional != 'all' and args.optional not in families:
        parser.error('unknown optional family: ' + args.optional)
    selected = [s for s in optional if args.optional == 'all' or s['family'] == args.optional]
    target = Path.home() / '.agents' / 'skills'
    target.mkdir(parents=True, exist_ok=True)
    installed = 0
    skipped = 0
    with tempfile.TemporaryDirectory(prefix='kstack-optional-') as temp:
        repos = {}
        for skill in selected:
            destination = target / skill['name']
            if destination.exists() or destination.is_symlink():
                skipped += 1
                continue
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
            found = license_file(repos[key])
            license_text = found.read_text(encoding='utf-8') if found else ''
            license_id = detect_license(license_text)
            if license_id not in REDISTRIBUTABLE:
                raise SystemExit('Missing redistributable upstream licence: ' + skill['name'])
            note = upstream_note(skill, skill['commit'], license_id, license_text, [])
            with tempfile.TemporaryDirectory(prefix='.kstack-', dir=target) as staging:
                staged = Path(staging) / skill['name']
                shutil.copytree(source, staged)
                (staged / UPSTREAM_NOTE).write_text(note, encoding='utf-8')
                if destination.exists() or destination.is_symlink():
                    skipped += 1
                    continue
                staged.rename(destination)
            installed += 1
    print(f'Installed {installed} skills to {target}. Preserved {skipped} existing folders.')


if __name__ == '__main__':
    main()
