---
description: Use when starting any conversation or task - establishes how to find, route, and invoke magic skills before any response or action
enabled: true
id: using-magic
name: using-magic
---

# Using Magic

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific scoped subtask that does not open or update a pull request or merge request, ignore this bootstrap skill and execute your assigned task directly. If your subtask opens or updates a pull request or merge request, you MUST still load and follow `/make-pr-easy-to-review`.
</SUBAGENT-STOP>

<EXTREMELY-IMPORTANT>
If you think there is even a 1% chance a skill might apply to what you are doing, you ABSOLUTELY MUST load and follow the skill BEFORE taking action or responding.

IF A SKILL APPLIES TO YOUR TASK, YOU DO NOT HAVE A CHOICE. YOU MUST USE IT.

This is not negotiable. You cannot rationalize your way out of this.
</EXTREMELY-IMPORTANT>

## Entry-Point Routing

Invoke the matching entry-point skill BEFORE any tool call, file read, codebase exploration, or clarifying question. If a narrower skill is explicitly requested, load that skill directly.

| Observable task signal | Entry-point skill |
| --- | --- |
| Writing, editing, debugging, refactoring, testing, reviewing, or shipping code, docs, or configuration, or running multi-step engineering workflows | [`/magic-mode`](../magic-mode/SKILL.md) |
| Opening, creating, updating, or preparing a pull request or merge request for review | [`/make-pr-easy-to-review`](../make-pr-easy-to-review/SKILL.md) (when opening a review-ready PR/MR, or right after opening/updating an early PR/MR) |
| Investigating a codebase, comparing options, or answering how, why, or where questions across files, web, or MCP | [`/research`](../research/SKILL.md) |
| Producing a brief, cited research summary with a head-to-head comparison table | [`/research-summary`](../research-summary/SKILL.md) |
| Writing or auditing formal proofs, loop invariants, state machines, or model-checked specifications | [`/proof-driven-development`](../proof-driven-development/SKILL.md) |
| Unsure which skill, playbook, or principle fits the request | [`/magic-help`](../magic-help/SKILL.md) |

## Exceptions (Skip Entry-Point Routing)

Skip entry-point routing only when one of these observable conditions holds:

- The user explicitly names a narrower skill (load and follow that skill instead).
- You were spawned as a subagent to execute a scoped subtask that does not open or update a pull request or merge request.
- The prompt is pure conversation with no repository, tool, or code action.
- The prompt is a single-fact lookup answerable in one file read or search call.

## Red Flags

These thoughts mean STOP. You are rationalizing around skill routing:

| Thought | Reality |
| --- | --- |
| "This is just a simple question" | Questions that inspect code or compare options are tasks. Check for `/research` or a narrower skill first. |
| "I need more context first" | Skill routing comes BEFORE clarifying questions or ad-hoc exploration. |
| "Let me explore the codebase first" | Skills tell you HOW to explore and delegate. Load the entry-point skill first. |
| "I can check git or files quickly" | Undisciplined reads burn main-thread context. Route first. |
| "This doesn't need a formal skill" | If an entry-point or domain skill applies, use it. |
| "I remember this skill" | Skills evolve. Read the current `SKILL.md` version. |
| "This doesn't count as a task" | Any repository, tool, or code action is a task. Check for skills first. |
| "The skill is overkill" | Simple things become complex. Follow the entry-point skill's sizing rules. |
| "I'll just do this one thing first" | Route BEFORE taking any tool action. |
| "I know what that means" | Knowing the concept does not equal following the skill. Load it. |

## Platform Adaptation

Read [harness-adapter.md](../magic-mode/references/harness-adapter.md) once per session for how neutral terms in kit skills map to your active harness (`Cursor`, `Claude Code`, `Codex`, `OpenCode`, and `Pi`).

## User Instructions

Direct user instructions and project rules (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `rules/`) take precedence over skills, which in turn override default model habits. Only skip a skill workflow when your human partner explicitly tells you to.
