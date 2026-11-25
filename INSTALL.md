# Install and update kstack

## Install

Install every kstack skill for all your agents:

```bash
npx skills add karanmrn/kstack
```

Install one skill. Use the folder name from [CATALOG.md](CATALOG.md):

```bash
npx skills add karanmrn/kstack --skill <name>
```

Add `-g` to install for your user instead of the current project. Add `-y` to skip the prompts.

For an upstream skill, you can also install it from its own repository. Then updates come straight from the author:

```bash
npx skills add backnotprop/pstack --skill architect
```

`kun` is link-only. Its repository has no licence, so kstack does not copy it. Install it from upstream:

```bash
npx skills add kunchenguid/kun --skill kun
```

## Optional skills

The core pack remains the default.
The optional installer adds skills from pinned upstream commits to `~/.agents/skills`.
It leaves existing skill folders unchanged.
Each new folder includes an `UPSTREAM.md` with its source commit and upstream licence notice.
It requires Python 3, Git and network access.

```bash
python3 scripts/install.py --optional          # all optional families
python3 scripts/install.py --optional design   # one family
python3 scripts/install.py --optional research
python3 scripts/install.py --optional workflows
```

Run the script from a checkout of kstack.
Use `npx skills add karanmrn/kstack` to install the core pack.
See [CATALOG.md](CATALOG.md) for the optional skills, sources and licences.

## Update

```bash
npx skills update
```

Then restart your agent so it loads the new skill files.

## Maintain this repository

`kstack.json` is the single source of truth. It lists the accepted upstream families and every skill that kstack ships. `scripts/kstack.py` does the rest.

1. Select the in-family skills from your installed-skill lock. This keeps kstack's own skills:

   ```bash
   python3 scripts/kstack.py select --lock ~/.agents/.skill-lock.json
   ```

2. Copy each upstream skill from its checkout's current `HEAD`. The script clones missing repositories into the directory that you give. It does not fetch existing checkouts or use the manifest's recorded commits. It writes `UPSTREAM.md` and skips skills without a redistributable licence. It also removes each folder in `skills/` that `kstack.json` does not list.

   The command uses one checkout per source. It cannot reproduce different revisions from the same source in one pass.
   Before a bulk refresh, check the [historical revision retained in this refresh](docs/refresh-2026-11-16.md#restored-approved-skill).
   An upstream checkout that lacks a listed skill causes `vendor` to stop after it deletes that skill's existing folder.
   Preserve historical entries and their `UPSTREAM.md` files separately when refreshing the remaining skills.
   Before refreshing, inspect each skill's `UPSTREAM.md` for kstack adaptations.
   The vendor command overwrites these adaptations. Restore them before rendering the catalogue.

   ```bash
   python3 scripts/kstack.py vendor --upstream-root /tmp/kstack-upstream
   ```

3. Write `CATALOG.md` and the README skill table:

   ```bash
   python3 scripts/kstack.py render
   ```

4. Run the tests:

   ```bash
   python3 -m unittest discover -s tests
   ```

To add a skill of your own, create `skills/<name>/SKILL.md`, add an entry with `"source": "karanmrn/kstack"` to `kstack.json`, and run `render`.
To accept a new upstream family, add it to `families` in `kstack.json`, then run all four steps.
