---
name: mac-disk-cleanup
description: Free disk space on a developer Mac safely. Measure first, back up what cannot be rebuilt, then delete. Use when a Mac is low on disk space, or when you clean caches, build output, simulators, containers or old agent worktrees.
---

# Mac disk clean-up

Order: **measure, classify, back up, delete, measure again**. Delete only what you can rebuild or what a human approved.

## 1. Measure

```bash
df -h /System/Volumes/Data
du -xhd1 ~ 2>/dev/null | sort -hr | head -20
du -xhd1 ~/Library 2>/dev/null | sort -hr | head -20
```

Go down into the largest folders until each large item has a name and a size. Record the free space now. You compare against it at the end.

## 2. Classify

| Class | Examples | Action |
|---|---|---|
| Rebuildable cache | `~/Library/Caches/*`, `~/.npm/_cacache`, `~/.cache/*`, `~/Library/Caches/Homebrew`, `~/.gradle/caches`, `~/.cargo/registry/cache` | Delete with the tool's own command when it has one. |
| Build output | `node_modules`, `target`, `.next`, `dist`, `build`, `DerivedData` in projects that you do not use now | Delete. The project rebuilds them. |
| Tool data | Docker images and volumes, Xcode simulators and device support, old SDKs, Ollama or other model weights | Use the tool's command. Volumes can hold real data: ask first. |
| Agent work | Old git worktrees and clones | Use [`audit-agent-worktrees`](../audit-agent-worktrees/SKILL.md). Never delete them as plain folders. |
| User data | Documents, Desktop, Downloads, Photos, Mail, app data, databases, `.env` files, keys | Never delete. Report the size and let the human decide. |

Prefer the tool's own clean-up command. It knows what is safe:

```bash
npm cache clean --force
brew cleanup --prune=all
docker system df              # look first
docker image prune -a         # images can be pulled again
xcrun simctl delete unavailable
pnpm store prune
uv cache clean
go clean -cache
```

Do not run `docker volume prune` or `docker system prune --volumes` without approval. Volumes can hold the only copy of a database.

## 3. Back up

Before you delete anything that is not a rebuildable cache, make a copy or confirm that one exists. Examples: a git remote that holds every commit, a Time Machine snapshot, or an archive on another disk.

```bash
tmutil listlocalsnapshots /
tar -czf <backup-dir>/<name>.tar.gz -C <parent> <folder>
```

A backup on the same disk does not free space. Put it on another disk, or confirm the remote copy instead.

## 4. Delete

- Delete by exact path. Never use a wildcard over a home folder, and never `rm -rf` a path built from a variable that can be empty.
- Move user-visible files to the Trash (`trash <path>` or Finder), so the human can restore them.
- Close the app that owns a cache before you delete the cache.
- Empty the Trash only when the human approves.

## 5. Measure again

Run `df -h /System/Volumes/Data` again. Report the free space before and after, each item that you removed with its size, each backup path, and each large item that you left for the human.

APFS local snapshots can hold deleted data. If free space did not change, run `tmutil listlocalsnapshots /` and tell the human. Do not delete snapshots without approval.
