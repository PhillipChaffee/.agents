---
alwaysApply: true
description: Route engineering, code cleanup, PR/MR reviewability, research, and formal-proof tasks to /magic-mode, /clean-code, /make-pr-easy-to-review, /research, or /proof-driven-development before acting
---

# Workflow Routing

Before acting on a task, load and follow the matching entry-point skill:

| Observable task signal | Entry-point skill |
| --- | --- |
| Writing, designing, architecting, editing, debugging, refactoring, testing, reviewing, or shipping code, systems, docs, or configuration | `/magic-mode` |
| Opening, creating, updating, or preparing a pull request or merge request for review | `/clean-code` (on code diffs before opening or updating) and `/make-pr-easy-to-review` (on PR/MR structure and description) |
| Investigating a codebase, comparing options, or answering how, why, or where questions across files, web, or MCP | `/research` |
| Writing or auditing formal proofs, loop invariants, state machines, or model-checked specifications | `/proof-driven-development` |
| Unsure which skill, playbook, or principle fits the request | `/magic-help` |

## Exceptions (skip routing)

- The user explicitly names a narrower skill (load that skill instead).
- You were spawned as a subagent to execute a scoped subtask that does not open or update a pull request or merge request.
- The prompt is pure conversation with no repository, tool, or code action.
- The prompt is a single-fact lookup answerable in one file read or search.
