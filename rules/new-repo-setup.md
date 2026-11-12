---
alwaysApply: true
description: >-
  Bootstrap every new repository from the full-lint reference repo with
  canonical lint, type-check, docstring, formatter, coverage, and hygiene gates,
  and set up magic.
---

# New repository setup

Bootstrap every new repository from [`full-lint`](https://github.com/PhillipChaffee/full-lint) and set up [`magic`](https://github.com/PhillipChaffee/magic) before the first commit. Never hand-roll lint, type-check, docstring, formatter, coverage, or hygiene config from memory.

## When this applies

Any greenfield repository, service, or package with its own git tree.

## How to comply

1. **Language has a folder in `full-lint`** (`<lang>/`). Run the matching `init-<lang>-repo` skill (`~/.agents/skills/init-<lang>-repo/SKILL.md`, or `<lang>/init-<lang>-repo/SKILL.md` in `full-lint`), copy its `templates/`, and pass lint, type, docstring, formatter, `>= 95%` coverage, and hygiene gates before the first commit.
2. **Language has no folder yet.** Clone <https://github.com/PhillipChaffee/full-lint> and run `add-language` (`~/.agents/skills/add-language/SKILL.md` or `add-language/SKILL.md` in `full-lint`) to research official sources, author `<lang>/`, and prove the coverage gate fails below `95%`, then bootstrap per step 1.
3. **Set up `magic`.** Install the plugin or sync `~/.agents` from <https://github.com/PhillipChaffee/magic>, then run `/setup-magic`. Scope 2 onboarding writes `docs/agents/issue-tracker.md` and offers `/create-verification-skill` and `/create-formal-verification-skill`. Scope 1 configures model roles when none exist yet.

## Exceptions

- Extending existing enforcement inside a repository that is already bootstrapped.
- `full-lint` itself, extended with `add-language` rather than its own templates.
