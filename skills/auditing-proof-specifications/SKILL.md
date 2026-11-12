---
description: "Use when reviewing or auditing formal proofs, specifications, or AI-generated verification PRs in Lean 4, Rocq, Verus, Dafny, SPARK, Kani, TLA+, or Frama-C, or before claiming any formal verification passes."
enabled: true
id: auditing-proof-specifications
name: auditing-proof-specifications
---

# Auditing Proof Specifications and the Four Gaps

## Overview

Even when a theorem prover or model checker prints `VERIFICATION SUCCESSFUL` (exit code `0`), a system can still fail in production. A proof checker verifies that the proof term or code satisfies the stated specification under the stated axioms and bounds, and it **never** verifies that you stated the right theorem, that your model matches production code, that bounded checks hold above bound $K$, or that side-channels outside the mathematical semantics are absent.

**A passing verifier with a weak spec, an escape hatch, or an unlinked model is a false proof.** Never approve or claim completion on a formal verification change without auditing all four remaining gaps, locking the contract AST (`verify-spec-lock.mjs`), and running the escape-hatch detector (`check-proof-cheats.mjs`).

## When to Use

- Before declaring any proof, contract, or model check complete.
- Validating formal specifications against an existing reference codebase before synthesizing a new implementation.
- Reviewing AI-generated or human-authored PRs containing Verus, Dafny, SPARK, Lean 4, Rocq, Kani, CBMC, TLA+, or Frama-C proofs.
- Designing CI gates to prevent AI specification gaming (`sorry`, `admit`, `assume`, `external_body`, `trusted`, weakened `ensures`, strengthened `requires`).
- Bridging a formal model (Lean 4, TLA+, P, Alloy) to a production implementation in Rust, Go, TypeScript, C, or Python.

## Wave Assignment

This skill is a depth-1 leaf and the **Wave 4** auditor in the `/proof-driven-development` pipeline. Under `orchestrator: thin`, the root chat dispatches it on a seat from the `arena cross-judge pool` (`deep`), preferring a family different from both the chat's `orchestrator:` line and the family that wrote the proof. It executes directly in this session and spawns no subagent, because a second wave inside a leaf would nest a wave inside a wave. When the harness exposes no subagent tool, run it inline in this session as well. The verdict goes back to the parent as the 4-Gap report plus the commands it ran.

## The Four Remaining Gaps Audit Contract (REQUIRED in Every Audit)

Every proof audit or verification hand-off must explicitly evaluate all four gaps below in order and report a verdict (`PASS`, `FAIL`, or `BOUNDED/DOCUMENTED`) for each:

### Gap 1: The Specification Gap & AI Specification Gaming

A proof only guarantees the specification you wrote. Check **completeness**, **mechanized non-vacuity**, **mutation kill rate**, and **contract AST locking**:

- **Two-Sided Completeness Law:** Does the postcondition specify *both* structural properties and conservation/relational properties?
  - *Classic trap:* Proving `Sorted(sort(xs))` without proving `sort(xs)` is a permutation of `xs` (`forall x, count(x, sort(xs)) == count(x, xs)` or `res@.to_multiset() =~= xs@.to_multiset()`). A function returning `[]` passes `Sorted([])` vacuously!
  - *Protocol/serialization trap:* Proving memory safety and cipher primitives while omitting wire-protocol field ordering (e.g., swapping `shared_secret` and `exchange_hash` in SSH key derivation).
  - *Policy trap:* Proving positive authorization (`permit` grants access) without negative dominance (`forbid` always overrides `permit`).
- **Mechanized Non-Vacuity Lemmas (`verify_spec_not_vacuous`):** Did the author strengthen `requires` or `kani::assume` (e.g., `requires msg.len() == 0` or contradictory invariants) so valid runtime inputs are excluded and $P \implies Q$ passes vacuously? Require a mechanized `proof fn verify_spec_not_vacuous` lemma (proving $\exists s.\; \text{inv}(s) \land P(s) \land Q(s)$ on contract skeletons) or `kani::cover!` statements proving non-trivial paths are reachable.
- **The $N$-Mutant Specification Kill Gate (Gate C):** To prove the specifications themselves have zero logical gaps, plant $N$ single-line semantic mutations (one per theorem ID, such as inverting a priority tie-breaker, dropping an uninterruptible item on `reset()`, or skipping a guard) in a scratch copy of the reference or target codebase and verify that the spec probes/oracles kill **100% ($N/N$) of planted mutants** while passing on the unmutated code. Every mutant probe must execute behavioral code, since source-text regex checks (`inspect.getsource`) do not count.
- **AST-Extracted Contract Locking (`spec.lock`):** Raw `git diff --exit-code` fails when specifications (`spec fn`, `requires`, `ensures`) and executable implementation bodies (`{ ... }` + loop invariants) live in the same source file (Verus, Dafny, SPARK, Frama-C). Before AI proof/code synthesis begins, extract and hash only the specification AST (`.tla`, `.cfg`, `.lean`, type definitions, `spec fn`, `verify_spec_not_vacuous`, `requires`/`ensures` headers, and `#[kani::proof]` harnesses) into `spec.lock`, then verify `spec.lock` after synthesis so executable bodies can be filled in while contract modifications fail CI.

### Gap 2: The Model-to-Implementation Gap

Design-level specifications (TLA+, Alloy, P) and standalone proof-assistant models (Lean 4, Rocq) verify the model, not the production Rust, Go, TypeScript, or C code:

- **Atomicity mismatch:** Did the model treat a database read-modify-write or two network RPCs as one atomic step while production performs them without a lock or epoch fence?
- **3-Gate Pre-Synthesis Spec Validation (When Reference Code Exists):** Before trusting a new TLA+ or Lean 4 specification to drive a rewrite or port, validate the specification against the existing reference implementation:
  1. **Gate A (Forward Runtime Trace Validation in `*Trace.tla`).** Attach a non-invasive trace observer to the reference test suite (`pytest` / `vitest` / `cargo test`), record NDJSON state/event traces, and run `TLC` on trace validation specs (`TraceAcceptedProperty == <>(pc > Len(TraceData))`) to prove the TLA+ model accepts 100% of real system traces.
  2. **Gate B (Persistent Spec Oracle Differential Fuzzing).** Compile the functional specification (e.g., Lean 4) into a persistent `stdin`/`stdout` JSON-lines oracle binary and run $50{,}000$+ property-based examples (`Hypothesis` / `proptest` / `fast-check`) per module comparing the reference code against the Spec Oracle (`0` discrepancies).
  3. **Gate C ($N$-Mutant Spec Kill Gate).** Verify that the Gate A/B spec checks kill 100% ($N/N$) of planted single-line semantic mutations in the reference code.
- **Post-Synthesis Implementation Conformance Bridge:** If the proof does not run directly on the compiled source code, require at least one automated bridge in CI:
  1. **Verified code extraction / translation:** Aeneas (Rust $\to$ Lean 4), Fiat Cryptography (Rocq $\to$ C/Rust), KaRaMeL (F\* $\to$ C).
  2. **Refinement proof:** Proving every concrete implementation transition maps to a valid abstract state-machine step (e.g., Anvil, TLA-Verus).
  3. **High-volume differential harness ($10^5$ to $10^6$ traces) + Black-Box Wire Evals:** Running multi-threaded `proptest` / `Hypothesis` differential traces comparing the new implementation against the persistent Spec Oracle and reference engine, plus running end-to-end black-box protocol evaluation suites against the compiled binary.

### Gap 3: Bounded vs. Unbounded Guarantees

- **Loop unwinding and model bounds:** A bounded model check (`TLC` on 3 nodes, or `Kani`/`CBMC` with `#[kani::unwind(8)]`) proves zero bugs *up to bound $K$*. It proves nothing about $K + 1$ unless replaced by an inductive loop invariant (`proving-with-hoare-logic`) or an unbounded inductive theorem (`proving-with-dependent-types`).
- **Audit requirement:** Verify that unwinding assertions are enabled (`#[kani::unwind(K)]` without disabling unwinding checks) and that the exact bounds ($K$ iterations, $N$ nodes, $M$ bytes) are stated in the verification report.

### Gap 4: The Trusted Computing Base (TCB) & Unmodeled Reality

- **Escape hatches, `unsafe` whitelisting, & unverified boundaries:** Any function marked `#[verifier::external_body]`, `#[verifier::trusted]`, `#[verifier::exec_allows_no_decreases_clause]`, `@[extern]`, `@[implemented_by]`, `#[trusted]`, `#[kani::stub]`, `#[kani::stub_verified]`, `sorry`, `admit`, `axiom`, or linked via C FFI is **unverified**. Enforce `#![forbid(unsafe_code)]` across all verified crates; any low-level primitive that requires `unsafe` (such as an `UnsafeCell<MaybeUninit<T>>` lock-free ring buffer) must be explicitly whitelisted in `spec.lock` (`--allow-unsafe <rel-path>`) and verified under both `Kani` (bit-precise BMC) and `Miri` (operational Stacked/Tree-Borrows aliasing and memory-leak detection).
- **Non-functional & physical side channels:** A functional correctness proof (`valid == (computed_mac == expected_mac)`) operates over mathematical values, not execution time or power consumption. An early-exit byte comparison loop passes functional equivalence while leaking secret cryptographic keys via timing side-channels!
- **Audit requirement:** For cryptographic or secret-handling code, require constant-time execution discipline (no secret-dependent branches, early returns, or memory indices; use bitwise constant-time equality).

## Automated Escape-Hatch Scanner & AST Contract Lock

1. **Before synthesis (after Phase 1 & Phase 2 spec validation):** Lock all `.tla`, `.cfg`, `.lean`, and extracted Rust/Dafny contract AST headers (`pub struct`/`enum`, `spec fn`, `verify_spec_not_vacuous`, `requires`/`ensures` signatures, `#[kani::proof]` harnesses, and any `--allow-unsafe` paths) into `spec.lock`:

   ```bash
   node skills/auditing-proof-specifications/scripts/verify-spec-lock.mjs --generate <repo-root>
   ```

2. **During and after synthesis (in CI and before merge):** Verify that no locked spec or contract AST header was modified, no unwhitelisted `unsafe` block was added, and zero proof escape hatches exist:

   ```bash
   node skills/auditing-proof-specifications/scripts/verify-spec-lock.mjs --check <repo-root>
   node skills/auditing-proof-specifications/scripts/check-proof-cheats.mjs <path-to-code-or-specs>
   ```

3. **For Lean 4 theorems:** Also require in every proof file:

   ```lean
   #print axioms <theorem_name>
   ```

Reject any theorem whose `#print axioms` output includes `sorryAx`, a custom `axiom`, or `Lean.ofReduceBool`.

## Common Mistakes & Rationalizations

| Excuse | Reality |
| --- | --- |
| "Verus / Lean 4 / Kani / TLC exited 0 (`VERIFICATION SUCCESSFUL`), so the specs and code are bug-free" | Exit code `0` only means the solver accepted the formula it was handed. `verified_sort` returning `Vec::new()` exits `0` when the permutation law is missing. Always run the 3-Gate Spec Validation (`*Trace.tla`, Spec Oracle diff fuzzing, $N$-Mutant Kill Gate) and audit all 4 gaps. |
| "We'll freeze the Verus/Dafny files with `git diff --exit-code crates/` while the AI fills in `{ todo!() }` bodies" | `git diff` on the whole file fails the moment the agent writes the function body or loop invariants! Use `node skills/auditing-proof-specifications/scripts/verify-spec-lock.mjs` to hash only the extracted contract AST while leaving `{ ... }` implementation bodies unlocked. |
| "`#[verifier::external_body]` or `#[verifier::trusted]` is just on a helper serializer, the rest is proved" | `external_body` and `trusted` turn that function's `ensures` clause into an unchecked axiom. A bug inside `external_body` (like swapped SSH key-derivation fields) invalidates every proof that calls it. |
| "The HMAC comparison is proved functionally equal to `compute_hmac(msg, key) == *tag`" | Functional equality in value semantics ignores execution time. An early-return loop (`if a[i] != b[i] { return false; }`) creates a remote timing side-channel. |
| "We proved the policy engine in Lean 4 and have 12 unit tests on the Rust implementation" | 12 unit tests do not bridge a Lean 4 model to a separate hand-written Rust codebase. Require high-volume differential fuzzing against the persistent Lean executable oracle, verified extraction, or an in-language Verus proof. |

## Red Flags - STOP and Block Merge

- Any match from `node skills/auditing-proof-specifications/scripts/check-proof-cheats.mjs` (`sorry`, `admit`, `assume`, `external_body`, `trusted`, `exec_allows_no_decreases_clause`, `axiom`, `native_decide`, `{:verify false}`, `#[kani::stub]`, `#[kani::stub_verified]`, `--no-unwinding-assertions`, `-no-warn-signed-overflow`)
- Any contract AST mismatch or unwhitelisted `unsafe` block reported by `node skills/auditing-proof-specifications/scripts/verify-spec-lock.mjs --check`
- Transformation functions (sort, filter, serialize, rebalance) whose `ensures` clause checks shape (e.g., sortedness or tree height) without checking element/multiset conservation
- Contract skeletons without a mechanized `verify_spec_not_vacuous` lemma or `kani::cover!` witness
- Standalone Lean 4 / Rocq / TLA+ models of existing or target code that have not passed Gate A (trace validation), Gate B (persistent oracle differential fuzzing), and Gate C ($N$-mutant kill gate)
- Secret/MAC/key comparisons proved only for functional value equality while using secret-dependent branches or early returns

**All of these mean: Block the merge, report the exact gap(s) violated, and require the specification, contract lock, conformance bridge, or constant-time implementation to be fixed.**
