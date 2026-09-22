# Agent Guidelines

This file is the kit's always-applied convention layer (AGENTS.md-standard
compatible) and doubles as this repo's own instructions. Consumers that
auto-load `agents.md` get the distilled rules below; full rule texts live in
`rules/`.

## Always-applied conventions

### code-organization

Every new symbol goes where a reader would look for it: entry points stay thin (wiring only), data shapes go in the package's models/types module, generic helpers in the existing utils/helpers module — always search for an existing implementation first. When moving a symbol, move its tests, update imports and test patch/mock targets in the same change; renames and pure moves are their own commits. Grab-bag files must not accumulate unrelated functions; tests mirror source layout.

Full text: [rules/code-organization.md](rules/code-organization.md)

### comment-style

Comments add context the code cannot convey — why, not what; delete comments that restate the code. Present state only (no "moved", "was", "previously"; no roadmap language like "for now" or "until X lands"). Shared or leaf code never references "the caller". Never create a lone `Args:`/`Returns:` section for one new parameter; match the host docstring's density.

Full text: [rules/comment-style.md](rules/comment-style.md)

### git-worktrees

Every session that mutates a repo — code, docs, skills, config — works in a Git worktree at `~/worktrees/<clone-dir-basename>/<branch>`; the main checkout is never edited, and read-only sessions need none. Starting in the main checkout, announce the path, create the worktree on a new branch (`<issue#>-<slug>` with an issue, bare slug otherwise), and continue there; resume existing work in its existing worktree. After merge or abandonment, remove the worktree and delete its branch — ask first when uncommitted changes exist.

Full text: [rules/git-worktrees.md](rules/git-worktrees.md)

### look-it-up

Do not answer from memory when the answer can be looked up (APIs, tools, flags, config, error messages, version-specific behavior). Source order: official docs, then primary sources (code, changelogs, maintainer issues), then proven writeups only when official docs are missing. Cite the source; prefer official docs on conflict and say so; state explicitly when no reliable source exists.

Full text: [rules/look-it-up.md](rules/look-it-up.md)

### minimal-changes

Limit edits to only the files and lines necessary — no tangential refactors or "while I'm here" improvements unless requested. Search for existing functions before writing new logic; extract a shared utility when the same pattern appears twice. Deleting code is preferred over working around it.

Full text: [rules/minimal-changes.md](rules/minimal-changes.md)

### pull-requests

PR titles include the issue reference: `#123: Short description` — ask whether to create an issue if none exists, never drop an existing reference. Descriptions must contain `## Problem` (concrete symptoms), `## Fix` (approach + `### Changes` with bold scope labels), `## Impact` (improvements, trade-offs, residual risks), and `## Test Plan` (concrete verification steps). Ask rather than guess when context is missing.

Full text: [rules/pull-requests.md](rules/pull-requests.md)

### skill-creation

Before writing or editing any skill, read and follow your agent platform's skill-creation skill (Cursor: `/create-skill`); do not invent structure, frontmatter, or description style from memory. Keep frontmatter for discovery only; workflow detail in the body. `name` is lowercase-hyphenated, matches the folder, ≤64 chars; `description` is non-empty ≤1024 chars, third person, what + when, folded block scalar (`>-`) when longer than one line or containing colons. Validate frontmatter (YAML parse + name/description assertions) after every create or update.

Full text: [rules/skill-creation.md](rules/skill-creation.md)

### subagents

Work inline only for user-specified reads, quick lookups, known facts, or narrow checks mid-edit; delegate unfamiliar code, multi-file tracing, debugging, reviews, tradeoff analysis, and research — independent threads in parallel. The kit pins no models (ADR-0001): subagents run on the harness's configured subagent model, and a configured deep-thinking tier is reserved for rare, bounded, thinking-only work on a complete evidence packet with tools forbidden in the prompt. Dispatch prompts are self-contained; curate raw subagent output before presenting it; never paste it. `readonly: true` is wrong for researchers needing web/MCP access — forbid edits in the prompt instead.

Full text: [rules/subagents.md](rules/subagents.md)

## Optional rules

- [design-docs](rules/design-docs.md) — fixed eight-heading template for design docs (`Problem` → `Test Plan`, keep `N/A` headings). Opt-in per repo.
- [writing-voice](rules/writing-voice.md) — fill-in template for your own writing voice; replace placeholders and enable `alwaysApply` before use.

## Agent skills

### Issue tracker

Issues live in GitHub Issues on this repo, managed with the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

The five canonical triage roles use their default label strings. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout: `CONTEXT.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.
