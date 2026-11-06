---
name: delegate-to-model
description: Hand a task from the current agent to another model on your subscriptions - Codex CLI, Cursor agent CLI, or any OpenRouter model - and check the result before you use it. Use when you want a second opinion, a different model's strength, a parallel attempt, or to save quota on the current model.
---

# Delegate to another model

You stay the owner of the task. The other model is a worker. You write the handoff, run the worker, and check its result like code from a stranger.

## 1. Choose the worker

| Need | Worker | Why |
|---|---|---|
| Code change or deep bug hunt in a repo | Codex CLI (`codex exec`) | Runs tools and edits files in a sandbox. Has a built-in review command. |
| Code change with a model Cursor serves | Cursor agent CLI (`cursor-agent -p`) | Many vendor models behind one login. Has read-only plan and ask modes. |
| One answer, review or rewrite from a named model | OpenRouter | Any listed model through one API key. No file access. |

Check quota before a long run if you have a quota tool. Run `<cli> --help` once when a flag below fails. CLI flags change between versions.

## 2. Write the handoff

The worker sees only the handoff. Write it to a file, for example `handoff.md`:

```markdown
## Goal
<one sentence, and why it matters>

## Context
<repo path, branch, the files that matter, what you already ruled out>

## Task
<the exact work; what is in scope and what is out>

## Constraints
<read-only or allowed to edit; no commits, no pushes, no new dependencies unless stated>

## Done when
<a check the worker can run, e.g. "`npm test -- parser` passes">

## Report
<the shape of the answer: a diff summary, findings with file:line, or a JSON object>
```

Remove secrets, tokens and private data from the handoff. The text goes to another vendor.

## 3. Run the worker

Give a write-capable worker its own git worktree, so its edits cannot mix with yours:

```bash
git worktree add ../task-codex -b delegate/codex
```

Codex CLI:

```bash
codex exec -C ../task-codex -s workspace-write -m <model> \
  -o result.md - < handoff.md            # edits allowed
codex exec -C <repo> -s read-only -o result.md - < handoff.md   # analysis only
codex exec review                         # review the current repo changes
```

Cursor agent CLI (`agent` is the same binary):

```bash
cursor-agent --list-models
cursor-agent -p --workspace ../task-cursor --model <model> \
  --output-format text "$(cat handoff.md)" > result.md
cursor-agent -p --mode plan --workspace <repo> "$(cat handoff.md)" > result.md   # read-only
```

OpenRouter, through the CLI of the [`openrouter`](../openrouter/SKILL.md) skill. The reply goes to `result.md`, and tokens and cost go to stderr:

```bash
openrouter ask <vendor/model> - < handoff.md > result.md
```

`opencode run -m openrouter/<vendor/model> "$(cat handoff.md)"` does the same through OpenCode when it is set up.

Run long jobs in the background and wait for them to exit. Do not poll every few seconds.

## 4. Check the result

The worker's report is a claim, not evidence.

1. Read `result.md` in full. Check that it answers the handoff, in the shape you asked for.
2. For edits, read the diff yourself: `git -C ../task-codex diff`. Look for scope creep, deleted tests and weaker checks.
3. Run the "Done when" check yourself. Run the repo's tests and lint.
4. Check each factual claim and each `file:line` against the code.
5. Take the change into your branch only after these checks pass: cherry-pick or apply the diff, then remove the worker's worktree.

If the result fails, send one focused follow-up with the failure output (`codex exec resume --last`, or `cursor-agent --resume <chat-id>`). After two failed rounds, do the task yourself or choose another worker.

Report which model did which part, and what you verified.
