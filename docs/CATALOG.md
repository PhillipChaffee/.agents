# Catalog Reference

Complete reference of the **24 execution playbooks**, **76 active skills** (**51 workflow/domain skills** + **25 engineering principles**), **7 specialist sub-agents**, and **5 operational rules** shipped in `magic`.

---

## 24 Playbooks (auto-routed by `/magic-mode`)

| Category | Playbook | Use For |
| --- | --- | --- |
| **Understand & Diagnose** | [investigation](../skills/magic-mode/playbooks/investigation.md) | Read-only question: how `X` works, why `Y` was built this way, or whether an assumption holds |
| **Understand & Diagnose** | [runtime forensics](../skills/magic-mode/playbooks/runtime-forensics.md) | Diagnose a live symptom (memory leak, idle-CPU spin, glitch) from runtime instrumentation |
| **Understand & Diagnose** | [trace forensics](../skills/magic-mode/playbooks/trace-forensics.md) | Diagnose a captured profiling artifact (`cpuprofile`, trace, spindump, heap snapshot) |
| **Build, Fix & Optimize** | [feature](../skills/magic-mode/playbooks/feature.md) | New or changed behavior built from a named data shape |
| **Build, Fix & Optimize** | [bug fix](../skills/magic-mode/playbooks/bug-fix.md) | Reproduce a defect, root-cause it, and fix with runtime evidence |
| **Build, Fix & Optimize** | [refactoring](../skills/magic-mode/playbooks/refactoring.md) | Behavior-preserving change to code structure or shape |
| **Build, Fix & Optimize** | [perf issue](../skills/magic-mode/playbooks/perf-issue.md) | Trace a measured slowness and improve it against a baseline |
| **Build, Fix & Optimize** | [hillclimb](../skills/magic-mode/playbooks/hillclimb.md) | Sustained, hypothesis-driven improvement of one metric against a target |
| **Build, Fix & Optimize** | [prototype](../skills/magic-mode/playbooks/prototype.md) | Throwaway sketch to settle a design or empirical fork by observation |
| **Build, Fix & Optimize** | [system design](../skills/magic-mode/playbooks/system-design.md) | Produce a System Design Document, validated Mermaid diagrams, and an Implementation Plan before editing code |
| **Build, Fix & Optimize** | [visual parity](../skills/magic-mode/playbooks/visual-parity.md) | Pixel-exact UI equivalence between two implementations |
| **PRs & Shipping** | [opening a PR](../skills/magic-mode/playbooks/opening-a-pr.md) | Open a review-ready PR from small ordered commits (runs at the end of build playbooks) |
| **PRs & Shipping** | [babysit](../skills/magic-mode/playbooks/babysit.md) | Drive a PR or stack to merge-ready: conflicts, review threads, and CI |
| **PRs & Shipping** | [shipping](../skills/magic-mode/playbooks/shipping.md) | Independently verify a green stack and land the contiguous verified run bottom-up |
| **Scale & Autonomy** | [multi-phase plan](../skills/magic-mode/playbooks/multi-phase-plan.md) | Author a plan for work spanning multiple phases or stacked PRs |
| **Scale & Autonomy** | [autonomous run](../skills/magic-mode/playbooks/autonomous-run.md) | Drive a long task to completion against a checkable predicate without stopping |
| **Scale & Autonomy** | [orchestrate](../skills/magic-mode/playbooks/orchestrate.md) | Coordinate a multi-day, multi-PR program across fleets of sub-agents |
| **Scale & Autonomy** | [autopilot-full](../skills/magic-mode/playbooks/autopilot-full.md) | Run independent PRs to merged with one owner per PR and a swarm verdict before merge |
| **Scale & Autonomy** | [autopilot-stack](../skills/magic-mode/playbooks/autopilot-stack.md) | Build and verify one linear base-branch stack for the operator to review and land |
| **Session & Hygiene** | [session pickup](../skills/magic-mode/playbooks/session-pickup.md) | Resume or take over a prior agent's in-flight branch or transcript |
| **Session & Hygiene** | [pause safely](../skills/magic-mode/playbooks/pause-safely.md) | Suspend in-flight work cleanly so it can be resumed without state loss |
| **Session & Hygiene** | [worktree cleanup](../skills/magic-mode/playbooks/worktree-cleanup.md) | Reclaim disk by pruning merged/abandoned worktrees and stale simulators (safety-gated) |
| **Skills & Evals** | [authoring a skill](../skills/magic-mode/playbooks/authoring-a-skill.md) | Author or edit a `SKILL.md` |
| **Skills & Evals** | [eval](../skills/magic-mode/playbooks/eval.md) | Blind-test how a skill or prompt change affects agent behavior |

---

## 51 Situational, PR, Research, Formal Verification, Planning & Authoring Skills

| Group | Skill | Use It When |
| --- | --- | --- |
| **Entry & Routing** | [`/using-magic`](../skills/using-magic/SKILL.md) | Session-start bootstrap that routes tasks to `/magic-mode`, `/research`, `/proof-driven-development`, or `/magic-help` before acting |
| **Entry & Routing** | [`/magic-mode`](../skills/magic-mode/SKILL.md) | Default entry point for any non-trivial engineering task |
| **Entry & Routing** | [`/magic-help`](../skills/magic-help/SKILL.md) | Unsure which skill, playbook, or principle fits your task |
| **Entry & Routing** | [`/setup-magic`](../skills/setup-magic/SKILL.md) | Configuring per-role models and reasoning budgets |
| **Entry & Routing** | [`/figure-it-out`](../skills/figure-it-out/SKILL.md) | No bundled playbook fits; designs a bespoke, auditable playbook |
| **Planning & Execution** | [`/writing-plans`](../skills/writing-plans/SKILL.md) | Turning a spec or requirements for a multi-step task into a bite-sized TDD implementation plan before touching code |
| **Planning & Execution** | [`/subagent-driven-development`](../skills/subagent-driven-development/SKILL.md) | Executing an implementation plan with a fresh implementer and two-stage reviewer sub-agent per task |
| **Alignment & Prompting** | [`/in-your-own-words`](../skills/in-your-own-words/SKILL.md) | Having the agent play back your goal and problem before starting |
| **Alignment & Prompting** | [`/sharpen`](../skills/sharpen/SKILL.md) | Rewriting a prompt deeper (not longer) before sending it |
| **Research, Code & History** | [`/research`](../skills/research/SKILL.md) | Running tiered (direct, parallel, or scoped pipeline) research across codebase, web, and MCP tools into `docs/research/<topic>.md` |
| **Research, Code & History** | [`/research-summary`](../skills/research-summary/SKILL.md) | Producing a concise, cited research summary with head-to-head option comparison tables |
| **Research, Code & History** | [`/how`](../skills/how/SKILL.md) | Getting a cited walkthrough of how a subsystem works |
| **Research, Code & History** | [`/why`](../skills/why/SKILL.md) | Investigating why something was built this way across code, PRs, issues, and docs |
| **Research, Code & History** | [`/teach`](../skills/teach/SKILL.md) | Learning a change or subsystem explained from first principles |
| **Context & Catch-Up** | [`/recall`](../skills/recall/SKILL.md) | Rebuilding recent context on a topic when starting or resuming work |
| **Context & Catch-Up** | [`/ketchup`](../skills/ketchup/SKILL.md) | Catching up on what changed in the current chat, with every decision waiting on you |
| **Context & Catch-Up** | [`/ketchup-video`](../skills/ketchup-video/SKILL.md) | Rendering `/ketchup` as a short subtitled video of slides |
| **Design & Parallelism** | [`/architect`](../skills/architect/SKILL.md) | Settling types and module boundaries before writing cross-boundary code |
| **Design & Parallelism** | [`/arena`](../skills/arena/SKILL.md) | Running `N` parallel attempts at the same brief and grafting the best parts |
| **Design & Parallelism** | [`/swarm`](../skills/swarm/SKILL.md) | Dispatching `N` parallel workers across slices or races into one report |
| **Design & Parallelism** | [`/blast-radius`](../skills/blast-radius/SKILL.md) | Checking what else a small-looking change could break outside the diff |
| **Build & Implementation** | [`/tdd`](../skills/tdd/SKILL.md) | Fixing a bug test-first with a focused failing regression test when a cheap local test path exists |
| **Build & Implementation** | [`/clean-code`](../skills/clean-code/SKILL.md) | Cleaning AI code slop from diffs before commit, PR, or review, routing by language |
| **Build & Implementation** | [`/make-bot-ui`](../skills/make-bot-ui/SKILL.md) | Building a custom UI that wakes a bot over a webhook and exposes the page on Tailscale |
| **Formal Verification** | [`/proof-driven-development`](../skills/proof-driven-development/SKILL.md) | Choosing a formal proof technique, verifier tool, or multi-skill verification pipeline |
| **Formal Verification** | [`/proving-with-hoare-logic`](../skills/proving-with-hoare-logic/SKILL.md) | Proving code contracts, loop invariants, and bounds with SMT-backed verifiers (Verus, Dafny, SPARK, Creusot, Frama-C WP) |
| **Formal Verification** | [`/proving-with-dependent-types`](../skills/proving-with-dependent-types/SKILL.md) | Proving compiler passes, crypto, policy lattices, or state impossibility in Lean 4, Rocq, Isabelle/HOL, or F* |
| **Formal Verification** | [`/model-checking-protocols-and-code`](../skills/model-checking-protocols-and-code/SKILL.md) | Finding concurrency/retry/crash races in TLA+, P, or Alloy, or proving bit-exact panic/overflow freedom in Kani or CBMC |
| **Formal Verification** | [`/analyzing-with-abstract-interpretation`](../skills/analyzing-with-abstract-interpretation/SKILL.md) | Proving whole-program absence of runtime errors over abstract domains in Frama-C EVA, Astrée, or Goblint |
| **Formal Verification** | [`/auditing-proof-specifications`](../skills/auditing-proof-specifications/SKILL.md) | Auditing human or AI proofs for `sorry`/`admit`/`assume` escape hatches, vacuity, and the 4 remaining proof gaps |
| **Formal Verification** | [`/statechart`](../skills/statechart/SKILL.md) | Rendering TLA+ state machines and TLC counterexample traces as readable Mermaid statecharts |
| **Formal Verification** | [`/create-formal-verification-skill`](../skills/create-formal-verification-skill/SKILL.md) | Locking a proven formal check into a repository with covered files, bounds, and a sync commit |
| **Formal Verification** | [`/maintain-formal-verification-skill`](../skills/maintain-formal-verification-skill/SKILL.md) | Bringing a project's formal verification skill back in sync after merges or refactors |
| **Review & Verification** | [`/autopilot`](../skills/autopilot/SKILL.md) | Driving a PR to merge-ready (conflicts, triaged review/bot threads, in-scope CI) under a strict diff size budget |
| **Review & Verification** | [`/make-pr-easy-to-review`](../skills/make-pr-easy-to-review/SKILL.md) | Preparing PRs for review by cleaning commit history, improving PR descriptions, and adding reviewer guidance |
| **Review & Verification** | [`/thermo-nuclear-code-quality-review`](../skills/thermo-nuclear-code-quality-review/SKILL.md) | Running a strict maintainability audit for abstraction quality, >1k-line files, spaghetti branching, and code-judo simplifications |
| **Review & Verification** | [`/interrogate`](../skills/interrogate/SKILL.md) | Having diverse models adversarially review a diff to break it |
| **Review & Verification** | [`/benchmark-checklist`](../skills/benchmark-checklist/SKILL.md) | Vetting a benchmark speedup or regression number before trusting it |
| **Review & Verification** | [`/create-verification-skill`](../skills/create-verification-skill/SKILL.md) | Generating a project-local `verify-<app>` skill and feature map to drive the live app |
| **Review & Verification** | [`/maintain-verification-skill`](../skills/maintain-verification-skill/SKILL.md) | Syncing a project's `verify-<app>` skill and feature map after app changes |
| **Review & Verification** | [`/show-me-your-work`](../skills/show-me-your-work/SKILL.md) | Recording an auditable TSV decision log (`scripts/log.sh`) during autonomous runs |
| **Prose & Code Hygiene** | [`/no-comments`](../skills/no-comments/SKILL.md) | Stripping narration and alibi comments before review via `comment-sicko` |
| **Prose & Code Hygiene** | [`/unslop`](../skills/unslop/SKILL.md) | Removing AI tells and filler from prose |
| **Prose & Code Hygiene** | [`/technical-writing`](../skills/technical-writing/SKILL.md) | Writing docs, RFCs, READMEs, PR descriptions, and commit messages to standard |
| **Prose & Code Hygiene** | [`/simple-english`](../skills/simple-english/SKILL.md) | Writing and rewriting docs, runbooks, and replies in plain, layman-readable English in the spirit of ASD-STE100 |
| **Prose & Code Hygiene** | [`/bro`](../skills/bro/SKILL.md) | Restating the previous reply in plain human language |
| **Meta & Skill Evolution** | [`/writing-skills`](../skills/writing-skills/SKILL.md) | Authoring and testing new skills with sub-agent pressure scenarios (TDD for skills) |
| **Meta & Skill Evolution** | [`/writing-rules`](../skills/writing-rules/SKILL.md) | Triaging, authoring, and pressure-testing agent rules (`rules/` and `agents.kit.md`) with TDD |
| **Meta & Skill Evolution** | [`/reflect`](../skills/reflect/SKILL.md) | Capturing lessons from a completed task as concrete skill edits |
| **Meta & Skill Evolution** | [`/correct`](../skills/correct/SKILL.md) | Stopping repeated agent mistakes at the highest structural level that works |
| **Meta & Skill Evolution** | [`/automate-me`](../skills/automate-me/SKILL.md) | Drafting a personal `-mode` skill from your actual working history |

---

## 25 Engineering Principles (`/principle-<name>`)

| Group | Principle | Core Rule |
| --- | --- | --- |
| `core` | [take-a-step-back](../skills/principle-take-a-step-back/SKILL.md) | Question why the user is asking, check whether the current path serves their real goal, and flag hidden constraints or misconceptions with evidence |
| `core` | [laziness-protocol](../skills/principle-laziness-protocol/SKILL.md) | Bias toward deletion and the smallest change that solves the problem |
| `core` | [foundational-thinking](../skills/principle-foundational-thinking/SKILL.md) | Get the data structures right so downstream logic becomes obvious |
| `core` | [redesign-from-first-principles](../skills/principle-redesign-from-first-principles/SKILL.md) | Redesign as if the new requirement had been foundational from day one |
| `core` | [attack-the-premise](../skills/principle-attack-the-premise/SKILL.md) | When two fixes sharing one premise fail the same gate, test the premise before a third fix |
| `core` | [subtract-before-you-add](../skills/principle-subtract-before-you-add/SKILL.md) | Remove dead weight first, then build on the simpler base |
| `core` | [minimize-reader-load](../skills/principle-minimize-reader-load/SKILL.md) | Count layers and hidden state; collapse one-caller wrappers and shrink mutable scope |
| `core` | [outcome-oriented-execution](../skills/principle-outcome-oriented-execution/SKILL.md) | Converge on the target architecture; skip throwaway compatibility states |
| `core` | [experience-first](../skills/principle-experience-first/SKILL.md) | Choose user delight over implementation convenience |
| `core` | [exhaust-the-design-space](../skills/principle-exhaust-the-design-space/SKILL.md) | Build 2–3 competing prototypes and compare before committing |
| `core` | [build-the-lever](../skills/principle-build-the-lever/SKILL.md) | Build the deterministic script or tool that does or proves the work |
| `architecture` | [model-the-domain](../skills/principle-model-the-domain/SKILL.md) | Encode domain rules in a structure (state machine, table, typed model) instead of scattered branches |
| `architecture` | [boundary-discipline](../skills/principle-boundary-discipline/SKILL.md) | Validate at system boundaries; trust internal types; keep core logic pure |
| `architecture` | [type-system-discipline](../skills/principle-type-system-discipline/SKILL.md) | Make illegal states unrepresentable; brand semantic primitives; parse at boundaries |
| `architecture` | [make-operations-idempotent](../skills/principle-make-operations-idempotent/SKILL.md) | Converge to the same end state regardless of partial prior runs or retries |
| `architecture` | [migrate-callers-then-delete-legacy-apis](../skills/principle-migrate-callers-then-delete-legacy-apis/SKILL.md) | Migrate all callers and delete the old API in the same wave |
| `architecture` | [separate-before-serializing-shared-state](../skills/principle-separate-before-serializing-shared-state/SKILL.md) | Eliminate shared state first; serialize only for a true invariant |
| `verification` | [prove-it-works](../skills/principle-prove-it-works/SKILL.md) | Verify against the real artifact, not a proxy, self-report, or "it compiles" |
| `verification` | [fix-root-causes](../skills/principle-fix-root-causes/SKILL.md) | Trace each symptom to the first place the system went wrong and fix it there |
| `verification` | [sequence-verifiable-units](../skills/principle-sequence-verifiable-units/SKILL.md) | Break work into small units that each end in a check, verified before the next |
| `verification` | [test-behavior-not-implementation](../skills/principle-test-behavior-not-implementation/SKILL.md) | Assert what callers and users can observe, not internal implementation details |
| `verification` | [explain-the-number](../skills/principle-explain-the-number/SKILL.md) | Identify what limits a measured number before trusting or reporting it |
| `delegation` | [guard-the-context-window](../skills/principle-guard-the-context-window/SKILL.md) | Route bulk exploration and fan-out to sub-agents; keep summaries in the main thread |
| `delegation` | [never-block-on-the-human](../skills/principle-never-block-on-the-human/SKILL.md) | Proceed autonomously on reversible work; reserve confirmation for irreversible actions |
| `meta` | [encode-lessons-in-structure](../skills/principle-encode-lessons-in-structure/SKILL.md) | Encode recurring lessons as a lint, flag, check, or script instead of more prose |

---

## 7 Sub-Agents (`agents/`)

| Agent | Mode | Role |
| --- | --- | --- |
| [`magic-agent`](../agents/magic-agent/agent.md) | Read-Write | Delegate sub-agent spawned by `/magic-mode` playbooks; loads `magic-mode` and its principles |
| [`comment-sicko`](../agents/comment-sicko/agent.md) | Read-Write | Strips narration comments and flags `MUST KILL` refactor targets for `/no-comments` |
| [`research-planner`](../agents/research-planner/agent.md) | Read-Only (Thinking) | Decomposes complex investigations into parallel, right-sized researcher subtasks |
| [`researcher-lite`](../agents/researcher-lite/agent.md) | Read-Only | High-volume, low-cost lookups: definitions, call sites, config values |
| [`researcher-mid`](../agents/researcher-mid/agent.md) | Read-Only | Moderate reasoning: tracing subsystem data flows and cross-source gathering |
| [`researcher-deep`](../agents/researcher-deep/agent.md) | Read-Only | Deep architectural, security, performance, and multi-source synthesis |
| [`research-synthesizer`](../agents/research-synthesizer/agent.md) | Read-Only | Deduplicates, reconciles conflicts, and synthesizes researcher outputs with citations |

---

## 5 Operational Rules (`rules/` & `agents.kit.md`)

| File | Scope | Rule Summary |
| --- | --- | --- |
| [`agents.kit.md`](../agents.kit.md) | Installed as `~/.agents/agents.md` | Distilled root instruction layer (single-bullet rules: use `rg`, separate test files, GitHub user commit attribution, workflow routing pointer, `/clean-code` and `/make-pr-easy-to-review` on PR/MR open or update, chunked large-file creation, new-repo bootstrap) |
| [`rules/workflow-routing.md`](../rules/workflow-routing.md) | Always applied | Route engineering, code cleanup, PR/MR reviewability, research, and formal-proof tasks to `/magic-mode`, `/clean-code`, `/make-pr-easy-to-review`, `/research`, or `/proof-driven-development` before acting |
| [`rules/look-it-up.md`](../rules/look-it-up.md) | Always applied | Never answer factual tool/API questions from memory; check official docs and primary sources first |
| [`rules/new-repo-setup.md`](../rules/new-repo-setup.md) | New repo creation | Bootstrap greenfield repos from `full-lint` (`>= 95%` coverage + full hygiene gates) and set up `magic` |
| [`rules/sleeps-and-polling.md`](../rules/sleeps-and-polling.md) | CI & background waits | Cap single-call sleeps at `<= 30s` and return control between polls |
| [`rules/large-file-creation.md`](../rules/large-file-creation.md) | Files `> 1000` lines | Write the header/first section, append `<= 1000`-line sections with Edit or `cat >>` heredocs, and verify with `wc -l` |
