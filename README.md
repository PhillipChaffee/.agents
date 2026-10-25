# .agents

[![validate](https://github.com/PhillipChaffee/.agents/actions/workflows/validate.yml/badge.svg)](https://github.com/PhillipChaffee/.agents/actions/workflows/validate.yml) [![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

My personal agent kit — add-ons for my everyday coding workflow. The main
flow is [Matt Pocock's skills](https://github.com/mattpocock/skills),
installed separately; this kit layers on top of it: a combined two-tier code
review, tiered research, worktree discipline, always-applied rules, and a
harness-neutral port of [pstack](https://github.com/cursor/plugins/tree/main/pstack)
for rigorous, playbook-driven work. Published as
an [.agents Protocol](https://dotagentsprotocol.com) repo: the layout is
vendor-neutral, version-controllable, and installable into any conformant
consumer.

## The workflow

My main flow is Matt Pocock's skills, not part of this kit:

1. **Grill the idea** (`/grill-with-docs`) — interview it sharp, record decisions in `CONTEXT.md`
2. **Spec it** (`/to-spec`), **split tickets** (`/to-tickets`) with blocking edges
3. **Implement** each ticket (`/implement` driving `/tdd`), fresh context per ticket
4. **Close with `/code-review`** — served by this kit's combined two-tier review (see below)

`/triage` is the on-ramp for incoming issues; `/wayfinder` charts efforts too large
for one session. For a task that needs rigor more than ceremony, `/poteto-mode`
(see [pstack](#pstack-rigor-mode-and-playbooks) below) matches it to a playbook and
runs the right skills as the steps fire.

### Install the main flow first

```sh
npx skills@latest add mattpocock/skills
```

Pick the skills you want; run `/setup-matt-pocock-skills` once per repo to
record the issue tracker, triage labels, and domain-doc layout in
`docs/agents/`. Two names overlap deliberately: this kit's `code-review`
(combined two-tier) and `research` (tiered, repo-file output) replace his
two-axis `code-review` and `research` — skip those two when picking, or
uninstall his copies after, so the kit's versions own the names. The pstack
skills route `/tdd` and `/create-skill` to his copies, so keep those two.

## What this kit adds

The pieces his set doesn't ship, by what they get you in the flow:

- **Worktree discipline** — every mutating agent session works in a git
  worktree under `~/worktrees/`, never in the main checkout
- **A more in-depth code review** — the combined two-tier review: a standard
  two-axis pass, then when warranted a deep tier with a specialist subagent
  panel, an adversarial verifier, a walkthrough, and fixes applied in place
- **A better research skill** — tiered research from a direct answer up to a
  full research→synthesis pipeline, writing a cited
  `docs/research/<topic>.md` for the main flow to consume
- **A rigor mode with playbooks** — pstack's `/poteto-mode` matches a task to
  one of 23 playbooks (bug fix, feature, perf, babysit, shipping, orchestrate,
  …), cites 24 one-principle skills, and routes to `how`, `why`, `architect`,
  `arena`, `swarm`, `interrogate`, and the rest as the steps need them; ported
  so it runs on any harness, any model provider, and any forge
- **Specific subagent behavior** — delegation rules: when to work inline
  versus dispatch, self-contained prompts, curated-not-pasted output, model
  tiers pinned by the harness rather than the kit
- **A look-it-up policy** — no answers from memory when a source exists;
  official docs first, citations included
- **New projects set up with full linting** — the `full-lint` reference
  repo's `init-<lang>-repo` skills bootstrap a new project with the
  strictest workable lint, type-check, docstring, formatter, and coverage
  gates

### What's inside

#### Skills (57)

The kit's own:

| Skill | What it does |
| --- | --- |
| `code-review` | Two-tier review: standard = two-axis (Standards + Spec); deep = specialist panel + verifier + walkthrough + applied fixes |
| `research` | Tiered research: direct answers, background research, or a full research→synthesis pipeline; Tier 2/3 write a cited file to `docs/research/` for the main flow to consume |

The 55 pstack skills are listed under [pstack](#pstack-rigor-mode-and-playbooks).

#### Sub-agents (18)

| Group | Agents |
| --- | --- |
| Code review | `cr-planner`, `cr-security`, `cr-correctness`, `cr-performance`, `cr-architecture`, `cr-organization`, `cr-test-quality`, `cr-deployment-safety`, `cr-simplification`, `cr-verifier`, `cr-implementer` |
| Research | `researcher-lite`, `researcher-mid`, `researcher-deep`, `research-planner`, `research-synthesizer` |
| pstack | `poteto-agent` (the delegate wrapper for `/poteto-mode` runs), `comment-sicko` (the read-only comment reviewer behind `/no-comments`) |

#### Rules (7)

| Rule | What it covers |
| --- | --- |
| `code-organization` | Every symbol goes where a reader would look; moves carry tests, imports, and patch targets along |
| `comment-style` | Comments carry why, not what; present state only, host-docstring density |
| `git-worktrees` | Mutating agent sessions work in a worktree under `~/worktrees/`; the main checkout stays unedited |
| `look-it-up` | Look up what can be looked up — official docs first, then primary sources, cited |
| `minimal-changes` | Smallest change that works; delete over work around |
| `subagents` | Inline only for narrow checks; delegate the rest in parallel; self-contained prompts, curated output |
| `writing-voice` | Opt-in: fill-in template for your own writing voice |

Distilled into `agents.kit.md`, installed as `~/.agents/agents.md` (the
auto-loaded instruction layer); full
text in [rules/](rules/). The kit carries **no language rules** — per-language lint,
type, docstring, and coverage enforcement lives in the
[full-lint](https://github.com/PhillipChaffee/full-lint) reference
repo, applied per project by its `init-<lang>` skills; the kit's own repo-wide
hygiene gates are copied from that repo.

#### Domain docs

`CONTEXT.md` (glossary) + `docs/agents/` (tracker, triage labels,
domain-doc consumer rules).

## pstack: rigor mode and playbooks

[pstack](https://github.com/cursor/plugins/tree/main/pstack) is Lauren Tan's
Cursor plugin for writing less, higher-quality code: one entry skill that
routes a task to a playbook, a set of principles it cites by name, and
situational skills for understanding, designing, verifying, and shipping.
This kit carries a port of pstack 0.15.32 that keeps every skill's steps and
voice and changes only what tied it to one harness, one model provider, or
one forge (ADR-0008):

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

Not ported: `tdd` (the main flow's `/tdd` serves), `typescript-best-practices`
(ADR-0002), `make-bot-ui` (a Grok Bot feature), the `benny` automation pack
(Cursor Automations only), and the GitHub-bound `watch-pr` and `orch` tools;
the babysit and orchestrate playbooks describe the same loops over forge
operations and plain files.

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
git clone https://github.com/PhillipChaffee/.agents.git && cd .agents && ./scripts/install.sh --target agents
```

Installs into `~/.agents/` (protocol layout, lowercase `skill.md`), read by
protocol consumers such as OpenCode. The installer is non-destructive by
default: it manages only the paths in its own stamp manifest, skips unstamped
files that differ (use `--force`), and supports `--dry-run`, `--prune`,
`--uninstall`, and `--pull` (reverse-sync edits from the target back into the
repo). A skill ships every file under its directory, including the node and
shell scripts a few pstack skills run.

On install you choose your harness's fast/main/deep models and the installer
writes a consumer-local `models.json` beside the kit — the kit itself pins no
models. The pstack roles resolve to those tiers; run `/setup-pstack` to pin a
role to a specific model or build a cross-family review panel. MCP setup is
printed as guidance, never written.

## Prerequisites and notes

- The Matt Pocock skills listed above are the assumed workflow environment;
  install them separately (see [the workflow](#the-workflow)).
- The kit is forge-agnostic: its skills, rules, and agents reference no
  specific code host. Issue tracking is per-repo configuration, recorded by
  `/setup-matt-pocock-skills` in `docs/agents/issue-tracker.md` — GitHub,
  GitLab, or Linear all work. The pstack playbooks add a table of pull
  request operations to that file; this repo's copy maps them to `gh`.
- Sub-agents run on whatever subagent model your harness configures; swap in
  your own tiers — nothing here references a vendor model.
- Never commit provider keys or tokens anywhere in this kit.

## Credits

README presentation, the setup-skill pattern, and the installer UX are
inspired by [Matt Pocock's skills repo](https://github.com/mattpocock/skills).
The pstack skills, playbooks, principles, agents, and guide are
[Lauren Tan's pstack](https://github.com/cursor/plugins/tree/main/pstack),
MIT-licensed; the notice is in [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md).
This repo follows the [.agents Protocol](https://dotagentsprotocol.com),
tracking the current draft. Kit content is my own, MIT-licensed — borrow
freely.
