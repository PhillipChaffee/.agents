# Bug fix

**You own this task. Plan, review, verify.** Delegate investigation and the fix, stay in the lead, and keep each heavy step a flat depth-1 wave.

Be scientific. Every shipped line traces to runtime evidence. Belt-and-suspenders that "might help" is a hypothesis, not a fix. It does not ship. When evidence refutes a hypothesis, revert what it motivated. The smallest change the evidence justifies ships, nothing more.

Each wave resolves its subagent model from a role line in the `magic-models` role file. No leaf spawns a nested subagent.

1. **Wave 1, reproduce and instrument.** Dispatch one `magic-agent` on the `bug-fix` role line, default `main`, with the goal restated. It runs the change the way a user would through the project's verification skill (Non-negotiables), even when a debug or instrumentation protocol says to ask the user to reproduce. It synthesizes the trigger, tightens conditions, or adds instrumentation until the bug fires, then returns the repro command, the captured evidence, and the instrumentation diff. A leaf with no reachable surface returns `NEEDS-GROUNDING: <symbol>` with no edits. Ask the user only for a real dead end, with a stated reason the control surface cannot reach the target.
2. **Wave 2, ground the mechanism.** Run `how` over the affected subsystem (its `how explorer` line) and `why` for regression history (its `why investigators` line). When the cause crosses a function boundary, run `architect` as its own wave first. Binary-search the candidate hypotheses, keep the split that cuts the most problem space, and confirm the surviving *mechanism* with runtime evidence. Drive a long or stubborn hunt with the harness's `/loop` command, then apply the **take-a-step-back** principle skill to check that fixing the symptom serves the user's goal, and flag any misconception before Wave 3.
3. **Wave 3, fix at the root.** Dispatch one `magic-agent` on `bug-fix` with the confirmed mechanism, the repro command, and the file fence. It commits the failing test first per the `tdd` skill, then the smallest root-cause fix. Skip the failing test when it would be expensive, integration-heavy, or unclear. No symptom guards, and no belt-and-suspenders. When the fix needs a new shape, the leaf returns `NEEDS-GROUNDING: <shape>` and the root chat runs `architect` again.
4. **Wave 4, verify independently.** Dispatch `swarm workers`, default `main`, to rerun the original repro on the same surface plus the touched-path checks. Unit tests show branch behavior, not bug absence. "Inconclusive" or wrong-surface is not a pass. Flag it.
5. Stage the commits so the failing repro lands before the fix in git history. This is the canonical **principle-sequence-verifiable-units** pass, the failing test first and the fix on top.
6. **Wave 5, open the PR.** Run **Opening a PR**, whose commit splitting, `/make-pr-easy-to-review`, PR body, and reply draft run in one `judgment and prose` (default `deep`) `magic-agent`.

**Reply.** Say what was broken, the root cause, the fix, and how you verified it. Paste failing-then-passing repro output verbatim.
