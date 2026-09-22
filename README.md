# .agents

My personal agent kit — add-ons for my everyday coding workflow. The main
flow is [Matt Pocock's skills](https://github.com/mattpocock/skills),
installed separately; this kit layers on top of it: a combined two-tier code
review, tiered research, worktree discipline, and always-applied rules. Published as
an [.agents Protocol](https://dotagentsprotocol.com) repo: the layout is
vendor-neutral, version-controllable, and installable into any conformant
consumer.

## The workflow

My main flow is Matt Pocock's skills, not part of this kit:

1. **Grill the idea** (`/grill-with-docs`) — interview it sharp, record decisions in `CONTEXT.md` and ADRs
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

#### Rules (9)

Always-applied conventions — minimal changes, code organization, comment and
subagent discipline, worktree discipline, delegation and
look-it-up policy — distilled
in [agents.md](agents.md) (the auto-loaded instruction layer); full text in
[rules/](rules/). Two optional rules (`design-docs`, `writing-voice`) are opt-in
per repo. The kit carries **no language rules** (ADR-0002) — per-language lint,
type, docstring, and coverage enforcement lives in the
[67-sus-95-clean](https://github.com/PhillipChaffee/67-sus-95-clean) reference
repo, applied per project by its `init-<lang>` skills.

#### Domain docs

`CONTEXT.md` (glossary) + `docs/adr/` (decisions) + `docs/agents/` (tracker,
triage labels, domain-doc consumer rules).

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
models (ADR-0001). MCP setup is printed as guidance, never written.

## Prerequisites and notes

- The Matt Pocock skills listed above are the assumed workflow environment;
  install them separately (see [the workflow](#the-workflow)).
- This kit targets GitHub issues and PRs. GitLab, Linear, and Django-process
  conventions are work-side and out of scope (ADR-0003).
- Sub-agents run on whatever subagent model your harness configures; swap in
  your own tiers — nothing here references a vendor model.
- Never commit provider keys or tokens anywhere in this kit.

## Credits

README presentation, the setup-skill pattern, and the installer UX are
inspired by [Matt Pocock's skills repo](https://github.com/mattpocock/skills).
This repo follows the [.agents Protocol](https://dotagentsprotocol.com),
tracking the current draft. Kit content is my own, MIT-licensed — borrow
freely.
