import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import kstack  # noqa: E402

MIT_TEXT = "MIT License\n\nCopyright (c) 2026 Example\n\nPermission is hereby granted, free of charge, to any person\n"
FAMILIES = [
    {"name": "Upstream", "sources": ["example/skills", "other/*"]},
    {"name": "kstack", "sources": ["me/kstack"]},
]


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_repo(path: Path, files: dict[str, str]) -> None:
    for name, text in files.items():
        write(path / name, text)
    subprocess.run(["git", "init", "-q", str(path)], check=True)
    subprocess.run(["git", "-C", str(path), "add", "-A"], check=True)
    subprocess.run(
        ["git", "-C", str(path), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "init"],
        check=True,
    )


class KstackTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "repo"
        self.upstream = Path(self.temp.name) / "upstream"
        write(
            self.root / "kstack.json",
            json.dumps(
                {
                    "repository": "me/kstack",
                    "families": FAMILIES,
                    "skills": [{"name": "own", "source": "me/kstack", "path": "skills/own"}],
                }
            ),
        )
        write(self.root / "skills" / "own" / "SKILL.md", "---\nname: own\ndescription: Own skill.\n---\n")
        write(self.root / "README.md", "# kstack\n\n<!-- kstack:skills:start -->\nold\n<!-- kstack:skills:end -->\n")

    def tearDown(self):
        self.temp.cleanup()

    def manifest(self) -> dict:
        return json.loads((self.root / "kstack.json").read_text(encoding="utf-8"))

    def select_from(self, skills: dict) -> list[str]:
        lock = Path(self.temp.name) / "lock.json"
        lock.write_text(json.dumps({"skills": skills}), encoding="utf-8")
        return kstack.select(self.root, lock)

    def test_select_keeps_only_family_skills_and_own_skills(self):
        names = self.select_from(
            {
                "Alpha": {"source": "example/skills", "skillPath": "skills/group/alpha/SKILL.md"},
                "beta": {"source": "other/tools", "skillPath": "skills/beta/SKILL.md"},
                "noise": {"source": "random/skills", "skillPath": "skills/noise/SKILL.md"},
            }
        )
        self.assertEqual(names, ["alpha", "beta", "own"])
        alpha = next(s for s in self.manifest()["skills"] if s["name"] == "alpha")
        self.assertEqual(alpha, {"name": "alpha", "source": "example/skills", "path": "skills/group/alpha"})

    def test_select_refuses_two_skills_with_one_folder_name(self):
        with self.assertRaises(SystemExit):
            self.select_from(
                {
                    "a": {"source": "example/skills", "skillPath": "x/dup/SKILL.md"},
                    "b": {"source": "other/tools", "skillPath": "y/dup/SKILL.md"},
                }
            )

    def test_vendor_copies_licensed_skills_links_unlicensed_and_prunes(self):
        make_repo(
            self.upstream / "example__skills",
            {
                "LICENSE": MIT_TEXT,
                "skills/group/alpha/SKILL.md": '---\nname: alpha\ndescription: "Say \\"hi\\" | wave."\n---\n',
                "skills/group/alpha/ref.md": "reference\n",
                "skills/gamma/SKILL.md": "---\nname: gamma\ndescription: Write a verdict: yes or no.\n---\n# Body: kept\n",
            },
        )
        make_repo(
            self.upstream / "other__tools",
            {"skills/beta/SKILL.md": "---\nname: beta\ndescription: Beta.\n---\n"},
        )
        self.select_from(
            {
                "alpha": {"source": "example/skills", "skillPath": "skills/group/alpha/SKILL.md"},
                "beta": {"source": "other/tools", "skillPath": "skills/beta/SKILL.md"},
                "gamma": {"source": "example/skills", "skillPath": "skills/gamma/SKILL.md"},
            }
        )
        write(self.root / "skills" / "stale" / "SKILL.md", "---\nname: stale\n---\n")

        copied, link_only, removed = kstack.vendor(self.root, self.upstream)

        self.assertEqual((copied, link_only, removed), (2, ["beta"], ["stale"]))
        alpha = self.root / "skills" / "alpha"
        self.assertTrue((alpha / "ref.md").is_file())
        note = (alpha / "UPSTREAM.md").read_text(encoding="utf-8")
        self.assertIn("[example/skills](https://github.com/example/skills/tree/", note)
        self.assertIn("## Licence: MIT", note)
        self.assertIn("Copyright (c) 2026 Example", note)
        self.assertNotIn("in quotes", note)
        gamma = self.root / "skills" / "gamma"
        self.assertEqual(
            (gamma / "SKILL.md").read_text(encoding="utf-8"),
            '---\nname: gamma\ndescription: "Write a verdict: yes or no."\n---\n# Body: kept\n',
        )
        self.assertIn("`description` value", (gamma / "UPSTREAM.md").read_text(encoding="utf-8"))
        self.assertFalse((self.root / "skills" / "beta").exists())
        self.assertTrue((self.root / "skills" / "own" / "SKILL.md").is_file())
        self.assertFalse((self.root / "skills" / "own" / "UPSTREAM.md").exists())
        licences = {s["name"]: s.get("license") for s in self.manifest()["skills"]}
        self.assertEqual(licences, {"alpha": "MIT", "beta": "none", "gamma": "MIT", "own": None})

        kstack.render(self.root)
        catalog = (self.root / "CATALOG.md").read_text(encoding="utf-8")
        self.assertIn("kstack ships 4 skills.", catalog)
        self.assertIn('| [`alpha`](skills/alpha/) | Upstream | Say "hi" \\| wave. |', catalog)
        self.assertIn("| `beta` (link-only) | Upstream |", catalog)
        self.assertIn("| [`own`](skills/own/) | kstack | Own skill. | kstack | kstack |", catalog)
        readme = (self.root / "README.md").read_text(encoding="utf-8")
        self.assertNotIn("old", readme)
        self.assertIn("| [`own`](skills/own/) | Own skill. | kstack |", readme)
        self.assertLess(readme.index("`alpha`"), readme.index("`own`"))

    def test_first_sentence_skips_short_fragments_and_truncates(self):
        self.assertEqual(kstack.first_sentence("Stop. Then explain the plan again."), "Stop. Then explain the plan again.")
        self.assertEqual(kstack.first_sentence("A long first sentence here. Second."), "A long first sentence here.")
        self.assertTrue(kstack.first_sentence("word " * 60).endswith("..."))


class RepositoryTest(unittest.TestCase):
    def test_skills_folder_matches_manifest(self):
        manifest = kstack.load_manifest(REPO_ROOT)
        own = manifest["repository"]
        listed = set()
        for skill in manifest["skills"]:
            self.assertIsNotNone(kstack.family_for(manifest, skill["source"]), skill["name"])
            folder = REPO_ROOT / "skills" / skill["name"]
            if skill["source"] == own:
                self.assertTrue((folder / "SKILL.md").is_file(), skill["name"])
                self.assertFalse((folder / "UPSTREAM.md").exists(), skill["name"])
                listed.add(skill["name"])
            elif skill.get("license") in kstack.REDISTRIBUTABLE:
                self.assertTrue((folder / "SKILL.md").is_file(), skill["name"])
                self.assertIn(skill["commit"][:7], (folder / "UPSTREAM.md").read_text(encoding="utf-8"))
                listed.add(skill["name"])
            else:
                self.assertFalse(folder.exists(), f"{skill['name']} has no redistributable licence")
        present = {entry.name for entry in (REPO_ROOT / "skills").iterdir()}
        self.assertEqual(present, listed)

    def test_generated_files_are_current(self):
        with tempfile.TemporaryDirectory() as temp:
            copy = Path(temp)
            for name in ("kstack.json", "README.md", "CATALOG.md"):
                shutil.copy(REPO_ROOT / name, copy / name)
            (copy / "skills").symlink_to(REPO_ROOT / "skills")
            kstack.render(copy)
            for name in ("README.md", "CATALOG.md"):
                self.assertEqual(
                    (copy / name).read_text(encoding="utf-8"),
                    (REPO_ROOT / name).read_text(encoding="utf-8"),
                    f"{name} is stale: run python3 scripts/kstack.py render",
                )


if __name__ == "__main__":
    unittest.main()
