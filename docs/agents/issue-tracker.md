# Issue tracker: GitHub

Issues and specs for this repo live as GitHub issues. Use the `gh` CLI for all operations.

## Conventions

- **Create an issue**: `gh issue create --title "..." --body "..."`. Use a heredoc for multi-line bodies.
- **Read an issue**: `gh issue view <number> --comments`, filtering comments by `jq` and also fetching labels.
- **List issues**: `gh issue list --state open --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'` with appropriate `--label` and `--state` filters.
- **Comment on an issue**: `gh issue comment <number> --body "..."`
- **Apply / remove labels**: `gh issue edit <number> --add-label "..."` / `--remove-label "..."`
- **Close**: `gh issue close <number> --comment "..."`

Infer the repo from `git remote -v`; `gh` does this automatically when run inside a clone.

## Pull requests as a triage surface

**PRs as a request surface: no.** _(Set to `yes` if this repo treats external PRs as feature requests; `/triage` reads this flag.)_

When set to `yes`, PRs run through the same labels and states as issues, using the `gh pr` equivalents:

- **Read a PR**: `gh pr view <number> --comments` and `gh pr diff <number>` for the diff.
- **List external PRs for triage**: `gh pr list --state open --json number,title,body,labels,author,authorAssociation,comments` then keep only `authorAssociation` of `CONTRIBUTOR`, `FIRST_TIME_CONTRIBUTOR`, or `NONE` (drop `OWNER`/`MEMBER`/`COLLABORATOR`).
- **Comment / label / close**: `gh pr comment`, `gh pr edit --add-label`/`--remove-label`, `gh pr close`.

GitHub shares one number space across issues and PRs, so a bare `#42` may be either: resolve with `gh pr view 42` and fall back to `gh issue view 42`.

## When a skill says "publish to the issue tracker"

Create a GitHub issue.

## When a skill says "fetch the relevant ticket"

Run `gh issue view <number> --comments`.

## Wayfinding operations

Used by `/wayfinder`. The **map** is a single issue with **child** issues as tickets.

- **Map**: a single issue labelled `wayfinder:map`, holding the Notes / Decisions-so-far / Fog body. `gh issue create --label wayfinder:map`.
- **Child ticket**: an issue linked to the map as a GitHub sub-issue (`gh api` on the sub-issues endpoint). Where sub-issues aren't enabled, add the child to a task list in the map body and put `Part of #<map>` at the top of the child body. Labels: `wayfinder:<type>` (`research`/`prototype`/`grilling`/`task`). Once claimed, the ticket is assigned to the driving dev.
- **Blocking**: GitHub's **native issue dependencies**, the canonical, UI-visible representation. Add an edge with `gh api --method POST repos/<owner>/<repo>/issues/<child>/dependencies/blocked_by -F issue_id=<blocker-db-id>`, where `<blocker-db-id>` is the blocker's numeric **database id** (`gh api repos/<owner>/<repo>/issues/<n> --jq .id`, _not_ the `#number` or `node_id`). GitHub reports `issue_dependencies_summary.blocked_by` (open blockers only, the live gate). Where dependencies aren't available, fall back to a `Blocked by: #<n>, #<n>` line at the top of the child body. A ticket is unblocked when every blocker is closed.
- **Frontier query**: list the map's open children (`gh issue list --state open`, scoped to the map's sub-issues / task list), drop any with an open blocker (`issue_dependencies_summary.blocked_by > 0`, or an open issue in the `Blocked by` line) or an assignee; first in map order wins.
- **Claim**: `gh issue edit <n> --add-assignee @me`, the session's first write.
- **Resolve**: `gh issue comment <n> --body "<answer>"`, then `gh issue close <n>`, then append a context pointer (gist + link) to the map's Decisions-so-far.

## Pull request operations

The pstack playbooks name forge operations (defined in `skills/poteto-mode/references/forge-operations.md`) and leave the command to this file. On this repo they resolve to `gh`:

| Operation | Command |
| --- | --- |
| open PR | `gh pr create --base <branch> --title "..." --body-file <file>` (never `--draft`) |
| view PR | `gh pr view <n> --json state,baseRefName,headRefOid,mergeable,mergeStateStatus,isDraft,url` |
| PR for branch | `gh pr list --head <branch> --state open --json number,state,baseRefName` |
| list PRs | `gh pr list --author @me --state all --limit 1000 --json number,state,headRefName,baseRefName` |
| list checks | `gh pr checks <n> --json name,state,conclusion,link` |
| watch checks | `gh pr checks <n> --watch` |
| job log | `gh run view <run-id> --log-failed` |
| rerun checks | `gh run rerun <run-id>` (a whole run, never `--failed`) |
| list review threads | `gh api graphql` over `pullRequest.reviewThreads` with `isResolved`, `comments.author.login`, `path`, `line`, `body` |
| reply to thread | `gh api --method POST repos/<owner>/<repo>/pulls/<n>/comments/<comment-id>/replies --input <payload.json>` |
| resolve thread | `gh api graphql` mutation `resolveReviewThread` |
| edit PR | `gh pr edit <n> --base <branch>` / `--title` / `--body-file <file>` |
| mark ready | `gh pr ready <n>` |
| merge PR | `gh pr merge <n> --squash`, then read back with view PR |
| arm auto-merge | `gh pr merge <n> --squash --auto` |
| PR history | `gh pr view <n> --json title,body,author,createdAt,mergedAt,labels,closingIssuesReferences,comments,reviews` |

`worktree-audit.sh` takes the list PRs command through `WORKTREE_AUDIT_PR_CMD`, for example `gh pr list --author @me --state all --limit 1000 --json number,state,headRefName | jq '[.[] | {number, state, head: .headRefName}]'`.
