# .agents

[![validate](https://github.com/PhillipChaffee/.agents/actions/workflows/validate.yml/badge.svg)](https://github.com/PhillipChaffee/.agents/actions/workflows/validate.yml) [![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

My personal agent kit — add-ons for my everyday coding workflow. The main
flow is [Matt Pocock's skills](https://github.com/mattpocock/skills),
installed separately; this kit layers on top of it: a combined two-tier code
review, tiered research, worktree discipline, and always-applied rules. Published as
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
for one session.

### Install the main flow first

```sh
npx skills@latest add mattpocock/skills
```

Pick the skills you want; run `/setup-matt-pocock-skills` once per repo to
record the issue tracker, triage labels, and domain-doc layout in
`docs/agents/`. Two names overlap deliberately: this kit's `code-review`
(combined two-tier) and `research` (tiered, repo-file output) replace his
two-axis `code-review` and `research` — skip those two when picking, or
uninstall his copies after, so the kit's versions own the names.

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

#### Skills (2)

| Skill | What it does |
| --- | --- |
| `code-review` | Two-tier review: standard = two-axis (Standards + Spec); deep = specialist panel + verifier + walkthrough + applied fixes |
| `research` | Tiered research: direct answers, background research, or a full research→synthesis pipeline; Tier 2/3 write a cited file to `docs/research/` for the main flow to consume |

#### Sub-agents (16)

| Group | Agents |
| --- | --- |
| Code review | `cr-planner`, `cr-security`, `cr-correctness`, `cr-performance`, `cr-architecture`, `cr-organization`, `cr-test-quality`, `cr-deployment-safety`, `cr-simplification`, `cr-verifier`, `cr-implementer` |
| Research | `researcher-lite`, `researcher-mid`, `researcher-deep`, `research-planner`, `research-synthesizer` |

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

Distilled into [agents.md](agents.md) (the auto-loaded instruction layer); full
text in [rules/](rules/). The kit carries **no language rules** — per-language lint,
type, docstring, and coverage enforcement lives in the
[full-lint](https://github.com/PhillipChaffee/full-lint) reference
repo, applied per project by its `init-<lang>` skills; the kit's own repo-wide
hygiene gates are copied from that repo.

#### Domain docs

`CONTEXT.md` (glossary) + `docs/agents/` (tracker, triage labels,
domain-doc consumer rules).

## Install

```sh
git clone https://github.com/PhillipChaffee/.agents.git && cd .agents && ./scripts/install.sh --target agents
```

Installs into `~/.agents/` (protocol layout, lowercase `skill.md`), read by
protocol consumers such as OpenCode. The installer is non-destructive by
default: it manages only the paths in its own stamp manifest, skips unstamped
files that differ (use `--force`), and supports `--dry-run`, `--prune`,
`--uninstall`, and `--pull` (reverse-sync edits from the target back into the
repo).

On install you choose your harness's fast/main/deep models and the installer
writes a consumer-local `models.json` beside the kit — the kit itself pins no
models. MCP setup is printed as guidance, never written.

## Prerequisites and notes

- The Matt Pocock skills listed above are the assumed workflow environment;
  install them separately (see [the workflow](#the-workflow)).
- The kit is forge-agnostic: its skills, rules, and agents reference no
  specific code host. Issue tracking is per-repo configuration, recorded by
  `/setup-matt-pocock-skills` in `docs/agents/issue-tracker.md` — GitHub,
  GitLab, or Linear all work.
- Sub-agents run on whatever subagent model your harness configures; swap in
  your own tiers — nothing here references a vendor model.
- Never commit provider keys or tokens anywhere in this kit.

## Credits

README presentation, the setup-skill pattern, and the installer UX are
inspired by [Matt Pocock's skills repo](https://github.com/mattpocock/skills).
This repo follows the [.agents Protocol](https://dotagentsprotocol.com),
tracking the current draft. Kit content is my own, MIT-licensed — borrow
freely.
