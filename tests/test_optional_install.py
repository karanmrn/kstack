import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'install.py'

class OptionalInstallTest(unittest.TestCase):
    def test_default_family_and_unknown_family(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'repo'
            home = Path(tmp) / 'home'
            (root / 'skills' / 'core').mkdir(parents=True)
            (root / 'skills' / 'core' / 'SKILL.md').write_text('core')
            upstream = Path(tmp) / 'upstream'
            (upstream / 'skills' / 'extra').mkdir(parents=True)
            (upstream / 'skills' / 'extra' / 'SKILL.md').write_text('extra')
            subprocess.run(['git', 'init', '-q', str(upstream)], check=True)
            subprocess.run(['git', '-C', str(upstream), 'add', '.'], check=True)
            subprocess.run(['git', '-C', str(upstream), '-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '-qm', 'test'], check=True)
            commit = subprocess.check_output(['git', '-C', str(upstream), 'rev-parse', 'HEAD'], text=True).strip()
            (root / 'kstack.json').write_text(json.dumps({'optional': [{'name':'extra', 'family':'design', 'source':str(upstream), 'path':'skills/extra', 'commit':commit}]}))
            env = dict(os.environ, HOME=str(home))
            def run(*args):
                return subprocess.run([sys.executable, str(SCRIPT), '--root', str(root), *args], env=env, capture_output=True, text=True)
            self.assertEqual(run().returncode, 0)
            self.assertTrue((home / '.agents/skills/core/SKILL.md').is_file())
            self.assertFalse((home / '.agents/skills/extra').exists())
            self.assertNotEqual(run('--optional', 'invalid').returncode, 0)
            (home / '.agents/skills/core/SKILL.md').write_text('preserve')
            self.assertEqual(run('--optional', 'design').returncode, 0)
            self.assertEqual((home / '.agents/skills/core/SKILL.md').read_text(), 'preserve')
            self.assertEqual((home / '.agents/skills/extra/SKILL.md').read_text(), 'extra')

if __name__ == '__main__':
    unittest.main()
