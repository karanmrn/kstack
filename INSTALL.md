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

2. Copy each upstream skill at its upstream HEAD. The script clones missing repositories into the directory that you give, writes `UPSTREAM.md`, skips skills without a redistributable licence, and removes every folder in `skills/` that `kstack.json` does not list:

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
