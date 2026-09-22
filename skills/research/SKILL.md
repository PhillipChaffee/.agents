---
description: >-
  Tiered research and planning workflow that first estimates a task's complexity,
  then runs the matching effort level: a direct answer for trivial asks, background
  or parallel research writing a cited file in the repo for standard ones, or a
  scoped research -> synthesis pipeline for complex ones. Use when the user asks
  to research, investigate, look into, dig into, figure out, scope, deep dive,
  compare options, or plan something, or otherwise needs information gathered and
  synthesized across the codebase, the web, or connected tools.
enabled: true
id: research
name: research
---

# Research (tiered orchestrator)

Always do **Step 0 (complexity triage)** first, then run exactly one tier. Scale
effort to the task: don't spin up subagents for a trivial question, and don't
hand-answer a broad investigation that deserves the full pipeline.

Subagents run in isolated contexts and do not see this conversation. Every prompt must restate
the goal, relevant context, sources, constraints, and expected output. The kit pins no models
(ADR-0001): run subagents on the harness's configured subagent model, per `rules/subagents.md`.
If the harness configures a deep-thinking tier, reserve it for the optional roles marked below —
thinking-only, complete evidence packet, tools forbidden.

## Step 0 - Complexity triage (always)

Score the request across four axes, then pick a tier:

- **Breadth** - how many distinct areas / files / sources are involved?
- **Depth** - how much reasoning, domain knowledge, or synthesis is required?
- **Ambiguity** - is the question well-formed, or does it need scoping first?
- **Stakes** - how costly is a shallow or wrong answer?

State the chosen tier in one short line before proceeding (e.g.
`Triage: Tier 2 (standard) - 3 independent threads, low ambiguity`). Then run that
tier. When genuinely on the fence between two tiers, pick the lower one but say so.

- **Tier 1 - Direct**: answerable from what you already know or with one
  quick lookup. Narrow scope, low stakes.
- **Tier 2 - Standard**: a handful of mostly-independent threads; the shape of the
  answer is clear; little upfront scoping needed. Runs as background or parallel
  delegated research and leaves a cited file in the repo.
- **Tier 3 - Complex / Deep**: broad, ambiguous, high-stakes, or needs a plan
  before research can even start. Multiple interacting threads, heavy synthesis.
  Choosing Tier 3 **commits you to delegated scoping, research, and synthesis**.

## Tier 1 - Direct

1. Answer directly from your own knowledge.
2. If a single fact / file / symbol needs confirming, spawn **one**
   `researcher-lite` for it; otherwise use your own tools inline. If the main
   chat's model cannot use tools inline, spawn a collector instead.
3. Give a concise answer with citations (`file:line` for code, URLs for web). No
   planner, no synthesizer, no file output unless asked.

## Tier 2 - Standard

1. Create a short todo list (one item per research thread + "synthesize").
2. Decompose the request inline into 2-4 subtasks. Mark each as independent or
   dependent on another subtask's output, and assign each a tier (lite vs mid) by
   its difficulty.
3. **Dispatch dependency-aware research**: launch independent researchers in
   parallel. For dependent subtasks, wait for the dependency to return, then launch the next
   researcher with the prior findings included in its self-contained prompt.
4. Collect the findings and **synthesize them yourself** (no synthesizer subagent
   at this tier). Deduplicate overlaps; resolve contradictions or flag them.
5. **Write the output file**: save the synthesized, cited summary to
   `docs/research/<topic>.md` in the repo (create the directory if needed). The
   file — not a chat dump — is what later steps (`/grill-with-docs`, `/to-spec`)
   consume. Also give a short chat summary with the file path.

## Tier 3 - Complex (full pipeline)

Tier 3 is a **delegation pipeline, not a solo investigation**. Your role is to
scope the work, dispatch collectors and researchers, optionally use a configured
deep-thinking tier for the roles marked below, and relay the synthesized result.
All source inspection belongs to collector/researcher subagents.

**Definition of a valid Tier 3 run.** Before you present anything, you must have
made, in order:

1. **one or more** collector calls to gather planning evidence (scoping),
2. optionally **one** planning call on the deep-thinking tier (only when the upgrade
   criteria below apply and a complete evidence packet exists),
3. **one or more** researcher calls for the planned subtasks, and
4. exactly **one** `research-synthesizer` call.

### Upgrade criteria (deep-thinking tier, only when the harness configures one)

| Role | Upgrade when |
| ------ | ---------------- |
| `researcher-deep` | Heavy architecture/tradeoff, security/performance, or conflicting-source reasoning, and the subtask evidence packet is already complete (thinking-only; no further source inspection). |
| planning call | Difficult decomposition remains after collectors assembled a complete evidence packet — including irreversible sequencing or cross-service contract design. |
| `research-synthesizer` | Large, conflicting, or high-stakes researcher outputs need deeper judgment to curate. |

`researcher-mid` never gets the deep-thinking tier — if thinking-only deep reasoning
is needed, assign the subtask to `researcher-deep` instead. Tier 2 never launches a
planner or synthesizer (the main chat synthesizes). Tier 3 alone does not justify the
upgrade; after collectors finish, prefer it for planning or synthesis only when the
remaining question is difficult and thinking-only. Upgrade prompts must forbid tools
and source lookups and must stop with exact missing evidence rather than gathering anything.

### Steps

1. **Track it**: create a todo list - `scope -> plan -> research (N subtasks)
   -> synthesize -> present`.
2. **Collect planning evidence**: use collector subagents to gather the codebase,
   web, MCP, log, or command evidence needed to scope concrete research subtasks.
   Launch independent collection in parallel. Never give scoping work to the
   deep-thinking tier.
3. **Plan**: normally decompose the work inline from the collected evidence.
   Upgrade to the planning role on the deep-thinking tier when the upgrade criteria
   apply.
   - Give it one discrete planning or reasoning question and a compact, complete
     evidence packet containing the request, constraints, source inventory, relevant
     excerpts, competing findings, and unresolved decisions.
   - Explicitly forbid tools, file reads, repository searches, web or MCP fetches,
     shell commands, tests, builds, and diagnostics.
   - If it reports missing evidence, send that exact gap to a collector, then resume
     with the completed packet. Never let it gather the missing evidence.
4. **Review the plan** briefly. Adjust tiers, merge redundant subtasks, or drop
   out-of-scope ones. Resolve blocking user choices before spending more research
   effort.
5. **Dispatch dependency-aware research (MANDATORY subagents)**: launch all
   subtasks with no unmet dependencies in parallel. After each wave returns, launch
   the next subtasks whose dependencies are complete and include the needed prior
   findings in each self-contained prompt. Keep unrelated work parallel and use
   batches of 4-6 for large fan-outs.
6. **Synthesize (MANDATORY subagent)**: spawn `research-synthesizer` with the original
   request, the plan, and all researcher outputs (attributed by subtask id). Do **not**
   write the summary yourself - the synthesis must run in an isolated context. It
   returns one curated, deduplicated summary with citations preserved.
7. **Write and present**: save the synthesized summary to
   `docs/research/<topic>.md` (create the directory if needed), then relay it in
   chat with the file path. Always surface open questions / gaps and the sources used.

## Dispatch

- Launch independent researchers in parallel; run dependent work sequentially with prior findings.
- If a named agent type is unavailable, use the harness's generic agent with the
  kit's agent definition inlined and the same instructions. Never skip a required role.
- Do not pass `readonly: true` to researchers that need web or MCP access; prohibit edits in the
  prompt instead.
- Curate and deduplicate outputs, preserve citations, and surface conflicts or gaps.

## Guardrails

- **Triage out loud**: always state the chosen tier and a one-line reason first.
- **Tier 3 means delegate**: if collectors did not gather scoping evidence,
  researchers did not inspect the sources, and a synthesizer did not merge their
  findings, you did not run Tier 3.
- **No model pins**: subagents run on the harness-configured model; the deep-thinking
  tier, if configured, is thinking-only on a complete evidence packet and never
  gathers its own evidence.
- **Cite everything**: `file:line` for code, URLs for web, tool/source name for MCP.
- **Right-size effort**: prefer the lowest tier that fully answers the question.
- **File output for Tier 2/3**: the deliverable lands at `docs/research/<topic>.md`
  so the main flow can consume it; the chat summary points at the file.
- **Surface gaps**: list what couldn't be confirmed and what would resolve it.
