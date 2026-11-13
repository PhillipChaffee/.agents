# System Design Skill Augmentations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the existing `magic` skill suite (`/architect`, `/arena`, `/interrogate`, `/benchmark-checklist`, `/blast-radius`, `/correct`, `magic-mode`, `playbooks/{system-design,refactoring,prototype}.md`, and `principle-*`) to execute a Staff-grade system design process across greenfield, extension, and reshape work—and support a 3-artifact design-only mode (`System Design Document`, validated `System Design Diagrams`, and `Implementation Plan`)—with zero new top-level skill directories.

**Architecture:** `skills/architect/SKILL.md` becomes a 2-axis right-sized orchestrator (`Context Mode` across greenfield, extension, and reshape $\times$ `Rigor Track` `S`, `M`, or `L`) backed by `references/quantitative-envelope.md` (6 deterministic capacity equations + 2026 hardware constants), `references/design-doc-template.md` (Diátaxis-separated SDD + Track-scoped Mermaid diagram rules), `scripts/check-mermaid.mjs` (zero-dependency diagram + `E1..En` DFMEA parity linter), updated `runner-prompt.md`, and 6 distributed red flags in `design-red-flags.md`. Parallel edits add orthogonal runner axes in `/arena`, Pre-Code Design Mode + 10-Class Postmortem Corpus in `/interrogate`, a stateful 6-Step Expand-Contract + Reverse-Sync carve-out in `principle-migrate-callers-then-delete-legacy-apis` and `refactoring.md`, and queueing-knee, rolling-deploy skew, and decreasing-budget checks across `/benchmark-checklist`, `/blast-radius`, and `/correct`.

**Tech Stack:** Markdown skill/rule files (`SKILL.md`, `rules/*.md`), zero-dependency Node.js (`node:test`, `node:assert/strict`, Node ESM), and `./scripts/validate.sh`.

**Spec:** `docs/research/kit-system-design-audit-and-augmentation.md` and `docs/research/design-doc-diagram-plan-output.md`

## Global Constraints

- Zero new top-level skills in `skills/`: keep `ALL_58_MAGIC_SKILLS.length === 58` in `tests/magic-sync.test.mjs` and `expectedSkillDirs.length === 74` in `tests/opencode-and-pi-plugins.test.mjs`.
- Follow `skills/writing-skills/SKILL.md`, `skills/technical-writing/SKILL.md`, and `skills/unslop/SKILL.md`: use positive recipes, tab-indented code snippets, straight quotes, zero em/en dashes, zero mid-sentence colons, zero prose slashes (write `"and"` / `"or"` instead of `a/b`), zero abstract metaphors (`"ratchet"`, `"evacuate"`, `"endgame"`), and observable predicates instead of subjective nuance clauses.
- Follow `skills/writing-rules/SKILL.md`: keep `rules/workflow-routing.md` frontmatter sorted (`alwaysApply`, `description`) and body under 150 words; keep `agents.kit.md` bullets at $\le 25$ words.
- Obey ADR-0001, ADR-0002, and ADR-0007 (`./scripts/validate.sh`): zero vendor model slugs, zero Cursor-only subagent fields, zero repo-relative `.cursor/` paths, zero language-specific config files in language-agnostic rules/skills, and zero forge CLIs.
- Preserve Variant C output-format invariants (`tests/output-format-skills.test.mjs`) on all 22 covered files and keep every file-count claim (`24 playbooks`, `74 active skills`) consistent across `docs/CATALOG.md`, `README.md`, and `docs/magic-guide/02-magic-mode.md`.
- Every task must pass `node --test` and `./scripts/validate.sh` with exit code `0` before committing.

## Review Focus

1. **Greenfield vs. Extension vs. Reshape routing:** `/architect` must branch by Context Mode so Greenfield defines a Problem Charter and boundaries instead of calling `/how` on nonexistent code, Extension runs `/how` on host seams, and Reshape runs both `/how` and `/why` before changing anything.
2. **Track S lightness:** Local in-process module/type changes (`Track S`) must bypass the 6 capacity equations, storage/metastability checks, standalone SDDs, and formal TLA+ models so agents don't choke on ceremony.
3. **In-memory vs. Stateful migration boundary:** Same-wave caller deletion must apply strictly to single-deploy-unit in-memory internal APIs; any persisted schema, queue payload, wire format, or rolling $N-1$ and $N+1$ boundary must route once to the canonical 6-Step Expand-Contract + Reverse-Sync protocol.
4. **Pre-code `/interrogate` truth bar:** When reviewing a pre-code design or plan, adversaries must be allowed to survive either via a runnable math/state-machine counterexample OR a cited contradiction/omission against `references/postmortem-corpus.md` or the design's DFMEA table (without inventing dummy `exit 1` scripts).
5. **Mermaid linter precision (`check-mermaid.mjs`):** Edge-to-DFMEA `E<N>` parity must match only explicit flowchart edge ID prefixes (`E1:`, `E2:`) so `E2E` labels and `sequenceDiagram`/`stateDiagram-v2` blocks never false-fail, and `Legend` nodes must be excluded from the `<= 15` node budget.

---

## File Map

| File Path | Action | Responsibility |
| --- | --- | --- |
| `tests/system-design-skills.test.mjs` | Create | Automated structural and behavioral tests across Tasks 1–5 (including running `quantitative-envelope.md` and `check-mermaid.mjs`). |
| `rules/workflow-routing.md` | Modify | Add `designing, architecting` and `systems` to `/magic-mode` triggers ($<150$ words). |
| `skills/using-magic/SKILL.md` | Modify | Mirror `designing, architecting` in the Entry-Point Routing table for `/magic-mode`. |
| `skills/magic-mode/SKILL.md` | Modify | Update Non-negotiables trigger (`system or subsystem design`) and register `System design.` in `## Playbooks`. |
| `skills/architect/references/quantitative-envelope.md` | Create | Phase 1 reference: Serial SLO, Data Gravity, 6 capacity/queueing equations, 2026 hardware constants, and runnable Node calculator. |
| `skills/architect/SKILL.md` | Modify | Add Phase 0 (Context Mode $\times$ Track `S`, `M`, `L`), Phase A envelope gate + opportunistic `CONTEXT.md` read, Phase B orthogonal axes, Phase C optional frontier grilling / Track L formal routing / `design-only` stop gate, and ADR/SDD output routing. |
| `skills/architect/references/runner-prompt.md` | Modify | Add Khononov Coupling Balance, Single-Quantum default, Split `decide` and `perform`, RUM + *WiscKey*, fencing tokens, Transactional Outbox, 5 metastability breakers, and TigerStyle bounds. |
| `skills/architect/references/design-red-flags.md` | Modify | Append 6 distributed/stateful red flags (`High-volatility distributed boundary`, `Uncoordinated dual-write`, `Unfenced lease or lock`, `Unbounded queue, loop, or retry`, `Control-plane dependency on the hot path`, `One-way write cutover without reverse sync`). |
| `skills/architect/references/rationale-template.md` | Modify | Keep as crisp 1-page Track S rationale with a conditional pointer directing Track M and Track L systems to `design-doc-template.md`. |
| `skills/arena/SKILL.md` | Modify | Add optional per-runner Orthogonal Constraint Axes in Phase A while scoring all candidates against one shared rubric in Phase C/D. |
| `skills/interrogate/references/postmortem-corpus.md` | Create | 10-class production postmortem checklist (`Bad Global Config` through `Rolling Deploy Wire Incompatibility`) and required defenses. |
| `skills/interrogate/SKILL.md` | Modify | Add Pre-Code Design Mode accepting runnable math/state probes or cited DFMEA/corpus omissions; handle designs with no uncommitted code diff cleanly. |
| `skills/principle-migrate-callers-then-delete-legacy-apis/SKILL.md` | Modify | Own the canonical distinction between single-deploy-unit in-memory APIs and persisted/wire/rolling boundaries, hosting the 6-Step Expand-Contract + Step 5 Async Reverse Sync protocol. |
| `skills/magic-mode/playbooks/refactoring.md` | Modify | Scope step 5 same-wave deletion strictly to in-memory internal APIs and link stateful/wire reshapes directly to `principle-migrate-callers-then-delete-legacy-apis`. |
| `skills/magic-mode/playbooks/prototype.md` | Modify | Add pure state-reducer (`decide(state, event)`) interactive scenario harness mode for domain-rule and state-machine forks. |
| `skills/principle-make-operations-idempotent/SKILL.md` | Modify | Add monotonic fencing tokens, idempotency TTL sizing, and Transactional Outbox or CDC. |
| `skills/principle-separate-before-serializing-shared-state/SKILL.md` | Modify | Add USL coherency ceiling ($N_{\max}$) and hot-key partition skew write-sharding / admission control. |
| `skills/benchmark-checklist/SKILL.md` | Modify | Link pre-design capacity checks to `quantitative-envelope.md` and add Question 8 (Kingman $\rho \le 0.70$ knee, tail fan-out, coordinated omission). |
| `skills/blast-radius/SKILL.md` | Modify | Extend Step 3 with $N-1$ and $N+1$ rolling-deploy wire skew, metastable amplification loops, and Shuffle Sharding $\binom{N}{k}$ blast radius. |
| `skills/correct/SKILL.md` | Modify | Add language-agnostic module-boundary/acyclicity CI checks and a decreasing legacy-usage budget (avoiding the banned `"ratchet"` metaphor). |
| `skills/architect/references/design-doc-template.md` | Create | Consolidated Diátaxis SDD template (Sections 0–8, `<= 1,200` words Track M, `1,500-2,500` words Track L) + Track-scoped Mermaid diagram rules (`flowchart LR`, `sequenceDiagram`, `stateDiagram-v2`, `<= 15` nodes, `E1..En` DFMEA table). |
| `skills/architect/scripts/check-mermaid.mjs` | Create | Zero-dependency Node ESM linter validating Markdown Mermaid fences, banned types, balanced blocks, `<= 15` non-legend nodes, and `E<N>` DFMEA parity. |
| `skills/magic-mode/playbooks/system-design.md` | Create | 3-artifact design-only playbook (`docs/designs/YYYY-MM-DD-<slug>.md` + validated Mermaid diagrams + `/writing-plans` implementation plan) that forbids production code edits and stops for review. |
| `skills/magic-help/SKILL.md` | Modify | Document the `System design` playbook and `/architect design-only` mode while keeping all 14 custom skill links intact. |
| `docs/CATALOG.md`, `README.md`, `docs/magic-guide/{02-magic-mode,04-design}.md` | Modify | Update playbook count (`23` to `24`), index `system-design.md`, and document Track `S/M/L` and pre-code `/interrogate`. |

---

### Task 1: Entry-Point Routing (`rules/workflow-routing.md`, `skills/using-magic/SKILL.md`, `skills/magic-mode/SKILL.md`)

**Files:**
- Modify: `rules/workflow-routing.md:10-16`
- Modify: `skills/using-magic/SKILL.md:26-33`
- Modify: `skills/magic-mode/SKILL.md:22,126-154`
- Create: `tests/system-design-skills.test.mjs`

**Interfaces:**
- Consumes: `skills/writing-rules/SKILL.md`, `tests/writing-rules.test.mjs`, `tests/output-format-skills.test.mjs`
- Produces: `tests/system-design-skills.test.mjs` and updated routing triggers for greenfield and brownfield system design tasks

- [ ] **Step 1: Write the failing test in `tests/system-design-skills.test.mjs`**

```javascript
import { spawnSync } from "node:child_process";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";

const repoRoot = path.resolve(import.meta.dirname, "..");

test("Task 1: workflow-routing, using-magic, and magic-mode route designing and architecting tasks cleanly", () => {
	const routing = fs.readFileSync(path.join(repoRoot, "rules/workflow-routing.md"), "utf8");
	const usingMagic = fs.readFileSync(path.join(repoRoot, "skills/using-magic/SKILL.md"), "utf8");
	const magicMode = fs.readFileSync(path.join(repoRoot, "skills/magic-mode/SKILL.md"), "utf8");
	assert.match(routing, /designing, architecting/i);
	assert.match(usingMagic, /designing, architecting/i);
	assert.match(magicMode, /system or subsystem design/i);
	assert.match(magicMode, /\*\*System design\.\*\*/);
	const fmEnd = routing.indexOf("\n---", 4);
	const bodyWords = routing.slice(fmEnd + 4).trim().split(/\s+/).filter(Boolean).length;
	assert.ok(bodyWords < 150, `workflow-routing.md body has ${bodyWords} words (max 149)`);
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test tests/system-design-skills.test.mjs`
Expected: FAIL with `AssertionError: The input did not match the regular expression /designing, architecting/i`

- [ ] **Step 3: Update `rules/workflow-routing.md`, `skills/using-magic/SKILL.md`, and `skills/magic-mode/SKILL.md`**

1. In `rules/workflow-routing.md:12` and `skills/using-magic/SKILL.md:28`, update the `/magic-mode` row to `Writing, designing, architecting, editing, debugging, refactoring, testing, reviewing, or shipping code, systems, docs, or configuration`. Keep `rules/workflow-routing.md` frontmatter keys sorted (`alwaysApply`, `description`) and body under 150 words.
2. In `skills/magic-mode/SKILL.md:22`, change `Code crossing a function boundary` to `Code crossing a function boundary, or a system or subsystem design` so non-code system design tasks trigger `architect`. Under `## Playbooks` (`lines 137-142`), add `- **System design.** Designing a new system, subsystem, or stateful change with a system design doc, diagrams, and implementation plan before coding. File: playbooks/system-design.md.`. Keep Variant C rules (`tests/output-format-skills.test.mjs`) intact.

- [ ] **Step 4: Run tests and validator**

Run: `node --test tests/system-design-skills.test.mjs tests/writing-rules.test.mjs tests/output-format-skills.test.mjs && ./scripts/validate.sh`
Expected: PASS (`OK validation passed`)

- [ ] **Step 5: Commit**

```bash
git add rules/workflow-routing.md skills/using-magic/SKILL.md skills/magic-mode/SKILL.md tests/system-design-skills.test.mjs
git commit -m "feat(routing): route greenfield and brownfield system design tasks to /magic-mode"
```

---

### Task 2: `/architect` 2-Axis Triage, Quantitative Envelope & Distributed Design Rules (`skills/architect/`)

**Files:**
- Create: `skills/architect/references/quantitative-envelope.md`
- Modify: `skills/architect/SKILL.md:1-82`
- Modify: `skills/architect/references/runner-prompt.md:1-21`
- Modify: `skills/architect/references/design-red-flags.md:1-56`
- Modify: `skills/architect/references/rationale-template.md:1-38`
- Test: `tests/system-design-skills.test.mjs`

**Interfaces:**
- Consumes: `skills/writing-skills/SKILL.md`, `skills/technical-writing/SKILL.md`, `skills/proving-with-hoare-logic/SKILL.md:32-45` (Split `decide` and `perform`), `skills/model-checking-protocols-and-code/SKILL.md`
- Produces: `skills/architect/references/quantitative-envelope.md` (with runnable Node calculator) + 2-axis Phase 0 (`Greenfield`, `Brownfield Extension`, `Brownfield Reshape` $\times$ `Track S`, `Track M`, `Track L`) + Track L formal/DST routing + 3-rule ADR persistence in `docs/adr/`

- [ ] **Step 1: Write the failing tests in `tests/system-design-skills.test.mjs`**

```javascript
test("Task 2: architect 2-axis triage, runnable quantitative-envelope calculator, 14 red flags, and rationale pointer work", () => {
	const arch = fs.readFileSync(path.join(repoRoot, "skills/architect/SKILL.md"), "utf8");
	const envRefPath = path.join(repoRoot, "skills/architect/references/quantitative-envelope.md");
	assert.ok(fs.existsSync(envRefPath), "missing skills/architect/references/quantitative-envelope.md");
	const envRef = fs.readFileSync(envRefPath, "utf8");
	const runner = fs.readFileSync(path.join(repoRoot, "skills/architect/references/runner-prompt.md"), "utf8");
	const redFlags = fs.readFileSync(path.join(repoRoot, "skills/architect/references/design-red-flags.md"), "utf8");
	const rationale = fs.readFileSync(path.join(repoRoot, "skills/architect/references/rationale-template.md"), "utf8");

	for (const token of [
		"## Phase 0: Triage",
		"Greenfield",
		"Brownfield Extension",
		"Brownfield Reshape",
		"Track S",
		"Track M",
		"Track L",
		"references/quantitative-envelope.md",
		"model-checking-protocols-and-code",
		"docs/adr/",
		"design-only",
	]) {
		assert.ok(arch.includes(token), `architect/SKILL.md missing ${token}`);
	}

	// Verify embedded Node calculator executes cleanly and prints key metrics
	const jsMatch = envRef.match(/```javascript\n([\s\S]*?)```/);
	assert.ok(jsMatch, "quantitative-envelope.md must contain a runnable ```javascript block");
	const run = spawnSync(process.execPath, ["-e", jsMatch[1]], { encoding: "utf8" });
	assert.equal(run.status, 0, `calculator failed: ${run.stderr}`);
	assert.match(run.stdout, /littlesLawDegradedConcurrency/);
	assert.match(run.stdout, /uslMaxNodes/);
	assert.match(run.stdout, /fanoutTailProbPct/);

	for (const rule of ["Coupling balance", "decide", "perform", "WiscKey", "fencing token", "Transactional Outbox", "retry token bucket", "singleflight", "Static Stability", "TigerStyle"]) {
		assert.match(runner, new RegExp(rule, "i"), `runner-prompt.md missing ${rule}`);
	}

	const h2Headings = redFlags.match(/^## .+$/gm) ?? [];
	assert.equal(h2Headings.length, 14, `expected 14 red-flag H2 sections, got ${h2Headings.length}`);
	assert.match(rationale, /design-doc-template\.md/);
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test tests/system-design-skills.test.mjs`
Expected: FAIL with `missing skills/architect/references/quantitative-envelope.md`

- [ ] **Step 3: Create `quantitative-envelope.md` and update `architect/SKILL.md`, `runner-prompt.md`, `design-red-flags.md`, and `rationale-template.md`**

Author cleanly per `/technical-writing` and `/unslop` (tab-indented code blocks, straight quotes, zero prose slashes):
1. `skills/architect/references/quantitative-envelope.md`: Document Serial Availability ($\prod A_i \ge \text{SLO}$), Data Gravity ($T_{\text{migration}} > \text{RTO} \implies$ Type-1 door), Peak QPS & Bandwidth, 3-Year RUM Storage ($WA$ and $SA$), Little's Law at degraded $p99$ ($L_{\max} = \lambda_{\text{peak}} \times W_{\text{degraded}}$), Kingman Queueing ($\rho \le 0.70$), Universal Scalability Law ($N_{\max} = \lfloor\sqrt{(1-\alpha)/\beta}\rfloor$), Tail-Latency Fan-Out ($1 - p^k$), the 2026 `napkin-math` physical constants table (`L1`–`L3`, `DRAM`, `NUMA`, `NVMe`, `Cross-AZ`, `EBS`, `S3 Express CAS`), and a tab-indented runnable ```` ```javascript ```` snippet computing `littlesLawDegradedConcurrency`, `uslMaxNodes`, and `fanoutTailProbPct`.
2. `skills/architect/SKILL.md`:
   - Add **Phase 0: Triage** with two compact tables: `Context Mode` (`Greenfield`, `Brownfield Extension`, `Brownfield Reshape`) and `Rigor Track` (`Track S`, `Track M`, `Track L`, stating explicitly that `Track S` bypasses `quantitative-envelope.md`, distributed red flags, and TLA+ routing), plus Serial Availability and Data Gravity checks.
   - Update **Phase A: Ground the problem** to branch on `Context Mode`: `Greenfield` defines the Problem Charter, external boundaries, and hard invariants without calling `how` on nonexistent code; `Brownfield Extension` runs `how` on host seams and reads `CONTEXT.md` if present; `Brownfield Reshape` runs both `how` and `why`. For `Track M` and `Track L`, run the calculator in `references/quantitative-envelope.md` and paste the computed output.
   - Update **Phase B: Sketch** so `Track M` and `Track L` assign orthogonal constraint axes to the `arena` runners (Runner 1: Single-Quantum Modular Monolith; Runner 2: Disaggregated scale, cellular isolation, and independent quotas; Runner 3: Failure, partition, skew, and metastability resilience).
   - Update **Phase C: Agree (opt-in)** to support `design-only` mode (stop before Phase D, used by `playbooks/system-design.md` or when invoked as `"/architect design-only"`), optional Design-Tree Frontier grilling during a checkpoint (resolve codebase facts via subagents first, then ask only the unblocked decision frontier with recommended answers), and Track L routing of stateful or concurrent protocols to `model-checking-protocols-and-code` or a seeded simulation harness before Phase D.
   - Update **Outputs** to keep Track S as usage + `not implemented` stubs + 1-page `rationale-template.md`, direct Track M and Track L design docs to `references/design-doc-template.md` under `docs/designs/YYYY-MM-DD-<slug>.md`, and persist `docs/adr/NNNN-<slug>.md` when the 3-rule ADR bar holds (hard to reverse, surprising without context, real tradeoff).
3. `skills/architect/references/runner-prompt.md`: Add 5 concise bullets covering Coupling balance ($\text{Pain} = S \times D \times V$, Single-Quantum Modular Monolith default), Split `decide` and `perform` cores, Storage and consistency explicitness for Track M and Track L (RUM spectrum, *WiscKey* value separation $>1\text{ KB}$, Snapshot Isolation write-skew audit, monotonic fencing tokens, Transactional Outbox), 5 Metastability breakers ($\le 10\%$ retry token bucket + full jitter, `singleflight` leases, reconnect surge bounds, deadline propagation with LIFO or CoDel load shedding, allocation-free error paths, Static Stability), and TigerStyle bounds (explicit static upper bounds, unit suffixes such as `timeout_ms`, paired positive and negative boundary assertions).
4. `skills/architect/references/design-red-flags.md`: Append the 6 H2 sections (`## High-volatility distributed boundary`, `## Uncoordinated dual-write`, `## Unfenced lease or lock`, `## Unbounded queue, loop, or retry`, `## Control-plane dependency on the hot path`, `## One-way write cutover without reverse sync`).
5. `skills/architect/references/rationale-template.md`: Keep the 1-page Track S structure intact and add a 1-line note under the title directing Track M and Track L designs to `design-doc-template.md` instead of duplicating template sections.

- [ ] **Step 4: Run tests and validator**

Run: `node --test tests/system-design-skills.test.mjs && ./scripts/validate.sh`
Expected: PASS (`OK validation passed`)

- [ ] **Step 5: Commit**

```bash
git add skills/architect/SKILL.md skills/architect/references/ tests/system-design-skills.test.mjs
git commit -m "feat(architect): add 2-axis right-sizing, quantitative envelope, distributed red flags, and ADR persistence"
```

---

### Task 3: Orthogonal Axes in `/arena` & Pre-Code Design Mode + Postmortem Corpus in `/interrogate`

**Files:**
- Modify: `skills/arena/SKILL.md:12-26`
- Create: `skills/interrogate/references/postmortem-corpus.md`
- Modify: `skills/interrogate/SKILL.md:10-38`
- Test: `tests/system-design-skills.test.mjs`

**Interfaces:**
- Consumes: `skills/architect/SKILL.md`, `tests/magic-sync.test.mjs:81-90` (`postmortem-corpus.md` allowed; retired filenames must stay absent), `tests/output-format-skills.test.mjs`
- Produces: Orthogonal runner axis option in `skills/arena/SKILL.md` and Pre-Code Design Mode + 10-class `references/postmortem-corpus.md` in `skills/interrogate/`

- [ ] **Step 1: Write the failing tests in `tests/system-design-skills.test.mjs`**

```javascript
test("Task 3: arena supports orthogonal constraint axes and interrogate supports pre-code probes plus 10-class postmortem corpus", () => {
	const arena = fs.readFileSync(path.join(repoRoot, "skills/arena/SKILL.md"), "utf8");
	assert.match(arena, /orthogonal constraint axes/i);

	const corpusPath = path.join(repoRoot, "skills/interrogate/references/postmortem-corpus.md");
	assert.ok(fs.existsSync(corpusPath), "missing skills/interrogate/references/postmortem-corpus.md");
	const corpus = fs.readFileSync(corpusPath, "utf8");
	const interrogate = fs.readFileSync(path.join(repoRoot, "skills/interrogate/SKILL.md"), "utf8");

	assert.match(interrogate, /references\/postmortem-corpus\.md/);
	assert.match(interrogate, /Pre-Code Design Mode/i);
	assert.match(interrogate, /DFMEA/i);

	for (const outageClass of [
		"Bad Global Config",
		"Downstream Gray Failure",
		"Retry and Reconnect Amplification Storm",
		"Cache Cold-Start",
		"Poison-Pill Input",
		"Clock Drift",
		"Asymmetric Network Partition",
		"Storage Compaction",
		"Hidden Resource Exhaustion",
		"Rolling Deploy Wire Incompatibility",
	]) {
		assert.ok(corpus.includes(outageClass), `postmortem-corpus.md missing ${outageClass}`);
	}
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test tests/system-design-skills.test.mjs`
Expected: FAIL with `AssertionError: The input did not match the regular expression /orthogonal constraint axes/i`

- [ ] **Step 3: Update `skills/arena/SKILL.md`, create `skills/interrogate/references/postmortem-corpus.md`, and update `skills/interrogate/SKILL.md`**

1. In `skills/arena/SKILL.md:14-26`: keep the shared prompt as default, and add an **Orthogonal constraint axes** option in Phase A and Phase B: when invoked for architecture exploration (such as `/architect` Track M and Track L), pass the shared problem contract plus a per-runner constraint axis while grading all candidates on the same Phase C and Phase D rubric.
2. Create `skills/interrogate/references/postmortem-corpus.md` with the 10-row production failure table (`Bad Global Config` through `Rolling Deploy Wire Incompatibility`), precedents, and required mechanical defenses.
3. In `skills/interrogate/SKILL.md:14-28`: preserve `"Adversaries try to break a change or a design"` (`tests/magic-sync.test.mjs:83`) and Variant C formatting (`tests/output-format-skills.test.mjs`), and add a **Pre-Code Design Mode** conditional:
   - When the scope is a design doc, sketch, or plan (not a code diff), pass the document path instead of copying git diffs, and evaluate adversaries against `references/postmortem-corpus.md`.
   - Under **Verify**, accept a pre-code finding ONLY if it passes one of two objective gates: (1) a runnable **quantitative or state-machine counterexample** script violating the design's stated numbers or invariants, OR (2) a **cited contract omission or contradiction** (`section:line` in the doc showing an exposed boundary edge in the DFMEA table or an applicable class in `references/postmortem-corpus.md` with no defense). Drop speculative risks and dummy scripts.

- [ ] **Step 4: Run tests and validator**

Run: `node --test tests/system-design-skills.test.mjs tests/magic-sync.test.mjs tests/output-format-skills.test.mjs && ./scripts/validate.sh`
Expected: PASS (`OK validation passed`)

- [ ] **Step 5: Commit**

```bash
git add skills/arena/SKILL.md skills/interrogate/SKILL.md skills/interrogate/references/postmortem-corpus.md tests/system-design-skills.test.mjs
git commit -m "feat(arena,interrogate): add orthogonal runner axes and pre-code postmortem corpus checks"
```

---

### Task 4: Stateful Migration Carve-Out, Principles, Prototype, Perf Knee, Blast Radius & CI Checks

**Files:**
- Modify: `skills/principle-migrate-callers-then-delete-legacy-apis/SKILL.md:1-18`
- Modify: `skills/magic-mode/playbooks/refactoring.md:10-15`
- Modify: `skills/magic-mode/playbooks/prototype.md:7-15`
- Modify: `skills/principle-make-operations-idempotent/SKILL.md:1-25`
- Modify: `skills/principle-separate-before-serializing-shared-state/SKILL.md:1-21`
- Modify: `skills/benchmark-checklist/SKILL.md:10-35`
- Modify: `skills/blast-radius/SKILL.md:30-42`
- Modify: `skills/correct/SKILL.md:18-32`
- Test: `tests/system-design-skills.test.mjs`

**Interfaces:**
- Consumes: `skills/architect/references/quantitative-envelope.md` (Task 2), `skills/technical-writing/SKILL.md:20` & `skills/unslop/SKILL.md:55` (no `"ratchet"` metaphor), `tests/output-format-skills.test.mjs`
- Produces: Canonical 6-Step Expand-Contract + Reverse-Sync rules in `principle-migrate-callers-then-delete-legacy-apis`, delegated cleanly from `refactoring.md`; pure-reducer mode in `prototype.md`; distributed invariants across principles, `/benchmark-checklist`, `/blast-radius`, and `/correct`

- [ ] **Step 1: Write the failing tests in `tests/system-design-skills.test.mjs`**

```javascript
test("Task 4: migration carve-out, principles, prototype, benchmark knee, blast-radius skew, and language-agnostic correct rules align", () => {
	const migrate = fs.readFileSync(path.join(repoRoot, "skills/principle-migrate-callers-then-delete-legacy-apis/SKILL.md"), "utf8");
	const refactoring = fs.readFileSync(path.join(repoRoot, "skills/magic-mode/playbooks/refactoring.md"), "utf8");
	const prototype = fs.readFileSync(path.join(repoRoot, "skills/magic-mode/playbooks/prototype.md"), "utf8");
	const idemp = fs.readFileSync(path.join(repoRoot, "skills/principle-make-operations-idempotent/SKILL.md"), "utf8");
	const sepState = fs.readFileSync(path.join(repoRoot, "skills/principle-separate-before-serializing-shared-state/SKILL.md"), "utf8");
	const bench = fs.readFileSync(path.join(repoRoot, "skills/benchmark-checklist/SKILL.md"), "utf8");
	const blast = fs.readFileSync(path.join(repoRoot, "skills/blast-radius/SKILL.md"), "utf8");
	const correct = fs.readFileSync(path.join(repoRoot, "skills/correct/SKILL.md"), "utf8");

	assert.match(migrate, /Expand-Contract/i);
	assert.match(migrate, /reverse sync/i);
	assert.match(refactoring, /Expand-Contract/i);
	assert.match(prototype, /pure reducer|state machine/i);
	assert.match(idemp, /fencing token/i);
	assert.match(idemp, /Transactional Outbox/i);
	assert.match(sepState, /Universal Scalability Law|N_max/i);
	assert.match(sepState, /hot-key|write-sharding/i);
	assert.match(bench, /quantitative-envelope\.md/);
	assert.match(bench, /coordinated omission/i);
	assert.match(blast, /rolling deploy|mixed-version/i);
	assert.match(blast, /shuffle sharding/i);
	assert.match(correct, /decreasing usage budget/i);
	assert.doesNotMatch(correct, /\bratchet\b/i);
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test tests/system-design-skills.test.mjs`
Expected: FAIL with `AssertionError: The input did not match the regular expression /Expand-Contract/i`

- [ ] **Step 3: Apply single-source-of-truth updates across the 8 files**

1. `skills/principle-migrate-callers-then-delete-legacy-apis/SKILL.md`: Add `## When NOT to apply (persisted, wire, or rolling boundaries)` stating that any change touching persisted schemas, storage formats, queues, cross-service RPCs, or rolling $N-1$ and $N+1$ deploys must follow the **6-Step Zero-Downtime Expand-Contract Protocol** (1. Expand, 2. Dual-write + version-guarded idempotent backfill, 3. Shadow dark-read parity, 4. Progressive read cutover, 5. Write cutover with asynchronous reverse sync back to the old store for lossless rollback, 6. Contract once baked).
2. `skills/magic-mode/playbooks/refactoring.md:11`: Scope same-wave deletion strictly to **single-deploy-unit in-memory internal APIs**, and delegate persisted, wire, or rolling-deploy reshapes directly to `principle-migrate-callers-then-delete-legacy-apis` without duplicating the 6 steps.
3. `skills/magic-mode/playbooks/prototype.md:8-10`: Add the pure state-reducer (`decide(state, event)`) + interactive scenario walkthrough option for domain-rule forks.
4. `skills/principle-make-operations-idempotent/SKILL.md:16-25`: Add monotonic fencing tokens (`generation_clock` checked by storage), idempotency key TTL sizing ($T_{\text{TTL}} \ge T_{\text{retry\_window}} + T_{\text{DLQ\_replay}}$), and Transactional Outbox or CDC.
5. `skills/principle-separate-before-serializing-shared-state/SKILL.md:16-21`: Add the USL coherency ceiling ($N_{\max}$) and hot-key partition skew mitigations (write-sharding across $K$ salted sub-keys or Global Admission Control token buckets).
6. `skills/benchmark-checklist/SKILL.md`: Link pre-design capacity math to `../architect/references/quantitative-envelope.md` and add Question 8 covering Kingman's $\rho \le 0.70$ knee, $p99$ tail fan-out, and open-loop arrival timing to avoid coordinated omission.
7. `skills/blast-radius/SKILL.md:35`: Append three distributed checks to Step 3: mixed-version $N-1$ and $N+1$ rolling-deploy skew, metastable amplification loops (retries, cache stampedes, reconnect storms, untested fallbacks), and Shuffle Sharding $\binom{N}{k}$ tenant blast radius.
8. `skills/correct/SKILL.md:20-25`: Keep language-agnostic per ADR-0002; under Level 1 and Level 2, name module entry-point and cycle checks in the project's boundary tool and a committed **decreasing usage budget** (`MAX_ALLOWED` counter that fails on growth and only decreases as legacy callers are removed). Do not use the banned `"ratchet"` metaphor (`unslop` rule 26).

- [ ] **Step 4: Run tests and validator**

Run: `node --test tests/system-design-skills.test.mjs tests/magic-sync.test.mjs tests/output-format-skills.test.mjs && ./scripts/validate.sh`
Expected: PASS (`OK validation passed`)

- [ ] **Step 5: Commit**

```bash
git add skills/principle-migrate-callers-then-delete-legacy-apis/SKILL.md skills/magic-mode/playbooks/refactoring.md skills/magic-mode/playbooks/prototype.md skills/principle-make-operations-idempotent/SKILL.md skills/principle-separate-before-serializing-shared-state/SKILL.md skills/benchmark-checklist/SKILL.md skills/blast-radius/SKILL.md skills/correct/SKILL.md tests/system-design-skills.test.mjs
git commit -m "feat(principles,verify): add Expand-Contract + Reverse Sync carve-out, fencing/USL rules, and queueing/skew checks"
```

---

### Task 5: 3-Artifact Design-Only Playbook, SDD + Diagram Template, Mermaid Linter & Guide Sync

**Files:**
- Create: `skills/architect/references/design-doc-template.md`
- Create: `skills/architect/scripts/check-mermaid.mjs`
- Create: `skills/magic-mode/playbooks/system-design.md`
- Modify: `skills/magic-help/SKILL.md` (`## Playbooks and principles` & `Close calls`)
- Modify: `docs/CATALOG.md:1-35`
- Modify: `README.md:113,136`
- Modify: `docs/magic-guide/02-magic-mode.md:3`
- Modify: `docs/magic-guide/04-design.md:1-131`
- Test: `tests/system-design-skills.test.mjs`

**Interfaces:**
- Consumes: `skills/architect/SKILL.md`, `skills/writing-plans/SKILL.md`, `skills/magic-mode/playbooks/multi-phase-plan.md`, `skills/technical-writing/SKILL.md`, `docs/research/design-doc-diagram-plan-output.md`
- Produces:
  - Consolidated `skills/architect/references/design-doc-template.md` (Sections 0–8 SDD skeleton + embedded Track-scoped Mermaid diagram rules)
  - Zero-dependency CLI `node skills/architect/scripts/check-mermaid.mjs <markdown-file>`
  - `skills/magic-mode/playbooks/system-design.md` chaining `/architect` (`design-only`) $\to$ `docs/designs/YYYY-MM-DD-<slug>.md` + validated Mermaid diagrams $\to$ optional `docs/adr/NNNN-<slug>.md` $\to$ `/writing-plans` (`docs/superpowers/plans/YYYY-MM-DD-<slug>.md`, using `multi-phase-plan.md` only when explicitly asked for a stacked multi-PR checklist over a runnable repo) $\to$ stop and present all three deliverables before coding

- [ ] **Step 1: Write the failing tests in `tests/system-design-skills.test.mjs`**

```javascript
test("Task 5: 3-artifact system-design playbook, design-doc template, check-mermaid linter, and synchronized counts/guides pass", () => {
	const playbook = path.join(repoRoot, "skills/magic-mode/playbooks/system-design.md");
	const sddTmpl = path.join(repoRoot, "skills/architect/references/design-doc-template.md");
	const checker = path.join(repoRoot, "skills/architect/scripts/check-mermaid.mjs");
	for (const p of [playbook, sddTmpl, checker]) {
		assert.ok(fs.existsSync(p), `missing ${path.relative(repoRoot, p)}`);
	}

	const pbText = fs.readFileSync(playbook, "utf8");
	assert.match(pbText, /docs\/designs\//);
	assert.match(pbText, /check-mermaid\.mjs/);
	assert.match(pbText, /writing-plans/);
	assert.match(pbText, /Do not create or edit application source or production test files/i);

	for (const [rel, pattern] of [
		["docs/CATALOG.md", /24 execution playbooks/],
		["README.md", /24 step-by-step playbooks/],
		["docs/magic-guide/02-magic-mode.md", /twenty-four playbooks/],
		["docs/magic-guide/04-design.md", /Track S/],
		["docs/magic-guide/04-design.md", /system-design\.md/],
	]) {
		const text = fs.readFileSync(path.join(repoRoot, rel), "utf8");
		assert.match(text, pattern, `${rel} missing ${pattern}`);
	}

	// Verify all check-mermaid.mjs rejection rules + non-false-positive behavior on E2E / Legend / sequenceDiagram
	const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "mermaid-check-"));
	try {
		const runCheck = (name, lines) => {
			const file = path.join(tmpDir, name);
			fs.writeFileSync(file, lines.join("\n"));
			return spawnSync(process.execPath, [checker, file], { encoding: "utf8" });
		};

		// 1. Missing E2 in DFMEA table fails
		assert.equal(runCheck("missing-edge.md", [
			"```mermaid", "flowchart LR", '  A -->|"E1: gRPC sync"| B', '  A -->|"E2: Kafka async"| C', "```",
			"| Edge ID | Protocol |", "| --- | --- |", "| E1 | gRPC |",
		]).status, 1);

		// 2. Banned diagram type (architecture-beta / C4Container) fails
		assert.equal(runCheck("arch-beta.md", ["```mermaid", "architecture-beta", "  service api", "```"]).status, 1);
		assert.equal(runCheck("c4.md", ["```mermaid", "C4Container", "  Container(a, \"API\")", "```"]).status, 1);

		// 3. Lowercase `end` node ID fails, and unbalanced subgraph fails
		assert.equal(runCheck("bad-end.md", ["```mermaid", "flowchart LR", "  start --> end", "```"]).status, 1);
		assert.equal(runCheck("unbalanced.md", ["```mermaid", "flowchart LR", '  subgraph Plane["Data"]', "    A --> B", "```"]).status, 1);

		// 4. >15 non-legend nodes fails
		const tooMany = ["```mermaid", "flowchart LR", ...Array.from({ length: 16 }, (_, i) => `  N${i}["Node ${i}"]`), "```"];
		assert.equal(runCheck("too-many.md", tooMany).status, 1);

		// 5. Valid Track M/L doc with Legend (>15 total tokens if Legend counted, <=15 real nodes), E2E prose, sequenceDiagram, and DFMEA passes
		const good = runCheck("good.md", [
			"```mermaid",
			"flowchart LR",
			'  subgraph DataPlane["Data Plane"]',
			'    API["API Gateway"] -->|"E1: gRPC sync"| DB[("Orders DB")]',
			'    API -.->|"E2: Kafka async"| W["Worker"]',
			'    W -->|"runs E2E check"| Sink["Audit"]',
			"  end",
			'  subgraph Legend["Legend"]',
			'    L1["Sync"] --> L2["Async"]',
			"  end",
			"```",
			"```mermaid",
			"sequenceDiagram",
			"  autonumber",
			"  API->>DB: write order",
			"```",
			"| Edge ID | Protocol |", "| --- | --- |", "| E1 | gRPC |", "| E2 | Kafka |",
		]);
		assert.equal(good.status, 0, `expected good.md to pass: ${good.stderr}`);
	} finally {
		fs.rmSync(tmpDir, { recursive: true, force: true });
	}
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test tests/system-design-skills.test.mjs`
Expected: FAIL with `missing skills/magic-mode/playbooks/system-design.md`

- [ ] **Step 3: Create `design-doc-template.md`, `check-mermaid.mjs`, and `system-design.md`, and update help/catalog/README/guides**

1. Create `skills/architect/references/design-doc-template.md`: combine the 9-section Diátaxis SDD template (Sections 0–8, `<= 1,200` words Track M, `1,500–2,500` words Track L, zero DDL dumps or task lists) with the Track-scoped Mermaid diagram rules directly inside Section 3 (`flowchart LR` with `subgraph` trust/blast-radius boundaries, `[(Store)]` cylinders, solid `-->` sync vs dashed `-.->` async arrows with `E1..En` prefixes, `subgraph Legend`, `sequenceDiagram` with `autonumber` + `alt` failure path, `stateDiagram-v2` for Track L lifecycles, `<= 15` non-legend nodes per diagram, banning `architecture-beta`/`C4Context`/`C4Container`, and 1:1 `E1..En` DFMEA table parity).
2. Create zero-dependency `skills/architect/scripts/check-mermaid.mjs` (Node ESM) checking every fenced ```` ```mermaid ```` block in the passed Markdown path:
   - Rejects `architecture-beta`, `C4Context`, and `C4Container`.
   - Rejects lowercase `end` used as a node ID (`/\bend\b/` on flowchart edge/declaration lines that are not block-closing `end`).
   - Checks balanced `subgraph`, `alt`, `opt`, `loop`, `par`, `critical`, `break`, and `rect` blocks against `end` lines.
   - Counts unique non-legend node IDs inside `flowchart` blocks (ignoring nodes declared inside `subgraph Legend`) and fails when count `> 15`.
   - Extracts explicit `E<N>` edge-label prefixes (`/\|\s*"?(E\d+)\s*[:|]/g`) from `flowchart` blocks and, when any `E<N>` edge exists, verifies each `E<N>` appears in a Markdown table cell (`/\|\s*E\d+\s*\|/`).
3. Create `skills/magic-mode/playbooks/system-design.md`: (1) Forbid creating or editing application source or production test files (allowing `/tmp` probes and envelope calculations); (2) Run `/architect` with `design-only` (Phase 0–C + optional Frontier Grill + Pre-Code `/interrogate` + Track L model check); (3) Write `docs/designs/YYYY-MM-DD-<slug>.md` per `design-doc-template.md` (skip standalone SDD on Track S) and run `node skills/architect/scripts/check-mermaid.mjs <file>`; (4) Persist `docs/adr/NNNN-<slug>.md` when the 3-rule ADR bar holds; (5) Run `/writing-plans` passing `**Spec:** docs/designs/...` into `docs/superpowers/plans/YYYY-MM-DD-<slug>.md` (use `playbooks/multi-phase-plan.md` only when explicitly asked for a stacked multi-PR checklist over a runnable repo); (6) Stop and return the exact paths to the System Design Document, System Design Diagrams, and Implementation Plan.
4. Update `skills/magic-help/SKILL.md`, `docs/CATALOG.md` (`24 execution playbooks` + `system-design.md` row), `README.md:113,136` (`24 step-by-step playbooks`, `24 playbooks`, keeping line 125 `pstack` historical note at `23`), `docs/magic-guide/02-magic-mode.md:3` (`twenty-four playbooks`), and `docs/magic-guide/04-design.md` (Track `S`, `M`, `L`, `system-design.md`, and pre-code `/interrogate`).

- [ ] **Step 4: Run the full repository test suite and kit validator**

Run: `node --test && python3 -m unittest discover -s tests && ./scripts/validate.sh`
Expected: PASS (`74` skill check in `opencode-and-pi-plugins.test.mjs` passes, `magic-sync.test.mjs` passes, `output-format-skills.test.mjs` passes, `test_install.py` passes, `system-design-skills.test.mjs` passes, and `./scripts/validate.sh` exits `0`)

- [ ] **Step 5: Commit**

```bash
git add skills/architect/references/design-doc-template.md skills/architect/scripts/check-mermaid.mjs skills/magic-mode/playbooks/system-design.md skills/magic-help/SKILL.md docs/CATALOG.md README.md docs/magic-guide/02-magic-mode.md docs/magic-guide/04-design.md tests/system-design-skills.test.mjs
git commit -m "feat(architect,magic-mode): add 3-artifact system-design playbook, SDD/diagram template, and mermaid linter"
```
