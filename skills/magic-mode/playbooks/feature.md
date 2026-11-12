# Feature

**You own the design. Plan, review, verify.** Delegate implementation, stay in the lead, and keep every heavy step a flat depth-1 wave.

Each wave resolves its subagent model from a role line in the `magic-models` role file (see `../references/model-roles.md`). This chat is the depth-0 dispatcher, and no leaf spawns a nested subagent.

1. **Wave 1, ground.** Run the `how` skill over the affected subsystem. Its `how explorer` and `how explainer` lines come from the `magic-models` role file. Then apply the **take-a-step-back** principle skill to confirm the requested change actually serves the user's goal given the real system shape and deployment topology.
2. **Wave 2, design.** Run the `architect` skill. Its `arena synthesizer` line checks `take-a-step-back`, names the domain data shape and its organizing structure per **principle-model-the-domain** (a state machine over scattered booleans, a table or registry over branching, a typed model over repeated shape assumptions), and drafts the throughput checkpoint as four todo items. A dimension that genuinely does not apply keeps its item with `n/a: <reason>` rather than being dropped.
   - **Blocking first steps.** Gates run before fan-out.
   - **Independent workstreams.** Disjoint files, services, or layers parallelize. Shared writes serialize.
   - **Shared mutable state.** Split the target first (the **separate-before-serializing-shared-state** principle skill). Serialize only for real invariants.
   - **Smallest safe decomposition.** If one worker is best, name why.
3. **Wave 3a, blocking scaffold.** Dispatch one `magic-agent` on the `feature, refactoring` line (default `main`), or on `hardest tasks` (default `deep`) for cross-cutting design, gnarly concurrency, and subtle algorithms. Its brief names the file paths, the data shape, the blocking prerequisite, and the success criteria. It returns the scaffold and the file list that Wave 3b partitions.
4. **Wave 3b, parallel implementation.** The root chat fans out one `magic-agent` per independent slice at depth 1, each in its own worktree (the **separate-before-serializing-shared-state** principle skill). No owner splits its own work further, and each leaf finishes its own edits, checks, and commits. When the implementation admits multiple valid shapes (error handling, abstraction layer, test structure), run this wave as `arena` from the root chat so the runners surface the alternatives and the cross-judge guards the pick. Comments per **Comments**. Surgical edits, re-ground against the source for upstream-derived files. Port shared-primitive improvements to all consumers and verify each. Commit liberally.
5. **Wave 4, verify on the matching surface.** Dispatch `swarm workers` (default `main`) to run the live checks the project's verification skill names. "Inconclusive" or wrong-surface is not a pass. Flag it.
6. Rebase into small, ordered commits and stack follow-ups. Use the **principle-sequence-verifiable-units** skill, building, verifying, and committing each small unit before the next.
7. If the design is contested, run `interrogate` before shipping.
8. **Wave 5, review and open the PR.** Dispatch `comment-sicko` flat from this chat per **no-comments**. Then run **Opening a PR**, whose commit splitting, `/make-pr-easy-to-review`, PR body, and reply draft run in one `judgment and prose` (default `deep`) `magic-agent`.

Code-coupled work (one feature, one migration) keeps its checkpoint with the Wave 3a scaffold, and only the root chat splits parallel slices. Parent-level fan-out is for slices that produce independent artifacts (audits, cross-subsystem investigations, competing experiments). Rewrite the checkpoint at phase boundaries, and spawn a fresh owner for a new round rather than chaining interrupts.

**Reply.** Cover what you built, what you chose and why, the throughput checkpoint, and the open decisions. Tables for design alternatives.
