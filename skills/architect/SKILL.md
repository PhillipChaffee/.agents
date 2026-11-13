---
description: "Sketch types, signatures, and module structure before code, then stay in the loop while implementation fills in. Use for /architect, 'architect this', 'design this', or non-trivial work where jumping to code would lock in the wrong shape."
enabled: true
id: architect
name: architect
---

# Architect

Sketch system boundaries, types, function signatures, and module shapes before coding. Synthesize across multiple model perspectives, then either stop at the design artifacts or fill in implementation code against the chosen contract.

## Start

Open a todolist with one entry per phase before starting.

0. Triage
1. Ground
2. Sketch
3. Agree
4. Implement
5. Scrap

## Phase 0: Triage

Classify the task on two axes before reading subsystems or launching runners.

| Context Mode | Observable Condition | Grounding Rule |
| --- | --- | --- |
| `Greenfield` | New system, service, or repo with no host code to integrate | Skip **how** and **why**, then write the Problem Charter, external boundaries, hard invariants, and initial `CONTEXT.md` terms. |
| `Brownfield Extension` | Adding a module, table, queue, or service onto existing code | Run **how** on host seams and read `CONTEXT.md` if present. Run **why** only when changing existing ownership. |
| `Brownfield Reshape` | Modifying, splitting, or migrating an existing subsystem or schema | Run both **how** and **why**, pin current behavior first, and check the migration policy in **principle-migrate-callers-then-delete-legacy-apis**. |

| Rigor Track | Observable Condition | Gate Scope |
| --- | --- | --- |
| `Track S` | In-process module or type change with zero new persisted tables, queues, caches, or network hops | Bypass `references/quantitative-envelope.md`, distributed red flags, and TLA+ routing. Keep `references/rationale-template.md`. |
| `Track M` | Stateful subsystem change adding or altering a table, index, lock, queue, cache, or cross-module contract | Run `references/quantitative-envelope.md`, apply all 14 red flags, and target `references/design-doc-template.md`. |
| `Track L` | New deployable service or quantum, storage engine, consistency shift, or greater than `10x` scale target | Full `Track M` gates plus formal state-machine verification, pre-code **interrogate**, and persistent `docs/adr/` records. |

On `Track M` and `Track L`, run the Serial Availability (`prod(A_i) >= SLO`) and Data Gravity (`T_migration > RTO`) checks in [`references/quantitative-envelope.md`](references/quantitative-envelope.md) to identify impossible sync chains and Type-1 one-way doors early.

## Phase A: Ground the problem

Execute the Context Mode rule from Phase 0. Naming a file is not grounding. For `Brownfield Extension` and `Brownfield Reshape`, produce the architectural explanation **how** prescribes and read `CONTEXT.md` if the repository keeps one. After grounding, apply the **take-a-step-back** principle skill before sketching: verify that the requested design actually serves the user's goal and does not optimize the wrong layer or ignore an existing mechanism. If grounding shows the premise is off track, flag what the user missed with evidence and redirect before Phase B.


For `Track M` and `Track L`, run the calculator in [`references/quantitative-envelope.md`](references/quantitative-envelope.md) with the workload inputs and record the printed JSON numbers as hard constraints before Phase B.

## Phase B: Sketch

Run the **arena** skill with the design task and Phase A artifacts. Pass [`references/runner-prompt.md`](references/runner-prompt.md) as the runner brief.

Take runners from the `architect runners` line in the `magic-models` role file (see `model-roles.md`), in place of `arena runners`. If that line is missing, use the role's default tier. Alias and rejected entries follow **arena** Phase A rules.

Design it twice. Require at least two structurally distinct candidates before synthesis, per the **exhaust-the-design-space** principle skill. On `Track M` and `Track L`, assign orthogonal constraint axes across the configured runners (use Axes 1 and 2 when two runners run, or cycle all three axes across three or more runners):

- Runner 1 optimizes for a single-quantum modular monolith and minimal interface surface.
- Runner 2 optimizes for disaggregated scale, cellular blast-radius isolation, and independent quotas.
- Runner 3 optimizes for failure, partition, skew, and metastability resilience first.

Screen every candidate against [`references/design-red-flags.md`](references/design-red-flags.md) before synthesis. Assume the next contributor is an agent that sees only the files it opened, copies the nearest example, and takes the shortest path that compiles.

Compare viable candidates on interface depth. Prefer the design that hides more complexity behind a smaller, simpler public surface. Arena returns one synthesized design package whose synthesis decision fills the rationale or design doc.

## Phase C: Agree (opt-in and Track L formal gate)

By default, build tasks proceed directly to Phase D without pausing.

Stop before Phase D when any of these conditions hold:

1. The invoker asks for a checkpoint (`"/architect with checkpoint"`, `"stop and show me before implementing"`). Surface the design and pause for sign-off.
2. The invoker asks for design artifacts without implementation (`"/architect design-only"`, `playbooks/system-design.md`, or `"output a plan, design doc, and diagram"`). Deliver the outputs without editing application source code.
3. The invoker asks to sharpen ambiguous requirements (`"grill me"`). Run a dependency-ordered frontier interview loop: resolve codebase facts via subagents first, then ask only unblocked product and invariant decisions with recommended defaults. Proceed to Phase D once the unblocked frontier is empty unless a checkpoint or `design-only` stop also applies.

For adversarial pressure on a `Track M` or `Track L` design before Phase D, run the **interrogate** skill in Pre-Code Design Mode against the sketch and [`references/design-doc-template.md`](references/design-doc-template.md). For `Track L` stateful protocols, concurrent coordination, or custom retry state machines, route core transitions to the **model-checking-protocols-and-code** skill or a seeded simulation harness before writing production network, disk, or runtime shell code.

If the human pushes back on the shape, treat that as Phase A evidence. Re-ground and re-run Phase B before writing more code.

## Phase D: Implement against the sketch

Replace `not implemented` bodies with code and pseudocode with logic. Treat the synthesized sketch as the contract, and follow Phase 0's migration boundary for persisted schemas, wire protocols, or rolling deployments. Deviations are architectural signals to surface, not friction to absorb silently.

## Phase E: Scrap when the architecture is wrong

If implementation keeps producing friction the sketch cannot absorb, throw the sketch out instead of bolting fixes onto a wrong design, per **redesign-from-first-principles** and **fix-root-causes**. Watch for patterns:

- The same workaround appearing repeatedly across unrelated code.
- Multiple unrelated edge cases needing special-case branches.
- Types needing escape hatches (`any`, casts, always-set optionals) to compile.
- The "we need a lock" reflex when the sketch assumed unshared state.
- Callers needing to know internal module rules to use the interface.
- Two or more independent Phase D deviations of the same shape.

When you scrap:

1. Re-run **how** over what was built.
2. Redesign as if the new constraints had been day-one assumptions.
3. Subtract dead weight first per **subtract-before-you-add**.
4. Return to Phase B and re-run **arena**.

## Outputs

- **`Track S`:** Caller usage first, then `not implemented` type signatures and module map alongside a 1-page rationale shaped per [`references/rationale-template.md`](references/rationale-template.md).
- **`Track M` and `Track L`:** A Diátaxis-separated System Design Document with validated Mermaid diagrams and DFMEA table shaped per [`references/design-doc-template.md`](references/design-doc-template.md), saved at `docs/designs/YYYY-MM-DD-<slug>.md` when running design-only or alongside implementation.
- **Architecture Decision Records:** Persist a concise record at `docs/adr/NNNN-<slug>.md` whenever all three ADR conditions hold: hard to reverse, surprising without context, and the result of a real tradeoff between viable alternatives.
