# Issue tracker templates

Each template is a starting point for a repository's `docs/agents/issue-tracker.md`. The template records where a repository keeps its issues and PRs, and the command or tool for every operation a magic skill needs.

`/setup-magic` Scope 2 copies the template that matches the repository forge, replaces `<owner>/<repo>` with the real repository, and deletes the rows the forge does not offer. A skill reads the repository's `docs/agents/issue-tracker.md` before its first forge operation and uses the commands recorded there. The operation names come from [`forge-operations.md`](../../magic-mode/references/forge-operations.md).

## GitHub

This repository tracks issues and PRs on GitHub. The remote is `<owner>/<repo>`.

### GitHub issue operations

| Operation | `gh` command | GitHub MCP |
| --- | --- | --- |
| list | `gh issue list --state open` | `list_issues` |
| view | `gh issue view <number> --comments` | `issue_read` |
| create | `gh issue create --title "..." --body-file <file>` | `issue_write` with `method: create` |
| edit | `gh issue edit <number> --title "..." --body-file <file>` | `issue_write` with `method: update` |
| comment | `gh issue comment <number> --body-file <file>` | `add_issue_comment` |
| label | `gh issue edit <number> --add-label "..." --remove-label "..."` | `issue_write` with `method: update` and the label list |
| close | `gh issue close <number>` | `issue_write` with `state: closed` |

### GitHub forge operations

| Operation | `gh` command | GitHub MCP |
| --- | --- | --- |
| open PR | `gh pr create --base <base> --title "..." --body-file <file>` | `create_pull_request` |
| view PR | `gh pr view <number> --json state,baseRefName,headRefOid,mergeable,mergeStateStatus,isDraft,url` | `pull_request_read` with `method: get` |
| PR for branch | `gh pr list --head <branch> --state open --json number,url` | `list_pull_requests` with the head filter |
| list PRs | `gh pr list --state open --json number,state,headRefName,baseRefName` | `list_pull_requests` |
| list checks | `gh pr checks <number> --json name,state,link` | `pull_request_read` with `method: get_check_runs` |
| watch checks | `gh pr checks <number> --watch` | poll `pull_request_read` with `method: get_check_runs` |
| job log | `gh run view <run-id> --log-failed` | `get_job_logs` |
| rerun checks | `gh run rerun <run-id>` | rerun the workflow run, then poll `list checks` |
| list review threads | `gh api graphql` reviewThreads query | `pull_request_read` with `method: get_review_comments` |
| reply to thread | `gh api` addPullRequestReviewThreadReply mutation | `add_reply_to_pull_request_comment` |
| resolve thread | `gh api graphql` resolveReviewThread mutation | `resolve_review_thread` |
| edit PR | `gh pr edit <number> --base <base> --title "..." --body-file <file>` | `update_pull_request` |
| mark ready | `gh pr ready <number>` | `update_pull_request` with the draft flag cleared |
| merge PR | `gh pr merge <number> --squash` | `merge_pull_request` |
| arm auto-merge | `gh pr merge <number> --auto --squash` | not offered, use the CLI |
| PR history | `gh pr view <number> --json title,body,author,createdAt,mergedAt,labels,closingIssuesReferences,reviews,comments` | `pull_request_read` with the matching methods |

Pass a reply body or a PR body as a file. Never interpolate it into a shell command.

## GitLab

This repository tracks issues and merge requests on GitLab. The remote is `<owner>/<repo>`.

### GitLab issue operations

| Operation | `glab` command | GitLab MCP |
| --- | --- | --- |
| list | `glab issue list` | `list_issues` |
| view | `glab issue view <number> --comments` | `get_issue` |
| create | `glab issue create --title "..." --description "..."` | `create_issue` |
| edit | `glab issue update <number> --title "..." --description "..."` | `update_issue` |
| comment | `glab issue note <number> --message "..."` | `create_issue_note` |
| label | `glab issue update <number> --label "..." --unlabel "..."` | `update_issue` with the label list |
| close | `glab issue close <number>` | `update_issue` with the closed state |

GitLab calls comments notes. `glab issue close` accepts no closing comment, so post the note first, then close.

### GitLab forge operations

| Operation | `glab` command | GitLab MCP |
| --- | --- | --- |
| open PR | `glab mr create --target-branch <base> --title "..." --description "..."` | `create_merge_request` |
| view PR | `glab mr view <number>` | `get_merge_request` |
| PR for branch | `glab mr list --source-branch <branch>` | `list_merge_requests` with the source branch filter |
| list PRs | `glab mr list` | `list_merge_requests` |
| list checks | `glab ci status` | `list_pipelines` and `get_pipeline` |
| watch checks | poll `glab ci status` until every job reaches a terminal state | poll `get_pipeline` |
| job log | `glab ci trace <job-id>` | `get_job_log` |
| rerun checks | `glab ci retry <job-id>` | `retry_job` |
| list review threads | `glab api projects/<id>/merge_requests/<iid>/discussions` | `list_merge_request_discussions` |
| reply to thread | `glab api` POST on the discussion notes endpoint | `create_merge_request_discussion_note` |
| resolve thread | `glab api --method PUT` on the discussion with `resolved=true` | `resolve_merge_request_discussion` |
| edit PR | `glab mr update <number> --target-branch <base> --title "..."` | `update_merge_request` |
| mark ready | `glab mr update <number> --ready` | `update_merge_request` with the draft flag cleared |
| merge PR | `glab mr merge <number> --squash` | `merge_merge_request` |
| arm auto-merge | `glab mr merge <number> --auto-merge` | `merge_merge_request` when the project allows it |
| PR history | `glab mr view <number> --comments` | `get_merge_request` with notes |

Some teams require the ticket ID in the MR title, such as `feat(metrics): expose worker telemetry (ENG-1234)`. Record that convention here when it applies. It applies to every MR in a stack.

## Linear plus GitHub or GitLab

Linear holds the issues. A GitHub or GitLab remote holds the code. Record both halves, and keep the issue key beside each branch and MR title.

### Linear issue operations

| Operation | Linear MCP |
| --- | --- |
| list | `list_issues` with team and state filters |
| view | `get_issue` |
| create | `save_issue` without an id |
| edit | `save_issue` with the issue id |
| comment | `save_comment` with the issue id |
| label | `save_issue` with `addLabels` and `removeLabels` |
| close | `save_issue` with the completed state |

### Linear forge operations

Use the GitHub or GitLab table above for all 16 operations. Put the Linear issue key in every branch name, PR title, and PR body. Read the issue with `get_issue` before opening the PR, and comment the PR URL back with `save_comment`.

## Local Markdown

This repository tracks issues as files under `docs/issues/`. Each file is named `<number>-<slug>.md` and carries a title, state, labels, and a body.

### Local Markdown issue operations

| Operation | Action |
| --- | --- |
| list | List `docs/issues/*.md` and read the state field |
| view | Read the file |
| create | Write a file with the next number |
| edit | Edit the file |
| comment | Append a dated comment section |
| label | Edit the labels field |
| close | Set the state field to closed |

### Local Markdown forge operations

A local markdown repository has no forge. Record the manual step the team uses for each operation, and keep the same operation names.

| Operation | Action |
| --- | --- |
| open PR | Open a branch and a PR or MR on whatever code host the remote names |
| view PR | Read the PR or MR state on that host |
| PR for branch | Look up the open PR or MR for the branch |
| list PRs | List the open PRs or MRs on that host |
| list checks | Read the checks or pipeline on that host |
| watch checks | Poll `list checks` until every check reaches a terminal state |
| job log | Read the failed job log on that host |
| rerun checks | Start one fresh run on that host |
| list review threads | Read the review threads on that host |
| reply to thread | Post a reply from a file |
| resolve thread | Mark the thread resolved |
| edit PR | Change the base, title, or body |
| mark ready | Convert the draft to ready |
| merge PR | Squash-merge and read the PR back with `view PR` |
| arm auto-merge | Ask the host to merge when checks pass |
| PR history | Read the merged change through its PR or MR |
