# System Design Document Template

Use this template for `Track M` (target `<= 1,200` words) and `Track L` (target `1,500-2,500` words core body) designs, saved at `docs/designs/YYYY-MM-DD-<slug>.md`. Keep the Diátaxis boundary strict: explain choices, invariants, and trade-offs here, and put file trees, function signatures, full DDL dumps, and step-by-step migration tasks in the linked Implementation Plan.

## 0. Metadata and TL;DR

- **Status:** Draft | Review | Accepted | Committed | Superseded
- **Authors and Deciders:** <names>
- **Context Mode and Track:** `<Greenfield | Brownfield Extension | Brownfield Reshape>` · `<Track M | Track L>`
- **Review Deadline and Revisit Date:** <YYYY-MM-DD> · <YYYY-MM-DD>
- **TL;DR:** <2-3 plain sentences stating the architectural choice, primary trade-off, and verification boundary.>

## 1. Context, scope, and strategy kernel

State objective baseline facts, hard SLO, RPO, and RTO constraints, and link `CONTEXT.md` if present. Write the three-part strategy kernel: Diagnosis (primary structural bottleneck), Guiding Policy (chosen architectural rule), and Coherent Actions.

## 2. Goals, non-goals, and tenets

List measurable **Goals** and concrete **Non-Goals** (plausible capabilities explicitly excluded). For `Track L`, add 2-3 priority tenets (`"A over B"`).

## 3. System architecture and boundary contract

Follow these Mermaid diagram standards directly in this section (validated via `node skills/architect/scripts/check-mermaid.mjs`):

- **Allowed diagram types:** `flowchart LR` for C2 container topology (using `subgraph` for trust, cell, and control-vs-data-plane boundaries and `[(Store)]` cylinders for state), `sequenceDiagram` (`autonumber` + `alt` timeout, retry, and DLQ branch), and `stateDiagram-v2` (`Track L` lifecycles). Never use `architecture-beta`, `C4Context`, or `C4Container`.
- **Node and clarity limits:** Cap every diagram at `<= 15` non-legend nodes, keep labels quoted (`API["Orders API"]`), never use lowercase `end` as a node ID, avoid `direction` inside connected subgraphs, use solid `-->` for sync and dashed `-.->` for async edges, include `subgraph Legend` when mixing edge types or planes, and list `"What this diagram does not show"` for `Track L`.
- **Required views:** `Track M` requires a `flowchart LR` container topology and a `sequenceDiagram` critical write and failure path. `Track L` adds a C1 context or cell-isolation view and a `stateDiagram-v2` protocol lifecycle.

Embed the diagrams, then map every `E1..En` flowchart edge 1:1 in the table below:

| Edge ID | From and To | Protocol and Auth | Sync or Async | Failure Policy (`fail`, `degrade`, `queue`, `ignore`) | Timeout ms and Retry Budget | Idempotency or Fencing |
| --- | --- | --- | --- | --- | --- | --- |
| `E1` | `<A -> B>` | `<gRPC mTLS>` | `sync` | `fail` | `250 ms`, `<= 10%` token bucket | `<idempotency_key>` |

## 4. Quantitative envelope and FinOps unit cost

Paste the JSON output from `node -e` using [`quantitative-envelope.md`](quantitative-envelope.md) (`qpsPeak`, `peakBandwidthMBps`, `threeYearStorageTB`, `littlesLawDegradedConcurrency`, `kingmanMultiplier` at `rho <= 0.70`, `uslMaxNodes`, `fanoutTailProbPct`), plus estimated unit economics (`$/1K req`, `$/GB` storage, cross-AZ egress).

## 5. Alternatives considered and tradeoffs accepted

Compare at least **two orthogonal candidates** from **arena** plus **"Do Nothing"** on coupling pain (`Strength * Distance * Volatility`), interface depth, failure modes, and cost. State accepted trade-offs as `"We accept X in exchange for Y"`.

## 6. Resilience, metastability, STRIDE, and data classification

- **Metastability breakers:** Name explicit defenses for retry storms, cache stampedes (`singleflight`), reconnect storms, FIFO queue expiration (deadline propagation + LIFO or CoDel), and error-path allocation, plus Static Stability when the control plane is unreachable.
- **Data classification and STRIDE:** Name the highest data tier (`Public | Internal | Restricted`) and list top STRIDE threats with preventative and detective controls whenever an asset crosses a trust boundary.

## 7. Rollout invariants and rollback contract

Specify `N-1` and `N+1` compatibility invariants, the `6-step Expand-Contract with reverse sync` boundary when migrating persisted state or wire contracts, SLO burn-rate auto-rollback triggers, and key USE and RED telemetry SLIs.

## 8. Open questions, ADRs, and implementation plan

List unresolved questions with named deciders, link any spawned `docs/adr/NNNN-<slug>.md` records, and link the companion `docs/superpowers/plans/YYYY-MM-DD-<slug>.md` implementation plan.
