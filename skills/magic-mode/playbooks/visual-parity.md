# Visual parity

**You own pixel-exact equivalence. The baseline is the spec. You do not touch it.** Equivalence is verified by image diff, not by eye. Every heavy step is a flat depth-1 wave whose model comes from a role line in the `magic-models` role file.

1. **Wave 1, baseline.** A baseline is a visual regression harness that screenshots the current component across its states, plus the target when matching two implementations. No baseline, no parity claim. It is a blocking prerequisite, not a follow-up. Dispatch one `magic-agent` on the `feature, refactoring` line (default `main`) to build and record it before any migration.
2. **Anti-shortcut gate.** This chat records the bans before component work starts, with no harness changes, no baseline edits, and no component restructuring to make a diff pass. If the baseline looks wrong, stop and ask rather than touch it. A proposal to weaken either is rejected here.
3. **Wave 2, component owners.** Migrate one component at a time. Every component owner is a depth-1 `magic-agent` on the `feature, refactoring` line, each in its own isolated worktree, one owner per component (the **principle-separate-before-serializing-shared-state** skill). Shared primitives migrate first as a blocking Wave 2a before the parallel Wave 2b components.
4. **Wave 3, pixel diff.** Dispatch `swarm workers` (default `main`) to verify each component against its baseline via image diff on the matching surface through the project's verification skill. A nonzero diff is a fail. Investigate the pixel delta, and run `/loop` per component until the diff is zero.
5. **Wave 4, open the PR** per component or per safe batch. Commit splitting, `/make-pr-easy-to-review`, the PR body, and the reply draft run in one `judgment and prose` (default `deep`) `magic-agent`.

**Reply.** List the components migrated, the diff result for each, the baseline harness location, and what's left.
