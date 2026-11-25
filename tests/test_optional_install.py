import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'install.py'
MIT_TEXT = 'MIT License\n\nCopyright (c) 2026 Example\n\nPermission is hereby granted, free of charge, to any person\n'


class OptionalInstallTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'repo'
        self.home = Path(self.temp.name) / 'home'
        self.upstream = Path(self.temp.name) / 'upstream'
        self.target = self.home / '.agents' / 'skills'
        core = self.root / 'skills' / 'core'
        core.mkdir(parents=True)
        (core / 'SKILL.md').write_text('core')
        self.skills = []
        for family, name, path in [
            ('design', 'animate', 'skills/animate'),
            ('research', 'last30days', 'skills/last30days'),
            ('workflows', 'rpi', 'plugins/rpi/skills/rpi'),
        ]:
            source = self.upstream / path
            source.mkdir(parents=True)
            (source / 'SKILL.md').write_text(name)
            self.skills.append({'name': name, 'family': family, 'source': str(self.upstream), 'path': path, 'license': 'MIT'})
        (self.upstream / 'LICENSE').write_text(MIT_TEXT)
        (self.upstream / 'skills/animate/LICENSE').write_text('Skill-specific notice\n')
        subprocess.run(['git', 'init', '-q', str(self.upstream)], check=True)
        self.commit()
        self.revision = subprocess.check_output(['git', '-C', str(self.upstream), 'rev-parse', 'HEAD'], text=True).strip()
        for skill in self.skills:
            skill['commit'] = self.revision
        self.write_manifest()
        (self.upstream / 'LICENSE').write_text('Later licence\n')
        (self.upstream / 'skills/animate/SKILL.md').write_text('later payload')
        self.commit()

    def commit(self):
        subprocess.run(['git', '-C', str(self.upstream), 'add', '.'], check=True)
        subprocess.run(['git', '-C', str(self.upstream), '-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '-qm', 'fixture'], check=True)

    def write_manifest(self):
        (self.root / 'kstack.json').write_text(json.dumps({'optional': self.skills}))

    def run_installer(self, *args, home=None):
        return subprocess.run(
            [sys.executable, str(SCRIPT), '--root', str(self.root), *args],
            env=dict(os.environ, HOME=str(home or self.home)), capture_output=True, text=True,
        )

    def test_requires_optional_selection_and_rejects_unknown_family(self):
        for args in [(), ('--optional', 'invalid')]:
            with self.subTest(args=args):
                result = self.run_installer(*args)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(self.target.exists())

    def test_selections_copy_only_requested_optional_skills_with_notices(self):
        for selection in ['design', 'research', 'workflows', 'all', None]:
            with self.subTest(selection=selection):
                home = self.home / str(selection)
                args = ['--optional'] + ([selection] if selection else [])
                result = self.run_installer(*args, home=home)
                self.assertEqual(result.returncode, 0, result.stderr)
                target = home / '.agents' / 'skills'
                expected = {'design': {'animate'}, 'research': {'last30days'}, 'workflows': {'rpi'}}
                names = expected.get(selection, {'animate', 'last30days', 'rpi'})
                self.assertEqual({p.name for p in target.iterdir()}, names)
                for name in names:
                    self.assertEqual((target / name / 'SKILL.md').read_text(), name)
                    note = (target / name / 'UPSTREAM.md').read_text()
                    self.assertIn(MIT_TEXT, note)
                    self.assertIn(self.revision, note)
                    self.assertIn(str(self.upstream), note)
                    skill = next(s for s in self.skills if s['name'] == name)
                    self.assertIn(skill['path'], note)
                if 'animate' in names:
                    self.assertEqual((target / 'animate/LICENSE').read_text(), 'Skill-specific notice\n')

    def test_root_licence_and_provenance_survive_clone_cleanup(self):
        result = self.run_installer('--optional', 'all')
        self.assertEqual(result.returncode, 0, result.stderr)
        for skill in self.skills:
            with self.subTest(name=skill['name']):
                note = (self.target / skill['name'] / 'UPSTREAM.md').read_text()
                self.assertIn(MIT_TEXT, note)
                self.assertIn(self.revision, note)
                self.assertIn(skill['path'], note)
                self.assertIn(skill['source'], note)

    def test_unlicensed_upstream_is_not_copied(self):
        (self.upstream / 'LICENSE').unlink()
        self.commit()
        revision = subprocess.check_output(['git', '-C', str(self.upstream), 'rev-parse', 'HEAD'], text=True).strip()
        for skill in self.skills:
            skill['commit'] = revision
        self.write_manifest()
        result = self.run_installer('--optional', 'all')
        self.assertNotEqual(result.returncode, 0)
        for skill in self.skills:
            self.assertFalse((self.target / skill['name']).exists())

    def test_existing_destinations_need_no_upstream(self):
        self.target.mkdir(parents=True)
        (self.target / 'animate').mkdir()
        (self.target / 'animate/SKILL.md').write_text('custom')
        (self.target / 'last30days').write_text('existing file')
        (self.target / 'rpi').symlink_to(self.target / 'missing')
        (self.target / 'core').mkdir()
        (self.target / 'core/SKILL.md').write_text('custom core')
        shutil.rmtree(self.upstream)
        for selection in ['design', 'research', 'workflows', 'all', None]:
            with self.subTest(selection=selection):
                args = ['--optional'] + ([selection] if selection else [])
                result = self.run_installer(*args)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual((self.target / 'animate/SKILL.md').read_text(), 'custom')
                self.assertEqual((self.target / 'last30days').read_text(), 'existing file')
                self.assertTrue((self.target / 'rpi').is_symlink())
                self.assertEqual((self.target / 'core/SKILL.md').read_text(), 'custom core')

    def test_mixed_existing_and_new_destinations(self):
        self.target.mkdir(parents=True)
        (self.target / 'animate').mkdir()
        (self.target / 'animate/SKILL.md').write_text('custom')
        self.skills[0]['source'] = str(self.upstream / 'unavailable')
        self.write_manifest()
        result = self.run_installer('--optional', 'all')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.target / 'animate/SKILL.md').read_text(), 'custom')
        self.assertTrue((self.target / 'last30days/UPSTREAM.md').is_file())
        self.assertTrue((self.target / 'rpi/UPSTREAM.md').is_file())


if __name__ == '__main__':
    unittest.main()
