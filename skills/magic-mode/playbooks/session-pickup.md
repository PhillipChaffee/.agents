# Session pickup

**You own the resume point. Read the prior trail, don't redo it.** Each heavy step is a flat depth-1 wave whose model comes from a role line in the `magic-models` role file.

1. **Wave 1, mine the trail.** Dispatch `fast, mechanical, miners` (default `fast`) with the transcript path, agent URL, or pushed branch. A local transcript lives under the active workspace's session transcript store (the harness adapter names the path, and it never globs across other workspaces' stores, because that crosses workspace boundaries and reads private chats from unrelated projects). The miner reads the metadata overview and last messages first, then scans back for the decision points, and returns a reduced timeline with its citations (the **principle-guard-the-context-window** skill).
2. **Wave 2, reconstruct and recommend.** Dispatch one `magic-agent` on `judgment and prose` (default `deep`) with the timeline, the branch and worktree, and the goal. It reconstructs operational state from `git log`, `git diff` against the base, the open todos, and the decisions made. The prior trail is authoritative input, so it does not re-derive it. It diffs done against pending, names the resume point, and recommends one verdict, continue the execution, ship a finished recommendation, ratify or override a prior conclusion, or postmortem a failed run. A "let me verify from scratch" pass is a failure here, because it treats an authoritative trail as untrustworthy.
3. **Wave 3, verify on the real artifact.** Dispatch `swarm workers` (default `main`) to check the inherited claims against the original goal on the real artifact (the **principle-prove-it-works** skill). A passing prior self-report is not the proof.
4. Route the remaining work to the matching playbook, which owns the rest. The pickup playbook ends here.

**Reply.** Say where the prior agent stopped, what you inherited vs redid (ideally nothing redone), the resume point, and the outcome.
