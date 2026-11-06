---
name: supervise-agent-fleet
description: Supervise several coding agents that work in parallel and ship through pull requests. Use when you dispatch tasks to agents, watch their progress, review their PRs, or land a batch of PRs as a merge wave.
---

# Supervise an agent fleet

You are the supervisor. Agents do the project work. You dispatch, watch, review and land it. One agent owns one task, one branch, one worktree and one PR.

## 1. Dispatch

For each task, write a brief that is complete by itself. The agent sees only the brief.

- The goal in one sentence, and the reason for it.
- Scope: what is in and what is out.
- The isolation: a fresh worktree on a new branch from the current default branch.
- Done: the exact evidence that proves the task, such as a passing test, a measured number or a screenshot.
- Ship: push the branch and open a ready PR. The agent never merges.
- Report: one status line for each phase change, and `blocked`, `needs-decision` or `done` with the PR URL.

Dispatch only tasks that touch different files, or put one task after the other. Two agents that edit one file make a merge conflict that neither agent can see.

Done when every task has a brief, a worktree and a running agent.

## 2. Watch

Read status lines. Do not poll every agent on a timer.

| Signal | Action |
|---|---|
| `working` | Leave the agent alone. |
| `needs-decision` | Decide if the brief gives you the authority. If not, ask the human. Reply with the decision and record that it is resolved. |
| `blocked` | Read the evidence. Fix the cause or give the missing access. Do not let the agent retry the same failure. |
| No signal for a long time | Look at the agent's terminal. If it is stuck, send one direct steer. If that fails, stop it and dispatch again with a better brief. |
| `done` | Go to step 3. |

## 3. Review each PR

Read the PR from the forge, not from the agent's summary.

1. Confirm the PR is not a draft and its branch holds the agent's latest commit.
2. Read the full diff. Compare it with the brief: missing scope, extra scope, removed tests, weaker checks.
3. Confirm CI is green. A red or flaky check is a finding, also when the PR did not cause it.
4. Check the proof in the PR body: before and after evidence that a reviewer can repeat.
5. Send each finding back to the same agent as one concrete instruction. Review again after each push.

A PR is ready when the diff matches the brief, CI is green and no review comment is open.

## 4. Land a merge wave

A merge wave lands a batch of ready PRs in a safe order. Merge only with the human's explicit approval for this wave.

1. Order the PRs: shared foundations first, then the PRs that depend on them, then independent PRs.
2. Merge one PR. Then update each next PR on the new default branch and wait for its CI to pass again.
3. If a rebase has a conflict, send it back to the agent that owns the PR. Do not resolve conflicts in the supervisor's checkout.
4. After the wave, pull the default branch and run the full test suite once.

The wave is done when every PR in it is merged or returned with a reason, and the default branch is green.

## 5. Clean up

Remove a worktree only after its work is merged, or its unmerged commits exist on a pushed branch. Use [`audit-agent-worktrees`](../audit-agent-worktrees/SKILL.md) for old worktrees.

## Rules

- The supervisor never edits project files. Send the change to an agent.
- One writer for each branch. Never let two agents push to the same branch.
- Report outcomes as they are. A failed task is reported as failed, with its evidence.
