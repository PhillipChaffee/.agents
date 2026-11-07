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

## When to Use

- Proving deep mathematical laws that defeat automated SMT solvers: compiler optimization equivalence, cryptographic primitives, recursive AST evaluators, or authorization policy lattices (e.g., "`forbid` always overrides `permit`").
- Proving impossibility ("forbidden state $S$ can never be reached") by constructing a total function into the uninhabited type (`S -> False` or `S -> Empty`).
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
   - State theorems with universal quantification ($\forall$) over arbitrary inputs, lists, or ASTs—never finite sample fixtures.
   - When proving state-machine safety or impossibility, define an inductive **multi-step reachability relation** (`Reachable : State -> Prop` with `init` and step constructors), not merely a single-step negation (`¬ Step s s'`).
2. **Complete Constructive Proof Strategy:**
   - **Imperative `do` loops in Lean 4:** Discharge with `vcgen invariants` supplying the prefix/accumulator invariant.
   - **Accumulator folds (`List.foldl`):** Never induct directly on a specialized initial accumulator. Prove a generalized helper lemma using `induction xs generalizing acc` (plus an absorption lemma when a state like `.forbid` is a fixed point), then instantiate the initial accumulator.
   - **Impossibility via uninhabited types:** Prove a total function `Reachable s -> ForbiddenState s -> False` (or eliminate a dependent witness structure into `Empty`), showing every constructor of `Reachable` contradicts `ForbiddenState s`.
3. **Kernel Axiom Audit:**
   - Append `#print axioms <theorem_name>` (Lean 4) or `Print Assumptions <theorem_name>.` (Rocq) for every theorem.
   - Confirm the output lists no `sorryAx`, no user-declared `axiom`, and no `Lean.ofReduceBool`.
4. **Model-to-Implementation Bridge:**
   - When the Lean 4 / Rocq / F\* specification models production code written in another language (Rust, TypeScript, Go, C), specify the conformance mechanism: verified code extraction (Aeneas, Fiat, KaRaMeL) or structure-aware differential testing comparing the executable formal specification against the production engine.

## Core Pattern: Executable Spec, Fold Generalization, and Uninhabited Impossibility in Lean 4

```lean
-- 1. Imperative loop proved against functional spec via vcgen
def mySum (l : Array Nat) : Nat := Id.run do
  let mut out := 0
  for i in l do
    out := out + i
  return out

theorem mySum_correct (l : Array Nat) : mySum l = l.sum := by
  generalize h : mySum l = x
  apply Id.of_run_eq_wp h
  vcgen invariants
  · fun prefixArr suffixArr out => prefixArr.sum = out
  with finish

-- 2. Multi-step state reachability + impossibility via uninhabited False
inductive Status where
  | authorized | captured | settled | voided
  deriving DecidableEq, Repr

structure LedgerState where
  status   : Status
  captured : Bool
  amount   : Nat
  deriving DecidableEq, Repr

inductive Reachable : LedgerState -> Prop where
  | init (a : Nat) :
      Reachable ⟨.authorized, false, a⟩
  | capture {s : LedgerState} :
      Reachable s -> s.status = .authorized ->
      Reachable ⟨.captured, true, s.amount⟩
  | voidAuth {s : LedgerState} :
      Reachable s -> s.status = .authorized ->
      Reachable ⟨.voided, s.captured, s.amount⟩
  | settle {s : LedgerState} :
      Reachable s -> s.status = .captured ->
      Reachable ⟨.settled, s.captured, s.amount⟩

/-- Forbidden state: a payment is settled without ever having been captured. -/
structure SettledWithoutCapture (s : LedgerState) : Prop where
  isSettled   : s.status = .settled
  notCaptured : s.captured = false

/-- Curry-Howard impossibility: SettledWithoutCapture is uninhabited for all reachable states. -/
theorem settled_without_capture_impossible {s : LedgerState}
    (hreach : Reachable s) (hbad : SettledWithoutCapture s) : False := by
  induction hreach with
  | init _ =>
    cases hbad.isSettled
  | capture _ _ _ =>
    cases hbad.isSettled
  | voidAuth _ _ _ =>
    cases hbad.isSettled
  | @settle prev hprev hstat ih =>
    -- To settle, prev.status = .captured; inspect how prev became .captured
    cases hprev with
    | init _ => cases hstat
    | capture _ _ =>
      have hcap : (LedgerState.mk .settled true _).captured = false := hbad.notCaptured
      cases hcap
    | voidAuth _ _ => cases hstat
    | settle _ _ => cases hstat

#print axioms mySum_correct
#print axioms settled_without_capture_impossible
```

## Common Mistakes & Rationalizations

| Excuse | Reality |
| --- | --- |
| "Just prove it on 3 sample inputs with `by decide` or `rfl`" | `decide`/`rfl` on concrete fixtures is a unit test, not a universal theorem (`∀`). It proves nothing about input #4. |
| "Add `axiom foldl_helper` for the annoying accumulator step" | An unproved `axiom` bypasses the kernel. A single inconsistent or slightly wrong axiom lets you prove `False`. Generalize the accumulator (`induction xs generalizing acc`). |
| "Use a boolean runtime validator `isInvalidState s == false` instead of `S -> False`" | A runtime boolean check only tests states you pass to it. A total function `Reachable s -> BadState s -> False` proves no execution path can ever construct `BadState`. |
| "Proving `¬ Step .settled s'` is enough to show impossibility" | Single-step outgoing negation only shows `.settled` is terminal; it does not prove that an illegal state cannot be reached from `init`. Always induct over multi-step `Reachable`. |
| "Skip `#print axioms` to save lines" | `#print axioms` is 1 line and is the only local check that catches hidden `sorryAx`, custom axioms, or `native_decide` trust bypasses. |

## Red Flags - STOP and Fix Properly

- Leaving `sorry`, `admit`, `axiom`, `postulate`, `unsafe`, `@[implemented_by]`, or `native_decide` in a proof
- Marking an executable specification function `partial def` or `noncomputable` so it cannot be inductively proved or executed as a differential-testing oracle
- Replacing a universal theorem (`∀ xs`) with concrete examples (`example : evaluate [p1, p2] req = .forbid := rfl`)
- Proving only single-step transition properties instead of inducting over `Reachable : State -> Prop`
- Omitting `#print axioms` / `Print Assumptions` from the proof output
- Proving a Lean 4 / Rocq model of a Rust, TypeScript, or Go service without specifying how the production code is checked against the model

**All of these mean: Generalize the inductive invariant, complete the constructive term, verify `#print axioms`, and state the model-to-code conformance bridge.**
