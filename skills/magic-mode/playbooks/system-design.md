# System design

**You own the design artifacts. Do not create or edit application source or production test files.**

Use this playbook when the user asks to design a system, subsystem, or stateful change and stop after producing a System Design Document, System Design Diagrams, and an Implementation Plan.

1. Keep application source and production tests untouched. Run temporary capacity calculations or isolated scratch probes only to verify quantitative limits or state-machine claims.
2. Run **architect** in `design-only` mode:
   - Execute Phase 0 two-axis triage (`Context Mode` and `Rigor Track`) and Phase A grounding plus `../architect/references/quantitative-envelope.md` for `Track M` and `Track L`.
   - Execute Phase B **arena** exploration with orthogonal constraint axes and screen all 14 red flags.
   - In Phase C, run frontier grilling if requirements are ambiguous, run Pre-Code **interrogate** against `../interrogate/references/postmortem-corpus.md`, and for `Track L` stateful protocols route core transitions through **model-checking-protocols-and-code**.
3. For `Track M` and `Track L`, write the System Design Document and embedded Mermaid diagrams to `docs/designs/YYYY-MM-DD-<slug>.md` (unless the user names another path) shaped per `../architect/references/design-doc-template.md`. On `Track S`, skip `docs/designs/` and keep the 1-page `../architect/references/rationale-template.md` sketch.
4. Validate every Mermaid diagram and `E1..En` boundary contract row by running `node skills/architect/scripts/check-mermaid.mjs docs/designs/YYYY-MM-DD-<slug>.md` (resolving `<kit>/skills/architect/scripts/check-mermaid.mjs` in protocol installs) and fix every reported error until exit code `0`.
5. When all three ADR conditions hold (hard to reverse, surprising without context, real tradeoff), persist the decision record to `docs/adr/NNNN-<slug>.md`.
6. Write the ordered implementation plan without modifying application code: run **writing-plans** pointing `**Spec:**` at `docs/designs/YYYY-MM-DD-<slug>.md` to save `docs/superpowers/plans/YYYY-MM-DD-<slug>.md` (use `playbooks/multi-phase-plan.md` only when explicitly asked for a stacked multi-PR checklist over a runnable repo).
7. Stop and present the deliverables for approval before implementing.

**Reply:** the `Context Mode` and `Rigor Track` classification, paths to the System Design Document (plus embedded diagrams), optional ADRs, and Implementation Plan, key quantitative constraints and `check-mermaid.mjs` result, and a request for confirmation before coding.
