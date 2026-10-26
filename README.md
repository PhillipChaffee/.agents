# .agents

[![validate](https://github.com/PhillipChaffee/.agents/actions/workflows/validate.yml/badge.svg)](https://github.com/PhillipChaffee/.agents/actions/workflows/validate.yml) [![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

My public agent setup, synced from `~/.agents`. Home additions, edits, and
deletions define the published agent content. Repository documentation,
installation, validation, and CI live alongside that content. A port of
[pstack](https://github.com/cursor/plugins/tree/main/pstack) adds playbooks
for rigorous coding, design, verification, and review.

## Contents

- **56 active skills:** the 55 pstack skills below, plus `writing-skills` from
  [Superpowers](https://github.com/obra/superpowers). Its companion plugin skills
  and runtime guides remain external dependencies.
- **Seven agents:** the five research agents (`researcher-lite`, `researcher-mid`,
  `researcher-deep`, `research-planner`, `research-synthesizer`) plus pstack's
  `poteto-agent` and `comment-sicko`.
- **Four rules:** `look-it-up`, `new-repo-setup`, `opencode-config-profiles`, and
  `sleeps-and-polling`. Profile names and paths describe my setup, not required
  consumer configuration.
- **37 disabled skills:** the dated Matt Pocock archive in `skills-disabled/`.
  These are preserved as source, not installed or activated.

`agents.kit.md` mirrors the home instruction file and installs as
`~/.agents/agents.md`. The repository's own `agents.md` is separate.
The lockfiles record public upstream provenance; `.kit-stamp` is generated
installation state and is not published. Home `scripts/` are not published.

The home-imported third-party directories retain their source bytes. Their formatting and
example links are excluded from cosmetic lint, but not from secret scanning.
See [third-party notices](THIRD-PARTY-NOTICES.md) for licenses and pinned sources.
Historical design decisions are retained in [docs/adr/](docs/adr/).

## pstack: rigor mode and playbooks

[pstack](https://github.com/cursor/plugins/tree/main/pstack) is Lauren Tan's
Cursor plugin for writing less, higher-quality code: one entry skill that
routes a task to a playbook, a set of principles it cites by name, and
situational skills for understanding, designing, verifying, and shipping.
This kit carries a port of pstack 0.15.32 with harness, model, and forge
adapters (ADR-0008), plus safety fixes for cleanup and generated output paths:

- **Any harness.** Cursor tool names, subagent fields, paths, and features are
  replaced by a neutral vocabulary, mapped to Cursor, Claude Code, and
  protocol consumers in
  [the harness adapter](skills/poteto-mode/references/harness-adapter.md).
  Read it once per session.
- **Any models.** Model slugs are replaced by named roles that resolve to the
  tiers you chose at install (`fast`, `main`, `deep`), with an optional
  per-role override file that `/setup-pstack` writes. See
  [model roles](skills/poteto-mode/references/model-roles.md).
- **Any forge.** `gh` and Origin commands are replaced by named forge
  operations that your repo's `docs/agents/issue-tracker.md` maps to
  commands. See
  [forge operations](skills/poteto-mode/references/forge-operations.md).

Get started: run `/setup-pstack` once, then type `/poteto-mode` and describe
the task with a way to check it. The [pstack guide](docs/pstack-guide/README.md)
walks through a first task; `/poteto-help` answers "which skill?" questions.

Not ported: `tdd` (use an external `/tdd` skill), `typescript-best-practices`
(ADR-0002), `make-bot-ui` (a Grok Bot feature), the `benny` automation pack
(Cursor Automations only), and the GitHub-bound `watch-pr` and `orch` tools;
the babysit and orchestrate playbooks describe the same loops over forge
operations and plain files.

`/tdd` and `/create-skill` remain external dependencies; install them separately.
Their presence in a disabled archive does not activate them.

<details>
<summary>the 23 playbooks</summary>

| Playbook | For |
| --- | --- |
| [investigation](skills/poteto-mode/playbooks/investigation.md) | A read-only question. How does x work, why was y built this way, are we sure. |
| [bug fix](skills/poteto-mode/playbooks/bug-fix.md) | Reproduce a defect, root-cause it, and fix with runtime evidence. |
| [perf issue](skills/poteto-mode/playbooks/perf-issue.md) | Trace a measured slowness and improve it against a baseline. |
| [hillclimb](skills/poteto-mode/playbooks/hillclimb.md) | Sustained, scientific improvement of one metric against a target. |
| [runtime forensics](skills/poteto-mode/playbooks/runtime-forensics.md) | Diagnose a live symptom (leak, idle-CPU spin, glitch) from instrumentation. |
| [trace forensics](skills/poteto-mode/playbooks/trace-forensics.md) | Diagnose a captured profiling artifact. |
| [feature](skills/poteto-mode/playbooks/feature.md) | New or changed behavior, built from a named data shape. |
| [refactoring](skills/poteto-mode/playbooks/refactoring.md) | A behavior-preserving change to structure or shape. |
| [prototype](skills/poteto-mode/playbooks/prototype.md) | A throwaway sketch to make a decision cheaply, or to settle an empirical fork by observing it. |
| [visual parity](skills/poteto-mode/playbooks/visual-parity.md) | Pixel-exact UI equivalence between two implementations. |
| [authoring a skill](skills/poteto-mode/playbooks/authoring-a-skill.md) | Writing or editing a SKILL.md. |
| [eval](skills/poteto-mode/playbooks/eval.md) | Test how a skill or prompt change affects agent behavior, blinded. |
| [babysit](skills/poteto-mode/playbooks/babysit.md) | Drive a PR or a stack to merge-ready: conflicts, review threads, CI. |
| [shipping](skills/poteto-mode/playbooks/shipping.md) | Independently verify a green stack, then land the contiguous verified run bottom-up. |
| [autonomous run](skills/poteto-mode/playbooks/autonomous-run.md) | Drive a long task to completion without stopping. |
| [orchestrate](skills/poteto-mode/playbooks/orchestrate.md) | A standing project handed to one coordinator chat: multi-day, many stacked PRs, fleets of subagents. |
| [autopilot-full](skills/poteto-mode/playbooks/autopilot-full.md) | Run independent PRs to merged with one owner per PR and a swarm verdict before each merge. |
| [autopilot-stack](skills/poteto-mode/playbooks/autopilot-stack.md) | Build and verify one linear base-branch stack for the operator to review and land. |
| [session pickup](skills/poteto-mode/playbooks/session-pickup.md) | Resume or take over a prior agent's in-flight work. |
| [pause safely](skills/poteto-mode/playbooks/pause-safely.md) | Suspend in-flight work cleanly so it can be resumed later. |
| [multi-phase plan](skills/poteto-mode/playbooks/multi-phase-plan.md) | Work that spans phases or stacked PRs. |
| [worktree cleanup](skills/poteto-mode/playbooks/worktree-cleanup.md) | Reclaim disk by pruning merged or abandoned worktrees and stale simulators, safety-gated. |
| [opening a PR](skills/poteto-mode/playbooks/opening-a-pr.md) | Open a ready PR from small ordered commits. Invoked at the end of every other playbook. |

</details>

<details>
<summary>the 31 situational skills</summary>

| Skill | Use it when |
| --- | --- |
| [`/poteto-mode`](skills/poteto-mode/SKILL.md) | Default entry point for any non-trivial task. |
| [`/poteto-help`](skills/poteto-help/SKILL.md) | You're new to pstack, or unsure which skill, playbook, or principle fits. |
| [`/setup-pstack`](skills/setup-pstack/SKILL.md) | You want to pick which models pstack uses per role. Writes the role file. |
| [`/in-your-own-words`](skills/in-your-own-words/SKILL.md) | You want the agent to play back your goal and the problem before it starts. |
| [`/sharpen`](skills/sharpen/SKILL.md) | You want a prompt made deeper, not bigger, before you send it. |
| [`/how`](skills/how/SKILL.md) | You want a walkthrough of how a subsystem works. |
| [`/why`](skills/why/SKILL.md) | You want to know why something was built this way, with evidence from every source the session can reach. |
| [`/recall`](skills/recall/SKILL.md) | You're starting or resuming work and want your recent context on a topic rebuilt. |
| [`/ketchup`](skills/ketchup/SKILL.md) | You want what changed in this chat since your last message, with every call waiting on you. |
| [`/ketchup-video`](skills/ketchup-video/SKILL.md) | You want the `/ketchup` catch-up as a short silent video of slides. |
| [`/blast-radius`](skills/blast-radius/SKILL.md) | You have a small-looking change and want to know what else it could break. |
| [`/architect`](skills/architect/SKILL.md) | You're about to write code that crosses a function boundary and want the shape settled first. |
| [`/arena`](skills/arena/SKILL.md) | You want N parallel attempts at the same thing, then the best parts of each. |
| [`/swarm`](skills/swarm/SKILL.md) | You want N parallel workers across different slices or races, then one report. |
| [`/interrogate`](skills/interrogate/SKILL.md) | You have a diff and want different models to try to break it. |
| [`/automate-me`](skills/automate-me/SKILL.md) | You want your own `-mode` skill, drafted from how you've actually worked. |
| [`/reflect`](skills/reflect/SKILL.md) | A long task landed and you want the recipe captured as a skill edit. |
| [`/correct`](skills/correct/SKILL.md) | You keep correcting agents for the same mistakes. Fixes each class at the highest level that works. |
| [`/teach`](skills/teach/SKILL.md) | You want to actually understand a change or subsystem. |
| [`/benchmark-checklist`](skills/benchmark-checklist/SKILL.md) | You ran a benchmark or measured a speedup or regression. Vets the number first. |
| [`/no-comments`](skills/no-comments/SKILL.md) | Strip comments before review; spawns Comment Sicko. |
| [`/figure-it-out`](skills/figure-it-out/SKILL.md) | No bundled playbook fits. Designs a rigorous, auditable playbook for the task. |
| [`/show-me-your-work`](skills/show-me-your-work/SKILL.md) | You want a reviewable decision trail. Logs decisions to a TSV you can commit. |
| [`/create-verification-skill`](skills/create-verification-skill/SKILL.md) | Your project has no scripted way to prove app behavior. Generates a project-local verify skill. |
| [`/maintain-verification-skill`](skills/maintain-verification-skill/SKILL.md) | Your verify skill's feature map has drifted from the app. |
| [`/create-formal-verification-skill`](skills/create-formal-verification-skill/SKILL.md) | Tests can't reach the case that breaks a race, retry, state machine, parser, or unsafe code. |
| [`/maintain-formal-verification-skill`](skills/maintain-formal-verification-skill/SKILL.md) | Code your formal verification covers has changed since it was last checked. |
| [`/statechart`](skills/statechart/SKILL.md) | Someone who owns the behavior needs to see it as a Mermaid statechart generated from a TLA+ model. |
| [`/unslop`](skills/unslop/SKILL.md) | You're cleaning up writing. Removes AI tells. |
| [`/bro`](skills/bro/SKILL.md) | You want the last message restated in plain human language. |
| [`/technical-writing`](skills/technical-writing/SKILL.md) | Layered doc standard for docs, RFCs, readmes, PR descriptions, commit messages. |

</details>

<details>
<summary>the 24 principles</summary>

| Principle | Group | Rule |
| --- | --- | --- |
| [laziness-protocol](skills/principle-laziness-protocol/SKILL.md) | core | Bias toward deletion and the smallest change that solves the problem. |
| [foundational-thinking](skills/principle-foundational-thinking/SKILL.md) | core | Get the data structures right so downstream code becomes obvious. |
| [redesign-from-first-principles](skills/principle-redesign-from-first-principles/SKILL.md) | core | Redesign as if the requirement had been foundational from day one. |
| [attack-the-premise](skills/principle-attack-the-premise/SKILL.md) | core | When two fixes sharing one premise failed the same gate, test the premise before a third fix. |
| [subtract-before-you-add](skills/principle-subtract-before-you-add/SKILL.md) | core | Remove dead weight first, then build on the simpler base. |
| [minimize-reader-load](skills/principle-minimize-reader-load/SKILL.md) | core | Count layers and hidden state; collapse one-caller wrappers, shrink mutable scope. |
| [outcome-oriented-execution](skills/principle-outcome-oriented-execution/SKILL.md) | core | Converge on the target architecture; skip throwaway compatibility states. |
| [experience-first](skills/principle-experience-first/SKILL.md) | core | Choose user delight over implementation convenience. |
| [exhaust-the-design-space](skills/principle-exhaust-the-design-space/SKILL.md) | core | Build 2-3 competing prototypes and compare before committing. |
| [build-the-lever](skills/principle-build-the-lever/SKILL.md) | core | Build the tool that does or proves it instead of working by hand. |
| [model-the-domain](skills/principle-model-the-domain/SKILL.md) | architecture | Encode the domain in a structure instead of scattered conditionals. |
| [boundary-discipline](skills/principle-boundary-discipline/SKILL.md) | architecture | Guards at system boundaries; trust internal types; keep business logic pure. |
| [type-system-discipline](skills/principle-type-system-discipline/SKILL.md) | architecture | Make illegal states unrepresentable; parse external data at boundaries. |
| [make-operations-idempotent](skills/principle-make-operations-idempotent/SKILL.md) | architecture | Converge to the same end state regardless of partial prior runs. |
| [migrate-callers-then-delete-legacy-apis](skills/principle-migrate-callers-then-delete-legacy-apis/SKILL.md) | architecture | Migrate callers and delete the old API in the same wave. |
| [separate-before-serializing-shared-state](skills/principle-separate-before-serializing-shared-state/SKILL.md) | architecture | Eliminate the sharing first; serialize only for a real invariant. |
| [prove-it-works](skills/principle-prove-it-works/SKILL.md) | verification | Verify against the real artifact, not a proxy or "it compiles". |
| [fix-root-causes](skills/principle-fix-root-causes/SKILL.md) | verification | Trace each symptom to the first place the system went wrong and fix it there. |
| [sequence-verifiable-units](skills/principle-sequence-verifiable-units/SKILL.md) | verification | Small units that each end in a check, verified before the next. |
| [test-behavior-not-implementation](skills/principle-test-behavior-not-implementation/SKILL.md) | verification | Assert what the code's users can observe. |
| [explain-the-number](skills/principle-explain-the-number/SKILL.md) | verification | Find what limits a measured number before you trust it. |
| [guard-the-context-window](skills/principle-guard-the-context-window/SKILL.md) | delegation | Route bulk to subagents; keep summaries in the main thread. |
| [never-block-on-the-human](skills/principle-never-block-on-the-human/SKILL.md) | delegation | Proceed on reversible work; reserve confirmation for irreversible actions. |
| [encode-lessons-in-structure](skills/principle-encode-lessons-in-structure/SKILL.md) | meta | Encode the rule as a lint, flag, check, or script instead of more text. |

</details>

## Install

```sh
git clone https://github.com/PhillipChaffee/.agents.git
cd .agents
./scripts/install.sh --target agents
```

The installer copies active skills and their assets, agents, rules, the home
instruction file, and license notices into `~/.agents`. It does not install
the disabled archive, source lockfiles, or repository-only scripts.
Skill entry points retain both `skill.md` and `SKILL.md` spellings for tools
that require the uppercase filename on case-sensitive filesystems.

Unstamped files that differ are skipped unless `--force` is supplied. Managed
files can be overwritten: preserve local edits before reinstalling. `--dry-run`
previews changes; `--prune` removes obsolete managed files; `--uninstall` removes
managed files while preserving unmanaged files. `--pull` updates existing
mapped source files only; it does not import new paths or deletions.

An interactive installation records consumer-local fast/main/deep choices in
`models.json`; `/setup-pstack` can configure individual role overrides.

Configure models and MCP servers in your harness. Never commit provider keys,
tokens, or private configuration.

## Checks

```sh
./scripts/validate.sh
python3 -m unittest discover -s tests
node --test tests/*.test.mjs
```

CI also checks spelling, Markdown, links, secrets, duplicated code, shell
scripts, and workflow configuration.
