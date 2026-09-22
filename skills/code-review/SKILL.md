---
description: Plan and perform code reviews of the changes since a fixed point. Two tiers: a fast two-axis review (Standards + Spec) and a deep specialist panel with false-positive filtering, walkthrough, and applied fixes. Use when reviewing a branch, PR, diff, or when the user asks for a code review.
enabled: true
id: code-review
name: code-review
---

# Code Review (two-tier)

One skill, two tiers, chosen by triage. The tiers cover different gaps and share one pipeline shape: pin the diff, dispatch parallel subagents, filter and present findings.

- **Standard tier** — two-axis review. Fast, two subagents: does the code follow the repo's documented standards, and does it implement what the spec asked?
- **Deep tier** — everything in the standard tier **plus** a planner-selected panel of specialist reviewers (security, correctness, performance, architecture, test quality, deployment safety, simplification, organization) and a verifier that filters false positives before you see anything, with walkthrough and opt-in fix application.

The kit pins no models (ADR-0001): run subagents on the harness's configured subagent model, per `rules/subagents.md`. Named agents are defined in `agents/`; if a named type is unavailable, use the harness's generic agent with that agent definition inlined.

## 1. Pin the scope

Determine what to review using this priority:

1. **User specifies scope** — fixed point (commit SHA, branch, tag), PR number/URL, or file paths
2. **On a feature branch** — all changes vs the default branch (`git diff main...HEAD`)
3. **Staged changes** — `git diff --staged`
4. **Unstaged changes** — `git diff`
5. **Latest commit** — `git show HEAD`

Capture the diff command once (three-dot against the merge-base when comparing branches) plus the commit list (`git log --oneline`). Confirm the fixed point resolves and the diff is non-empty before dispatching anything — a bad ref should fail here, not inside parallel subagents.

## 2. Tier triage

State the tier in one line before proceeding. Default is **standard**; go **deep** when any hold:

- Security, auth, or permission boundaries are touched
- Schema changes, migrations, or deploy sequencing
- Concurrency or state-machine behavior
- Cross-service contracts or multi-repo interactions
- Large, heterogeneous, or ambiguous changesets
- The user asks for a deep, thorough, or exhaustive review

When genuinely on the fence, pick standard and say so.

## 3. Find the spec source (both tiers)

Look for the originating spec, in this order:

1. Issue references in commit messages (`#123`, `Closes #45`, GitLab `!67`), fetched via the workflow in `docs/agents/issue-tracker.md`.
2. A path the user passed as an argument.
3. A spec file under `docs/`, `specs/`, or `.scratch/` matching the branch or feature.
4. Nothing found → ask the user where the spec is. If there isn't one, the Spec axis reports "no spec available" and is skipped.

## Standard tier

### Standards subagent

Prompt must include:

- The diff command and commit list.
- The standards-source files found in the repo (CODING_STANDARDS.md, CONTRIBUTING.md, `rules/` files the consumer keeps, etc.).
- The smell baseline pasted in full (the sub-agent has no other access to it).
- The brief: report, per file/hunk, (a) every violation of a documented standard — cite the standard (file + rule); (b) any baseline smell — name it and quote the hunk. Documented-standard breaches can be hard; baseline smells are always judgement calls, and a documented repo standard overrides the baseline. Skip anything tooling already enforces. Under 400 words.

The **smell baseline** (Fowler, _Refactoring_ ch. 3; each reads _what it is_ → _how to fix_):

- **Mysterious Name**: a name that doesn't reveal what it does or holds → rename; no honest name means the design's murky.
- **Duplicated Code**: the same logic shape in more than one hunk or file → extract the shared shape.
- **Feature Envy**: a method that reaches into another object's data more than its own → move it onto the data it envies.
- **Data Clumps**: the same few fields/params keep travelling together → bundle into one type.
- **Primitive Obsession**: a primitive standing in for a domain concept → give the concept its own small type.
- **Repeated Switches**: the same switch on the same type recurs → polymorphism, or one shared map.
- **Shotgun Surgery**: one logical change forces scattered edits → gather into one module.
- **Divergent Change**: one module edited for several unrelated reasons → split it.
- **Speculative Generality**: abstraction for needs the spec doesn't have → delete it.
- **Message Chains**: long `a.b().c().d()` navigation → hide the walk behind one method.
- **Middle Man**: a class that mostly delegates onward → cut it.
- **Refused Bequest**: an implementer that ignores most of what it inherits → composition over inheritance.

### Spec sub-agent

Prompt must include the diff command, commit list, and the spec (path or fetched contents):

- (a) requirements the spec asked for that are missing or partial;
- (b) behaviour in the diff that wasn't asked for (scope creep);
- (c) requirements that look implemented but where the implementation looks wrong.

Quote the spec line for each finding. Under 400 words. If the spec is missing, skip this sub-agent and note it in the report.

### Aggregate

Present findings under `## Standards` and `## Spec` headings, verbatim or lightly cleaned. **Never merge or rerank across axes** — a change can pass one axis and fail the other, and merging lets one mask the other. End with a one-line summary per axis: total findings and the worst issue in that axis.

## Deep tier

### Plan (mandatory)

Run exactly one **Code Review Planner** (`cr-planner`). Pass it the diff, changed paths, change purpose, the spec source found in step 3, user priorities, and prior verifier findings when re-reviewing. It returns the selected reviewer set, focus briefs, verifier instructions, and any justified upgrade candidates. Treat **Code Organization** as a default pick whenever the diff adds files, moves or renames symbols, or introduces helpers.

### Review (parallel)

Launch the planner-selected reviewers in one message, each with the diff, changed paths, and its planner-authored focus brief. Every reviewer is read-only and returns structured findings or an exact "no issues" string.

| Agent | Domain |
| ------- | -------- |
| `cr-security` | Injection, auth, secrets, data exposure |
| `cr-correctness` | Logic bugs, edge cases, None handling |
| `cr-performance` | N+1 queries, blocking ops, memory, hot paths |
| `cr-architecture` | SRP, coupling, layering, cross-service contracts |
| `cr-test-quality` | Coverage gaps, anti-patterns, test ROI |
| `cr-deployment-safety` | Migrations, deploy order, feature flags, rollback |
| `cr-simplification` | Over-engineering, duplication, change atomicity |
| `cr-organization` | File/folder placement, module homes, moved-symbol hygiene |

Deep tier additionally runs the two standard-tier axes (Standards and Spec subagents) in the same parallel wave — the specialist panel does not replace them.

### Verify (mandatory)

Launch the **Code Review Verifier** (`cr-verifier`) with the diff, the planner's verifier instructions, and all reviewer outputs attributed by source (`[Security]`, `[Correctness]`, …). It tags every finding — not just blockers — as `confirmed`, `false_positive`, or `needs_rephrase`. Process: `confirmed` → include; `needs_rephrase` → apply rephrase, include; `false_positive` → list under "Findings rejected by verifier" with its reason (the user may override).

### Synthesize

1. Collect confirmed and rephrased findings.
2. Deduplicate — two reviewers flagging the same issue from different angles merge into one finding with both perspectives.
3. Categorize: show-stopper bugs, architectural concerns, smaller suggestions, nits.
4. Rank within each category by severity.
5. Collapse clean reviewers into a one-line All Clear section.
6. Produce the curated summary. Keep the Standards/Spec axes as their own sections within it — the axes still never merge into each other.

**Output format** (omit empty sections):

```text
## Code review summary

**Verdict**: Ready to Merge | Needs Attention | Needs Work
**Counts**: N blockers • N suggestions • N nits • N findings rejected by verifier

## The big picture
<1-2 sentence framing>

## Show-stopper bugs
N. **<title>** — `file:line`. <explanation + suggested fix>

## Architectural concerns
N. **<title>**. <explanation + approach>

## Standards
<standards-axis findings>

## Spec
<spec-axis findings>

## Smaller suggestions
- <terse one-liner with `file:line`>

## Nits
- <one-liner per finding>

## Findings rejected by verifier
- <terse one-liner + verifier's reason>

## All Clear
- <reviewer>: <one-line summary>

---
Reply with your decisions, or say "walk me through" to step through each blocker.
```

### Walkthrough mode

Triggered by the user saying "walk me through" after the summary. For each blocker in order: re-state in full (title, `file:line`, code excerpt, what the verifier confirmed) → explain why it blocks → propose 1-3 specific fixes with trade-offs → ask Accept fix / Reject (with reason) / Discuss / Next → record the decision in chat. After all blockers, offer to walk suggestions. Then summarize captured decisions and move to the fix step.

### Fix step (opt-in)

Surface the captured decision list and confirm:

```text
Apply N approved fixes now via the implementer subagent? [yes / no / edit list]
```

- **yes** → launch the **Code Review Implementer** (`cr-implementer`) with the diff and the approved fixes; it edits source files in place and returns a summary. Report it back, then suggest re-running `/code-review` and the project's tests to verify nothing regressed.
- **no** → end; the user applies fixes manually.
- **edit list** → let the user toggle the apply-list and re-confirm.

### Verdict guidelines

- **Ready to Merge** — no blockers or suggestions; at most nits.
- **Needs Attention** — medium-severity issues or important suggestions worth addressing.
- **Needs Work** — critical/high blockers that must be fixed.

## Review-only mode

Enter when the user asks for it explicitly ("review only — don't walk through or fix") or when another skill invokes this skill and signals review-only intent. Run the full tier pipeline, emit the summary **without** the trailing walkthrough prompt, and halt — no walkthrough prompt, no fix step, no implementer.

## Scope boundaries

Only review files in the changeset. A finding outside the diff is an `out-of-scope:` note suggesting a follow-up, never a blocker.

## Communication style

- Use "we" or "this code" instead of "you". Explain the _why_ for every finding. Assume positive intent.
- Reviewer output is input, not deliverable: produce a curated summary scannable in one read, and drop into per-blocker mode when asked.
