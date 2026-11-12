---
description: "Use when configuring magic globally or onboarding a repository, including /setup-magic, model roles, reasoning budget, harness doctor checks, and docs/agents/issue-tracker.md scaffolding."
enabled: true
id: setup-magic
name: setup-magic
---

# Setup magic

This skill has two scopes. Scope 1 configures the user's global model roles and harness. Scope 2 onboards one repository. Run one scope or both.

## Step 0. Select scope

Ask one multiple-choice question. Offer these three choices with these exact labels.

- Both global harness setup and repository onboarding. Default when neither a global `magic-models` file nor `docs/agents/issue-tracker.md` exists.
- Scope 1 only (User and harness global models and doctor).
- Scope 2 only (Repository onboarding). Default when a global `magic-models` file exists and the repository has no `docs/agents/issue-tracker.md`.

Run the Scope 1 steps when the answer includes Scope 1. Run the Scope 2 steps when it includes Scope 2. Scope 2 runs standalone in a new repository without prompting Scope 1 again.

## Scope 1. User and harness global

### Step 1. Detect the harness, models, and current state

Read [`harness-adapter.md`](../magic-mode/references/harness-adapter.md) to learn where this harness loads an always-applied rule and how it passes a model to a subagent. Detect the active harness, the models you can pass to a subagent, an existing `magic-models` file, and an existing `~/.agents/models.json`.

On OpenCode, write one shared `~/.config/opencode/rules/magic-models.md` by default. When OpenCode profile overlays (`personal`, `work-dev`, `work-prod`) have distinct provider entitlements, write one `magic-models-<profile>.md` per profile instead. When you write a per-profile file, also register it. Add its path to the profile overlay JSON's `"instructions"` array, such as `~/.config/opencode/profiles/<profile>.json`, or set `MAGIC_MODELS_PATH` in that profile's environment. Without one of those, OpenCode never loads the file.

### Step 2. Ask the five core choices

Ask these in order. Prefer a multiple-choice question over free text.

(a) Orchestrator mode. Offer `thin` as the recommended default and `standard` as the alternative. `thin` keeps the parent chat as a depth-1 wave dispatcher and delegates scoping, planning, coding, grafting, verification, diff review, and PR prose to role-routed subagents. `standard` lets a strong parent chat handle scoping, diff review, and leaf prose itself.

(b) Reasoning budget. Offer these four labels and name the current budget when the role file records one. With no rule, say that `large` matches the skill defaults.

- `unlimited (max reasoning)`
- `large (xhigh reasoning)`
- `medium (high reasoning)`
- `small (medium reasoning)`

(c) Core tier models. Ask for one model per tier slot, meaning `orchestrator` (the parent chat model), `fast`, `main`, and `deep`.

(d) Optional cross-family secondary model. Offer a model from a family other than the primary tiers. Use it for panel seats and for `arena cross-judge pool`.

(e) Role table. Show the auto-populated role table from Step 4 and ask whether to accept it or customize individual roles. On a re-run, keep every role the user changed by tier, model, or alias.

### Step 3. Validate model identifiers

A real model identifier must be available in this session. Keep every suffix the harness accepts.

- OpenCode `#<variant>`
- Cursor `[effort=...]`
- Claude Code family aliases plus `effort`
- Codex `reasoning_effort`

The tier names `orchestrator`, `fast`, `main`, and `deep`, plus the aliases `inherit-parent` and `auto`, always pass. When `# orchestrator: thin` is set, warn if any role whose default tier is `main` or `deep` still resolves to `inherit-parent` or `auto`. Such a role runs on the parent chat model, which is the weak-parent failure thin mode exists to avoid.

### Step 4. Write the role file

Write `magic-models` at the path `harness-adapter.md` names. Add the always-applied YAML frontmatter where the harness requires it.

```yaml
---
alwaysApply: true
description: magic model and orchestrator role configuration
---
```

Then write the directives, the four tier lines, and all 24 role lines from [`model-roles.md`](../magic-mode/references/model-roles.md). Overwrite the whole file so re-runs stay idempotent. Never overwrite `CLAUDE.md`, `AGENTS.md`, or `agents.md`. The block below shows the recommended defaults, with the chosen mode and budget substituted on a real run.

```text
# magic model configuration. One line per role. Delete a line to fall back to the default tier.
# `inherit-parent` or `auto` leaves the model field out, so the role runs on the parent chat model.
# orchestrator: thin
# budget: large (xhigh)
orchestrator: <the parent chat model>
fast: <a fast model>
main: <a main model>
deep: <a deep model>
feature, refactoring: main
bug-fix: main
perf-issue: main
hillclimb: main
hardest tasks: deep
judgment and prose: deep
how explorer: main
how explainer: deep
why investigators: main
why synthesizer: deep
reflect tooling: main
reflect judgment, divergent, synthesizer: deep
swarm workers: main
arena runners: deep, <a model from another family>
arena cross-judge pool: deep, <a model from another family>
architect runners: deep, main
interrogate reviewers: deep, main
fast, mechanical, miners: fast
researcher-lite, collectors: fast
researcher-mid: main
researcher-deep, planner, synthesizer: deep
arena synthesizer: deep
sdd reviewer: main
comment-sicko: main
```

### Step 5. Sync models.json and run the Harness Doctor

Write `~/.agents/models.json` with `orchestrator`, `fast`, `main`, and `deep` under `presets`. This keeps the tier fallback working on a plugin-only install that never ran `scripts/install.sh`.

Then run the harness checks named in [`harness-adapter.md`](../magic-mode/references/harness-adapter.md).

- Codex needs `multi_agent = true` and `default_subagent_model` in `~/.codex/config.toml`, plus one `~/.codex/agents/<id>.toml` per registered agent role.
- Claude Code treats `CLAUDE_CODE_SUBAGENT_MODEL` as an optional backstop for a spawn that carries no model field.
- Pi needs `pi-subagents` installed, or every spawn runs sequentially in the current session.

## Scope 2. Repository onboarding

Scope 2 is idempotent. A re-run changes only the files that are missing or that the user asks to update.

### Step 6. Check and scaffold the issue tracker

Check `docs/agents/issue-tracker.md`. When it exists, show its forge and go to Step 7.

When it is absent, inspect `git remote -v` and the CLIs and MCP servers this session exposes. Ask one multiple-choice question with these choices.

- GitHub
- GitLab
- Linear plus GitLab or GitHub for code
- Local Markdown
- Skip

For GitHub, GitLab, or Linear, write `docs/agents/issue-tracker.md` from [`references/issue-tracker-templates.md`](./references/issue-tracker-templates.md). Cover both the issue operations and all 16 PR and MR operations listed in [`forge-operations.md`](../magic-mode/references/forge-operations.md). For Local Markdown, use the Local Markdown template and keep issue files under `docs/issues/`. On Skip, leave the file absent and go to Step 7.

### Step 7. Check the domain docs and bootstrap gates

Check `CONTEXT.md` and `docs/adr/`. When either is absent, offer once to scaffold a minimal domain glossary and an ADR directory stub. Write only on a yes.

On a greenfield repository with no commits or no lint setup, read [`new-repo-setup.md`](../../rules/new-repo-setup.md) and confirm that the matching `init-<lang>-repo` skill ran and its gates pass.

### Step 8. Offer the verification skills

Run both offers once each, and skip an offer when the project already has that skill.

(a) Check for a `verify-*` skill or another way to drive the real app. If absent, offer once:

"want a project-local verification skill, so agents can drive the app the way a user does and prove changes work? I can generate one with /create-verification-skill."

On yes, invoke `/create-verification-skill`. On no, move on without pushing.

(b) Check for a formal verification skill that runs a model checker, a proof, or another verifier against the code. If absent, offer once:

"want a formal verification skill, so agents can prove a key property of your code holds in every case in scope, not only the cases tests reach? I can generate one with /create-formal-verification-skill."

On yes, invoke `/create-formal-verification-skill`. On no, move on without pushing.

## Report

Tell the user which scopes ran, the role file path written, the tracker file written or skipped, and any harness check that still needs a manual change.
