# Architect runner prompt

The orchestrator passes this file through to every parallel candidate runner during Phase B and fills in the variable inputs around it: the task, the Phase A grounding artifacts, any assigned orthogonal constraint axis, the isolated working directory, and the output path. The working directory is a git worktree when available, otherwise a per-runner subdirectory under the sketch dir. Independence between candidates matters most.

You are producing one candidate design in architect's parallel exploration. Read the **architect** skill in full first. Output a candidate design package: type sketch, function signatures, module map, and rationale shaped per [`rationale-template.md`](rationale-template.md) (for `Track S`) or [`design-doc-template.md`](design-doc-template.md) (for `Track M` and `Track L`).

Apply the following discipline. The orchestrator compares candidates on these axes to pick a base.

- **Caller's usage first.** Write the README-style usage and two or three real call sites before the types, then derive the type sketch from them. Reconcile the sketch to the usage, not the reverse.
- **Data structures first.** Get the core types right and the code becomes obvious. Trace each dominant access pattern through the proposed structure. If the answer is "we'll add a map, index, or cache later," the structure is wrong.
- **Interface depth.** Prefer a simple public surface that pulls complexity into the callee. Keep transport, storage, and wire types behind the boundary and parse into domain types inside.
- **Coupling balance and quantum boundary.** Evaluate coupling pain (`Strength * Distance * Volatility`). Default to a single-quantum modular monolith unless independent scaling, fault isolation, or team cognitive load justifies a network hop.
- **Split `decide` and `perform` cores.** Keep stateful transitions inside a pure synchronous `decide` function with zero I/O, leaving network, database, and clock calls in a thin imperative `perform` shell.
- **Shared state.** If two actors might write concurrently, default to per-actor owned state merged at the read boundary, per **separate-before-serializing-shared-state**.
- **Storage and consistency (`Track M` and `Track L`).** Name the storage structure along the RUM spectrum (with *WiscKey* key-value separation for payloads over 1 KB), specify the exact isolation level after checking for Snapshot Isolation write skew, enforce monotonic fencing tokens on every lease or lock, and use Transactional Outbox or CDC instead of uncoordinated dual-writes.
- **Metastability breakers (`Track M` and `Track L`).** Cap retries via a client-side adaptive retry token bucket (`<= 10%` overhead) with full jitter at a single retry layer, protect hot cache keys with `singleflight` leases, propagate deadlines with bounded LIFO or CoDel load shedding, keep error paths allocation-free, and preserve Static Stability when the control plane fails.
- **TigerStyle bounds.** Put explicit static upper bounds on every loop, queue, batch, query, and map, put units in field names (`timeout_ms`, `max_payload_bytes`), and pair positive and negative boundary assertions.
- **Make boundaries visible and short.** Use `not implemented` errors for stub bodies, `// TODO` pseudocode for tricky logic, invariants encoded in types, validation at boundaries, single source of truth per invariant, idempotent transitions per **make-operations-idempotent**, and call chains within three files per **minimize-reader-load**.

You are one of the parallel runners. If assigned a constraint axis, push that axis rigorously rather than hedging toward a generic middle. Differences between candidates create the signal for base selection and grafting.
