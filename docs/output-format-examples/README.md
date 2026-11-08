# Output Format A/B Comparison Examples

Open any two files below side by side in your editor or Markdown preview to compare how each skill variant formats the exact same response:

> **Prompt given to every variant:**
>
> 1. Explain how `/statechart` (`skills/statechart/scripts/statechart.mjs`) works and how it prevents the path-traversal bug tested in `tests/pr26-regressions.test.mjs`.
> 2. Report the verification status of running `node --test tests/pr26-regressions.test.mjs`.

## Files to Compare

| File | Variant | Blinded Score | Key Shape Differences |
| --- | --- | --- | --- |
| [`00-baseline-red.md`](00-baseline-red.md) | **Baseline (RED)** | `16 / 100` | Unmodified `/poteto-mode` + `/how`: 3 to 7 sentence prose paragraphs, 0 tables, 0 diagrams, no bottom `TL;DR`. |
| [`01-variant-a-table-first.md`](01-variant-a-table-first.md) | **Variant A (Table-First + Callout TL;DR)** | `95 / 100` | Opens immediately with tables (`Subcommands`, `File Map`), 1 `flowchart LR`, plain bullets, and a bottom `> **TL;DR:**` blockquote callout. |
| [`02-variant-b-visual-first.md`](02-variant-b-visual-first.md) | **Variant B (Visual-First + 3-Bullet Summary)** | `96 / 100` | Opens with 2 visuals (`flowchart LR` + ASCII before/after path comparison), `- **Bold lead.**` bullets, 1 combined table, and a 3-bullet `## Summary (TL;DR)`. |
| [`03-variant-c-section-framed.md`](03-variant-c-section-framed.md) | **Variant C (Selected Default: Section-Framed + Code + Plain TL;DR)** | `96 / 100` | 1-sentence prose framing before each table and `flowchart TD`, inline source snippet, and a 2-sentence prose `## TL;DR` at the bottom. |
| [`04-variant-d-synthesized.md`](04-variant-d-synthesized.md) | **Variant D (Alternative Synthesis)** | `100 / 100` | Combines Variant A's 3 dedicated tables, Variant B's Mermaid + ASCII visual pair and bold-lead bullets, and a bottom `## Summary (TL;DR)` with `What / Proof / Next` bullets. |

## TL;DR

Variant C ([`03-variant-c-section-framed.md`](03-variant-c-section-framed.md)) is locked in across `/poteto-mode` and all companion output-formatting skills in the repository, while all five comparison files remain in this directory for side-by-side reference.
