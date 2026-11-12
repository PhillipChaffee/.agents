---
description: Use when starting any conversation or task - establishes how to find, route, and invoke magic skills before any response or action
enabled: true
id: using-magic
name: using-magic
---

# Using Magic

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific scoped subtask that does not open or update a pull request or merge request, ignore this bootstrap skill and execute your assigned task directly. If your subtask opens or updates a pull request or merge request, you MUST still load and follow `/clean-code` (when code changed) and `/make-pr-easy-to-review`.

You are a depth-1 leaf. Run the skill your parent named directly in this session, do every read, check, and edit yourself, and never spawn a subagent. This stop is what keeps a thin-mode `magic-agent` wrap from recursing.
</SUBAGENT-STOP>

<EXTREMELY-IMPORTANT>
If you think there is even a 1% chance a skill might apply to what you are doing, you ABSOLUTELY MUST load and follow the skill BEFORE taking action or responding.

IF A SKILL APPLIES TO YOUR TASK, YOU DO NOT HAVE A CHOICE. YOU MUST USE IT.

This is not negotiable. You cannot rationalize your way out of this.
</EXTREMELY-IMPORTANT>

## Pre-Routing Guard

Route before you explore. Until the entry-point skill loads, make no multi-file exploration, no wide search, and no inline code edit. One file read or one search call to classify the task is the limit.

## Entry-Point Routing

Invoke the matching entry-point skill BEFORE any tool call, file read, codebase exploration, or clarifying question. If a narrower skill is explicitly requested, load that skill directly.

| Observable task signal | Entry-point skill |
| --- | --- |
| Writing, editing, debugging, refactoring, testing, reviewing, or shipping code, docs, or configuration, or running multi-step engineering workflows | [`/magic-mode`](../magic-mode/SKILL.md) |
| Opening, creating, updating, or preparing a pull request or merge request for review | [`/clean-code`](../clean-code/SKILL.md) (on code diffs before opening or updating) and [`/make-pr-easy-to-review`](../make-pr-easy-to-review/SKILL.md) (on PR/MR structure and description) |
| Investigating a codebase, comparing options, or answering how, why, or where questions across files, web, or MCP | [`/research`](../research/SKILL.md) |
| Producing a brief, cited research summary with a head-to-head comparison table | [`/research-summary`](../research-summary/SKILL.md) |
| Writing or auditing formal proofs, loop invariants, state machines, or model-checked specifications | [`/proof-driven-development`](../proof-driven-development/SKILL.md) |
| Unsure which skill, playbook, or principle fits the request | [`/magic-help`](../magic-help/SKILL.md) |

## Thin-Orchestrator Dispatch

Read the `magic-models` orchestrator line, which reads `orchestrator: thin` by default. Under thin mode, when the harness exposes a subagent tool, a direct call to a heavy leaf skill dispatches one depth-1 `magic-agent` that carries that skill's `SKILL.md` path and runs it. The leaf hits `<SUBAGENT-STOP>` above, executes directly, and spawns nothing, so the wrap can never recurse.

The heavy leaf skills are `/tdd`, `/technical-writing`, `/sharpen`, `/make-bot-ui`, `/benchmark-checklist`, the `/proving-*` skills, `/model-checking-protocols-and-code`, `/analyzing-with-abstract-interpretation`, `/auditing-proof-specifications`, and `/statechart`. When the harness exposes no subagent tool, as on Pi without `pi-subagents`, run the leaf skill sequentially in this session instead of failing. Under `orchestrator: standard`, run it inline.

Wrap each heavy leaf on the `magic-models` role its work deserves. Use the `hardest tasks` role for the `/proving-*` skills, `/model-checking-protocols-and-code`, `/analyzing-with-abstract-interpretation`, and `/statechart`. Use a seat from the `arena cross-judge pool`, preferring a family different from the chat's `orchestrator:` line, for `/auditing-proof-specifications`. Use `judgment and prose` for `/technical-writing`, `/sharpen`, and `/benchmark-checklist`. Use `feature, refactoring` for `/tdd` and `/make-bot-ui`.

Skills that dispatch their own depth-1 waves stay out of this list, because a second wrap would nest a wave inside a wave. Such skills include `/blast-radius`, `/arena`, `/architect`, `/research`, `/why`, `/no-comments`, `/interrogate`, `/make-pr-easy-to-review`, `/thermo-nuclear-code-quality-review`, `/writing-plans`, `/subagent-driven-development`, `/writing-skills`, `/proof-driven-development`, and the standalone skills that run their own waves. Load them in the root chat and let their own dispatch rules keep the parent flat.

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
