#!/usr/bin/env python3
"""Curate kstack: select, vendor and catalog the skills in this repository.

kstack.json is the single source of truth. It lists the upstream families
kstack accepts and every skill the repository ships.

Commands:
  select   Rebuild the upstream skill list from an installed-skill lock file.
           Only skills whose source matches a family pattern are kept.
  vendor   Copy each upstream skill folder into skills/ at the upstream HEAD,
           write its UPSTREAM.md provenance note, and remove every folder
           under skills/ that the manifest does not list. A frontmatter
           value that is not valid YAML is put in quotes, and UPSTREAM.md
           records it. A skill whose upstream licence does not allow
           redistribution is not copied. It is listed as link-only.
  render   Write CATALOG.md and the skill table in README.md.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
IGNORED_NAMES = {".git", "__pycache__", ".DS_Store"}
UPSTREAM_NOTE = "UPSTREAM.md"
TABLE_START = "<!-- kstack:skills:start -->"
TABLE_END = "<!-- kstack:skills:end -->"
REDISTRIBUTABLE = {"MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC"}


# Manifest -------------------------------------------------------------------


def load_manifest(root: Path) -> dict:
    return json.loads((root / "kstack.json").read_text(encoding="utf-8"))


def save_manifest(root: Path, manifest: dict) -> None:
    manifest["skills"].sort(key=lambda skill: skill["name"].casefold())
    text = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    (root / "kstack.json").write_text(text, encoding="utf-8")


def family_for(manifest: dict, source: str) -> dict | None:
    for family in manifest["families"]:
        if any(fnmatch.fnmatchcase(source, pattern) for pattern in family["sources"]):
            return family
    return None


# select ---------------------------------------------------------------------


def select(root: Path, lock_path: Path) -> list[str]:
    manifest = load_manifest(root)
    lock = json.loads(lock_path.read_text(encoding="utf-8")).get("skills", {})
    previous = {skill["name"]: skill for skill in manifest["skills"]}
    own_source = manifest["repository"]
    selected = [skill for skill in manifest["skills"] if skill["source"] == own_source]
    names = {skill["name"] for skill in selected}
    for entry in lock.values():
        source = entry.get("source", "")
        skill_path = entry.get("skillPath", "")
        if source == own_source or not family_for(manifest, source) or not skill_path:
            continue
        path = str(Path(skill_path).parent)
        name = Path(path).name
        if name in names:
            raise SystemExit(f"error: two skills share the folder name {name!r}")
        names.add(name)
        skill = {"name": name, "source": source, "path": path}
        old = previous.get(name, {})
        for key in ("commit", "license", "summary"):
            if old.get("source") == source and key in old:
                skill[key] = old[key]
        selected.append(skill)
    manifest["skills"] = selected
    save_manifest(root, manifest)
    return sorted(names)


# vendor ---------------------------------------------------------------------


def git(*args: str) -> str:
    result = subprocess.run(["git", *args], capture_output=True, text=True, check=True)
    return result.stdout.strip()


def checkout(upstream_root: Path, source: str, cache: dict[str, Path]) -> Path:
    if source in cache:
        return cache[source]
    target = upstream_root / source.replace("/", "__")
    if not target.is_dir():
        upstream_root.mkdir(parents=True, exist_ok=True)
        git("clone", "--quiet", "--depth", "1", f"https://github.com/{source}", str(target))
    cache[source] = target
    return target


def license_file(repo: Path) -> Path | None:
    for candidate in sorted(repo.iterdir()):
        if candidate.is_file() and re.match(r"(?i)^(licen[cs]e|copying)(\.|$)", candidate.name):
            return candidate
    return None


def detect_license(text: str) -> str:
    if "Permission is hereby granted, free of charge" in text:
        return "MIT"
    if "Apache License" in text and "Version 2.0" in text:
        return "Apache-2.0"
    if "Permission to use, copy, modify, and/or distribute" in text:
        return "ISC"
    if "Redistribution and use in source and binary forms" in text:
        return "BSD-3-Clause" if "Neither the name" in text else "BSD-2-Clause"
    return "unknown"


def ignore_entries(_directory: str, names: list[str]) -> set[str]:
    return {name for name in names if name in IGNORED_NAMES}


def quote_plain_scalars(skill_file: Path) -> list[str]:
    """Quote frontmatter values that strict YAML parsers reject.

    A plain scalar that contains ": " or " #" is not valid YAML. Some
    installers then skip the skill. Return the keys that were quoted.
    """
    text = skill_file.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return []
    parts = text.split("---", 2)
    if len(parts) < 3:
        return []
    lines = parts[1].split("\n")
    quoted: list[str] = []
    for index, line in enumerate(lines):
        match = re.match(r"^([A-Za-z_][\w-]*):[ \t]+(.+)$", line)
        if not match:
            continue
        key, value = match.group(1), match.group(2).rstrip()
        if value[0] in "\"'|>[{&*!" or (": " not in value and " #" not in value):
            continue
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        lines[index] = f'{key}: "{escaped}"'
        quoted.append(key)
    if quoted:
        skill_file.write_text("---".join([parts[0], "\n".join(lines), parts[2]]), encoding="utf-8")
    return quoted


def upstream_note(skill: dict, commit: str, license_id: str, license_text: str, quoted: list[str]) -> str:
    url = f"https://github.com/{skill['source']}/tree/{commit}/{skill['path']}"
    if quoted:
        keys = ", ".join(f"`{key}`" for key in quoted)
        change = (
            f"kstack adds this file. kstack also puts the {keys} value of the `SKILL.md` frontmatter "
            "in quotes, because the upstream value is not valid YAML. Nothing else changes.\n"
        )
    else:
        change = "kstack adds only this file.\n"
    return (
        "# Upstream\n\n"
        f"This folder is a copy of `{skill['path']}` from [{skill['source']}]({url}) "
        f"at commit `{commit[:7]}`.\n"
        f"{change}"
        "Report problems with the skill upstream.\n\n"
        f"## Licence: {license_id}\n\n"
        "The upstream licence text follows without change.\n\n"
        "```text\n"
        f"{license_text.rstrip()}\n"
        "```\n"
    )


def vendor(root: Path, upstream_root: Path) -> tuple[int, list[str], list[str]]:
    manifest = load_manifest(root)
    skills_dir = root / "skills"
    skills_dir.mkdir(exist_ok=True)
    cache: dict[str, Path] = {}
    copied = 0
    link_only: list[str] = []
    for skill in manifest["skills"]:
        if skill["source"] == manifest["repository"]:
            continue
        repo = checkout(upstream_root, skill["source"], cache)
        found = license_file(repo)
        license_text = found.read_text(encoding="utf-8") if found else ""
        license_id = detect_license(license_text) if found else "none"
        skill["commit"] = git("-C", str(repo), "rev-parse", "HEAD")
        skill["license"] = license_id
        target = skills_dir / skill["name"]
        if target.exists():
            shutil.rmtree(target)
        if license_id not in REDISTRIBUTABLE:
            link_only.append(skill["name"])
            continue
        source_dir = repo / skill["path"]
        if not (source_dir / "SKILL.md").is_file():
            raise SystemExit(f"error: {skill['source']} has no SKILL.md under {skill['path']}")
        shutil.copytree(source_dir, target, symlinks=False, ignore=ignore_entries)
        quoted = quote_plain_scalars(target / "SKILL.md")
        note = upstream_note(skill, skill["commit"], license_id, license_text, quoted)
        (target / UPSTREAM_NOTE).write_text(note, encoding="utf-8")
        copied += 1

    shipped = {skill["name"] for skill in manifest["skills"] if skill["name"] not in link_only}
    removed: list[str] = []
    for entry in sorted(skills_dir.iterdir()):
        if entry.name not in shipped:
            removed.append(entry.name)
            shutil.rmtree(entry) if entry.is_dir() else entry.unlink()
    for name in sorted(shipped):
        if not (skills_dir / name / "SKILL.md").is_file():
            raise SystemExit(f"error: skills/{name}/SKILL.md is missing")
    save_manifest(root, manifest)
    return copied, link_only, removed


# render ---------------------------------------------------------------------


def frontmatter_value(text: str, key: str) -> str | None:
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    lines = parts[1].splitlines()
    prefix = f"{key}:"
    for index, line in enumerate(lines):
        if not line.startswith(prefix):
            continue
        value = line[len(prefix) :].strip()
        if value in {"", ">", ">-", "|", "|-"}:
            continuation: list[str] = []
            for next_line in lines[index + 1 :]:
                if next_line and not next_line[0].isspace():
                    break
                if next_line.strip():
                    continuation.append(next_line.strip())
            return " ".join(continuation) or None
        if len(value) > 1 and value[0] == value[-1] == '"':
            return value[1:-1].replace('\\"', '"') or None
        if len(value) > 1 and value[0] == value[-1] == "'":
            return value[1:-1].replace("''", "'") or None
        return value or None
    return None


def clean_cell(value: str) -> str:
    value = value.replace("\u2014", "-").replace("\u2013", "-")
    return re.sub(r"\s+", " ", value).strip().replace("|", r"\|")


def first_sentence(value: str, limit: int = 140) -> str:
    sentence = ""
    for match in re.finditer(r".+?[.!?](?=\s|$)", value):
        sentence = value[: match.end()].strip()
        if len(sentence) >= 20:
            break
    sentence = sentence or value
    if len(sentence) > limit:
        sentence = sentence[: limit - 3].rsplit(" ", 1)[0] + "..."
    return sentence


def describe(root: Path, skill: dict, manifest: dict) -> str:
    skill_file = root / "skills" / skill["name"] / "SKILL.md"
    if skill_file.is_file():
        text = skill_file.read_text(encoding="utf-8", errors="replace")
        description = frontmatter_value(text, "description")
        if description:
            return clean_cell(description)
    return clean_cell(skill.get("summary", "Link-only. Read the upstream SKILL.md."))


def source_link(skill: dict, manifest: dict) -> str:
    if skill["source"] == manifest["repository"]:
        return "kstack"
    commit = skill.get("commit", "HEAD")
    return f"[{skill['source']}](https://github.com/{skill['source']}/tree/{commit}/{skill['path']})"


def skill_link(root: Path, skill: dict) -> str:
    if (root / "skills" / skill["name"] / "SKILL.md").is_file():
        return f"[`{skill['name']}`](skills/{skill['name']}/)"
    return f"`{skill['name']}` (link-only)"


def ordered(manifest: dict) -> list[tuple[dict, dict]]:
    families = manifest["families"]
    rows = []
    for skill in manifest["skills"]:
        family = family_for(manifest, skill["source"])
        if family is None:
            raise SystemExit(f"error: {skill['name']} has a source outside every family")
        rows.append((family, skill))
    return sorted(rows, key=lambda row: (families.index(row[0]), row[1]["name"].casefold()))


def render_catalog(root: Path, manifest: dict) -> str:
    lines = [
        "# Skill catalog",
        "",
        f"kstack ships {len(manifest['skills'])} skills. This file is generated by "
        "`python3 scripts/kstack.py render` from `kstack.json` and each `SKILL.md`.",
        "Each vendored folder has an `UPSTREAM.md` with its source commit and licence.",
        "",
        "| Skill | Family | What it does | Source | Licence |",
        "|---|---|---|---|---|",
    ]
    for family, skill in ordered(manifest):
        license_id = "kstack" if skill["source"] == manifest["repository"] else skill.get("license", "?")
        lines.append(
            f"| {skill_link(root, skill)} | {family['name']} | {describe(root, skill, manifest)} "
            f"| {source_link(skill, manifest)} | {license_id} |"
        )
    return "\n".join(lines) + "\n"


def render_readme_table(root: Path, manifest: dict) -> str:
    lines = ["| Skill | Purpose | Source |", "|---|---|---|"]
    for family, skill in ordered(manifest):
        purpose = first_sentence(describe(root, skill, manifest))
        lines.append(f"| {skill_link(root, skill)} | {purpose} | {family['name']} |")
    return "\n".join(lines)


def render(root: Path) -> int:
    manifest = load_manifest(root)
    (root / "CATALOG.md").write_text(render_catalog(root, manifest), encoding="utf-8")
    readme_path = root / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    if TABLE_START not in readme or TABLE_END not in readme:
        raise SystemExit("error: README.md has no kstack skill table markers")
    head, rest = readme.split(TABLE_START, 1)
    _, tail = rest.split(TABLE_END, 1)
    table = render_readme_table(root, manifest)
    readme_path.write_text(f"{head}{TABLE_START}\n{table}\n{TABLE_END}{tail}", encoding="utf-8")
    return len(manifest["skills"])


# CLI ------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="repository root (default: this repo)")
    commands = parser.add_subparsers(dest="command", required=True)
    select_parser = commands.add_parser("select", help="rebuild the skill list from a lock file")
    select_parser.add_argument("--lock", type=Path, default=Path("~/.agents/.skill-lock.json"))
    vendor_parser = commands.add_parser("vendor", help="copy upstream skills into skills/")
    vendor_parser.add_argument(
        "--upstream-root",
        type=Path,
        required=True,
        help="directory of upstream checkouts named owner__repo; missing ones are cloned",
    )
    commands.add_parser("render", help="write CATALOG.md and the README table")
    args = parser.parse_args(argv)
    root = args.root.resolve()

    if args.command == "select":
        names = select(root, args.lock.expanduser())
        print(f"Selected {len(names)} skills.")
    elif args.command == "vendor":
        copied, link_only, removed = vendor(root, args.upstream_root.expanduser())
        print(f"Vendored {copied} skills. Link-only: {', '.join(link_only) or 'none'}. Removed {len(removed)} folders.")
    else:
        count = render(root)
        print(f"Rendered {count} skills.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
