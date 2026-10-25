# .agents Kit

Phillip Chaffee's public agent kit: skills, rules, and sub-agents published under the .agents Protocol, powering a forge-agnostic grill-to-review main flow.

## Language

**Kit**:
The published artifact of this repo — skills, rules, and sub-agents, installable into a conformant harness. _Avoid_: repo (when meaning the artifact, not the git tree), agent pack

**Harness**:
The agent platform that loads the kit (OpenCode today; Cursor, Claude Code possible). The kit stays harness-neutral; harnesses configure their own models. _Avoid_: editor, toolchain

**Skill**:
A workflow in a `skills/<name>/SKILL.md` directory, invoked by the model or user. _Avoid_: slash command, plugin

**Rule**:
An always-applied convention loaded into every session; full text in `rules/`, distilled into `agents.md`. _Avoid_: lint, policy

**Agent**:
A named specialist the harness dispatches into an isolated context; defined in `agents/`, driven by skills. _Avoid_: reviewer, worker

**Forge**:
A code host with issues and PRs/MRs. The kit is forge-agnostic — nothing in `skills/`, `rules/`, or `agents/` targets a host, and issue tracking is per-repo configuration (`docs/agents/issue-tracker.md`, written by `/setup-matt-pocock-skills`): GitHub, GitLab, and Linear all work. _Avoid_: code host, remote

**Main flow**:
The canonical path for feature work: grill the idea, spec it, split tickets, implement test-first, close with the two-tier code review. _Avoid_: pipeline, shipping flow

**Worktree**:
A linked checkout of a repo created with `git worktree add`, where every mutating session happens. _Avoid_: branch folder, scratch clone

**Main checkout**:
The repo's primary working directory, left unedited by agents; new work goes in a worktree instead. _Avoid_: root repo, home directory

**Reference repo**:
full-lint — the strictest-setups repo that owns per-language lint, type, docstring, and coverage enforcement, applied per project by its `init-<lang>-repo` skills, plus the repo-wide hygiene gates this kit self-lints with. _Avoid_: lint repo, standards repo

**Playbook**:
A step list under `skills/poteto-mode/playbooks/` that `/poteto-mode` matches a task to and copies into the todo list verbatim. _Avoid_: recipe, workflow (when meaning the file)

**Principle skill**:
One of the 24 `principle-*` skills, each a single engineering rule that `poteto-mode` indexes and cites by name. _Avoid_: guideline, value

**Role**:
A named model slot a pstack skill spawns a subagent on (`code`, `judgment and prose`, `arena runners`, ...), resolved through the consumer's `pstack-models` role file and then the kit's fast/main/deep tiers; defined in `skills/poteto-mode/references/model-roles.md`. _Avoid_: model slug, preset

**Forge operation**:
A named action on the code host (open PR, list checks, reply to thread, ...) that a pstack playbook asks for and the repo's `docs/agents/issue-tracker.md` maps to a command; defined in `skills/poteto-mode/references/forge-operations.md`. _Avoid_: gh command, API call

**Harness adapter**:
The table at `skills/poteto-mode/references/harness-adapter.md` that maps the pstack skills' neutral terms (subagent kinds, the loop command, the transcript store, rule and skill directories) to each harness. _Avoid_: compatibility shim, Claude Code adapter
