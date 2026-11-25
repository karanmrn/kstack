---
name: hill-climb
description: Use when the user asks for hill climb or an iterative four-model review against a measurable target.
---

# Hill climb

Improve one scoped outcome through measured experiments and independent reviews.
The driver owns the scope, measurements, decisions, and edits.
Reviewers are read-only and must not edit the checkout.
Do not start this skill if the user's instructions prohibit delegation.

## Set the experiment

1. Trace the relevant behaviour and choose a realistic workload.
2. Define one measurable metric, its direction, a target, and a repeatable command.
3. Choose a regression gate and a maximum round count before the first round.
4. Agree the minimum completed round count with the user before experimentation. Propose 2 when the user supplies no minimum.
5. Use the user's target and maximum round count when supplied, otherwise choose and report them.
6. Ensure both round limits are positive integers and the minimum does not exceed the maximum.
7. Check that the measurement distinguishes relevant workloads and records errors and work completed.
8. Freeze the measurement command and workload, then record the baseline and a passing regression gate.
9. Keep a decision log outside tracked files, with hypothesis, change, before, after, delta, gate, and verdict.

If the measurement cannot reproduce the problem or distinguish relevant cases, repair it before freezing it.
If no meaningful measurement or regression gate can be established, report the blocker instead of claiming improvement.
Use repeated samples when the measurement is noisy and state the noise threshold.
Do not change the frozen measure or lower the target to manufacture success.

## Review round

Launch exactly these four independent reviewers in parallel at high effort on the same unchanged checkout:

| Reviewer | Harness | Model |
| --- | --- | --- |
| GPT Sol 6.2 | Codex | `gpt-6.2-sol` |
| GPT Astra 6.2 | Codex | `gpt-6.2-astra` |
| Claude Fable 5.2 | Claude Code | `claude-fable-5-2` |
| Claude Opus 5.5 | Claude Code | `claude-opus-5-5` |

Give each reviewer the same request, scope, relevant context, and current diff.
Ask for independent findings with severity, evidence, and a score out of 10.
Ask reviewers to flag uncertainty and avoid recommendations outside the agreed scope.
Do not share other reviewers' findings until the round is complete.
Do not edit the checkout until every reviewer has finished.

From Claude Code, Codex, or a shell, start these commands concurrently from the target checkout.
Set `PROMPT` to the complete review request.
Set `REVIEW_OUTPUT_DIR` to the absolute path of an existing writable directory outside the checkout.
The Claude commands restrict built-in tools to read-only inspection.
The Codex sandbox restricts filesystem writes.

```bash
codex exec -m gpt-6.2-sol -c 'model_reasoning_effort="high"' -s read-only "$PROMPT" > "$REVIEW_OUTPUT_DIR/sol.out" & sol_pid=$!
codex exec -m gpt-6.2-astra -c 'model_reasoning_effort="high"' -s read-only "$PROMPT" > "$REVIEW_OUTPUT_DIR/astra.out" & astra_pid=$!
claude -p --model claude-fable-5-2 --effort high --tools 'Read,Grep,Glob' -- "$PROMPT" > "$REVIEW_OUTPUT_DIR/fable.out" & fable_pid=$!
claude -p --model claude-opus-5-5 --effort high --tools 'Read,Grep,Glob' -- "$PROMPT" > "$REVIEW_OUTPUT_DIR/opus.out" & opus_pid=$!
for pid in "$sol_pid" "$astra_pid" "$fable_pid" "$opus_pid"; do
  if wait "$pid"; then printf "%s: success\n" "$pid"; else printf "%s: failed\n" "$pid"; fi
done
```

Capture each process exit status individually, along with its output, when running these commands.
Check that each response came from the requested model when the harness exposes that evidence.
If a model is unavailable, fails, or returns no usable review, report it and stop the round.
Never substitute another model or invent a score.
If a reviewer omits its score, record `no score` and treat the round as incomplete.

## Improve and repeat

Verify each finding against the code and relevant behaviour.
Record rejected findings and their reasons.
Fix verified findings within scope, one hypothesis per iteration.
Measure each change with the frozen command and run the regression gate.
Keep a change only when it improves the metric beyond noise and the gate passes.
A correctness fix may also be kept when the metric holds and the gate passes.
Otherwise revert only that iteration's change and record the result.
Never discard pre-existing or unrelated work.
Record every iteration in the decision log and do not stack unmeasured changes.

After the fixes, start a fresh review round on the updated checkout.
Record each reviewer's score and the count of new findings by severity for every round.
Count a review round as completed only when all four reviewers return usable reviews with scores.
A run succeeds only when all these conditions hold:

- The completed review round count reaches the agreed minimum.
- The metric meets its target.
- No new verified medium-or-higher findings remain.
- All four scores in the latest completed round meet the target score.

Define the target score before the first round, defaulting to 9/10 when the user gives none.
If a plateau occurs, inspect the source again and try a different class of hypothesis before stopping.
Stop when the run succeeds, the maximum round count is reached, or only marginal ideas remain.
Report an incomplete result and each unmet condition if the run stops before the success predicate is met.
Do not expand scope merely to increase scores.
Do not claim consensus or success when a reviewer is missing or the predicate is unmet.

## Report

Report the frozen metric, target, baseline, final result, regression gate, decision log, and kept and reverted iterations.
Include outstanding findings, disagreements, missing reviewers, and the reason for stopping.
Report the agreed minimum, the maximum round count, and the completed review round count.
If a pull request exists, add a `Council review` section to its description, subject to the user's publishing authority.
Otherwise include the same table in the final report.
Include each round's new finding counts by severity alongside the scores.

| Delegate | Round 1 | Round 2 |
| --- | --- | --- |
| GPT Sol 6.2 | score/10 | score/10 |
| GPT Astra 6.2 | score/10 | score/10 |
| Claude Fable 5.2 | score/10 | score/10 |
| Claude Opus 5.5 | score/10 | score/10 |

This skill adapts the review structure from [t3dotgg/tstack's council](https://github.com/t3dotgg/tstack/tree/11e37a74d0a6868c121cd0910ab2b3bd9873b92a/skills/council) and the experiment loop from [poteto's hillclimb playbook](https://github.com/backnotprop/pstack/blob/2a5621683e2bbb274efea8b52dd69f5beef6c25f/skills/poteto-mode/playbooks/hillclimb.md).
