---
description: "Use when reviewing, cleaning, or preparing code changes before committing or opening a pull request or merge request."
enabled: true
id: clean-code
name: clean-code
---

# Clean Code

Clean touched and added code in `git diff` against the base branch before opening or updating a pull request or merge request.

Always preserve intended behavior and keep existing test assertions strict. Never refactor untouched files outside the diff, and never weaken test guardrails to make checks pass.

## Language Router

Route each touched file to its language guide before reviewing changes.

| File extension | Reference guide | Scope and focus |
| --- | --- | --- |
| `.py`, `.pyi` | `references/python.md` | Python AI anti-patterns, typing hygiene, Django pitfalls, and ORM usage |
| `.ts`, `.tsx`, `.mts`, `.cts`, `.js`, `.jsx` | `references/typescript.md` | TypeScript typing discipline, schemas, unions, casts, and tests |
| Other code extensions (`.rs`, `.go`, `.java`, etc.) | Universal AI Slop Checklist | Core slop patterns, dead branches, test theater, and wrappers |
| `.md`, prose files | Skip for `/unslop` | Text slop and writing voice belong in `/unslop` |

## Universal AI Slop Checklist

Scan every modified or added line against these twelve language-agnostic patterns.

| # | Anti-pattern | Tell | Clean alternative |
| --- | --- | --- | --- |
| 1 | Type degradation and escape hatches | Untyped containers, wildcards, raw strings, dynamic property reflection | Strong domain models, typed schemas, or explicit interface contracts |
| 2 | Redundant defensive validation | Re-checking the same bounds, types, or nullability deep inside internal code | Validate once at system ingress; trust internal domain types |
| 3 | Mock theater and private coupling | Spying on internal private functions under test, mocks that assert against themselves | Test observable behavior through public APIs with real inputs or fakes |
| 4 | Blanket error swallowing | Catch-all handlers with silent defaults that discard root-cause stack traces | Catch only narrow expected errors; let unexpected programmer bugs fail loudly |
| 5 | Decorative banners and echo comments | Visual divider banners, commented-out dead code, comments that repeat code names | Delete divider noise; document non-obvious constraints and intent |
| 6 | Single-caller wrapper fragmentation | 1-line helper functions used in only one place to game complexity metrics | Inline the expression at the call site; simplify the underlying branching |
| 7 | Accretion in monolithic files | Appending more branches and magic numbers into sprawling files | Extract cohesive domain modules and shared configuration constants |
| 8 | Encapsulation bypass | Calling unexported or private symbols across module boundaries | Define an explicit public contract; respect module boundaries |
| 9 | Inefficient imperative loops | Row-by-row lookups or writes in loops, destructive delete-and-recreate cycles | Batch lookups, bulk writes, and differential state updates |
| 10 | Weakened test guardrails | Inverting or relaxing assertions to match broken behavior or bypass CI | Fix the underlying logic; never weaken security or schema assertions |
| 11 | Dead code and speculative branches | Unused parameters, dead configuration flags, and unreachable error branches | Delete dead code; build only what is required for current behavior |
| 12 | Hidden imports and coupling cycles | Deferred imports buried inside function bodies to hide circular dependencies | Re-layer modules so dependencies flow in one direction without cycles |

## Execution Steps

Follow these steps to clean touched code before committing.

1. **Inspect the diff.** Run `git diff origin/main...HEAD` or the closest upstream base to inspect all touched lines.
2. **Route files by language.** Check the Language Router to load `references/python.md`, `references/typescript.md`, or the universal checklist.
3. **Scan for slop patterns.** Check every added or modified line against the universal slop checklist and language reference rules.
4. **Clean the diff.** Replace anti-patterns with clean domain modeling, inline single-caller wrappers, eliminate banners, and strengthen types.
5. **Verify with narrowest checks.** Run relevant unit tests, linters, and type checkers to prove behavior and contracts remain intact.

## Rationalization Countermeasures

Watch for these common rationalizations when inspecting diffs.

| Rationalization | Trap and reality | Required fix |
| --- | --- | --- |
| "It is defensive programming." | Bypasses type safety, hides real bugs, and breaks framework invariants. | Trust verified types inside boundaries; let invalid states fail fast. |
| "It avoids a circular dependency." | Deferred imports inside function bodies hide architectural coupling and cycles. | Re-layer modules so dependencies flow strictly in one direction. |
| "The tests pass." | Tests that mock internal functions pass even when runtime behavior breaks. | Test public behavior against real contracts without spying on internals. |
| "Just adjust the test expectation to ship." | Weakens security guardrails and leaks private endpoints or regressions. | Fix the underlying code; never weaken or invert test assertions. |
| "It is just a loose data bag." | Allows impossible or contradictory combinations of state to exist. | Model mutually exclusive states with explicit variants or unions. |
| "The 1-line helper improves readability." | Introduces cognitive indirection and games complexity linters without reuse. | Inline single-caller expressions directly at their call site. |
| "Catching all errors prevents crashes." | Swallows critical bugs like syntax errors or null pointer defects without alerting. | Catch only specific expected domain exceptions; fail loud on unexpected errors. |

## Final Response

Keep every prose block to at most 1-2 sentences, report clean-code findings in a Markdown table, and end with a 1-2 sentence `## TL;DR` section at the bottom.

- Report inspected files, patterns identified, and edits applied.
- Confirm behavior was verified using narrowest executable checks.
- Close with `## TL;DR` (1-2 plain sentences stating the cleaned areas and verification status).

## TL;DR

Clean all touched code in the diff against the universal checklist and language reference guides before opening or updating a PR or MR. Verify every change with narrow executable checks without altering behavior or weakening tests.
