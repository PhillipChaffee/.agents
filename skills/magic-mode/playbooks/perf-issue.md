# Perf issue

**You own the measurement story. Plan, review, verify the numbers.** Tie every fix to a measurement, and never read source instead of measuring. Each heavy step is a flat depth-1 wave whose model comes from a role line in the `magic-models` role file.

1. **Wave 1, baseline.** Dispatch one `magic-agent` on the `perf-issue` line (default `main`) to capture a baseline trace through the project's verification skill. Vet the baseline, and each later number, with the **benchmark-checklist** skill before anyone acts on it. The leaf returns the artifact path, the command, and the workload.
2. **Wave 2, ground hypotheses.** Run `how` over the affected subsystem (its `how explorer` line). Don't claim a perf ceiling without running it first.
   Try the performance mantras in order, cheapest first:
   1. Don't do it. Stop work whose result nothing uses rather than cheapening it.
   2. Do it, but don't do it again.
   3. Do it less.
   4. Do it later.
   5. Do it when they're not looking.
   6. Do it concurrently.
   7. Do it cheaper.

   When an earlier mantra meets the target, stop.
3. **Wave 3, plan and implement.** Dispatch one `magic-agent` on `perf-issue`, default `main`, or on `hardest tasks`, default `deep`, when the fix needs cross-cutting design or subtle concurrency. Its brief carries the trace, the chosen mantra, and the file fence. It captures the post-fix trace in the same session. When the fix crosses a function boundary, the root chat runs `architect` first as its own wave. Verify each attempt before trying the next, per **principle-sequence-verifiable-units**.
4. **Wave 4, compare.** Dispatch `swarm workers` (default `main`) to parse and compare the artifacts (JSON to sqlite, then a diff) and to rerun the doctrine checks. A second `perf-issue` leaf captures any trace the comparison asks for. "Inconclusive" or wrong-surface is not a pass. Flag it.
5. Cite the measurement in the PR.
6. **Wave 5, open the PR.** Run **Opening a PR**, whose commit splitting, `/make-pr-easy-to-review`, PR body, and reply draft run in one `judgment and prose` (default `deep`) `magic-agent`.

For sustained improvement against a metric rather than a one-off fix, use the Hillclimb playbook (`playbooks/hillclimb.md`).

**Reply.** Give the baseline number, the post-fix number, the delta, and the artifact path.
