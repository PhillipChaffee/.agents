# Thin-Orchestrator Wave Delegation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert `magic`'s entry-point routing, `/magic-mode` and its playbooks, `/research`, multi-model panels (`/arena`, `/architect`, `/interrogate`), upstream-adapted skills (`writing-plans`, `subagent-driven-development`, `make-pr-easy-to-review`, `thermo-nuclear-code-quality-review`), and standalone/formal-proof skills into flat depth-1 wave dispatchers so a cheaper, lighter main model can run the session cleanly without inline cognitive bottlenecks or depth-2 subagent failures.

**Architecture:** The root chat (`depth = 0`) acts strictly as a flat wave state-machine dispatcher: it routes skills, owns `todowrite`, asks user questions, arms `/loop`, runs deterministic lock/budget scripts, and passes scratch/repo file paths between depth-1 leaf subagents (`depth = 1`). All heavy scoping, architecture/plan design, Arena base-selection & grafting, production coding, live/formal verification, diff auditing, and PR/reply prose run in role-routed leaf subagents configured by Plan 1's `magic-models` contract (`# orchestrator: thin` by default). Upstream-adapted skills are updated directly in-repo with clean frontmatter, resolved links, and updated `THIRD-PARTY-NOTICES.md` attribution.

**Tech Stack:** Markdown (`SKILL.md`, `playbooks/*.md`, `agent.md`, `rules/*.md`), Bash (`scripts/validate.sh`), Node.js ESM (`node:test`), Python 3 (`unittest`).

**Spec:** `docs/research/thin-orchestrator-and-setup-magic.md`

## Global Constraints

- Prerequisites from Plan 1 (`docs/superpowers/plans/2026-11-11-setup-magic-and-harness-plumbing.md`): `model-roles.md` defines `# orchestrator: thin | standard` and the 22 canonical role names (plus 4 tier lines: `orchestrator`, `fast`, `main`, `deep`; including `fast, mechanical, miners`, `researcher-lite, collectors`, `researcher-mid`, `researcher-deep, planner, synthesizer`, `arena synthesizer`, `sdd reviewer`, `comment-sicko`, `arena cross-judge pool`, etc.).
- Max portable subagent nesting depth is `1` (`main -> leaf subagent`): no leaf subagent (`magic-agent`, `comment-sicko`, PR owner, or explorer) may depend on spawning sub-subagents (`agents/comment-sicko/agent.md:31`, `playbooks/feature.md:19`, `playbooks/autopilot-full.md:10`, `playbooks/orchestrate.md:11`).
- Keep skill count at `75` (`tests/opencode-and-pi-plugins.test.mjs:157`) and operational rule count at `5` (`tests/writing-rules.test.mjs:38-55`), with every `rules/*.md` body strictly `< 250` words and `tests/test_install.py:65` continuing to forbid `rules/subagents.md`.
- Remove all vendor model pins, Cursor-only fields, and hardcoded `gh` / `gt` / `origin` CLIs across all active skills, **including** `skills/autopilot/SKILL.md:95` (`Claude Opus 5.5 xhigh`), `writing-plans`, `subagent-driven-development`, `make-pr-easy-to-review`, and `thermo-nuclear-code-quality-review` once validator exclusions are lifted (`ADR-0001`, `ADR-0007`).
- Preserve Variant C output-format requirements (`1-2 sentence` prose blocks, Markdown `table`s, bottom `## TL;DR`) on every file in `tests/output-format-skills.test.mjs:8-31`, and preserve zero en/em-dashes (`\u2013\u2014`) and zero mid-sentence colons (`: \S`) on `make-pr-easy-to-review` lines in `skills/magic-mode/playbooks/multi-phase-plan.md` (`tests/magic-sync.test.mjs:154-159`, `skills/magic-mode/scripts/check-plan.mjs:78-80`).
- Sort top-level YAML frontmatter keys alphabetically in every `SKILL.md` (`description`, `name`) so `./scripts/validate.sh` produces **zero** `WARN` lines as well as zero `FAIL` lines.

## Review Focus

1. **Harness without a subagent tool (Pi without `pi-subagents`):** Thin-orchestrator delegation rules in `using-magic/SKILL.md`, `workflow-routing.md`, and `magic-mode/SKILL.md` must key on the observable predicate *"when the harness exposes a subagent tool"* (`harness-adapter.md:11`) so Pi without `pi-subagents` executes sequentially instead of failing or inventing `Task` calls.
2. **Infinite subagent recursion on direct leaf-skill invocation:** When `# orchestrator: thin` wraps a direct user invocation of a leaf skill (such as `/tdd` or `/thermo-nuclear-code-quality-review`) in a depth-1 `magic-agent`, `<SUBAGENT-STOP>` in `using-magic/SKILL.md:10-12` and `workflow-routing.md:21` must guarantee the spawned leaf worker executes the skill directly and never re-delegates.
3. **Validator & link-checker un-ignoring of Superpowers & `cursor-team-kit` skills:** Removing `writing-skills`, `writing-plans`, `subagent-driven-development`, `make-pr-easy-to-review`, and `thermo-nuclear-code-quality-review` from `scripts/validate.sh:168` and `scripts/magic-verbatim.txt` immediately exposes broken relative links (`../../requesting-code-review/code-reviewer.md`, `../using-superpowers/...`), unsorted frontmatter, and `gh pr` commands. Task 4 tests and fixes every single one.
4. **Tamper-proof `spec.lock` boundary in 4-Wave PDD:** In `proof-driven-development` and `auditing-proof-specifications`, the main dispatcher (`depth = 0`) must run deterministic `node skills/auditing-proof-specifications/scripts/verify-spec-lock.mjs --generate` *after* Wave 1/2 Spec Authoring finishes and *before* Wave 3 Proof Synthesis starts, then run `--check` after Wave 3 so the proof-synthesis worker cannot weaken the spec.
5. **Validator regex blind spot on capitalized vendor names:** `scripts/validate.sh:152-158` missed `Claude Opus 5.5 xhigh` in `autopilot/SKILL.md:95` because `BANNED` only matched lowercase hyphenated `claude-[a-z]+-[0-9]`; Task 3 adds capitalized vendor model detection to `BANNED` and tests it.

---

## File Structure

- Modify (Task 1, Entry Routing and Core `magic-mode` Dispatcher): `skills/using-magic/SKILL.md`, `rules/workflow-routing.md`, `skills/magic-mode/SKILL.md`, `agents/magic-agent/agent.md`, `agents/comment-sicko/agent.md`, `skills/magic-help/SKILL.md`.
- Modify (Task 2, Flagship Multi-Agent and Research Skills): `skills/{research,research-summary,why,arena,architect,no-comments,interrogate,blast-radius}/SKILL.md`, `agents/{research-planner,research-synthesizer,researcher-deep}/agent.md`.
- Modify (Task 3, Playbook Waves and `/autopilot`): `skills/magic-mode/playbooks/*.md` (`21` playbooks), `skills/autopilot/SKILL.md`, `scripts/validate.sh`.
- Modify (Task 4, Upstream Skill Adaptations and Notices): `skills/{writing-plans,subagent-driven-development,writing-skills,make-pr-easy-to-review,thermo-nuclear-code-quality-review}/**`, `scripts/magic-verbatim.txt`, `scripts/validate.sh`, `THIRD-PARTY-NOTICES.md`, `lychee.toml`, `.markdownlint-cli2.jsonc`, `.typos.toml`, `tests/magic-sync.test.mjs`.
- Modify (Task 5, Standalone Skills, 4-Wave PDD, and Repo Drift): `skills/{teach,recall,ketchup,ketchup-video,correct,figure-it-out,automate-me,reflect,show-me-your-work,writing-rules,create-verification-skill,maintain-verification-skill,create-formal-verification-skill,maintain-formal-verification-skill,proof-driven-development,proving-with-hoare-logic,proving-with-dependent-types,model-checking-protocols-and-code,analyzing-with-abstract-interpretation,auditing-proof-specifications,statechart}/SKILL.md`, `docs/adr/{0004-mattpocock-main-flow,0005-combined-two-tier-code-review,0008-pstack-port}.md`, `docs/magic-guide/{README,02-magic-mode,05-build-and-clean,09-make-it-yours}.md`.
- Create: `tests/thin-orchestrator.test.mjs`.

---

### Task 1: Thin-Orchestrator Entry Routing (`using-magic`, `workflow-routing.md`) & Core `magic-mode` Wave Rules

**Files:**

- Modify: `skills/using-magic/SKILL.md:10-67`
- Modify: `rules/workflow-routing.md:1-23`
- Modify: `skills/magic-mode/SKILL.md:15-36,93-125`
- Modify: `agents/magic-agent/agent.md:1-13`
- Modify: `agents/comment-sicko/agent.md:28-37`
- Modify: `skills/magic-help/SKILL.md:26-49,129-135`
- Create: `tests/thin-orchestrator.test.mjs`

**Interfaces:**

- Consumes: `# orchestrator: thin | standard` and role names from `skills/magic-mode/references/model-roles.md`.
- Produces:
  - `rules/workflow-routing.md` (`< 250` words) and `skills/using-magic/SKILL.md`: pre-routing guard forbidding multi-file exploration or inline code edits before routing, plus thin-mode leaf wrapping (*when `# orchestrator: thin` (default) and the harness exposes a subagent tool, direct invocations of heavy leaf skills dispatch one depth-1 `magic-agent` carrying that skill's `SKILL.md` path while `<SUBAGENT-STOP>` executes directly in the leaf*).
  - `skills/magic-mode/SKILL.md`: **Depth-1 Leaf Subagent Rule**; `~/.agents/models.json` tier fallback before omitting `model` (`:99`); under `# orchestrator: thin`, delegates post-grounding `take-a-step-back`, domain-shape naming, diff review (`:101`), and final reply prose (`:105-121`) to `judgment and prose` (`deep`), and replaces `create-skill` with `/writing-skills` (`:26`).
  - `agents/magic-agent/agent.md` & `agents/comment-sicko/agent.md`: enforces depth-1 leaf execution (`comment-sicko` inspects callers/`git log -S` directly or emits `NEEDS-GROUNDING: <symbol>` instead of calling `/how` or `/why` at depth 2).

- [ ] **Step 1: Write the failing test in `tests/thin-orchestrator.test.mjs`**

```javascript
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";

const repoDir = path.resolve(import.meta.dirname, "..");

test("using-magic, workflow-routing, magic-mode, magic-agent, and comment-sicko enforce flat depth-1 thin orchestration", () => {
	const usingMagic = fs.readFileSync(path.join(repoDir, "skills/using-magic/SKILL.md"), "utf8");
	assert.match(usingMagic, /orchestrator:\s*thin/i);
	assert.match(usingMagic, /magic-agent/);

	const routing = fs.readFileSync(path.join(repoDir, "rules/workflow-routing.md"), "utf8");
	assert.match(routing, /orchestrator:\s*thin|subagent tool/i);

	const magicMode = fs.readFileSync(path.join(repoDir, "skills/magic-mode/SKILL.md"), "utf8");
	assert.match(magicMode, /depth\s*1|depth-1/i);
	assert.match(magicMode, /models\.json/);
	assert.doesNotMatch(magicMode, /\bcreate-skill\b/);

	const sicko = fs.readFileSync(path.join(repoDir, "agents/comment-sicko/agent.md"), "utf8");
	assert.doesNotMatch(sicko, /run `\/how`, `\/why`, or both/i);
	assert.match(sicko, /NEEDS-GROUNDING/);
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test tests/thin-orchestrator.test.mjs`
Expected: FAIL on missing `orchestrator: thin`.

- [ ] **Step 3: Implement Task 1 updates across the 6 files**

Keep `rules/workflow-routing.md` body under `250` words and preserve Variant C output rules in `skills/magic-mode/SKILL.md`.

- [ ] **Step 4: Run tests and validator**

Run: `node --test tests/thin-orchestrator.test.mjs tests/writing-rules.test.mjs tests/output-format-skills.test.mjs && ./scripts/validate.sh`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add skills/using-magic/SKILL.md rules/workflow-routing.md skills/magic-mode/SKILL.md agents/magic-agent/agent.md agents/comment-sicko/agent.md skills/magic-help/SKILL.md tests/thin-orchestrator.test.mjs
git commit -m "feat(routing): add flat depth-1 thin-orchestrator routing and flatten comment-sicko"
```

---

### Task 2: Flagship Multi-Agent & Research Wave Conversion (`/research`, `/why`, `/arena`, `/architect`, `/no-comments`, `/interrogate`, `/blast-radius`)

**Files:**

- Modify: `skills/research/SKILL.md:20-164`, `agents/{research-planner,research-synthesizer,researcher-deep}/agent.md`, `skills/research-summary/SKILL.md:10-30`
- Modify: `skills/why/SKILL.md:24-35`
- Modify: `skills/arena/SKILL.md:14-49`, `skills/architect/SKILL.md:22-77`, `skills/no-comments/SKILL.md:18-25`, `skills/interrogate/SKILL.md:15-36`, `skills/blast-radius/SKILL.md:30-53`
- Test: `tests/thin-orchestrator.test.mjs`

**Interfaces:**

- Consumes: `researcher-lite, collectors`, `researcher-mid`, `researcher-deep, planner, synthesizer`, `arena synthesizer`, `comment-sicko`, `hardest tasks`, `judgment and prose`, `feature, refactoring` from `model-roles.md`.
- Produces:
  - `skills/research/SKILL.md` + `agents/research*.md`: binds every research subagent to `magic-models`; reconciles tool access on `researcher-deep` and `research-synthesizer` while keeping `research-planner` strictly thinking-only; routes Tier 2 synthesis + `docs/research/<topic>.md` write through `research-synthesizer`; explicitly invokes `research-planner` by ID in Tier 3 Step 3.
  - `skills/research-summary/SKILL.md`: replaces missing `simple-english` (`:14`) with `/technical-writing` + `/unslop`, and routes formatting through `research-synthesizer`.
  - `skills/why/SKILL.md`: moves Step 2 (`git blame`, `git log --follow -p`, PR history) into a Wave 1 `researcher-lite, collectors` Anchor Collector subagent writing `code-anchor.md` to scratch.
  - `skills/arena/SKILL.md` & `skills/architect/SKILL.md`: adds mandatory Phase D+E `arena synthesizer` (`deep`) `magic-agent` wave for base selection, red-flag screening, and grafting (using `orchestrator:` in `magic-models` when parent model is hidden), and dispatches `architect` Phase D (`:52-55`) coding to a `feature, refactoring` / `hardest tasks` `magic-agent`.
  - `skills/no-comments/SKILL.md`, `skills/interrogate/SKILL.md`, `skills/blast-radius/SKILL.md`: names `comment-sicko` role and delegates `no-comments` Steps 2-4 refactoring to `magic-agent`; delegates `interrogate` repro-reruns & report merging to `judgment and prose`; delegates `blast-radius` Steps 1-5 tracing + proof script to a `hardest tasks` `magic-agent` (or `arena` panel).

- [ ] **Step 1: Extend `tests/thin-orchestrator.test.mjs` with failing assertions for Task 2**

Assert `skills/research/SKILL.md` names `research-planner`, `researcher-lite, collectors`, `researcher-mid`, and `researcher-deep, planner, synthesizer`; `skills/research-summary/SKILL.md` omits `simple-english`; `skills/arena/SKILL.md` names `arena synthesizer`; `skills/architect/SKILL.md` Phase D dispatches `magic-agent`; `skills/no-comments/SKILL.md` names `comment-sicko` role and delegates Steps 2-4; `skills/why/SKILL.md` delegates Step 2 Anchor collection.

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test tests/thin-orchestrator.test.mjs`
Expected: FAIL on missing `research-planner` and `arena synthesizer` bindings.

- [ ] **Step 3: Implement Task 2 updates across the 11 files**

Preserve `take-a-step-back` in `research/SKILL.md` and `architect/SKILL.md` and Variant C output rules across all `OUTPUT_FORMAT_FILES`.

- [ ] **Step 4: Run tests and validator**

Run: `node --test tests/thin-orchestrator.test.mjs tests/magic-sync.test.mjs tests/output-format-skills.test.mjs && ./scripts/validate.sh`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add skills/research/SKILL.md agents/research-planner/agent.md agents/research-synthesizer/agent.md agents/researcher-deep/agent.md skills/research-summary/SKILL.md skills/why/SKILL.md skills/arena/SKILL.md skills/architect/SKILL.md skills/no-comments/SKILL.md skills/interrogate/SKILL.md skills/blast-radius/SKILL.md tests/thin-orchestrator.test.mjs
git commit -m "feat(skills): convert research, why, arena, architect, no-comments, interrogate, and blast-radius to flat waves"
```

---

### Task 3: Convert `21` `/magic-mode` Playbooks & `/autopilot` to Flat Depth-1 Waves + Tighten Validator `BANNED` Regex

**Files:**

- Modify: `skills/magic-mode/playbooks/{feature,bug-fix,perf-issue,hillclimb,refactoring,prototype,visual-parity,authoring-a-skill,eval,runtime-forensics,trace-forensics,investigation,babysit,shipping,autonomous-run,multi-phase-plan,orchestrate,autopilot-full,autopilot-stack,session-pickup,opening-a-pr}.md`
- Modify: `skills/autopilot/SKILL.md:35-145`
- Modify: `scripts/validate.sh:152-158`
- Test: `tests/thin-orchestrator.test.mjs`

**Interfaces:**

- Consumes: `feature, refactoring`, `bug-fix`, `perf-issue`, `hillclimb`, `fast, mechanical, miners`, `swarm workers`, `judgment and prose`, `hardest tasks`, `arena cross-judge pool` from `model-roles.md`.
- Produces:
  - Flattened depth-1 playbooks: removes nested owner fan-out in `feature.md:19`, depth-2 `/no-comments` inside PR owners in `autopilot-full.md:10` / `opening-a-pr.md:32` (root coordinator dispatches `comment-sicko` at depth 1 at `code-ready`), and depth-2 sub-coordinators in `orchestrate.md:11` when harness depth is 1; names explicit `magic-models` roles for every helper (`fast, mechanical, miners` for transcript/trace miners and watchers; `judgment and prose` for `babysit` triage, `eval` rubric/audit, `authoring-a-skill` (`writing-skills`), `multi-phase-plan` authoring, `autopilot-full` gate countersigns, and Wave 5 commit-splitting + PR body + reply draft in `opening-a-pr.md`; `feature, refactoring` / `bug-fix` for `prototype`, `visual-parity`, `shipping` rebases, `babysit` fixes, and `autonomous-run` iterations).
  - `skills/autopilot/SKILL.md`: removes leaked `Claude Opus 5.5 xhigh` (`:95`) and deleted rule names (`:83-84`), and delegates merge-conflict resolution (`Wave 1`), CI + bot triage (`Wave 2`), and batched `fix-now` edits (`Wave 3`) to leaf subagents while main enforces numeric `growth_budget` and 2-pass stop gates.
  - `scripts/validate.sh:152-158`: extends `BANNED` regex to catch capitalized vendor prose names (`\bClaude (?:Opus|Sonnet|Haiku)\b`, `\bGPT-[0-9]`, `\bGemini [0-9]`, `\bGrok [0-9]`).

- [ ] **Step 1: Extend `tests/thin-orchestrator.test.mjs` with failing assertions for Task 3**

Assert `skills/autopilot/SKILL.md` does not match `/Claude Opus|python-docstrings-google|minimal-changes/`, delegates conflict resolution and `fix-now` implementation to subagents, `babysit.md`, `prototype.md`, `multi-phase-plan.md`, and `opening-a-pr.md` name `magic-models` subagent waves, `feature.md` has no internal nested owner fan-out, and `scripts/validate.sh` rejects `Claude Opus 5.5` in skill text.

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test tests/thin-orchestrator.test.mjs`
Expected: FAIL on `Claude Opus 5.5` in `skills/autopilot/SKILL.md:95`.

- [ ] **Step 3: Implement Task 3 updates across the 21 playbooks, `skills/autopilot/SKILL.md`, and `scripts/validate.sh`**

Strictly preserve `## Topology`, `## Supervision`, and `isolated-worktree subagents` in `orchestrate.md` (`tests/magic-sync.test.mjs:103-105`), `/make-pr-easy-to-review` and zero dashes / zero mid-sentence colons on matching lines in `multi-phase-plan.md` (`tests/magic-sync.test.mjs:153-159`), and `take-a-step-back` in all 6 checked playbooks (`tests/magic-sync.test.mjs:179-185`).

- [ ] **Step 4: Run tests and validator**

Run: `node --test tests/thin-orchestrator.test.mjs tests/magic-sync.test.mjs tests/pr26-regressions.test.mjs && ./scripts/validate.sh`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add skills/magic-mode/playbooks/ skills/autopilot/SKILL.md scripts/validate.sh tests/thin-orchestrator.test.mjs
git commit -m "feat(playbooks): convert 21 playbooks and autopilot to flat depth-1 waves and tighten validator"
```

---

### Task 4: Direct Adaptation of Upstream Skills (`writing-plans`, `subagent-driven-development`, `writing-skills`, `make-pr-easy-to-review`, `thermo-nuclear-code-quality-review`) & Un-Ignoring Validation

**Files:**

- Modify: `skills/writing-plans/SKILL.md:1-204`
- Modify: `skills/subagent-driven-development/SKILL.md:1-339`, `implementer-prompt.md`, `task-reviewer-prompt.md`, `re-review-prompt.md`, `references/{preflight,fix-loop,final-review}.md`
- Modify: `skills/writing-skills/SKILL.md:1-399`
- Modify: `skills/make-pr-easy-to-review/SKILL.md:1-59`, `skills/thermo-nuclear-code-quality-review/SKILL.md:1-192`
- Modify: `scripts/magic-verbatim.txt`, `scripts/validate.sh:122-170`, `THIRD-PARTY-NOTICES.md:3-12,103-109`, `lychee.toml:12-16`, `.markdownlint-cli2.jsonc:18-22`, `.typos.toml:1-6`, `tests/magic-sync.test.mjs:132-163`
- Test: `tests/thin-orchestrator.test.mjs`, `tests/magic-sync.test.mjs`

**Interfaces:**

- Consumes: `fast, mechanical, miners`, `feature, refactoring`, `sdd reviewer`, `hardest tasks`, `judgment and prose`, `arena cross-judge pool` from `model-roles.md`; `forge-operations.md`; `harness-adapter.md`.
- Produces:
  - Sorted frontmatter (`description`, `name`) across all 5 `SKILL.md` files (eliminating all 5 `./scripts/validate.sh` `WARN` lines).
  - `skills/writing-plans/SKILL.md`: replaces `superpowers:*` refs with `/subagent-driven-development` and `/magic-mode`; dispatches Wave 1 `how explorer`s + Wave 2 `hardest tasks` / `judgment and prose` Plan Author & Reviewer subagent under `# orchestrator: thin`; recommends Subagent-driven execution under `thin` mode.
  - `skills/subagent-driven-development/`: binds `## Model Selection` (`:140-176`) and prompt templates to `magic-models` (`fast, mechanical, miners`, `feature, refactoring`, `sdd reviewer`, `hardest tasks`, `judgment and prose` / `arena cross-judge pool`), delegates `preflight.md` & `fix-loop.md` breaker rulings to a `judgment and prose` adjudicator subagent, and fixes broken `../../requesting-code-review/code-reviewer.md` (`references/final-review.md:14` -> `../task-reviewer-prompt.md`) and `superpowers:*` references.
  - `skills/writing-skills/SKILL.md`: fixes `../using-superpowers/...` links (`:12`) -> `../magic-mode/references/harness-adapter.md` and `superpowers:test-driven-development` -> `/tdd`, maps RED/GREEN pressure subagents to `arena cross-judge pool`, and delegates skill drafting to `judgment and prose` under `thin` mode.
  - `skills/make-pr-easy-to-review/SKILL.md` & `skills/thermo-nuclear-code-quality-review/SKILL.md`: replaces `gh pr` commands (`:23`) with `forge-operations.md` operations (`view PR`, `edit PR`), adds depth-1 subagent execution (`judgment and prose` / `feature, refactoring` and `hardest tasks` / `interrogate reviewers`), clears file paths from `scripts/magic-verbatim.txt`, lifts exclusions in `scripts/validate.sh:168`, `lychee.toml`, and `.markdownlint-cli2.jsonc`, and updates `THIRD-PARTY-NOTICES.md` ("adapted from...") + `tests/magic-sync.test.mjs:161-163`.

- [ ] **Step 1: Extend `tests/thin-orchestrator.test.mjs` and update `tests/magic-sync.test.mjs:161-163` with failing assertions**

Assert `./scripts/validate.sh` outputs zero `WARN` lines and zero `FAIL` lines with `scripts/validate.sh:168` exclusions removed; `subagent-driven-development/SKILL.md` references `sdd reviewer` and `fast, mechanical, miners`; `references/final-review.md` has no `requesting-code-review` link; `make-pr-easy-to-review/SKILL.md` has no `gh pr` command; and `THIRD-PARTY-NOTICES.md` states `adapted from`.

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test tests/thin-orchestrator.test.mjs`
Expected: FAIL on `WARN` lines, `gh pr`, and `requesting-code-review`.

- [ ] **Step 3: Implement Task 4 adaptations across the 5 skills, validator, notices, and lint configs**

Keep `skills/writing-skills/render-graphs.js` intact (`tests/test_install.py:83`).

- [ ] **Step 4: Run validator, unit tests, and markdownlint**

Run: `./scripts/validate.sh && python3 -m unittest discover -s tests && node --test tests/*.test.mjs && npx --yes markdownlint-cli2`
Expected: PASS with `0` `WARN` lines and `0` markdownlint errors.

- [ ] **Step 5: Commit**

```bash
git add skills/writing-plans/ skills/subagent-driven-development/ skills/writing-skills/ skills/make-pr-easy-to-review/ skills/thermo-nuclear-code-quality-review/ scripts/magic-verbatim.txt scripts/validate.sh THIRD-PARTY-NOTICES.md lychee.toml .markdownlint-cli2.jsonc .typos.toml tests/magic-sync.test.mjs tests/thin-orchestrator.test.mjs
git commit -m "feat(skills): adapt superpowers and pr-review skills natively to magic-models and flat waves"
```

---

### Task 5: Standalone Skills, 4-Wave Formal Verification (`PDD`), & Repo Drift Cleanup

**Files:**

- Modify: `skills/{teach,recall,ketchup,ketchup-video,correct,figure-it-out,automate-me,reflect,show-me-your-work,writing-rules,create-verification-skill,maintain-verification-skill,create-formal-verification-skill,maintain-formal-verification-skill}/SKILL.md`
- Modify: `skills/{proof-driven-development,proving-with-hoare-logic,proving-with-dependent-types,model-checking-protocols-and-code,analyzing-with-abstract-interpretation,auditing-proof-specifications,statechart}/SKILL.md`
- Modify: `docs/adr/{0004-mattpocock-main-flow,0005-combined-two-tier-code-review,0008-pstack-port}.md`, `docs/magic-guide/{README,02-magic-mode,05-build-and-clean,09-make-it-yours}.md`, `lychee.toml:13-14`, `scripts/validate.sh:122-130`
- Test: `tests/thin-orchestrator.test.mjs`, `tests/proof-skills.test.mjs`

**Interfaces:**

- Consumes: `fast, mechanical, miners`, `judgment and prose`, `hardest tasks`, `swarm workers`, `arena cross-judge pool`, `why investigators`, `why synthesizer` from `model-roles.md`; `skills/auditing-proof-specifications/scripts/verify-spec-lock.mjs` and `check-proof-cheats.mjs`.
- Produces:
  - Explicit role bindings & wave delegation on remaining standalone skills: `recall` (`fast, mechanical, miners` miners + `why synthesizer` / `judgment and prose` brief synthesizer), `automate-me` (`fast, mechanical, miners` miners + `judgment and prose` `<handle>-mode` author via `/writing-skills`), `reflect` (replaces `create-skill` with `/writing-skills` and delegates approved edits to `judgment and prose`), `teach` (`judgment and prose` Teacher synthesizer), `ketchup-video` (`feature, refactoring` / `judgment and prose` slide/video builder), `show-me-your-work` (merges inline transcript scan `:58-64` into subagent and binds trail reviewer to `arena cross-judge pool`), `figure-it-out` (`hardest tasks` playbook architect + `arena cross-judge pool` unit judges), `correct` (`why investigators` miners + `hardest tasks` / `feature, refactoring` implementer), `writing-rules` (`arena cross-judge pool` RED/GREEN testers + `judgment and prose` drafter), `create/maintain-verification-skill` (`fast, mechanical, miners` source wave + `feature, refactoring` author + cold-start `swarm workers` verifier), and `create/maintain-formal-verification-skill` (`hardest tasks` author + cold-start `swarm workers` mutant prover).
  - **4-Wave PDD Pipeline** across `proof-driven-development`, its 5 child proof skills, and `statechart`: Wave 1 (`hardest tasks`) authors spec + vacuity witness / `--view` statechart; Wave 2 (`hardest tasks` / `swarm workers`) runs 3-Gate Spec-vs-Reference validation; **Main Dispatcher runs deterministic `node skills/auditing-proof-specifications/scripts/verify-spec-lock.mjs --generate`**; Wave 3 (`hardest tasks`) synthesizes proof & implementation; Wave 4 (`arena cross-judge pool` cross-family auditor) runs `verify-spec-lock.mjs --check`, `check-proof-cheats.mjs`, and `#print axioms`.
  - Repo drift cleanup: marks `ADR-0004` and `ADR-0005` superseded, updates `ADR-0008` (`magic-mode`, `25` principles, `0.15.36`, ported `tdd`/`typescript-best-practices`/`make-bot-ui`), removes `"tdd"` and `"create-skill"` from `EXTERNAL_SKILL_IDS` in `scripts/validate.sh:124-127` after replacing stale `create-skill` / external `/tdd` prose in `docs/magic-guide/`, and cleans up `lychee.toml:13-14`.

- [ ] **Step 1: Extend `tests/thin-orchestrator.test.mjs` and `tests/proof-skills.test.mjs` with failing assertions**

Assert `proof-driven-development/SKILL.md` defines the 4-wave subagent pipeline (`hardest tasks`, `arena cross-judge pool`, and main-dispatched `verify-spec-lock.mjs --generate` before Proof Synthesis); `recall/SKILL.md`, `automate-me/SKILL.md`, and `maintain-verification-skill/SKILL.md` reference `fast, mechanical, miners`; `show-me-your-work/SKILL.md` references `arena cross-judge pool`; zero active skills or `docs/magic-guide/*.md` files reference `create-skill` or `installed separately with the main flow` for `/tdd`; and `ADR-0005` carries a `Superseded` notice.

- [ ] **Step 2: Run tests to verify they fail**

Run: `node --test tests/thin-orchestrator.test.mjs tests/proof-skills.test.mjs`
Expected: FAIL on missing 4-wave PDD roles, `fast, mechanical, miners` in `recall`, and `create-skill` references.

- [ ] **Step 3: Implement Task 5 updates across standalone skills, PDD skills, ADRs, and guide docs**

Preserve all existing `tests/proof-skills.test.mjs` invariants, Variant C output-format sections (`tests/output-format-skills.test.mjs`), and `magic-help` skill links (`tests/magic-sync.test.mjs:111-129`, adding `/writing-skills`, `/writing-plans`, `/writing-rules`, and `/subagent-driven-development` to `magic-help`).

- [ ] **Step 4: Run the complete validation, unit test, node test, and lint gates**

Run: `./scripts/validate.sh && python3 -m unittest discover -s tests && node --test tests/*.test.mjs && npx --yes markdownlint-cli2`
Expected: PASS (`0` `FAIL`, `0` `WARN`, all Python and Node tests green, `0` markdownlint issues).

- [ ] **Step 5: Commit**

```bash
git add skills/ docs/ scripts/validate.sh lychee.toml tests/thin-orchestrator.test.mjs tests/proof-skills.test.mjs
git commit -m "feat(kit): complete thin-orchestrator waves across standalone and PDD skills and fix repo drift"
```
