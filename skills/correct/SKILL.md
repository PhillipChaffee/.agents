---
description: "Find the mistakes agents keep repeating in this repo and make each one impossible. Try architecture first, then types, then a lint whose error names the fix, then a test, and write docs last. Prove each check fails on a real past mistake. Repeat this each time the operator corrects you. Use for /correct."
enabled: true
id: correct
name: correct
---

# Correct

The operator keeps correcting agents in this repo for the same mistakes. Change the repo so the next agent can't make them.

Assume every contributor is an agent that sees only the files it opened, copies the nearest example, and takes the shortest path that compiles. Design the repo so a change that looks right from one file is right for the whole repo.

## How the work is dispatched

Wave 1 mines the evidence and runs on the `why investigators` role (`main`). It reads the evidence sources below and groups the mistakes into classes. A class counts once it has happened twice.

Wave 2 ships the enforcement and runs as one depth-1 `magic-agent`, on the `hardest tasks` role (`deep`) for the structural design or on `feature, refactoring` when the shape is already settled. The root chat hands it the Wave 1 classes and keeps the rule table. When the harness exposes no subagent tool, run both waves inline in this session.

## Find the mistake classes

Hand Wave 1 the evidence, meaning recent commits, reverts, review comments, agent instruction files, and comments that explain workarounds. Each class comes back with the commits or review comments that prove it, so the Wave 2 implementer cites real evidence rather than a plausible story.

## Fix each class at the highest level that works

1. **Eliminate it with architecture.** Give each piece of state one owner and each task one supported way. Hide internals so the wrong import fails. Replace hand-synced lists with one source of truth. Delete old ways and dead code an agent would copy.
2. **Enforce it with types so the bad state can't be written.** If bad code still compiles, add a lint or CI check whose error names the file, type, or function to use instead. If the pattern is already common, fail only when a change adds more.
3. **Test the behavior.** Fix or delete any test that still passes when the behavior it checks breaks, or that fails when only the internals change.
4. **Write docs or agent rules last, only for judgment calls.** Nothing fails when an agent skips them.

## Fix and prove

Then fix the most frequent classes now, one commit each. Prove each new check fails on a real past mistake. Run the same command locally and in CI. Exceptions go on the offending line with a reason, an expiry date, and a human's approval.

## Keep the rule table

Last, keep a table in the agent instruction file that pairs each rule with what enforces it. When the operator corrects you, fix the mistake and add the rule. If the rule was already there and nothing enforces it, that's a repeat, so fix it at the highest level in the same change. Drop a rule once its mistake can't happen.

**Reply.** Open with a 1-2 sentence framing line, then a Markdown table of each class (`| Class | Evidence | Gate | Why the stronger gate was not used |`), bullets for the commands that prove each gate, and a 1-2 sentence `## TL;DR` at the end.
