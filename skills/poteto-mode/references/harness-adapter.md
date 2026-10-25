# Harness adapter

pstack skills are written in a neutral vocabulary. This file maps each neutral term to the harnesses the kit's owner has used. Read it once per session before you follow a pstack skill. If your harness has no row, use the closest mechanism it offers and say so in your reply. Never pass a field or value your harness's tool schema rejects.

`<kit>` means the installed kit root, `~/.agents/` in the protocol layout. A sibling skill is `<kit>/skills/<name>/skill.md` there and `skills/<name>/SKILL.md` in this repository.

## Subagents

| Neutral term | Cursor | Claude Code | Protocol consumer (OpenCode and others) |
| --- | --- | --- | --- |
| The subagent tool; "spawn a subagent" | `Task` | `Agent` | The harness's task or agent tool |
| A general-purpose subagent | `subagent_type: generalPurpose` | `subagent_type: "general-purpose"` | The default agent |
| A `poteto-agent` or `comment-sicko` subagent | `subagent_type: "<id>"` when the kit's agents are registered; otherwise a general-purpose subagent with `<kit>/agents/<id>/agent.md` inlined in the brief | Same rule. Registered kit agents may carry a prefix in the type name. | Same rule |
| A read-only subagent | `readonly: true` | `subagent_type: "Explore"`. It keeps `Bash`, so the brief also says "do not edit files", and you check `git status` afterward. | The read-only agent type when there is one; otherwise the default agent with edits forbidden in the brief |
| A read-write subagent | `readonly: false` (agent mode). Read-only mode strips MCP access. | `general-purpose`. It keeps the session's MCP servers. | The default agent |
| An isolated-worktree subagent | `environment: "cloud"`, or a worktree you create per the kit's `git-worktrees` rule | `isolation: "worktree"`. Name the branch or commit the worker checks out. | Create the worktree per the kit's `git-worktrees` rule and point the subagent at it |
| A subagent on this machine | `environment: "local"` | Omit `isolation` | The default |
| "Tell the worker to check out `<b>` first" | `cloud_base_branch: <b>` | Say it in the brief | Say it in the brief |
| In the background | `run_in_background: true` | Omit. Subagents run in the background and notify you when they finish. | Per the harness |
| Resume an existing subagent | `resume` | Spawn a new agent and paste the earlier result into its brief | Per the harness; absent, spawn fresh |
| List the paths in the brief | `file_attachments` | Paths in the brief | Paths in the brief |
| The model for a role (see [model roles](model-roles.md)) | `model: <slug>` | `model` takes a family name and `effort` takes the reasoning level. A model from another provider cannot be passed, so omit `model` and say so. | Per the harness's subagent configuration; `~/.agents/models.json` holds the tier choices |
| Reasoning level | The effort token in the slug | `effort` | Where exposed |
| The fast speed variant | A `-fast` slug | Not exposed; ignore | Where exposed |

## Conversation and session

| Neutral term | Cursor | Claude Code | Protocol consumer |
| --- | --- | --- | --- |
| Ask the user one multiple-choice question | `AskQuestion` | `AskUserQuestion`. Absent in `-p` mode, so ask in plain text. | Plain text |
| Open a todo list | The built-in todo list | `TodoWrite` when the session offers it; otherwise keep the list in your reply and update it at each phase | A list in your reply, updated at each phase |
| Run the **name** skill or `/<name>` | Attach `/<name>`, or read the sibling `SKILL.md` and follow it | The `Skill` tool when it lists the skill; otherwise `Read` the sibling `SKILL.md` and follow it | Read `<kit>/skills/<name>/skill.md` and follow it |
| Keep a skill attached for the whole session | Pick it from the `/` menu with Option+Enter (Mac) or Alt+Enter (Windows) to make it a custom mode | Name it in the first message of each task, or add a line to `CLAUDE.md` | Add a line to `agents.md` |
| The loop command | `/loop` | `/loop` | A scheduled re-prompt, or the harness's loop feature |
| The harness's plan mode | Plan Mode | Plan mode | Where offered |
| The session transcript store | `~/.cursor/projects/<slug>/agent-transcripts/`, where the system prompt names the active workspace's directory | `~/.claude/projects/<slug>/<session>.jsonl`. The slug is the workspace path with each `/` and `.` changed to `-`. The newest `.jsonl` directly in that folder is the current session; its `<session>/subagents/` folder holds subagent transcripts. | Per the harness. With no readable transcript, pass a tight digest of the session instead. |
| The harness's tool list and the MCP servers it exposes | The available-tools map, or the enabled MCP servers | `ToolSearch` and the listed MCP servers | Per the harness |
| The harness's agent status view | The agents dashboard | None; probe the branch and the store | Per the harness |
| A harness restart | A Cursor restart | A new session | A new session |

Read only the active workspace's transcripts. Never glob across other workspaces; that reads private chats from unrelated projects.

## Files and locations

| Neutral term | Cursor | Claude Code | Protocol consumer |
| --- | --- | --- | --- |
| The project's skills directory | `.cursor/skills/` | `.claude/skills/` | `.agents/skills/` |
| The user's skills directory | `~/.cursor/skills/` | `~/.claude/skills/` | `~/.agents/skills/` |
| An always-applied rule | `.cursor/rules/<name>.mdc` with `alwaysApply: true`, or `~/.cursor/rules/` | `CLAUDE.md`, or a file in `~/.claude/rules/` | `agents.md`, or a file in `~/.agents/rules/` |
| The `pstack-models` role file | `~/.cursor/rules/pstack-models.mdc` | `~/.claude/rules/pstack-models.md` | `~/.agents/rules/pstack-models.md` |
| A harness-managed worktree directory | `.cursor/worktrees/<repo>/<name>` | The directory `isolation: "worktree"` creates | `~/worktrees/<repo>/<branch>` per the kit's `git-worktrees` rule |
| The agent store (a durable scratch directory the system prompt names) | The agent store path in the system prompt | The scratchpad directory in the system prompt | A directory you create outside the repo and name in your reply |

## Project features

| Neutral term | Cursor | Claude Code | Protocol consumer |
| --- | --- | --- | --- |
| The review bot | Bugbot | Claude Code Review, or whatever the repository runs | Whatever the repository runs |
| A scheduled automation | Cursor Automations | Scheduled tasks | cron, a CI schedule, or the harness's scheduler |
| The project's verification skill | A `verify-<app>` skill in the project's skills directory, generated by the **create-verification-skill** skill | Same | Same |
| Browser or CLI driving tools, when the project has no verification skill | The harness's browser tools | The built-in browser, Playwright, or Chrome tools | Playwright or the harness's equivalent |

When a step needs a feature your harness lacks and no row gives a substitute, put one line in your reply, `Skipped: <step>. <reason>.`, then go on to the next step. Do not stop, ask, or retry. When a later step needs what the skipped step would have made, leave a placeholder and name it in the line.
