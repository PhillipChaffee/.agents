---
description: "Spawn Comment Sicko, fix accepted findings, and offer encodings for claimed constraints."
enabled: true
id: no-comments
name: no-comments
---

# No comments

Spawn Comment Sicko. Act on accepted findings.

Defer to Comment Sicko's fresh perspective.

## Scope

Use the caller's files or diff. Otherwise use the current diff against the base branch, default `main`, including the working tree.

## Waves

Two depth-1 waves, and neither nests a subagent.

- **Wave 1, the audit.** `comment-sicko` reads the scope and reports.
- **Wave 2, the response.** One `magic-agent` owns Steps 2-4 below, which are the keep-list audit, the fix, and the in-scope root-cause refactor. Spawn it on the `feature, refactoring` line in the `magic-models` role file (see `model-roles.md`), default `main`, or on the `judgment and prose` line, default `deep`, when the round is a pure audit with no code change.

When `comment-sicko` returns `NEEDS-GROUNDING: <symbol>`, run `/how` or `/why` from this chat and add the result to the Wave 2 brief. Both skills are themselves depth-1 wave dispatchers, so grounding never runs inline here.

## Steps

1. Spawn a `comment-sicko` subagent (defined in `agents/comment-sicko/agent.md`; when the harness has no named agent types, a general-purpose subagent with that definition inlined). Take its model from the `comment-sicko` line in the `magic-models` role file (see `model-roles.md`), whose default is `main`. Pass the scope. Pick each subagent's reasoning level and fast or standard speed for the job, per the Subagents section of the **magic-mode** skill. Do not restate its rules. Then dispatch Wave 2 with the report, the scope, the diff, and Steps 2-4 as its brief.
2. **Audit the report in Wave 2.** Reject application-code edits, scope escapes, exception-protected deletions, misstated `MUST KILL` reasons, and flags that treat kept intentional code as guilty. Reshape flags on our-code surprises stay actionable. Do not restore those comments. A keep survives only with proof it is about something we cannot change. Audit missed scoped lint and TypeScript suppressions. Correctness or safety suppressions stay actionable `MUST KILL`s. Restore deletions only with exact exceptions and scoped proof. Before accepting thin `IMPORTANT` or `do not remove` kills or keeps, use the grounding result from the Waves section. If a kill is ambiguous, do not restore. If a keep is refuted or still ambiguous, delete it. If Wave 2 rejects the report, it reverts every invalid `comment-sicko` edit or reports the rejection without applying them, and returns the failure it found, such as a missing `Yes... Ha ha ha... Yes!` line or an invalid deletion. This chat then reruns Wave 1 once at depth 1 with that failure named. Wave 2 never spawns `comment-sicko` itself, and a second rejection is reported open and fails `/no-comments`.
3. **Fix trivial accepted flags in Wave 2** by deleting a dead path, dropping a parameter, or using the real API. If any fix needs a shape, stop and report the need. This chat then runs `/architect` once for the accepted set and surrounding code as its own wave, stops at the sketch, and hands the sketch to a fresh Wave 2 for Step 4.
4. **Implement in Wave 2.** Land the smallest root-cause fix in scope and remove every named workaround. If the root cause is out of scope, land the smallest in-scope fix and report the rest open. The **principle-fix-root-causes** and **principle-redesign-from-first-principles** skills guide intent only. Neither authorizes widening the fence nor fixing instances outside it. Never bolt on symptom guards. Return the proposed encodings from Step 5 as suggestions only, because the wave applies none.
5. **Offer encodings from this chat.** Constraint comments say `do not remove`, `do not change wording`, or `talk to X before changing`. Leave keeps about things we cannot change. Offer the cheapest in-scope type, runtime, test, or CI lint. Wait for interactive approval here. Unattended and eval require caller pre-approval. If approved, dispatch a fresh Wave 2 to encode then delete. Otherwise delete, report the constraint open, and sketch out-of-scope work.
6. Report the deletion count, restored comments, reruns, architect sketch, fixes, encoding offers, encodings, unenforced constraints, and other open work from the Wave 2 report plus this chat's decisions.
