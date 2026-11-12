# Trace forensics

**You own the diagnosis from the artifact.** Each heavy step is a flat depth-1 wave whose model comes from a role line in the `magic-models` role file.

Distinct from **Runtime forensics**, which instruments the live process. Here the capture already exists. The artifact is a fixed dataset, so read it, don't re-run it. Keep tooling generic, a DevTools or trace parser for cpuprofile and `.json.gz`, a text editor for a spindump, the heap tooling for a heapsnapshot.

1. **Wave 1, transform and query.** Dispatch one `magic-agent` on the `bug-fix` line (default `main`), or on `hardest tasks` (default `deep`) for a subtle call tree, with the artifact paths and the symptom. It identifies the format and loads it with the right tool, then dumps the trace or heap snapshot into sqlite, one row per sample, frame, or node, so the artifact reaches a queryable shape before anyone reads it.
2. **Wave 1 continues, narrow and attribute.** The same leaf queries for the frames that hold the most time and walks the call tree to the hot path. For a leak it follows the retainer chain from the leaked object to a GC root. For a spindump it finds the thread stuck on-CPU or blocked and its wait reason. It maps the hot frame to file, symbol, and line via the artifact's own symbols, because a frame with no source mapping is not yet a diagnosis. Where the artifact does not carry the symbols, it says so plainly.
3. **Wave 2, reduce for this chat.** Dispatch `fast, mechanical, miners` (default `fast`) to condense the query output into the reduced finding and its citations, and keep the raw dump out of this context (**principle-guard-the-context-window**).
4. When a paired capture exists, add the before and after diff to the Wave 2 brief so the reducer confirms the finding. Otherwise the finding is the strongest hypothesis the artifact supports, not a confirmed cause.
5. Hand back a cited diagnosis, no fix unless asked. Route to Bug fix or Perf issue once the cause is known. Throughput checkpoint stays one line, `throughput checkpoint: n/a, read-only forensics`.

**Reply.** Give the artifact and format, the reduced finding, the source location, the artifact paths, and whether a paired capture confirmed it.
