# Runtime forensics

**You own the diagnosis. Instrument the live process, don't theorize from source.** The deliverable is a cited diagnosis, not a fix. Each heavy step is a flat depth-1 wave whose model comes from a role line in the `magic-models` role file.

1. **Wave 1, capture and prove.** Dispatch one `magic-agent` on the `bug-fix` line (default `main`), or on `hardest tasks` (default `deep`) when the mechanism is subtle concurrency, to capture the live signal on the matching surface via the project's verification skill. The artifacts are a CPU profile for a spinning process, a heap snapshot for a leak, a CDP trace for a visual glitch. It then proves the mechanism cheaply, with instrumentation injected via CDP eval on the running process or a hotfix applied to the live code without reloading. A real artifact and a proven mechanism, never a guess.
2. **Wave 2, mine the artifact.** Dispatch `fast, mechanical, miners` (default `fast`) with the artifact paths to reduce each one to the smoking gun, the function on the hot path, the retainer chain from the leaked object to a GC root, or the loop firing without idle input. The same leaf maps the finding back to source, naming the file, the symbol, and the line that allocates or schedules. It returns the reduced finding, the source location, and the artifact paths, and keeps the raw profile out of this chat (**principle-guard-the-context-window**).
3. A finding with no source location is not yet a diagnosis, and a leaf that cannot resolve one reports the missing symbol rather than guessing.
4. Throughput checkpoint stays one line, `throughput checkpoint: n/a, read-only forensics`.

**Reply.** Name the signal captured, the reduced finding, how you proved the mechanism, the source location, and the artifact paths. No fix unless asked, and hand back to Bug fix or Perf once the cause is known.
