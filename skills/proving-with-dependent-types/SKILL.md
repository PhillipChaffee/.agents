---
description: "Use when proving deep mathematical theorems, functional equivalence, compiler passes, cryptographic primitives, or authorization policies using dependent types and interactive proof assistants such as Lean 4, Rocq, Isabelle/HOL, or F*, or when encoding state-machine impossibility via Curry-Howard uninhabited types."
enabled: true
id: proving-with-dependent-types
name: proving-with-dependent-types
---

# Proving with Dependent Types

## Overview

Under the **Curry-Howard correspondence**, mathematical logic and static type systems are the exact same structure: a proposition $P$ is a type, a proof of $P$ is a term inhabiting that type, and proof checking is type checking by a small trusted kernel.

**Violating the letter of kernel verification is violating the spirit of the proof.** Never leave `sorry`, `admit`, custom `axiom` declarations, `native_decide` (`Lean.ofReduceBool`), or finite fixture tests (`#eval` / `rfl` on sample inputs) in place of a universal kernel-checked proof.

**REQUIRED SUB-SKILL:** Use `auditing-proof-specifications` before claiming any proof is complete.

## Wave Assignment

This skill is a depth-1 leaf. Under `orchestrator: thin`, the root chat either dispatches it as a **Wave 3** worker from the `/proof-driven-development` pipeline or wraps it as a heavy leaf, and it runs on the `hardest tasks` role (`deep`). It executes directly in this session and spawns no subagent, because a second wave inside a leaf would nest a wave inside a wave. When the harness exposes no subagent tool, run it inline in this session as well. The hand-off back to the parent is the report plus the exact commands it must run, and the spec audit stays with `/auditing-proof-specifications`.

## When to Use

- Proving deep mathematical laws that defeat automated SMT solvers: compiler optimization equivalence, cryptographic primitives, recursive AST evaluators, or authorization policy lattices (e.g., "`forbid` always overrides `permit`").
- Proving impossibility ("forbidden state $S$ can never be reached") by constructing a total function into the uninhabited type (`S -> False` or `S -> Empty`).
- Building a kernel-verified executable reference model and persistent JSON-RPC Spec Oracle (`OracleMain.lean`) to differential-test both a legacy implementation and a new target port.
- Verifying Rust or C implementations translated into Lean 4 or F\* via Aeneas or KaRaMeL.
- Encoding lightweight Curry-Howard guarantees in everyday languages (TypeScript, Rust) using exhaustive `switch`/`match` with `never`/`!` and phantom or state-indexed types.

**When NOT to use:**

- Routine imperative bounds, array indexing, or loop contracts that an SMT solver discharges automatically in seconds (use `proving-with-hoare-logic`).
- Concurrent message interleavings, network partitions, or bounded bit-level panic checks (use `model-checking-protocols-and-code`).
- Whole-program C runtime error sweeps (use `analyzing-with-abstract-interpretation`).
- Unsure which verification paradigm fits (use `proof-driven-development`).

## The Curry-Howard Translation Table

| Mathematical Logic | Dependent Type System (Lean 4 / Rocq / F\*) | Mainstream Type System (Rust / TypeScript) |
| --- | --- | --- |
| Proposition $P$ | Type `P : Prop` or `Type` | Type `P` |
| Proof of $P$ | Term `t : P` | Value of type `P` |
| Implication $P \implies Q$ | Function type `P -> Q` | Function `(p: P) => Q` |
| Conjunction $P \land Q$ | Product / pair type `P × Q` / `P ∧ Q` | Tuple `[P, Q]` or struct |
| Disjunction $P \lor Q$ | Sum / inductive union `P ⊕ Q` / `P ∨ Q` | Discriminated union / `enum` |
| Universal $\forall x \in A,\; P(x)$ | Dependent function `(x : A) -> P x` | Generic function, type-indexed |
| Existential $\exists x \in A,\; P(x)$ | Dependent pair `Sigma (fun x : A => P x)` | Branded / validated wrapper |
| Falsehood ($\bot$) | Uninhabited type `False` / `Empty` | `never` / `enum Void {}` / `!` |
| Proof of impossibility $\lnot S$ | Total function `S -> False` | Exhaustive match reaching `never` |

## Required Output Contract for Dependent-Type Proofs

Whenever you write or review a dependent-type proof (or pair it with a mainstream type encoding), include all four parts below in order, even when asked for a quick shortcut:

1. **Universal Specification & Multi-Step Reachability:**
   - State theorems with universal quantification ($\forall$) over arbitrary inputs, lists, or ASTs, never finite sample fixtures.
   - Keep all domain types and state-transition functions in the specification modules 100% total (`def`, never `partial def` or `noncomputable`).
   - When proving state-machine safety or impossibility, define an inductive **multi-step reachability relation** (`Reachable : State -> Prop` with `init` and step constructors), not merely a single-step negation (`¬ Step s s'`).
2. **Complete Constructive Proof Strategy:**
   - **Imperative `do` loops in Lean 4:** Discharge with `vcgen invariants` supplying the prefix/accumulator invariant.
   - **Accumulator folds (`List.foldl`):** Never induct directly on a specialized initial accumulator. Prove a generalized helper lemma using `induction xs generalizing acc` (plus an absorption lemma when a state like `.forbid` is a fixed point), then instantiate the initial accumulator.
   - **Impossibility via uninhabited types:** Prove a total function `Reachable s -> ForbiddenState s -> False` (or eliminate a dependent witness structure into `Empty`), showing every constructor of `Reachable` contradicts `ForbiddenState s`.
3. **Kernel Axiom Audit:**
   - Append `#print axioms <theorem_name>` (Lean 4) or `Print Assumptions <theorem_name>.` (Rocq) for every theorem.
   - Confirm the output lists no `sorryAx`, no user-declared `axiom`, and no `Lean.ofReduceBool`.
4. **Model-to-Implementation Bridge (Persistent JSON-Lines Spec Oracle & Two-Stage Differential Conformance):**
   - **Never spawn `lake exe` inside a property-test loop:** Running `lake exe <oracle>` per test case incurs ~150 ms of build-lock + process-spawn overhead per trace ($350{,}000$ traces $\approx 14$ hours), tempting engineers to slash `max_examples` from $50{,}000$ to $20$. Instead:
     1. Build the oracle binary **once** (`lake build`) and invoke the compiled binary directly (`.lake/build/bin/<oracle-name>`).
     2. Implement a **Persistent `stdin`/`stdout` JSON-Lines Server (`OracleMain.lean`)** spawned once per test worker: read one JSON trace line from `stdin`, evaluate the pure total Lean model function, write one JSON result line to `stdout`, and call `stdout.flush`. (Only the outer `IO` stream loop in `OracleMain.lean` may use `partial def loop`; all model functions remain total.)
   - **Two-Stage (Three-Way) Differential Conformance (`Reference == Lean Oracle == Target`):**
     - **Stage 1 (Spec-vs-Reference Gate):** When porting or replacing an existing system (e.g., Python), run $50{,}000$+ property-based traces (`Hypothesis` / `fast-check`) per module comparing the *existing reference implementation* against the persistent Lean 4 oracle binary to prove the spec itself has zero unintended divergence from reality.
     - **Stage 2 (Target-vs-Oracle & Reference Gate):** Run $10^5$ to $10^6$ multi-threaded property-based traces (`proptest`) comparing the *new implementation* against the Lean 4 oracle and reference implementation.

## Core Pattern: Multi-Step Reachability Proof + Persistent `stdin`/`stdout` JSON-Lines Spec Oracle in Lean 4

```lean
import Lean.Data.Json

-- 1. Pure total specification & multi-step reachability in LedgerSpec.lean
inductive Status where
  | authorized | captured | settled | voided
  deriving DecidableEq, Repr

structure LedgerState where
  status   : Status
  captured : Bool
  amount   : Nat
  deriving DecidableEq, Repr

def stepEvent (s : LedgerState) (ev : String) : LedgerState :=
  match s.status, ev with
  | .authorized, "capture" => ⟨.captured, true, s.amount⟩
  | .authorized, "void"    => ⟨.voided, s.captured, s.amount⟩
  | .captured,   "settle"  => ⟨.settled, s.captured, s.amount⟩
  | _,           _         => s

inductive Reachable : LedgerState -> Prop where
  | init (a : Nat) :
      Reachable ⟨.authorized, false, a⟩
  | step {s : LedgerState} (ev : String) :
      Reachable s -> Reachable (stepEvent s ev)

structure SettledWithoutCapture (s : LedgerState) : Prop where
  isSettled   : s.status = .settled
  notCaptured : s.captured = false

theorem reachable_settled_implies_captured {s : LedgerState} (h : Reachable s) :
    (s.status = .captured ∨ s.status = .settled) -> s.captured = true := by
  induction h with
  | init _ =>
    intro hstat; rcases hstat with h | h <;> cases h
  | @step prev ev hprev ih =>
    unfold stepEvent
    cases hstat : prev.status <;> simp [hstat]
    · split <;> try simp
      · intro h; rcases h with h | h <;> cases h
      · intro h; rcases h with h | h <;> cases h
    · split
      · intro _; exact ih (Or.inl hstat)
      · intro _; exact ih (Or.inl hstat)
    · exact ih (Or.inr hstat)
    · intro h; rcases h with h | h <;> cases h

theorem settled_without_capture_impossible {s : LedgerState}
    (hreach : Reachable s) (hbad : SettledWithoutCapture s) : False := by
  have hcap : s.captured = true :=
    reachable_settled_implies_captured hreach (Or.inr hbad.isSettled)
  rw [hbad.notCaptured] at hcap
  cases hcap

#print axioms reachable_settled_implies_captured
#print axioms settled_without_capture_impossible

-- 2. Persistent stdin/stdout JSON-lines oracle server in OracleMain.lean
-- Compiled once via `lake build`, invoked as `.lake/build/bin/ledger-oracle`
partial def oracleLoop (stdin stdout : IO.FS.Stream) : IO Unit := do
  let line ← stdin.getLine
  if line.isEmpty then return ()
  let trimmed := line.trim
  if !trimmed.isEmpty then
    let resp := handleJsonTrace trimmed -- evaluates total `stepEvent` fold
    stdout.putStrLn resp
    stdout.flush
  oracleLoop stdin stdout
```

## Common Mistakes & Rationalizations

| Excuse | Reality |
| --- | --- |
| "Just prove it on 3 sample inputs with `by decide` or `rfl`" | `decide`/`rfl` on concrete fixtures is a unit test, not a universal theorem (`∀`). It proves nothing about input #4. |
| "Spawning `lake exe oracle` per Hypothesis/proptest case takes 150ms, so reduce `max_examples` from 50,000 to 20" | Spawning `lake exe` per example wastes 99.9% of time in build-tool and OS process startup. Compile once (`lake build`) and run a persistent `stdin`/`stdout` JSON-lines oracle process so 350,000 examples finish in seconds. Never slash `max_examples`. |
| "Skip testing the legacy Python code against the Lean 4 oracle; only test the new Rust code against Lean 4" | If your Lean 4 model subtly misstates a priority tie-breaker or edge case from the reference system, testing only `Rust == Lean` will faithfully build the wrong behavior into Rust. Always prove `Reference == Lean Oracle == Target` (Two-Stage Differential Conformance). |
| "Add `axiom foldl_helper` for the annoying accumulator step" | An unproved `axiom` bypasses the kernel. A single inconsistent or slightly wrong axiom lets you prove `False`. Generalize the accumulator (`induction xs generalizing acc`). |
| "Proving `¬ Step .settled s'` is enough to show impossibility" | Single-step outgoing negation only shows `.settled` is terminal; it does not prove that an illegal state cannot be reached from `init`. Always induct over multi-step `Reachable`. |

## Red Flags - STOP and Fix Properly

- Leaving `sorry`, `admit`, `axiom`, `postulate`, `unsafe`, `@[implemented_by]`, or `native_decide` in a proof
- Marking a pure specification function `partial def` or `noncomputable` (only the outer `IO` stdin loop in `OracleMain.lean` may be `partial def`)
- Spawning `lake exe` or a fresh subprocess on every property-test example, or reducing `max_examples` to work around subprocess startup latency
- Skipping Stage 1 differential testing (Reference $\leftrightarrow$ Lean 4 Oracle) when porting or reimplementing an existing system
- Replacing a universal theorem (`∀ xs`) with concrete examples (`example : evaluate [p1, p2] req = .forbid := rfl`)
- Proving only single-step transition properties instead of inducting over `Reachable : State -> Prop`
- Omitting `#print axioms` / `Print Assumptions` from the proof output

**All of these mean: Generalize the inductive invariant, keep model functions total, verify `#print axioms`, and run Two-Stage Differential Conformance against a persistent `.lake/build/bin/<oracle>` process.**
