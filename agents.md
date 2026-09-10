# Agent Guidelines

This file is the kit's always-applied convention layer (AGENTS.md-standard
compatible) and doubles as this repo's own instructions. Consumers that
auto-load `agents.md` get the distilled rules below; full rule texts live in
`rules/`.

## Always-applied conventions

### autopilot

Governs the `/autopilot` skill and `/ship` handoffs: record a size baseline once at start (never reset), with a growth budget of `min(200, max(50, ceil(baseline_changed_lines * 0.20)))` as a hard ceiling — tests count toward the budget, and exceeding the ceiling requires stopping for explicit user approval before committing or pushing. Scope is limited to merge conflicts (abort and ask if intents conflict), `fix-now` triaged items, and CI failures caused by the PR's own scope; restructure/performance/architecture findings use `pause-plan`. Implement only the `fix-now` set from a triage subagent, stop after two consecutive iterations blocked by the same issue, and exit only when mergeable + green + every comment triaged.

Full text: [rules/autopilot.md](rules/autopilot.md)

### code-organization

Every new symbol goes where a reader would look for it: entry points stay thin (wiring only), data shapes go in the package's models/types module, generic helpers in the existing utils/helpers module — always search for an existing implementation first. When moving a symbol, move its tests, update imports and test patch/mock targets in the same change; renames and pure moves are their own commits. Grab-bag files must not accumulate unrelated functions; tests mirror source layout.

Full text: [rules/code-organization.md](rules/code-organization.md)

### comment-style

Comments add context the code cannot convey — why, not what; delete comments that restate the code. Present state only (no "moved", "was", "previously"; no roadmap language like "for now" or "until X lands"). Shared or leaf code never references "the caller". Never create a lone `Args:`/`Returns:` section for one new parameter; match the host docstring's density.

Full text: [rules/comment-style.md](rules/comment-style.md)

### django-migrations

Never write or edit migration files by hand — always generate them with the ORM's migration generator (`python manage.py makemigrations`) so framework state stays consistent. For custom data migrations, generate an empty migration first (`makemigrations <app> --empty -n <name>`), then fill in the operation logic in that generated file.

Full text: [rules/django-migrations.md](rules/django-migrations.md)

### engineering

Views stay thin — business logic belongs in services/tasks, not views, admin actions, or serializers; heavy or risky work goes to background tasks; shared models live in `shared/`. Safe column removal is four steps (add, migrate code, defer, drop in a follow-up MR) — never drop a column in the same MR that stops using it. Never amend commits or force-push. Gate risky changes behind feature flags with `tenant_id` in context; flag hot-table migrations for after-hours deploys and agent-config/call-flow changes for non-live verification.

Full text: [rules/engineering.md](rules/engineering.md)

### github-vs-gitlab-mcp

Before any GitHub/GitLab MCP call, run `git remote -v` and route by host. GitLab work uses the GitLab MCP — never `glab`, `curl`, or REST/GraphQL via shell; if the GitLab MCP is missing or unauthenticated, stop and tell the user. If the remote is missing, ambiguous, or mirrored, ask which platform to target.

Full text: [rules/github-vs-gitlab-mcp.md](rules/github-vs-gitlab-mcp.md)

### linear-tickets

Every Linear ENG ticket body has exactly four sections in order — Description, Acceptance Criteria, Resources, Notes — with "None" in empty Resources/Notes. Titles are short and concrete (`service-b: deduplicate webhook delivery`), avoiding filler and user-story format. Acceptance Criteria are `- [ ]` checklists of verifiable outcomes, roughly ≤6 items; more means split the ticket. One owner per ticket.

Full text: [rules/linear-tickets.md](rules/linear-tickets.md)

### look-it-up

Do not answer from memory when the answer can be looked up (APIs, tools, flags, config, error messages, version-specific behavior). Source order: official docs, then primary sources (code, changelogs, maintainer issues), then proven writeups only when official docs are missing. Cite the source; prefer official docs on conflict and say so; state explicitly when no reliable source exists.

Full text: [rules/look-it-up.md](rules/look-it-up.md)

### merge-requests

MR titles include the ticket identifier: `TICKET-ID: Short description` — ask for one if missing, never drop an existing reference. Descriptions must contain `## Problem` (concrete symptoms), `## Fix` (approach + `### Changes` with bold scope labels), `## Impact` (improvements, trade-offs, residual risks), and `## Test Plan` (concrete verification steps). Ask rather than guess when context is missing.

Full text: [rules/merge-requests.md](rules/merge-requests.md)

### minimal-changes

Limit edits to only the files and lines necessary — no tangential refactors or "while I'm here" improvements unless requested. Search for existing functions before writing new logic; extract a shared utility when the same pattern appears twice. Deleting code is preferred over working around it.

Full text: [rules/minimal-changes.md](rules/minimal-changes.md)

### mr-review-chat-title

When starting an `mr-review` run, rename the chat via `rename_chat` (cursor-app-control MCP) as soon as the MR IID is known: `<repo> MR <iid> Review - <author>`. Rename first with repo + IID, then again once the author is known.

Full text: [rules/mr-review-chat-title.md](rules/mr-review-chat-title.md)

### plan-steps

Every implementation plan includes, in order: branch setup (`username/TICKET-ID-short-description` from the default branch), an Acceptance Criteria section (`- [ ]` items checkable yes/no, roughly ≤8), logical commit grouping with per-commit `ci-lint-test`, and the end sequence — verify acceptance criteria, final CI, `pre-mr-checklist`, then push and create MRs titled `TICKET-ID: Short description` with descriptions per the merge-requests rule.

Full text: [rules/plan-steps.md](rules/plan-steps.md)

### python

Applies to Python files (`**/*.py`, `pyproject.toml`, `poetry.lock`). Poetry for all dependency management and invocations (`poetry run pytest` / `ruff` / `mypy`); Ruff lint/format; mypy; pytest (never unittest); 100-char lines; full annotations. No `typing.Any` (use `object` or small Protocols); built-in generics; Pydantic `BaseModel` for structured data. Logging uses lazy `%s` formatting with an identifier (`order_id`, `tenant_id`) and `logger.exception` inside `except` blocks. No bare `except Exception`; explicit None/empty guards; top-of-file imports (`import datetime` → `datetime.date`). Django: `models.TextChoices` for string enums, `select_related`/`prefetch_related` against N+1, `fk_id` accessors, short transactions without external API calls, timeouts + rate-limit backoff on all external calls.

Full text: [rules/python.md](rules/python.md)

### python-class-sections

Applies to `**/*.py`. Class bodies are organized into sections named exactly `Properties`, `Public methods`, `Private methods` — omit empty sections. Section headers use the three-line `===` big-header form (indented to class-body level, blank line before and after), subsections the single-line `-- Name ----` form; no other header styles.

Full text: [rules/python-class-sections.md](rules/python-class-sections.md)

### python-docstrings-google

Applies to `**/*.py`. All docstrings use triple double quotes, open with a one-line imperative summary, ≤100 chars. Google-style sections in order `Args:`, `Returns:`/`Yields:`, `Raises:` (4-space indent, one entry per line, no type repetition); `Attributes:` for class attributes; one-line summaries allowed for trivial functions.

Full text: [rules/python-docstrings-google.md](rules/python-docstrings-google.md)

### python-pytest

Applies to test files (`**/test_*.py`, `**/*_test.py`, `**/conftest.py`, pytest config). Plain `test_*` functions with plain `assert` — no `unittest.TestCase`; one behavior per test with happy path + edge case. Fixtures for arrange/teardown (`yield`), function scope default; prefer built-ins (`tmp_path`, `monkeypatch`, `capsys`, `caplog`). `pytest.raises`/`warns` context-manager form with `match=`; `pytest.approx` for floats; marks always carry `reason=...` and custom marks are registered with `--strict-markers`. Tests are order-independent and parallel-safe.

Full text: [rules/python-pytest.md](rules/python-pytest.md)

### skill-creation

Before writing or editing any skill, read and follow your agent platform's skill-creation skill (Cursor: `/create-skill`); do not invent structure, frontmatter, or description style from memory. Keep frontmatter for discovery only; workflow detail in the body. `name` is lowercase-hyphenated, matches the folder, ≤64 chars; `description` is non-empty ≤1024 chars, third person, what + when, folded block scalar (`>-`) when longer than one line or containing colons. Validate frontmatter (YAML parse + name/description assertions) after every create or update.

Full text: [rules/skill-creation.md](rules/skill-creation.md)

### subagents

Work inline only for user-specified reads, quick lookups, known facts, or narrow checks mid-edit; delegate unfamiliar code, multi-file tracing, debugging, reviews, tradeoff analysis, and research — independent threads in parallel. `cursor-grok-4.6-high-fast` is the default model for nearly all subagents; slower deep-thinking models are reserved for rare, bounded, thinking-only work with a complete evidence packet, one discrete question, and tools forbidden in the prompt. Dispatch prompts are self-contained; curate raw subagent output before presenting it; never paste it. `readonly: true` is wrong for researchers needing web/MCP access — forbid edits in the prompt instead.

Full text: [rules/subagents.md](rules/subagents.md)

## Optional rules

- [design-docs](rules/design-docs.md) — fixed eight-heading template for design docs (`Problem` → `Test Plan`, keep `N/A` headings). Opt-in per repo.
- [writing-voice](rules/writing-voice.md) — fill-in template for your own writing voice; replace placeholders and enable `alwaysApply` before use.