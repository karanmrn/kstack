---
name: audit-agent-worktrees
description: Audit old git worktrees and clones that coding agents left behind, and delete only the ones whose work is safe. Use before you remove agent worktrees, prune worktree pools, or reclaim disk space from old agent checkouts.
---

# Audit agent worktrees

Agents leave many worktrees behind. Some hold the only copy of real work. This skill sorts each worktree into **safe to delete**, **keep** or **ask**, and deletes only the safe ones.

Unlanded work is work that is not on the default branch and not on a pushed branch. Never delete unlanded work without a human's explicit approval for that worktree.

## 1. Make the inventory

For each repository, list every worktree:

```bash
git -C <repo> fetch --all --prune
git -C <repo> worktree list --porcelain
```

Also find loose clones and copies outside `git worktree list`, for example under the agent tool's worktree directory. Record for each one: path, branch, HEAD commit, last change time, size (`du -sh`).

Skip any worktree that a running agent uses. Check for live processes with `lsof +D <path>` or the agent tool's own status command. A slot that looks unused is not proof that it is free.

Done when every worktree has one inventory row.

## 2. Classify each worktree

Run these checks inside the worktree. Each check gives evidence. Write the evidence into the row.

| Check | Command | Unlanded work if |
|---|---|---|
| Uncommitted changes | `git status --porcelain --untracked-files=all` | output is not empty (ignore build output that `.gitignore` covers) |
| Stashes | `git stash list` | a stash entry belongs to this branch |
| Commits not on the default branch | `git log --oneline origin/<default>..HEAD` | the list is not empty |
| Commits not pushed | `git log --oneline @{upstream}..HEAD` | the list is not empty, or the branch has no upstream |
| Squash-merged | `gh pr list --state merged --head <branch>` | no merged PR includes these commits |
| Open PR | `gh pr list --state open --head <branch>` | an open PR exists: keep the worktree |

A squash merge or rebase merge changes commit hashes. So `origin/<default>..HEAD` can list commits that are already landed. If a merged PR exists for the branch, compare its final diff with the branch tip (`git diff <merge-commit>^..<merge-commit>` against `git diff origin/<default>...HEAD`) before you call the work landed.

Sort each row:

- **Safe to delete**: clean tree, no own stash, and every commit is on the default branch, or on a pushed branch, or in a merged PR.
- **Keep**: an open PR, a live process, or recent activity.
- **Ask**: any unlanded work. Show the human the branch, the commits and the diff summary.

## 3. Back up, then delete

1. Push any branch whose commits exist nowhere else: `git push origin <branch>`. If you cannot push, make a bundle: `git bundle create <backup-dir>/<branch>.bundle origin/<default>..<branch>`.
2. Remove each safe worktree with its tool: `git -C <repo> worktree remove <path>`. Use the agent tool's own remove command when it manages a pool. Never use `--force` on a worktree that has unlanded work.
3. Run `git -C <repo> worktree prune` to clear stale records.
4. Record what you removed, the space it freed and every backup path.

Done when every row is deleted with evidence, kept with a reason, or waiting for a human answer.
