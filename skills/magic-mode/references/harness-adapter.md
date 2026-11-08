# Harness adapter

pstack skills are written in a neutral vocabulary. This file maps each neutral term to the harnesses the kit supports (`Cursor`, `Claude Code`, `Codex`, `OpenCode`, and `Pi`). Read it once per session before you follow a pstack skill. If your harness has no row, use the closest mechanism it offers and say so in your reply. Never pass a field or value your harness's tool schema rejects.

`<kit>` means the installed kit root, `~/.agents/` in the protocol layout. A sibling skill is `<kit>/skills/<name>/skill.md` there and `skills/<name>/SKILL.md` in this repository.

## Subagents

| Neutral term | Cursor | Claude Code | Codex | OpenCode (and `.agents` protocol consumers) | Pi |
| --- | --- | --- | --- | --- | --- |
| The subagent tool; "spawn a subagent" | `Task` | `Agent` | `spawn_agent {fork_turns: "none"}` (requires `multi_agent = true` in `~/.codex/config.toml`) | `task` (or the harness's task or agent tool) | Use `subagent` from `pi-subagents` when installed; otherwise execute sequentially in the current session |
| A general-purpose subagent | `subagent_type: generalPurpose` | `subagent_type: "general-purpose"` | `spawn_agent {fork_turns: "none"}` | The default agent (`subagent_type: "general"`) | `subagent` from `pi-subagents` when installed |
| A `poteto-agent` or `comment-sicko` subagent | `subagent_type: "<id>"` when the kit's agents are registered; otherwise a general-purpose subagent with `<kit>/agents/<id>/agent.md` inlined in the brief | Same rule. Registered kit agents may carry a prefix in the type name. | `agent_type: "<id>"` when registered in `~/.codex/agents/`; otherwise inline `<kit>/agents/<id>/agent.md` in the brief | Same rule | Inline `<kit>/agents/<id>/agent.md` in the brief |
| A read-only subagent | `readonly: true` | `subagent_type: "Explore"`. It keeps `Bash`, so the brief also says "do not edit files", and you check `git status` afterward. | `spawn_agent {fork_turns: "none"}` with edits forbidden in the brief | The read-only agent type when there is one; otherwise the default agent with edits forbidden in the brief | `subagent` with edits forbidden in the brief |
| A read-write subagent | `readonly: false` (agent mode). Read-only mode strips MCP access. | `general-purpose`. It keeps the session's MCP servers. | `spawn_agent {fork_turns: "none"}` | The default agent | `subagent` from `pi-subagents` when installed |
| An isolated-worktree subagent | `environment: "cloud"`, or a separate worktree on a new branch from the requested commit | `isolation: "worktree"`. Name the branch or commit the worker checks out. | Create a separate worktree on a new branch from the requested commit and point the subagent at it; do not reuse another worker's tree | Create a separate worktree on a new branch from the requested commit and point the subagent at it; do not reuse another worker's tree | Create a separate worktree on a new branch from the requested commit and point the subagent at it; do not reuse another worker's tree |
| A subagent on this machine | `environment: "local"` | Omit `isolation` | The default | The default | The default |
| "Tell the worker to check out `<b>` first" | `cloud_base_branch: <b>` | Say it in the brief | Say it in the brief | Say it in the brief | Say it in the brief |
| In the background | `run_in_background: true` | Omit. Subagents run in the background and notify you when they finish. | `spawn_agent` runs asynchronously; when idle with children outstanding, wait in bounded stretches with `wait_agent` (`timeout_ms` 300000-600000) | Per the harness | `subagent` async mode when available; otherwise per the extension |
| Resume an existing subagent | `resume` | Spawn a new agent and paste the earlier result into its brief | `followup_task` (delivers your message, triggers a turn, and reloads evicted children) | Per the harness; absent, spawn fresh | `subagent` resume workflow when available; otherwise spawn fresh |
| List the paths in the brief | `file_attachments` | Paths in the brief | Paths in the brief | Paths in the brief | Paths in the brief |
| The model for a role (see [model roles](model-roles.md)) | `model: <slug>` | `model` takes a family name and `effort` takes the reasoning level. A model from another provider cannot be passed, so omit `model` and say so. | Pass both `model` and `reasoning_effort` from the spawn allowlist (with `default_subagent_model` and `default_subagent_reasoning_effort` in `~/.codex/config.toml` as a backstop) | Per the harness's subagent configuration; `~/.agents/models.json` holds the tier choices | Per the harness or `pi-subagents` configuration |
| Reasoning level | The effort token in the slug | `effort` | `reasoning_effort` | Where exposed | Where exposed |
| The fast speed variant | A `-fast` slug | Not exposed; ignore | Where exposed in the spawn allowlist; otherwise ignore | Where exposed | Where exposed |

## Conversation and session

| Neutral term | Cursor | Claude Code | Codex | OpenCode | Pi |
| --- | --- | --- | --- | --- | --- |
| Ask the user one multiple-choice question | `AskQuestion` | `AskUserQuestion`. Absent in `-p` mode, so ask in plain text. | Plain text | `question` tool when offered; otherwise plain text | Plain text |
| Open a todo list | The built-in todo list | `TodoWrite` when the session offers it; otherwise keep the list in your reply and update it at each phase | `update_plan` when offered; otherwise keep the list in your reply and update it at each phase | `todowrite` when offered; otherwise a list in your reply, updated at each phase | Track tasks in plan files or `TODO.md` (or an installed todo/task extension tool) |
| Run the **name** skill or `/<name>` | Attach `/<name>`, or read the sibling `SKILL.md` and follow it | The `Skill` tool when it lists the skill; otherwise `Read` the sibling `SKILL.md` and follow it | Read `<kit>/skills/<name>/SKILL.md` (`skill.md` in a protocol install) and follow it | `skill` (V1) or `use_skill` (V2), or read `<kit>/skills/<name>/skill.md` and follow it | Load skills by reading `SKILL.md` with `read` and follow it |
| Keep a skill attached for the whole session | Pick it from the `/` menu with Option+Enter (Mac) or Alt+Enter (Windows) to make it a custom mode | Name it in the first message of each task, or add a line to `CLAUDE.md` | Add a line to `~/.codex/AGENTS.md` or project `AGENTS.md` | Add a line to `agents.md` | Add a line to `AGENTS.md` |
| The loop command | `/loop` | `/loop` | A scheduled re-prompt, or the harness's loop feature | A scheduled re-prompt, or the harness's loop feature | A scheduled re-prompt, or the harness's loop feature |
| The harness's plan mode | Plan Mode | Plan mode | Plan mode where offered | Where offered | Where offered |
| The session transcript store | `~/.cursor/projects/<slug>/agent-transcripts/`, where the system prompt names the active workspace's directory | `~/.claude/projects/<slug>/<session>.jsonl`. The slug is the workspace path with each `/` and `.` changed to `-`. The newest `.jsonl` directly in that folder is the current session; its `<session>/subagents/` folder holds subagent transcripts. | `~/.codex/sessions/`. With no readable transcript, pass a tight digest of the session instead. | Per the harness. With no readable transcript, pass a tight digest of the session instead. | Per the harness. With no readable transcript, pass a tight digest of the session instead. |
| The harness's tool list and the MCP servers it exposes | The available-tools map, or the enabled MCP servers | `ToolSearch` and the listed MCP servers | The active tool list and configured MCP servers | Per the harness | Per the harness |
| The harness's agent status view | The agents dashboard | None; probe the branch and the store | `list_agents` and `wait_agent` | Per the harness | Per the harness |
| A harness restart | A Cursor restart | A new session | A new session | A new session | A new session |

Read only the active workspace's transcripts. Never glob across other workspaces; that reads private chats from unrelated projects.

## Files and locations

| Neutral term | Cursor | Claude Code | Codex | OpenCode | Pi |
| --- | --- | --- | --- | --- | --- |
| The project's skills directory | `.cursor/skills/` | `.claude/skills/` | `.agents/skills/` | `.agents/skills/` | `.agents/skills/` or `.pi/skills/` |
| The user's skills directory | `~/.cursor/skills/` | `~/.claude/skills/` | `~/.agents/skills/` | `~/.agents/skills/` | `~/.agents/skills/` or `~/.pi/agent/skills/` |
| An always-applied rule | `.cursor/rules/<name>.mdc` with `alwaysApply: true`, or `~/.cursor/rules/` | `CLAUDE.md`, or a file in `~/.claude/rules/` | `~/.codex/AGENTS.md` or project `AGENTS.md` | `agents.md`, or a file in `~/.agents/rules/` | `AGENTS.md` |
| The `pstack-models` role file | `~/.cursor/rules/pstack-models.mdc` | `~/.claude/rules/pstack-models.md` | `~/.agents/rules/pstack-models.md` | `~/.agents/rules/pstack-models.md` | `~/.agents/rules/pstack-models.md` |
| A harness-managed worktree directory | `.cursor/worktrees/<repo>/<name>` | The directory `isolation: "worktree"` creates | The project's configured worktree directory, such as `~/worktrees/<clone>/<branch>` | The project's configured worktree directory, such as `~/worktrees/<clone>/<branch>` | The project's configured worktree directory, such as `~/worktrees/<clone>/<branch>` |
| The agent store (a durable scratch directory the system prompt names) | The agent store path in the system prompt | The scratchpad directory in the system prompt | A directory you create outside the repo and name in your reply | A directory you create outside the repo and name in your reply | A directory you create outside the repo and name in your reply |

## Project features

| Neutral term | Cursor | Claude Code | Codex | OpenCode | Pi |
| --- | --- | --- | --- | --- | --- |
| The review bot | Bugbot | Claude Code Review, or whatever the repository runs | Whatever the repository runs | Whatever the repository runs | Whatever the repository runs |
| A scheduled automation | Cursor Automations | Scheduled tasks | Automations, cron, or a CI schedule | cron, a CI schedule, or the harness's scheduler | cron, a CI schedule, or the harness's scheduler |
| The project's verification skill | A `verify-<app>` skill in the project's skills directory, generated by the **create-verification-skill** skill | Same | Same | Same | Same |
| Browser or CLI driving tools, when the project has no verification skill | The harness's browser tools | The built-in browser, Playwright, or Chrome tools | Playwright or the harness's equivalent | Playwright or the harness's equivalent | Playwright or the harness's equivalent |

When a step needs a feature your harness lacks and no row gives a substitute, put one line in your reply, `Skipped: <step>. <reason>.`, then go on to the next step. Do not stop, ask, or retry. When a later step needs what the skipped step would have made, leave a placeholder and name it in the line.
