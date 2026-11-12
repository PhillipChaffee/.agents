# Final Review and Finish

Part of `/subagent-driven-development`. Every task in the plan is complete.

## The whole-branch review

When every task is complete, dispatch one whole-branch review over the whole
branch. It gets a package too: run
`bash scripts/review-package PLAN_FILE MERGE_BASE HEAD` by its absolute path,
from the working tree you're executing in (MERGE_BASE = the commit the branch
started from, e.g. `git merge-base main HEAD`) and include the printed path in
the dispatch, so the reviewer reads one file instead of re-deriving the branch
diff with git commands.

Use [task-reviewer-prompt.md](../task-reviewer-prompt.md) as the template,
widened for the branch, and fill every placeholder explicitly:

- **Framing.** Replace the template's framing lines "You are reviewing one
  task's implementation" and "This is a task-scoped gate, not a merge review — a
  broad whole-branch review happens separately after all tasks are complete."
  with "This IS the pre-merge whole-branch review." Everything the template says
  about staying inside the diff still holds; only the scope claim changes. The
  reviewer must not treat a cross-task defect as out of scope.
- **`[BRIEF_FILE]`.** Pass the plan file path, and name the spec path inside
  it. Tell the reviewer to read both.
- **`[GLOBAL_CONSTRAINTS]`.** The plan's `## Global Constraints` section is the
  requirements lens, so copy it into the placeholder verbatim.
- **`[REPORT_FILE]`.** Pass `<workspace>/progress.md`, the ledger, which holds
  every task completion line, the `minor (deferred)` entries, and the
  `parked` lines with their rulings.
- **`[BASE_SHA]` / `[HEAD_SHA]` / `[DIFF_FILE]`.** Pass `MERGE_BASE`, `HEAD`,
  and the package path printed above. There is no task brief and no per-task
  report for this review.
- **Seats.** Take the model from the `arena cross-judge pool` role line in the
  `magic-models` role file (see `model-roles.md`), preferring a seat from a
  family other than the parent chat's. When the pool resolves to the parent's
  own family, or the role file has no such line, use `judgment and prose`
  (default `deep`) and say which family the review ran on. Never run the final
  review on the parent chat's model by omission.
- **Deferred minors.** Point the reviewer at every deferred minor and parked
  line in the ledger, and ask it to triage which of them must be fixed before
  merge. A roll-up nobody reads is a silent discard.

## One fix wave, one re-review

If the final whole-branch review returns findings, dispatch ONE fix subagent
with the complete findings list, not one fixer per finding. Per-finding fixers
each rebuild context and re-run suites; a real session's final-review fix wave
cost more than all its tasks combined. Use the `feature, refactoring` role
(default `main`), or `hardest tasks` (default `deep`) when the findings are
architectural.

Then run exactly one scoped re-review of the fix wave
(`bash scripts/review-package PLAN_FILE FIX_BASE HEAD` by its absolute path,
from the working tree you're executing in, over the fix range,
[re-review-prompt.md](../re-review-prompt.md)).

Adjudicate any residual findings as in the fix loop's breaker
([fix-loop.md](fix-loop.md)): park with rulings, or rule on the load-bearing
ones and ledger what you decided. Under `orchestrator: thin`, when the harness
exposes a subagent tool, those rulings are one depth-1 Adjudicator subagent on
the `judgment and prose` role. Only the four things that stop a running plan
(top of SKILL.md) stop you here. There is no second fix wave: residual
load-bearing findings surface to your human partner when the PR opens.

## Finish

Before you delete anything, collect every ledger line containing `Ruling:`,
preflight rulings, parked findings, breaker adjudications, all of them, into
your final message under "Rulings I made", in the order you made them, each
with what it costs if wrong. The list is exhaustive: if the ledger holds a
ruling, the list holds it. That list is the only place the decisions you took
on your human partner's behalf reach them, and they read it and rework
whatever you got wrong. A ruling that dies with the workspace was a decision
made in secret.

When the final whole-branch review is clean and its fixes are merged, delete
this plan's workspace (`rm -rf <workspace>`): the git history is the record
now. Sibling directories belong to other plans; leave them alone.

Finish by opening the PR through
[opening-a-pr.md](../../magic-mode/playbooks/opening-a-pr.md) and
`/make-pr-easy-to-review`, so the reviewer of the branch gets the cleaned
history and the written context the branch deserves.
