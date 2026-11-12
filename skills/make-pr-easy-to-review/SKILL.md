---
description: Prepare PRs for review by cleaning noisy history, improving PR descriptions, and adding reviewer guidance without changing code behavior. Use for "make this easy to review", "tidy this PR", "clean up commits", or "annotate the diff".
name: make-pr-easy-to-review
---

# Make PR Easy to Review

Prepare a PR so a reviewer can quickly understand the intent, important files, and risk. The default goal is reviewability without behavior changes.

## Resolve the forge first

This skill names the operation, never the command. Before the first PR operation, read the repository's `docs/agents/issue-tracker.md` as [forge-operations.md](../magic-mode/references/forge-operations.md) directs. That file names the forge and its tooling; keep that choice for every later operation in the session. A view is a **view PR**, an update is an **edit PR**, and a new PR is an **open PR**.

## Who runs this skill

- **Already inside a depth-1 leaf subagent** (see the stop rule in [using-magic](../using-magic/SKILL.md)): execute every step in this session. A leaf never spawns a subagent.
- **No subagent tool exposed**, or `orchestrator: standard`: execute every step in this session too.
- **Root chat under `orchestrator: thin` with a subagent tool exposed**: confirm the plan with the user, then dispatch one depth-1 `magic-agent` to perform the history cleanup and the description update. Take its model from the `judgment and prose` role in the `magic-models` role file (see [model-roles.md](../magic-mode/references/model-roles.md)) when the work is mostly narrative, or `feature, refactoring` when it rewrites a branch with conflict resolution, and pass it the plan, the PR identity, and the tree check below.

## Workflow

1. Resolve the target PR from the user-provided URL or current branch with **view PR**.
2. Inspect commits, diff size, changed paths, generated files, and PR description.
3. Identify reviewability issues: noisy commits, stale description, unrelated changes, mixed mechanical and logic changes, missing tests, or unclear reviewer entry points.
4. Propose a plan before rewriting history or force-pushing.
5. Apply safe improvements, then verify the tree or diff still matches the intended code.

## History Cleanup

Only rewrite history when the user asks for it or agrees to the plan. Before rewriting, record the PR's identity and the branch's tree:

```bash
# view PR gives title, head branch, base branch, state, and commits
git fetch origin <headRefName> <baseRefName>
ORIGINAL_TREE=$(git rev-parse origin/<headRefName>^{tree})
```

Good commit groupings usually follow dependency order:

1. Schema/storage or generated API definitions.
2. Core logic.
3. Wiring and integration.
4. UI or surface behavior.
5. Tests.

After rewriting, verify content identity:

```bash
echo "Original tree: $ORIGINAL_TREE"
echo "Current tree:  $(git rev-parse HEAD^{tree})"
git diff origin/<headRefName> --stat
```

Do not push if the tree changed unintentionally: `ORIGINAL_TREE` must equal `HEAD^{tree}`. Then update the PR with **edit PR**, body from a file.

## Reviewer Guidance

When code behavior should stay untouched, prefer PR description and review notes:

- Add a TL;DR that matches the actual diff.
- Separate core files from generated or mechanical files.
- Call out risky behavior changes, migration order, rollout plan, and test coverage.
- Link issue trackers, dashboards, or design docs when they explain intent.

## Guardrails

- Never hide meaningful behavior changes inside "cleanup".
- Do not bypass hooks unless the user explicitly asks.
- If the PR is too large to make reviewable with notes, recommend splitting instead of polishing around the problem.
