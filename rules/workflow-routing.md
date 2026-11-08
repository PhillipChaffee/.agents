---
alwaysApply: true
description: Route engineering, research, and formal-proof tasks to /poteto-mode, /research, or /proof-driven-development before acting
---

# Workflow Routing

Before acting on a task, load and follow the matching entry-point skill:

| Observable task signal | Entry-point skill |
| --- | --- |
| Writing, editing, debugging, refactoring, testing, reviewing, or shipping code, docs, or configuration | `/poteto-mode` |
| Investigating a codebase, comparing options, or answering how, why, or where questions across files, web, or MCP | `/research` |
| Writing or auditing formal proofs, loop invariants, state machines, or model-checked specifications | `/proof-driven-development` |
| Unsure which skill, playbook, or principle fits the request | `/poteto-help` |

## Exceptions (skip routing)

- The user explicitly names a narrower skill (load that skill instead).
- You were spawned as a subagent to execute a scoped subtask.
- The prompt is pure conversation with no repository, tool, or code action.
- The prompt is a single-fact lookup answerable in one file read or search.
