---
description: "Git worktree conventions: mutating agent work happens in a worktree under ~/worktrees, created on a new branch, removed after merge or abandonment."
alwaysApply: true
---

# Git Worktrees

Every session that mutates a repo — code, docs, skills, config — works inside
a Git worktree. Read-only sessions (research, review, lookups) need none. The
main checkout is never the site of agent edits.

## Create the Worktree

Starting in the main checkout, announce the worktree path, create it on a new
branch, and continue work from inside it — no permission needed:

```text
git worktree add ~/worktrees/<clone-dir-basename>/<branch> -b <branch>
```

- Key the path on the clone directory's basename (`~/git/foo` →
  `~/worktrees/foo/…`), not the repo name, so two clones of one repo never
  collide.
- Name the branch `<issue#>-<slug>` when the work maps to an issue
  (`123-add-worktree-rule`), a bare `<slug>` otherwise — matching the
  PR-title convention.
- Resume existing work in its existing worktree, which `git worktree list`
  finds; putting an existing branch in a new worktree is a question for the
  user, not a default.

A session already inside a worktree continues where it is.

## Retire the Worktree

After the PR merges or the work is abandoned, remove the worktree and delete
its branch:

```text
git worktree remove ~/worktrees/<clone-dir-basename>/<branch>
git branch -d <branch>
```

If `git status --porcelain` shows uncommitted changes, ask the user before
removing; do not discard them silently.
