# .agents Kit

Phillip Chaffee's public agent kit: skills, rules, and sub-agents published under the .agents Protocol, powering a grill-to-review main flow across two forges.

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
A code host with issues and PRs/MRs. This kit targets GitHub only; GitLab and Linear are work-side and out of scope. _Avoid_: code host, remote

**Main flow**:
The canonical path for feature work: grill the idea, spec it, split tickets, implement test-first, close with the two-tier code review. _Avoid_: pipeline, shipping flow

**Reference repo**:
67-sus-95-clean — the strictest-setups repo that owns per-language lint, type, docstring, and coverage enforcement, applied per project by its `init-<lang>-repo` skills. _Avoid_: lint repo, standards repo