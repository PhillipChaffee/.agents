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
effort to the task. Don't spin up subagents for a trivial question, and don't
hand-answer a broad investigation that deserves the full pipeline.

Subagents run in isolated contexts and do not see this conversation. Every prompt must restate
the goal, relevant context, sources, constraints, and expected output.

The parent chat runs at depth 0 as a flat dispatcher. Every spawned agent is a depth-1 leaf and
never spawns a nested subagent. When the harness exposes no subagent tool, run the waves
sequentially in this chat and say so instead of skipping a required role. The harness adapter's
Pi row records that case.

## Roles

Each spawn names a role line in the `magic-models` role file (see `model-roles.md`) and a default.
Set `model` to that line's value, or to the default when the role file or the line is missing. An
`auto` or `inherit-parent` value runs on the parent chat model, so omit `model`. If the harness
rejects the resolved model, fall back to the role's default tier and say so. Pick each subagent's
reasoning level and fast or standard speed for the job, per the Subagents section of the
**magic-mode** skill.

| Agent | Role line | Default |
| --- | --- | --- |
| `researcher-lite`, and every Tier 1 to Tier 3 collector | `researcher-lite, collectors` | `fast` |
| `researcher-mid` | `researcher-mid` | `main` |
| `researcher-deep`, `research-planner`, `research-synthesizer` | `researcher-deep, planner, synthesizer` | `deep` |

## Step 0 - Complexity triage (always)

First, apply [`/principle-take-a-step-back`](../principle-take-a-step-back/SKILL.md). Ask why the user is asking this question, what goal or decision it serves, whether the premise is off track (such as an XY problem, wrong architectural layer, or unstated system constraint), and whether there is a misconception you must flag before answering literally. If the premise is flawed or the requested mechanism would break the system, lead with that finding and redirect the research to what actually serves the user's goal instead of writing ready-to-paste configurations for a broken approach.

Then score the request across four axes and pick a tier:

- **Breadth** - how many distinct areas / files / sources are involved?
- **Depth** - how much reasoning, domain knowledge, or synthesis is required?
- **Ambiguity** - is the question well-formed, or does it need scoping first?
- **Stakes** - how costly is a shallow or wrong answer?

State the chosen tier in one short line before proceeding (e.g.
`Triage: Tier 2 (standard) - 3 independent threads, low ambiguity`). Then run that
tier. When genuinely on the fence between two tiers, pick the lower one but say so.

- **Tier 1 - Direct.** Answerable from what you already know or with one
  quick lookup. Narrow scope, low stakes.
- **Tier 2 - Standard.** A handful of mostly-independent threads; the shape of the
  answer is clear; little upfront scoping needed. Runs as background or parallel
  delegated research and leaves a cited file in the repo.
- **Tier 3 - Complex / Deep.** Broad, ambiguous, high-stakes, or needs a plan
  before research can even start. Multiple interacting threads, heavy synthesis.
  Choosing Tier 3 **commits you to delegated scoping, research, and synthesis**.

## Tier 1 - Direct

1. Answer from what is already in context, with citations (`file:line` for code, URLs for web).
   A pure in-context fact stays inline.
2. Under `orchestrator: thin`, confirm any codebase or web fact the router only remembers by
   spawning **one** `researcher-lite` on the `researcher-lite, collectors` role (default `fast`).
   A path, symbol, or value this chat did not read this session is a memory, not evidence, so
   never answer it from the router's recall.
3. No planner, no synthesizer, and no file output unless asked.

## Tier 2 - Standard

1. Create a short todo list (one item per research thread and one for synthesis).
2. Decompose the request inline into 2-4 subtasks. Mark each as independent or
   dependent on another subtask's output, and assign each a tier (lite vs mid) by
   its difficulty.
3. **Dispatch dependency-aware research.** Launch independent researchers in
   parallel. For dependent subtasks, wait for the dependency to return, then launch the next
   researcher with the prior findings included in its self-contained prompt.
4. **Synthesize in a wave.** Spawn `research-synthesizer` on the
   `researcher-deep, planner, synthesizer` role (default `deep`) with the original request, the
   plan, and every researcher output attributed by subtask id. Its brief carries this skill's
   output rules and the [`/principle-take-a-step-back`](../principle-take-a-step-back/SKILL.md)
   check. It deduplicates overlaps, applies that check, and resolves or flags contradictions.
   The main chat never synthesizes the findings itself at this tier.
5. **Persist and relay.** Write the synthesizer's returned markdown to
   `docs/research/<topic>.md` verbatim (create the directory if needed). Its frontmatter denies
   `Write`, so persist its bytes without editing them. Then give a short chat summary and the
   file path.

## Tier 3 - Complex (full pipeline)

Tier 3 is a **delegation pipeline, not a solo investigation**. Your role is to
scope the work, dispatch collectors, planners, and researchers, and relay the synthesized
result. All source inspection belongs to collector and researcher subagents.

**Definition of a valid Tier 3 run.** Before you present anything, you must have
made, in order:

1. **one or more** collector calls to gather planning evidence (scoping),
2. **one** planning step, which is the `research-planner` call on the
   `researcher-deep, planner, synthesizer` role under `orchestrator: thin`, and either that call or
   a parent-authored plan from the collected evidence under `orchestrator: standard`,
3. **one or more** researcher calls for the planned subtasks, and
4. exactly **one** `research-synthesizer` call.

### When each role runs

| Agent | Standard when |
| --- | --- |
| `research-planner` | Every Tier 3 run under `orchestrator: thin`, as Step 3. Under `orchestrator: standard`, only when difficult decomposition remains after collectors assemble a complete evidence packet, including irreversible sequencing or cross-service contract design. |
| `researcher-deep` | Heavy architecture or tradeoff, security or performance, or conflicting-source reasoning needs more judgment than `researcher-mid`. |
| `research-synthesizer` | Always, as the single final synthesis call. Large, conflicting, or high-stakes outputs raise its reasoning level. |

`researcher-mid` never takes the `researcher-deep, planner, synthesizer` role. Send a subtask
that needs heavy reasoning to `researcher-deep` instead. Tier 2 never launches a planner.

### Tool access

| Agent | Tools |
| --- | --- |
| `research-planner` | Thinking only. It reasons from the evidence packet and returns `## Missing evidence` when the packet is incomplete. It never reads, fetches, runs, or searches anything. |
| `researcher-deep` | Uses codebase, web, and MCP tools normally. It never edits files. |
| `research-synthesizer` | Reads its inputs and may re-read a cited source to resolve a conflict. It never edits files. |

Only the planner is thinking-only. Never tell `researcher-deep` or `research-synthesizer` to stop
gathering, reading, or looking up sources.

### Steps

1. **Track it.** Create a todo list - `scope -> plan -> research (N subtasks)
   -> synthesize -> present`.
2. **Collect planning evidence.** Spawn collector subagents on the
   `researcher-lite, collectors` role (default `fast`) to gather the codebase,
   web, MCP, log, or command evidence needed to scope concrete research subtasks.
   Launch independent collection in parallel. Never give scoping work to the planner.
3. **Plan.** Under `orchestrator: thin`, spawn `research-planner` on the
   `researcher-deep, planner, synthesizer` role (default `deep`) as the standard decomposition
   wave. Under `orchestrator: standard`, do the same when the `### When each role runs` table calls
   for it, or decompose inline from the collected evidence when the evidence is simple.
   - Give it one discrete planning or reasoning question and a compact, complete
     evidence packet containing the request, constraints, source inventory, relevant
     excerpts, competing findings, and unresolved decisions.
   - If it reports `## Missing evidence`, send that exact gap to a collector, then rerun it
     with the completed packet. Never let it gather the missing evidence.
4. **Review the plan.** Adjust tiers, merge redundant subtasks, or drop
   out-of-scope ones. Apply [`/principle-take-a-step-back`](../principle-take-a-step-back/SKILL.md) to verify the planned subtasks and synthesis will actually serve the user's underlying goal and flag any flawed premise discovered during scoping. Resolve blocking user choices before spending more research
   effort.
5. **Dispatch dependency-aware research (MANDATORY subagents).** Launch all
   subtasks with no unmet dependencies in parallel. After each wave returns, launch
   the next subtasks whose dependencies are complete and include the needed prior
   findings in each self-contained prompt. Keep unrelated work parallel and use
   batches of 4-6 for large fan-outs.
6. **Synthesize (MANDATORY subagent).** Spawn `research-synthesizer` on the
   `researcher-deep, planner, synthesizer` role (default `deep`) with the original
   request, the plan, and all researcher outputs (attributed by subtask id). Do **not**
   write the summary yourself, because the synthesis must run in an isolated context. It
   applies [`/principle-take-a-step-back`](../principle-take-a-step-back/SKILL.md), returns one
   curated, deduplicated summary with citations preserved, and names the recommended file path.
7. **Write and present.** Save the returned summary to
   `docs/research/<topic>.md` (create the directory if needed), then relay it in
   chat with the file path. Always surface open questions, gaps, and the sources used.

## Dispatch

- Launch independent researchers in parallel; run dependent work sequentially with prior findings.
- If a named agent type is unavailable, use the harness's generic agent with the
  kit's agent definition inlined and the same instructions. Never skip a required role.
- Do not pass `readonly: true` to researchers that need web or MCP access; prohibit edits in the
  prompt instead.
- Curate and deduplicate outputs, preserve citations, and surface conflicts or gaps.

## Guardrails

- **Triage out loud.** Always state the chosen tier and a one-line reason first.
- **Tier 3 means delegate.** If collectors did not gather scoping evidence, no planner or parent
  decomposed the work, researchers did not inspect the sources, and a synthesizer did not merge
  their findings, you did not run Tier 3.
- **Bind every spawn to a role.** Every research subagent takes its `magic-models` line from the
  Roles table above, so a hidden parent model never leaks into a deep role.
- **Cite everything.** Use `file:line` for code, URLs for web, and the tool or source name for MCP.
- **Right-size effort.** Prefer the lowest tier that fully answers the question.
- **File output for Tier 2/3.** The deliverable lands at `docs/research/<topic>.md`
  so the main flow can consume it; the chat summary points at the file.
- **Chat output shape.** Keep every prose block to at most 1-2 sentences, open each section with a 1-sentence framing line, use bullet points for supporting facts, use Markdown tables for comparisons/metrics/sources, include a Mermaid diagram when illustrating flows or architectures, and end the finished turn with a 1-2 sentence `## TL;DR` section at the bottom.
- **Surface gaps.** List what could not be confirmed and what would resolve it.
