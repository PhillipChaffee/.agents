# .agents

My agent kit for real engineering work — research, review, planning, and
shipping. Small, composable skills; specialized sub-agents for the heavy
thinking; always-applied rules that keep every session on the rails.
Published as an [.agents Protocol](https://dotagentsprotocol.com) repo: the
layout is vendor-neutral, version-controllable, and installable into any
conformant consumer.

The kit powers a specific workflow: run a fast model in the main window,
delegate deep work (research, code review, plan review) to sub-agents in
isolated contexts, and keep always-on conventions in rules rather than
hoping the model remembers them.

## What's inside

### Skills

| Skill | What it does | Requires agents |
| --- | --- | --- |
| `ci-lint-test` | Run a project's CI lint/test steps locally before pushing | — |
| `clean-plan` | Tidy an implementation plan so a simple agent can execute it | — |
| `code-review` | Multi-reviewer code review with specialized sub-agents | `cr-planner`, 8 `cr-*` reviewers, `cr-verifier`, `cr-implementer` |
| `deep-research` | Tiered research workflow that scales effort to the task | `researcher-lite/mid/deep`, `research-planner`, `research-synthesizer` |
| `looping-code-review` | Review → minimal fix → re-review loop on a branch | drives `code-review` |
| `looping-plan-review` | Architecture alignment, then plan-review convergence until Approve | drives `plan-review` |
| `mr-review` | End-to-end GitLab MR review; posts findings as draft notes | drives `code-review` |
| `plan-review` | Multi-reviewer plan/design review pipeline | `pr-planner`, 10 `pr-*` reviewers, `pr-verifier`, `pr-implementer` |
| `pre-mr-checklist` | Pre-merge hygiene: imports, types, logging, tests, secrets | — |
| `refactor-planner` | Design a behavior-preserving refactor before touching code | `refactor-code-scout`, `refactor-placement-scout` |
| `ship` | Linear ticket → research → plan → implement → MRs | many (`pr-*`, researchers, `cr-*`) |
| `ultracode` | Exhaustive multi-agent orchestration for high-stakes work | any |
| `setup-agent-kit` | One-time per-repo kit configuration: tracker, labels, doc dirs | — |

### Sub-agents (30)

| Group | Agents |
| --- | --- |
| Code review | `cr-planner`, `cr-security`, `cr-correctness`, `cr-performance`, `cr-architecture`, `cr-organization`, `cr-test-quality`, `cr-deployment-safety`, `cr-simplification`, `cr-verifier`, `cr-implementer` |
| Plan review | `pr-planner`, `pr-problem-scope`, `pr-feasibility`, `pr-risk-rollback`, `pr-completeness`, `pr-adversarial`, `pr-architecture`, `pr-organization`, `pr-naming`, `pr-simplification`, `pr-verifier`, `pr-implementer` |
| Refactor scouts | `refactor-code-scout`, `refactor-placement-scout` |
| Research | `researcher-lite`, `researcher-mid`, `researcher-deep`, `research-planner`, `research-synthesizer` |

### Rules (20)

Always-applied conventions — engineering workflow, minimal changes, plan
structure, MR descriptions, subagent delegation, Python/Django/pytest
style, comment and docstring discipline. Distilled in
[agents.md](agents.md) (the auto-loaded instruction layer); full text in
[rules/](rules/). Two optional rules (`design-docs`, `writing-voice`) are
opt-in per repo.

## Install

| Channel | Command | Notes |
| --- | --- | --- |
| .agents protocol (default) | `git clone https://github.com/PhillipChaffee/.agents.git && cd .agents && ./scripts/install.sh --target agents` | Installs into `~/.agents/` (protocol layout, lowercase `skill.md`). Read by protocol consumers such as the DotAgents desktop app — Cursor and Claude Code do **not** read `~/.agents`. |
| Cursor | `./scripts/install.sh --target cursor --adopt` | Kit trees into `~/.cursor/` (`skills/`, flat `agents/*.md`, `rules/*.mdc`). One-time `--adopt` binds an existing setup; the script never touches Cursor app data (`mcp.json`, `projects/`, `plugins/`, state). |
| Any agent via skills.sh | `npx skills add PhillipChaffee/.agents` | Installs `SKILL.md` files only — companion sub-agents are not included, so agent-dispatching skills degrade (see the requires-agents column). |
| .agents Hub bundle | coming soon | A `.dotagents` bundle installable via the Hub is planned. |

The installer is non-destructive by default: it manages only the paths in
its own stamp manifest, skips unstamped files that differ (use `--force`),
supports `--dry-run`, `--prune`, `--uninstall`, and `--pull` (reverse-sync
edits from the target back into the repo).

## Protocol mapping

| Kit artifact | Repo location | Notes |
| --- | --- | --- |
| `rules/*.mdc` | `rules/<id>.md` | Frontmatter preserved (`alwaysApply`, `globs`); distilled into [agents.md](agents.md) |
| flat `agents/*.md` | `agents/<id>/agent.md` | Protocol frontmatter (`id`, `role`, `enabled`, `connection-type`); ids unchanged so skill dispatch references resolve |
| `skills/<id>/SKILL.md` | same | Uppercase `SKILL.md` kept (Cursor/Claude/skills.sh discover that spelling); the installer emits lowercase `skill.md` into `~/.agents/` so the installed layout is protocol-exact |

## Prerequisites and notes

- `ship` and `mr-review` expect a Linear MCP and a GitLab MCP. Without
  them, tracker-dependent skills are unavailable; research and review
  skills work regardless. Run `setup-agent-kit` once per repo to record
  your tracker, labels, and doc dirs in `.agents/kit.json`.
- Agents carry vendor model slugs (e.g. `cursor-grok-4.6-high-fast`) in
  their `model` frontmatter key — a documented vendor extension; swap for
  your provider's equivalents.
- [mcp.json](mcp.json) and [models.json](models.json) are templates. The
  installer never writes them; never commit real tokens or provider keys.

## Credits

README presentation, the setup-skill pattern, and the installer UX are
inspired by [Matt Pocock's skills repo](https://github.com/mattpocock/skills).
This repo follows the [.agents Protocol](https://dotagentsprotocol.com),
tracking the current draft. Kit content is my own, MIT-licensed — borrow
freely.