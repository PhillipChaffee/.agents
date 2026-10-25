---
description: Configure which models pstack uses per role and at what reasoning budget. Detects your available models and writes an always-applied rule that overrides the skill defaults. Use for /setup-pstack, "configure pstack models", "pstack budget", or changing pstack's model choices.
enabled: true
id: setup-pstack
name: setup-pstack
---

# Setup pstack

Write the `pstack-models` role file (see [`model-roles.md`](../poteto-mode/references/model-roles.md)), an always-applied rule that sets pstack's model per role.

## Steps

### 1. Detect available models

Enumerate the model identifiers you can pass to a subagent in this session (the [harness adapter](../poteto-mode/references/harness-adapter.md) says how each harness takes a model for a subagent). That is the dependable source. If the harness also exposes a models API or CLI that lists the user's entitled models, prefer it for completeness. If you cannot detect any, offer the tier names `fast`, `main`, and `deep` plus `inherit-parent` and `auto`, or ask the user to paste the model identifiers they have access to. Never write a real model identifier you have not confirmed is available. The tier names and the aliases `inherit-parent` and `auto` are always valid even though they are not detected models.

### 2. Load current state

The default role-to-model mapping is the rule shape shown in step 5 below. If the role file already exists at the location the harness adapter names, read it and treat its `# budget` line and its role values as the current choices. Otherwise start from those defaults. A line whose role is not in step 5, such as `how critics`, is from a retired role. Drop it.

### 3. Budget, map, and confirm

**(a) Ask for a budget.** Prefer a multiple-choice question over free text (plain text where the harness has no question tool). Offer these four options with these exact labels, and name the current budget when the rule records one. With no rule, say that `large` matches the skill defaults.

- `unlimited — max reasoning`
- `large — xhigh reasoning`
- `medium — high reasoning`
- `small — medium reasoning`

**(b) Apply it.** Build the working table from the skill defaults, and on a re-run keep any role you changed by tier, model, list, or alias (`inherit-parent`, `auto`). `unlimited`, `large`, `medium`, and `small` set the starting reasoning level of every role, panel entries included, to `max`, `xhigh`, `high`, or `medium`, on the ladder `max` > `xhigh` > `high` > `medium` > `low`. Where the harness exposes a reasoning-effort setting, the `# budget` line sets that level. Where it does not, the `# budget` line records the label only. A model that tops out below the target stays at its highest level. `inherit-parent` and `auto` do not change. `large` keeps the defaults.

**(c) Show the roles and confirm.** Show every role with its model, marking any real model identifier not in the detected set as needing a choice. Also list each line step 2 dropped. Ask whether to accept as-is or change specific roles, offering the tier names and the detected models plus `inherit-parent` and `auto` (both mean: this role runs on the parent chat model, which is how users of the harness's automatic model selection stay on it) as the options. Prefer a multiple-choice question over free text. For panel roles (arena runners, architect runners, interrogate reviewers) the value is a list, and one subagent runs per entry, alias entries included, so the list length sets the count. `arena cross-judge pool` is also a list, but Arena selects one value from it whose model family differs from the parent's when possible. `swarm workers` is the default model for every worker unless a race or comparison assigns another model per arm.

### 4. Validate

Every real model identifier written must be in the detected set. The tier names `fast`, `main`, and `deep` and the aliases `inherit-parent` and `auto` always pass. If a chosen real model identifier is not available, stop and ask again.

### 5. Write the rule

Write the role file at the location the harness adapter names, with any header that harness needs for an always-applied rule, a `# budget` line with the chosen label and its target effort, and one line per role, using the same labels poteto-mode uses. Overwrite the whole file so re-runs stay idempotent. Never write `CLAUDE.md`, `AGENTS.md`, or `agents.md`. Shape:

```text
# pstack model configuration. One line per role. Delete a line to fall back to the default tier.
# `inherit-parent` or `auto` as a value: the role runs on the parent chat model (omit the model field). Alias entries in a panel list still count toward its fan-out.
# budget: large (xhigh)
feature, refactoring: main
bug-fix: main
perf-issue: main
hillclimb: main
judgment and prose: deep
hardest tasks: deep
how explorer: main
how explainer: deep
why investigators: main
why synthesizer: deep
reflect tooling: main
reflect judgment, divergent, synthesizer: deep
arena runners: deep, main
arena cross-judge pool: deep, main
swarm workers: main
architect runners: deep, main
interrogate reviewers: deep, main
```

### 6. Confirm

Tell the user the rule was written and that it applies to new sessions. Re-running this skill updates it.

### 7. Offer a verification skill (optional)

Check whether the project has a way to drive the real app for proof (a `verify-*` skill, or an existing harness). If not, offer once: "want a project-local verification skill, so agents can drive the app the way a user does and prove changes work? I can generate one with /create-verification-skill." On yes, invoke `/create-verification-skill` (resolves wherever the kit is installed). On no, move on without pushing.

### 8. Offer a formal verification skill (optional)

Check whether the project already has a formal verification skill (a project skill that runs a model checker, a proof, or another verifier against the code). If not, offer once: "want a formal verification skill, so agents can prove a key property of your code holds in every case in scope, not only the cases tests reach? I can generate one with /create-formal-verification-skill." On yes, invoke `/create-formal-verification-skill` (resolves wherever the kit is installed). On no, move on without pushing.
