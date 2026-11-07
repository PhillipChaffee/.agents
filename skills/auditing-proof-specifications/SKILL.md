---
description: "Use when reviewing or auditing formal proofs, specifications, or AI-generated verification PRs in Lean 4, Rocq, Verus, Dafny, SPARK, Kani, TLA+, or Frama-C, or before claiming any formal verification passes."
enabled: true
id: auditing-proof-specifications
name: auditing-proof-specifications
---

# Auditing Proof Specifications and the Four Gaps

## Overview

Even when a theorem prover or model checker prints `VERIFICATION SUCCESSFUL` (exit code `0`), a system can still fail in production. A proof checker verifies that the proof term or code satisfies the stated specification under the stated axioms and bounds—it **never** verifies that you stated the right theorem, that your model matches production code, that bounded checks hold above bound $K$, or that side-channels outside the mathematical semantics are absent.

**A passing verifier with a weak spec, an escape hatch, or an unlinked model is a false proof.** Never approve or claim completion on a formal verification change without auditing all four remaining gaps and running the escape-hatch detector.

## When to Use

- Before declaring any proof, contract, or model check complete.
- Reviewing AI-generated or human-authored PRs containing Verus, Dafny, SPARK, Lean 4, Rocq, Kani, CBMC, TLA+, or Frama-C proofs.
- Designing CI gates to prevent AI specification gaming (`sorry`, `admit`, `assume`, `external_body`, weakened `ensures`, strengthened `requires`).
- Bridging a formal model (Lean 4, TLA+, P, Alloy) to a production implementation in Rust, Go, TypeScript, C, or Python.

## The Four Remaining Gaps Audit Contract (REQUIRED in Every Audit)

Every proof audit or verification hand-off must explicitly evaluate all four gaps below in order and report a verdict (`PASS`, `FAIL`, or `BOUNDED/DOCUMENTED`) for each:

### Gap 1: The Specification Gap & AI Specification Gaming

A proof only guarantees the specification you wrote. Check both **completeness** and **anti-gaming**:

- **Two-Sided Completeness Law:** Does the postcondition specify *both* structural properties and conservation/relational properties?
  - *Classic trap:* Proving `Sorted(sort(xs))` without proving `sort(xs)` is a permutation of `xs` (`forall x, count(x, sort(xs)) == count(x, xs)` or `res@.to_multiset() =~= xs@.to_multiset()`). A function returning `[]` passes `Sorted([])` vacuously!
  - *Protocol/serialization trap:* Proving memory safety and cipher primitives while omitting wire-protocol field ordering (e.g., swapping `shared_secret` and `exchange_hash` in SSH key derivation).
  - *Policy trap:* Proving positive authorization (`permit` grants access) without negative dominance (`forbid` always overrides `permit`).
- **Precondition Non-Vacuity:** Did the author strengthen `requires` or `kani::assume` (e.g., `requires msg.len() == 0` or `requires false`) so valid runtime inputs are excluded and the implication $P \implies Q$ passes vacuously? Require a concrete witness test or `kani::cover!` proving $P$ is satisfiable on non-trivial inputs.
- **Immutable Spec Diff Check:** When an AI agent is tasked with proving existing code against a target spec, verify via `git diff` that the agent did not weaken `ensures`, strengthen `requires`, or alter `spec fn` / `def` definitions.

### Gap 2: The Model-to-Implementation Gap

Design-level specifications (TLA+, Alloy, P) and standalone proof-assistant models (Lean 4, Rocq) verify the model, not the production Rust, Go, TypeScript, or C code:

- **Atomicity mismatch:** Did the model treat a database read-modify-write or two network RPCs as one atomic step while production performs them without a lock or epoch fence?
- **Mandatory Conformance Bridge:** If the proof is not executed directly on the compiled source code (as Verus, Kani, SPARK, or Frama-C do), require at least one automated bridge in CI:
  1. **Verified code extraction / translation:** Aeneas (Rust $\to$ Lean 4), Fiat Cryptography (Rocq $\to$ C/Rust), KaRaMeL (F\* $\to$ C).
  2. **Refinement proof:** Proving every concrete implementation transition maps to a valid abstract state-machine step (e.g., Anvil, TLA-Verus).
  3. **Structure-aware differential testing / trace validation:** Running millions of randomized inputs through both the executable formal specification (e.g., Lean 4 oracle) and the production engine (e.g., Rust), or validating production execution traces against the state machine (`PObserve`).

### Gap 3: Bounded vs. Unbounded Guarantees

- **Loop unwinding and model bounds:** A bounded model check (`TLC` on 3 nodes, or `Kani`/`CBMC` with `#[kani::unwind(8)]`) proves zero bugs *up to bound $K$*. It proves nothing about $K + 1$ unless replaced by an inductive loop invariant (`proving-with-hoare-logic`) or an unbounded inductive theorem (`proving-with-dependent-types`).
- **Audit requirement:** Verify that unwinding assertions are enabled (`#[kani::unwind(K)]` without disabling unwinding checks) and that the exact bounds ($K$ iterations, $N$ nodes, $M$ bytes) are stated in the verification report.

### Gap 4: The Trusted Computing Base (TCB) & Unmodeled Reality

- **Escape hatches & unverified boundaries:** Any function marked `#[verifier::external_body]`, `@[extern]`, `@[implemented_by]`, `#[trusted]`, `#[kani::stub]`, `sorry`, `admit`, `axiom`, or linked via C FFI is **unverified**.
- **Non-functional & physical side channels:** A functional correctness proof (`valid == (computed_mac == expected_mac)`) operates over mathematical values, not execution time or power consumption. An early-exit byte comparison loop passes functional equivalence while leaking secret cryptographic keys via timing side-channels!
- **Audit requirement:** For cryptographic or secret-handling code, require constant-time execution discipline (no secret-dependent branches, early returns, or memory indices; use bitwise constant-time equality).

## Automated Escape-Hatch Scanner

Run the bundled cheat-detector script on every verification PR or proof directory:

```bash
node skills/auditing-proof-specifications/scripts/check-proof-cheats.mjs <path-to-code-or-specs>
```

For Lean 4 theorems, also require in the proof file:

```lean
#print axioms <theorem_name>
```

Reject any theorem whose `#print axioms` output includes `sorryAx`, a custom `axiom`, or `Lean.ofReduceBool`.

## Common Mistakes & Rationalizations

| Excuse | Reality |
| --- | --- |
| "Verus / Lean 4 / Kani exited 0 (`VERIFICATION SUCCESSFUL`), so the code is mathematically bug-free" | Exit code `0` only means the solver accepted the formula it was handed. `verified_sort` returning `Vec::new()` exits `0` when the permutation law is missing. Always audit all 4 gaps. |
| "`#[verifier::external_body]` is just on a helper serializer, the rest is proved" | `external_body` turns that function's `ensures` clause into an unchecked axiom. A bug inside `external_body` (like swapped SSH key-derivation fields) invalidates every proof that calls it. |
| "The HMAC comparison is proved functionally equal to `compute_hmac(msg, key) == *tag`" | Functional equality in value semantics ignores execution time. An early-return loop (`if a[i] != b[i] { return false; }`) creates a remote timing side-channel. |
| "We proved the policy engine in Lean 4 and have 12 unit tests on the Rust implementation" | 12 unit tests do not bridge a Lean 4 model to a separate hand-written Rust codebase. Require differential fuzzing against the Lean executable oracle, verified extraction, or an in-language Verus proof. |

## Red Flags - STOP and Block Merge

- Any match from `node skills/auditing-proof-specifications/scripts/check-proof-cheats.mjs` (`sorry`, `admit`, `assume`, `external_body`, `axiom`, `native_decide`, `{:verify false}`, `#[kani::stub]`, `--no-unwinding-assertions`, `-no-warn-signed-overflow`)
- Transformation functions (sort, filter, serialize, rebalance) whose `ensures` clause checks shape (e.g., sortedness or tree height) without checking element/multiset conservation
- PRs where an agent modified `requires`, `ensures`, or helper `spec fn` / predicate definitions on the target specification to make the proof pass
- Standalone Lean 4 / Rocq / TLA+ models of production code with zero differential testing, trace validation, or refinement link to the production implementation
- Secret/MAC/key comparisons proved only for functional value equality while using secret-dependent branches or early returns

**All of these mean: Block the merge, report the exact gap(s) violated, and require the specification, conformance bridge, or constant-time implementation to be fixed.**
