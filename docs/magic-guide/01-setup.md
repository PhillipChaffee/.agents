# Set up magic

In this page you install the kit, configure models and repository onboarding, and run your first task. Setup is one command plus a short conversation.

## Install the kit

In a terminal, run:

```text
git clone https://github.com/PhillipChaffee/magic.git && cd magic && ./scripts/install.sh --target agents
```

The installer lists each file it installs.

Each command in this guide is invoked as `/<name>`, such as `/setup-magic`, which writes its role file where your harness reads always-applied rules. The [harness adapter](../../skills/magic-mode/references/harness-adapter.md) covers the other differences.

## Pick your models and onboard the repository

Run:

```text
/setup-magic
```

[`/setup-magic`](../../skills/setup-magic/SKILL.md) has two scopes. Scope 1 configures your global models and harness. Scope 2 onboards one repository. When neither a global role file nor `docs/agents/issue-tracker.md` exists, it offers both.

Scope 1 asks five questions and writes the answers in one pass.

1. Orchestrator mode. `thin` is the default. It treats the main chat as a depth-1 wave dispatcher that plans, delegates, and checks while subagents do the scoping, coding, grafting, review, and verification. `standard` lets a strong main chat do scoping and prose itself.
2. Reasoning budget. Choose `unlimited`, `large`, `medium`, or `small`. `large` matches the skill defaults.
3. Core tier models. Pick one model per slot, meaning `orchestrator` for the parent chat, `fast` for cheap mechanical work, `main` for everyday work, and `deep` for design and adversarial judgment.
4. Optional cross-family secondary model. A model from another family gives panels and the `arena cross-judge pool` a stronger second opinion.
5. Accept or customize the role table. Setup fills all 24 role lines from your tier choices, and you change only the roles you care about.

The role file is an always-applied rule where the harness supports one, and otherwise a file the harness lists or magic reads before a spawn. Its lines are already in context when a magic skill runs. It lives where your harness auto-loads such a rule. The [harness adapter](../../skills/magic-mode/references/harness-adapter.md) names every path, including `~/.config/opencode/rules/magic-models.md`, `~/.cursor/rules/magic-models.mdc` with `alwaysApply: true`, `~/.claude/rules/magic-models.md`, `~/.pi/agent/rules/magic-models.md`, and the Codex pair of `~/.agents/rules/magic-models.md` plus `~/.codex/config.toml`.

Setup also writes `~/.agents/models.json` with `orchestrator`, `fast`, `main`, and `deep` under `presets`. That keeps tier fallback working even on a plugin-only install that never ran `scripts/install.sh`.

The defaults run at `xhigh` reasoning, the same as the `large` budget. `unlimited` lifts each model to its highest tier, up to `max`. A model that exposes `max` goes to `max`. A model that tops out at `xhigh` stays there. `medium` and `small` lower the reasoning and spend fewer tokens.

You only override what you care about. A role with no line in the rule keeps the skill's default. To restore a default, delete that role's line. A rerun of `/setup-magic` keeps any role whose model differs from the default. When a default changes, a rule written before the change still pins the old default, so delete those role lines, or delete the file, then run `/setup-magic` again.

You might be wondering what happens if you use the harness's automatic model selection. Set a role to `inherit-parent` or `auto` and magic omits the subagent `model` field, so the subagent inherits your parent chat model. Both values mean the same thing, and neither is a model identifier. Thin mode warns when a role whose default tier is `main` or `deep` still resolves to one of them, because that role then runs on the parent chat, which is the weak-parent failure thin mode exists to avoid. For a panel role the value is a list, and one subagent runs per entry, so the list length sets the panel size. Setup also configures `swarm workers`, the default model for every `/swarm` worker unless a race names a model for each arm.

## Onboard the repository

Scope 2 is idempotent, so you can run it in a new repo without repeating Scope 1. It checks `docs/agents/issue-tracker.md`. When the file is absent, it reads `git remote -v` and the tools in the session, asks one question, and writes the file from [`issue-tracker-templates.md`](../../skills/setup-magic/references/issue-tracker-templates.md). The file records where issues live and the command for every issue and PR operation a magic skill needs, including all 16 forge operations.

Scope 2 also offers a minimal `CONTEXT.md` and a `docs/adr/` stub when they are absent. On a greenfield repo with no commits or lint setup, it checks that the matching `init-<lang>-repo` gates ran, per [`new-repo-setup.md`](../../rules/new-repo-setup.md).

## Accept the verification offers, or don't

At the end of Scope 2, `/setup-magic` looks for a way to prove app behavior in your project, either a `verify-*` skill or an existing harness. If it finds neither, it offers once to generate one with [`/create-verification-skill`](../../skills/create-verification-skill/SKILL.md).

Say yes and it writes `.agents/skills/verify-<app>/`, a project-local skill that teaches agents to drive your app the way a user does. It proves the skill works once before handing it over. Say no and setup moves on. You can run `/create-verification-skill` yourself any time. [Verify and ship](./06-verify-and-ship.md#create-a-project-verification-skill) covers it in depth.

If you're new to magic, say yes. An agent that can check its own work keeps going until the check passes. An agent that can't hands every result back to you to check by hand. Of everything in this guide, the verification skill pays off the most.

Then setup offers once to generate a formal verification skill with [`/create-formal-verification-skill`](../../skills/create-formal-verification-skill/SKILL.md), unless the project already has one. Tests check the cases someone thought to write. A formal verification skill checks one key property of your code, such as "a job never runs twice at once", in every case within a stated scope. Say yes when your code has concurrency, retries, a state machine, or a parser, where a bug is costly and tests rarely reach the case that breaks. Otherwise say no, and run it later if that changes. [Verify and ship](./06-verify-and-ship.md#prove-a-property-with-a-formal-verification-skill) covers it.

After setup, start a new chat. The model rule applies to new sessions.

## Keep the cost in check

magic spends extra tokens on subagents and review panels. That's the price of the rigor. To spend fewer:

- Rerun `/setup-magic` and pick a smaller reasoning budget or cheaper tier models. A strong model in the main chat with cheaper, faster models in the code roles is a good split.
- Set a role to `auto` or `inherit-parent` so it runs on the chat's own model.
- Shorten a panel list. Each entry runs one subagent.
- Save `/magic-mode` for work that needs rigor. A small, obvious edit doesn't.

## Run your first task

Pick something real but small, and describe it the way you'd describe it to a colleague:

```text
/magic-mode add a --json flag to this command. text output stays byte-identical. verify both.
```

Watch the todo list. Its first items are the matched playbook's steps copied in, the Feature playbook for this prompt. If `/magic-mode` skips a step, the step stays in the list with `skip: <reason>`, so you can see what it chose not to do.

From here you can type normal follow-ups. To keep `/magic-mode` on for the whole chat, keep the skill attached for the whole session (the [harness adapter](../../skills/magic-mode/references/harness-adapter.md) names how). Plain Enter attaches the skill to one message, and it fades as the chat moves on.

Next, [route work through `/magic-mode`](./02-magic-mode.md).
