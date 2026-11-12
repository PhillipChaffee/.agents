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

Scan every modified or added line against these twelve patterns.

| # | Anti-pattern | Tell | Clean alternative |
| --- | --- | --- | --- |
| 1 | Widened types and type soup | `Any`, `object`, unvalidated `dict`, anonymous tuples, `Record<string, any>` | Strongly typed domain models, schemas, or protocols |
| 2 | Dynamic attribute probing | `getattr`, `hasattr`, `setattr`, reflection on known types | Direct attribute access `obj.attr`, explicit fields, narrowing |
| 3 | Internal mock theater | Mocking internal functions under test, `SimpleNamespace`, fake methods | Test through public boundaries with real fixtures or protocols |
| 4 | Redundant internal checks | Duplicating `isinstance`, `is True`, `.strip()` deep inside internal code | Parse once at system boundary; trust internal types |
| 5 | Section banners and echo docstrings | `# === Properties ===` ASCII lines, docstrings that only restate names | Delete decorative banners; document non-obvious invariants |
| 6 | Single-caller 1-line wrappers | 1-line helper functions called in only one place | Inline the expression directly at the call site |
| 7 | Pasting into god-files | Adding more branches to 2,000+ line sprawling files | Extract cohesive domain modules and shared constants |
| 8 | Cross-module private access | Calling `_private` methods across boundaries, mutating framework state | Promote helper to public contract; use public extension hooks |
| 9 | Inefficient database loops | Looping single-row ORM queries, `.delete()`-recreate destroying audit history | Batch operations (`bulk_create`), diff updates, pure validation |
| 10 | Test theater and weakened assertions | Inverting assertions to match bad output, mock SQL engines, tautological tests | Keep security guardrails strict; test against real databases |
| 11 | Hidden imports and path hacks | Inline function body `import` statements hiding cycles, `sys.path` edits | Top-of-file imports; extract leaf modules or use typing guards |
| 12 | Blanket error swallowing | `except Exception:` or empty `catch {}` discarding stack traces | Catch narrow expected errors; let unexpected crashes fail fast |

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
| "It is defensive programming." | Hides type defects and breaks framework properties like reverse relationships. | Use direct attribute access and trust typed schemas. |
| "It avoids a circular import." | Inline imports hide coupling and architectural cycle flaws. | Move imports to top of file and extract leaf modules. |
| "The tests pass." | Tests mocking internal implementation details pass while production breaks. | Test public behavior with real fixtures and integration points. |
| "Just adjust the test expectation to ship." | Weakens security guardrails and leaks private endpoints or regressions. | Fix the underlying code; never weaken or invert assertions. |
| "It is just an optional state bag." | Allows invalid combinations like loading and error simultaneously. | Replace with a discriminated union representing valid states. |
| "The 1-line helper improves readability." | Introduces cognitive indirection and games complexity metrics without reuse. | Inline single-caller expressions at their call site. |
| "We must catch all exceptions to prevent crashes." | Swallows critical bugs like attribute or type errors without alerting. | Catch only specific expected exceptions; let bugs raise. |

## Final Response

Keep every prose block to at most 1-2 sentences, report clean-code findings in a Markdown table, and end with a 1-2 sentence `## TL;DR` section at the bottom.

- Report inspected files, patterns identified, and edits applied.
- Confirm behavior was verified using narrowest executable checks.
- Close with `## TL;DR` (1-2 plain sentences stating the cleaned areas and verification status).

## TL;DR

Clean all touched code in the diff against the universal checklist and language reference guides before opening or updating a PR or MR. Verify every change with narrow executable checks without altering behavior or weakening tests.
