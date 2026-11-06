# kstack

kstack is a small, curated set of agent skills for running a dark software factory: agents that plan, build, review and ship code with little human help.
It holds only skills from five upstream families: [Addy Osmani's agent skills](https://github.com/addyosmani/agent-skills), [pstack](https://github.com/backnotprop/pstack), [tstack](https://github.com/t3dotgg/tstack), [Matt Pocock's skills](https://github.com/mattpocock/skills) and [Kun Chen's tools](https://github.com/kunchenguid).
It adds four skills of its own, written from real fleet workflows.
Each copied skill keeps an `UPSTREAM.md` with its source commit and licence. Star and follow the upstream repositories for the newest versions.

```bash
npx skills add karanmrn/kstack
```

See [INSTALL.md](INSTALL.md) to install one skill or to refresh the set, and [CATALOG.md](CATALOG.md) for full descriptions and licences.

## Skills

<!-- kstack:skills:start -->
| Skill | Purpose | Source |
|---|---|---|
| [`api-and-interface-design`](skills/api-and-interface-design/) | Guides stable API and interface design. | Addy Osmani |
| [`browser-testing-with-devtools`](skills/browser-testing-with-devtools/) | Tests in real browsers via Chrome DevTools MCP. | Addy Osmani |
| [`ci-cd-and-automation`](skills/ci-cd-and-automation/) | Automates CI/CD pipeline setup. | Addy Osmani |
| [`code-review-and-quality`](skills/code-review-and-quality/) | Conducts multi-axis code review. | Addy Osmani |
| [`code-simplification`](skills/code-simplification/) | Simplifies code for clarity. | Addy Osmani |
| [`constraint-driven-development`](skills/constraint-driven-development/) | Establishes a project's quality bar as a written contract and stops agents quietly lowering it. | Addy Osmani |
| [`context-engineering`](skills/context-engineering/) | Optimizes agent context setup. | Addy Osmani |
| [`debugging-and-error-recovery`](skills/debugging-and-error-recovery/) | Guides systematic root-cause debugging. | Addy Osmani |
| [`deprecation-and-migration`](skills/deprecation-and-migration/) | Manages deprecation and migration. | Addy Osmani |
| [`documentation-and-adrs`](skills/documentation-and-adrs/) | Records decisions and documentation. | Addy Osmani |
| [`doubt-driven-development`](skills/doubt-driven-development/) | Subjects every non-trivial decision to a fresh-context adversarial review before it stands. | Addy Osmani |
| [`frontend-ui-engineering`](skills/frontend-ui-engineering/) | Builds production-quality, accessible, responsive user-facing UIs. | Addy Osmani |
| [`git-workflow-and-versioning`](skills/git-workflow-and-versioning/) | Structures git workflow practices. | Addy Osmani |
| [`idea-refine`](skills/idea-refine/) | Refines raw ideas into sharp, actionable concepts through structured divergent and convergent thinking. | Addy Osmani |
| [`incremental-implementation`](skills/incremental-implementation/) | Delivers changes incrementally in thin, verifiable slices. | Addy Osmani |
| [`interview-me`](skills/interview-me/) | Extracts what the user actually wants instead of what they think they should want. | Addy Osmani |
| [`observability-and-instrumentation`](skills/observability-and-instrumentation/) | Instruments code so production behavior is visible and diagnosable. | Addy Osmani |
| [`performance-optimization`](skills/performance-optimization/) | Optimizes application performance across frontend, backend, queries, and databases. | Addy Osmani |
| [`planning-and-task-breakdown`](skills/planning-and-task-breakdown/) | Breaks work into ordered tasks. | Addy Osmani |
| [`security-and-hardening`](skills/security-and-hardening/) | Hardens code against vulnerabilities. | Addy Osmani |
| [`shipping-and-launch`](skills/shipping-and-launch/) | Prepares production launches. | Addy Osmani |
| [`source-driven-development`](skills/source-driven-development/) | Grounds every implementation decision in official documentation. | Addy Osmani |
| [`spec-driven-development`](skills/spec-driven-development/) | Creates specs before coding. | Addy Osmani |
| [`test-driven-development`](skills/test-driven-development/) | Drives development with tests using the red-green-refactor loop. | Addy Osmani |
| [`using-agent-skills`](skills/using-agent-skills/) | Discovers and invokes agent skills. | Addy Osmani |
| [`architect`](skills/architect/) | Sketch types, signatures, and module structure before code, then stay in the loop while implementation fills in. | pstack |
| [`arena`](skills/arena/) | Spawn N parallel candidates at the same task, pick a base, graft the strongest parts of the losers into it. | pstack |
| [`automate-me`](skills/automate-me/) | Use for "automate me", "create/update/refresh my -mode skill", "turn/capture my preferences or working style into a skill", or wanting... | pstack |
| [`benchmark-checklist`](skills/benchmark-checklist/) | Vet a perf measurement (limiter, tuning, limits, errors, repeatability, relevance, and whether the work happened) before you report or... | pstack |
| [`blast-radius`](skills/blast-radius/) | Find what a change could break somewhere else before it ships, beyond the diff, and prove the one fact it's safe because of by running... | pstack |
| [`bro`](skills/bro/) | Restate the last message in plain human language, with no jargon. | pstack |
| [`correct`](skills/correct/) | Find the mistakes agents keep repeating in this repo and make each one impossible. | pstack |
| [`create-formal-verification-skill`](skills/create-formal-verification-skill/) | Generate a project-local skill that formally verifies the code where a bug costs the most and tests reach the least, in any language,... | pstack |
| [`create-verification-skill`](skills/create-verification-skill/) | Generate a project-local verification skill that drives your app the way a user does - any language, framework, or platform. | pstack |
| [`figure-it-out`](skills/figure-it-out/) | Design an auditable playbook when no narrower one fits: a large migration, an ambitious multi-part change, or work a human reviews after... | pstack |
| [`how`](skills/how/) | Use for "how does X work", code walkthroughs before changing something, and placement / ownership / layering questions ("where should... | pstack |
| [`in-your-own-words`](skills/in-your-own-words/) | Restate in your own words what you think the user's goals are and what problem they're trying to solve. | pstack |
| [`interrogate`](skills/interrogate/) | Use for "interrogate", "adversarial review", "multi-model review", "challenge this", "stress test this code", "find blind spots", or... | pstack |
| [`ketchup`](skills/ketchup/) | Catch the user up on what changed in this chat since their last message, in plain words and small visuals. | pstack |
| [`ketchup-video`](skills/ketchup-video/) | Catch the user up like /ketchup, with a short subtitled video of slides for what happened and the waiting calls as text under it. | pstack |
| [`maintain-formal-verification-skill`](skills/maintain-formal-verification-skill/) | Bring a project's formal verification back in line with the code after the code changes: find the commits that touched verified code,... | pstack |
| [`maintain-verification-skill`](skills/maintain-verification-skill/) | Periodic pass that keeps a project's verification skill and feature map honest: parallel source readers per feature, one live session... | pstack |
| [`make-bot-ui`](skills/make-bot-ui/) | Use when building a custom UI (page, dashboard, buttons) that should wake a Grok Bot over a webhook, when the user must provide a... | pstack |
| [`no-comments`](skills/no-comments/) | Spawn Comment Sicko, fix accepted findings, and offer encodings for claimed constraints. | pstack |
| [`poteto-help`](skills/poteto-help/) | Guides users through pstack setup, /poteto-mode, and picking the skill, playbook, or principle for a task. | pstack |
| [`poteto-mode`](skills/poteto-mode/) | poteto's agent style for concise, detailed responses, deliberate subagents, unslopped prose, simple code, and verified work. | pstack |
| [`principle-attack-the-premise`](skills/principle-attack-the-premise/) | Apply when two or more fixes that share one premise have failed the same gate. | pstack |
| [`principle-boundary-discipline`](skills/principle-boundary-discipline/) | Apply when wiring validation, error handling, or framework adapters. | pstack |
| [`principle-build-the-lever`](skills/principle-build-the-lever/) | Apply to any non-trivial work, not just bulk work: edits, migrations, analyses, checks. | pstack |
| [`principle-encode-lessons-in-structure`](skills/principle-encode-lessons-in-structure/) | Apply when you catch yourself writing the same instruction a second time, or notice a recurring correction. | pstack |
| [`principle-exhaust-the-design-space`](skills/principle-exhaust-the-design-space/) | Apply when facing a novel UI interaction or architectural decision with no precedent in the codebase. | pstack |
| [`principle-experience-first`](skills/principle-experience-first/) | Apply when product, UX, or feature-scope tradeoffs come up. | pstack |
| [`principle-explain-the-number`](skills/principle-explain-the-number/) | Apply before you measure, and before you trust, report, or act on a number you measured: a speedup, a regression, a throughput, a... | pstack |
| [`principle-fix-root-causes`](skills/principle-fix-root-causes/) | Apply when debugging. | pstack |
| [`principle-foundational-thinking`](skills/principle-foundational-thinking/) | Apply before writing logic: choosing core types and data structures, sequencing scaffold-vs-feature work, asking what concurrent actors... | pstack |
| [`principle-guard-the-context-window`](skills/principle-guard-the-context-window/) | Apply when context is filling up: large outputs, long files, repeated reads, fan-out planning. | pstack |
| [`principle-laziness-protocol`](skills/principle-laziness-protocol/) | Apply when refactoring, evaluating diff size, or tempted to add abstractions, layers, or signal threading. | pstack |
| [`principle-make-operations-idempotent`](skills/principle-make-operations-idempotent/) | Apply when designing commands, lifecycle steps, or processing loops that run amid crashes, restarts, and retries. | pstack |
| [`principle-migrate-callers-then-delete-legacy-apis`](skills/principle-migrate-callers-then-delete-legacy-apis/) | Apply when introducing a new internal API while old callers still exist. | pstack |
| [`principle-minimize-reader-load`](skills/principle-minimize-reader-load/) | Apply when reviewing or shaping code that's hard to trace. | pstack |
| [`principle-model-the-domain`](skills/principle-model-the-domain/) | Apply when writing stateful logic, or when code branches a lot or repeats a shape assumption across files. | pstack |
| [`principle-never-block-on-the-human`](skills/principle-never-block-on-the-human/) | Apply when tempted to ask 'should I do X?' on reversible work. | pstack |
| [`principle-outcome-oriented-execution`](skills/principle-outcome-oriented-execution/) | Apply during planned rewrites and migrations with explicit phase boundaries. | pstack |
| [`principle-prove-it-works`](skills/principle-prove-it-works/) | Apply after completing a task, before declaring done. | pstack |
| [`principle-redesign-from-first-principles`](skills/principle-redesign-from-first-principles/) | Apply when integrating a new requirement into an existing design. | pstack |
| [`principle-separate-before-serializing-shared-state`](skills/principle-separate-before-serializing-shared-state/) | Apply when concurrent actors might write to the same file, branch, key, or state object. | pstack |
| [`principle-sequence-verifiable-units`](skills/principle-sequence-verifiable-units/) | Apply to multi-step work (sweeps, migrations, runs of similar edits) and to how you stack commits and PRs. | pstack |
| [`principle-subtract-before-you-add`](skills/principle-subtract-before-you-add/) | Apply when sequencing an addition, refactor, or rewrite. | pstack |
| [`principle-test-behavior-not-implementation`](skills/principle-test-behavior-not-implementation/) | Apply when you write, change, or keep a test. | pstack |
| [`principle-type-system-discipline`](skills/principle-type-system-discipline/) | Apply when designing types, reviewing a function signature, or writing code in any statically-typed language. | pstack |
| [`recall`](skills/recall/) | Reconstruct your recent working context from your own chat history, live state, and the shared record (user reports, prior fixes,... | pstack |
| [`reflect`](skills/reflect/) | Spawn three parallel review subagents over the active transcript, surface learnings, and route each to a concrete edit on an existing skill. | pstack |
| [`setup-pstack`](skills/setup-pstack/) | Configure which models pstack uses per role and at what reasoning budget. | pstack |
| [`sharpen`](skills/sharpen/) | Make a task deeper, not bigger, then rewrite the prompt. | pstack |
| [`show-me-your-work`](skills/show-me-your-work/) | Keep a reviewable decision trail for long-running or unattended work: a TSV log with one row per decision (what, why, evidence, result). | pstack |
| [`statechart`](skills/statechart/) | Check a TLA+ model of a system that moves between states, such as a product flow, a protocol, or a service, and draw it as a Mermaid... | pstack |
| [`swarm`](skills/swarm/) | Fan out N parallel workers, drain them, and return one report. | pstack |
| [`tdd`](skills/tdd/) | Use only when the user explicitly asks for TDD, a failing test, or a regression test, OR when the bug has an obvious cheap local test... | pstack |
| [`teach`](skills/teach/) | Explain a body of work plainly so a person actually understands it. | pstack |
| [`technical-writing`](skills/technical-writing/) | Layered technical-writing standard: Diátaxis structure, Google developer style sentences, STE instruction rules, Global English syntax. | pstack |
| [`typescript-best-practices`](skills/typescript-best-practices/) | TypeScript best practices. | pstack |
| [`unslop`](skills/unslop/) | Cut AI tells from any writing. | pstack |
| [`why`](skills/why/) | Use for 'why does X work this way', 'why we picked Y', design rationale, regressions, postmortems, or data-backed thresholds. | pstack |
| [`babysit-pr`](skills/babysit-pr/) | Monitor a pull request through review and CI. | tstack |
| [`council`](skills/council/) | Trigger this if the user says 'council'. | tstack |
| [`file-pr`](skills/file-pr/) | File a concise pull request. | tstack |
| [`full-send`](skills/full-send/) | Trigger this if the user says 'full send'. | tstack |
| [`full-stop`](skills/full-stop/) | Trigger this if the user says 'full stop', even as a closing "Full stop." that reads like emphasis. | tstack |
| [`leaving-pr-comments`](skills/leaving-pr-comments/) | Use whenever leaving comments on GitHub. | tstack |
| [`modernize`](skills/modernize/) | For getting old prs up to date. | tstack |
| [`sol-loop`](skills/sol-loop/) | Use when the user says "sol loop". | tstack |
| [`takeover`](skills/takeover/) | Take over existing work. | tstack |
| [`ask-matt`](skills/ask-matt/) | Ask which skill or flow fits your situation. | Matt Pocock |
| [`chief-of-staff`](skills/chief-of-staff/) | Pursue a long-running goal in a single session by co-ordinating subagents. | Matt Pocock |
| [`claude-handoff`](skills/claude-handoff/) | Hand the current conversation off to a fresh background agent that picks up the work immediately. | Matt Pocock |
| [`code-review`](skills/code-review/) | Review the changes since a fixed point (commit, branch, tag, or merge-base) along two axes: Standards (does the code follow this repo's... | Matt Pocock |
| [`codebase-design`](skills/codebase-design/) | Shared vocabulary for designing deep modules. | Matt Pocock |
| [`diagnosing-bugs`](skills/diagnosing-bugs/) | Diagnosis loop for hard bugs and performance regressions. | Matt Pocock |
| [`domain-modeling`](skills/domain-modeling/) | Build and sharpen a project's domain model. | Matt Pocock |
| [`git-guardrails-claude-code`](skills/git-guardrails-claude-code/) | Set up Claude Code hooks to block dangerous git commands (push, reset --hard, clean, branch -D, etc.) before they execute. | Matt Pocock |
| [`grill-me`](skills/grill-me/) | A relentless interview to sharpen a plan or design. | Matt Pocock |
| [`grill-with-docs`](skills/grill-with-docs/) | A relentless interview to sharpen a plan or design, which also creates docs (ADR's and glossary) as we go. | Matt Pocock |
| [`grilling`](skills/grilling/) | Grill the user relentlessly about a plan, decision, or idea. | Matt Pocock |
| [`handoff`](skills/handoff/) | Compact the current conversation into a handoff document for another agent to pick up. | Matt Pocock |
| [`implement`](skills/implement/) | Implement a piece of work based on a spec or set of tickets. | Matt Pocock |
| [`implement-spec`](skills/implement-spec/) | Implement the result of /to-spec and /to-tickets in code. | Matt Pocock |
| [`improve-codebase-architecture`](skills/improve-codebase-architecture/) | Scan a codebase for deepening opportunities, present them as a visual HTML report, then grill through whichever one you pick. | Matt Pocock |
| [`loop-me`](skills/loop-me/) | Grill me about specs for the workflows I want to build, within this workspace. | Matt Pocock |
| [`migrate-to-shoehorn`](skills/migrate-to-shoehorn/) | Migrate test files from `as` type assertions to @total-typescript/shoehorn. | Matt Pocock |
| [`pr`](skills/pr/) | Use when writing a PR body. | Matt Pocock |
| [`research`](skills/research/) | Investigate a question against high-trust primary sources and capture the findings as a Markdown file in the repo. | Matt Pocock |
| [`retro`](skills/retro/) | Conduct a retrospective on a coding session. | Matt Pocock |
| [`scaffold-exercises`](skills/scaffold-exercises/) | Create exercise directory structures with sections, problems, solutions, and explainers that pass linting. | Matt Pocock |
| [`setup-matt-pocock-skills`](skills/setup-matt-pocock-skills/) | Configure this repo for the engineering skills: set up its issue tracker, triage label vocabulary, and domain doc layout. | Matt Pocock |
| [`setup-pre-commit`](skills/setup-pre-commit/) | Set up Husky pre-commit hooks with lint-staged (Prettier), type checking, and tests in the current repo. | Matt Pocock |
| [`setup-ts-deep-modules`](skills/setup-ts-deep-modules/) | Wire dependency-cruiser into a TypeScript repo so each package is a deep module, with implementation hidden in subfolders and reachable... | Matt Pocock |
| [`to-questionnaire`](skills/to-questionnaire/) | Turn a decision you can't fully answer into a questionnaire for someone else to fill in. | Matt Pocock |
| [`to-spec`](skills/to-spec/) | Turn the current conversation into a spec and publish it to the project issue tracker: no interview, just synthesis of what you've... | Matt Pocock |
| [`to-tickets`](skills/to-tickets/) | Break a plan, spec, or the current conversation into a set of tracer-bullet tickets, each declaring its blocking edges, published to the... | Matt Pocock |
| [`triage`](skills/triage/) | Move issues and external PRs through a state machine of triage roles, categorise, verify, grill if needed, and write agent-ready briefs. | Matt Pocock |
| [`wait-what`](skills/wait-what/) | Stop. That last message did not land: re-pitch it. | Matt Pocock |
| [`wayfinder`](skills/wayfinder/) | Plan a huge chunk of work (more than one agent session can hold) as a shared map of decision tickets on your issue tracker, and resolve... | Matt Pocock |
| [`wizard`](skills/wizard/) | Generate an interactive bash wizard that walks a human through steps only they can perform. | Matt Pocock |
| [`writing-beats`](skills/writing-beats/) | Writing, exploit; assemble raw material into a journey of beats, grounding each term before a beat leans on it. | Matt Pocock |
| [`writing-for-agents`](skills/writing-for-agents/) | Writing documents for agents. | Matt Pocock |
| [`writing-fragments`](skills/writing-fragments/) | Writing, explore: mine raw fragments, no structure yet. | Matt Pocock |
| [`writing-shape`](skills/writing-shape/) | Writing, exploit: shape raw material into an article, paragraph by paragraph. | Matt Pocock |
| [`14-day-stale-pr-close`](skills/14-day-stale-pr-close/) | Use to close contributor PRs that have been waiting on the author for stale-days with no author push, comment, or review. | Kun Chen |
| [`ahoy`](skills/ahoy/) | Use when the captain explicitly says ahoy or /ahoy, or asks for a session recap of what happened since they last spoke, plus any visibly... | Kun Chen |
| [`axi`](skills/axi/) | Agent eXperience Interface (AXI) - ergonomic standards for building CLI tools that agents use via shell execution. | Kun Chen |
| [`cache-architecture`](skills/cache-architecture/) | Cache storage locations, permissions, context scoping, isolation rules, and lifecycle management in quota-axi. | Kun Chen |
| [`chrome-devtools-axi`](skills/chrome-devtools-axi/) | Control a Chrome browser session through the chrome-devtools-axi CLI - navigate, snapshot, click, fill forms, run JavaScript, inspect... | Kun Chen |
| [`compact-adviser`](skills/compact-adviser/) | Read or change compact-adviser settings for Codex - the mode (hint or off), the minimum context before a checkpoint is judged, the... | Kun Chen |
| [`gh-axi`](skills/gh-axi/) | Operate GitHub through the gh-axi CLI - issues, pull requests, discussions, stacked PRs, workflow runs, workflows, releases,... | Kun Chen |
| [`gnhf`](skills/gnhf/) | Use when the user asks to run GNHF, says they are going to sleep or leaving and wants an agent-managed coding run, asks to supervise,... | Kun Chen |
| `kun` (link-only) | Summon Kun to solve your problems. | Kun Chen |
| [`lavish`](skills/lavish/) | Turn complex or visual agent responses into rich, reviewable HTML artifacts (HTML files) the user can annotate and send feedback on,... | Kun Chen |
| [`no-mistakes`](skills/no-mistakes/) | Validate your code changes through the no-mistakes pipeline - automated code review, tests, lint, docs, push, PR, and CI - before they... | Kun Chen |
| [`provider-adapters`](skills/provider-adapters/) | Provider-specific auth sources, quota windows, endpoint shapes, error recovery, and quirks for the quota-axi providers with dedicated... | Kun Chen |
| [`provider-onboarding`](skills/provider-onboarding/) | Rules, checklist, credential selection machinery, multi-source handover, delegated refresh contract, and test discipline for onboarding... | Kun Chen |
| [`quota-axi`](skills/quota-axi/) | Report local Claude, Codex, Cursor, GitHub Copilot, Grok, Kimi, Z.AI, Alibaba, OpenCode Go, Antigravity, Command Code, MiniMax, MiMo,... | Kun Chen |
| [`quota-interpretation`](skills/quota-interpretation/) | Rules and algorithms for quota interpretation, pace calculation, runway derivation, selection signals, and output tier rendering (TOON,... | Kun Chen |
| [`release-ci`](skills/release-ci/) | Release automation, CI workflows, release-please configuration, contribution gate, and lockfile formatting in quota-axi. | Kun Chen |
| [`stow`](skills/stow/) | Sweep the current conversation for durable knowledge - user preferences, project facts, operational gotchas, standing decisions, and... | Kun Chen |
| [`tasks-axi`](skills/tasks-axi/) | Manage a task backlog through the tasks-axi CLI - add, list, show, start, and complete tasks; track blocked-by dependencies, structured... | Kun Chen |
| [`vision`](skills/vision/) | Draft and stress-test a VISION.md for a repository, then iterate with the author on an interactive review board until approved. | Kun Chen |
| [`vision-md-triage-verdict`](skills/vision-md-triage-verdict/) | Use before any final triage decision when the repo has a VISION.md. | Kun Chen |
| [`whathappened`](skills/whathappened/) | Brief what just happened on a topic and map public opinion from X (Twitter) only. | Kun Chen |
| [`audit-agent-worktrees`](skills/audit-agent-worktrees/) | Audit old git worktrees and clones that coding agents left behind, and delete only the ones whose work is safe. | kstack |
| [`delegate-to-model`](skills/delegate-to-model/) | Hand a task from the current agent to another model on your subscriptions - Codex CLI, Cursor agent CLI, or any OpenRouter model - and... | kstack |
| [`mac-disk-cleanup`](skills/mac-disk-cleanup/) | Free disk space on a developer Mac safely. | kstack |
| [`supervise-agent-fleet`](skills/supervise-agent-fleet/) | Supervise several coding agents that work in parallel and ship through pull requests. | kstack |
<!-- kstack:skills:end -->
