---
alwaysApply: true
description: >-
  Bootstrap every new repository from the full-lint reference repo with
  canonical lint, type-check, docstring, formatter, coverage, and hygiene gates,
  and set up magic.
---

# New repository setup

Bootstrap every new repository from [`full-lint`](https://github.com/PhillipChaffee/full-lint) and set up [`magic`](https://github.com/PhillipChaffee/magic) before the first commit. Never hand-roll lint, type-check, docstring, formatter, coverage, or hygiene configuration from memory.

## When this applies

Any greenfield repository, service, or package being created, scaffolded, or bootstrapped with its own git tree.

## How to comply

1. **Language has a folder in `full-lint`** (`<lang>/` at the repo root): run the matching `init-<lang>-repo` skill (`~/.agents/skills/init-<lang>-repo/SKILL.md`, or `<lang>/init-<lang>-repo/SKILL.md` in `full-lint`, installed via `scripts/install-skills.sh`), copy its `templates/`, and pass every lint, type, docstring, formatter, `>= 95%` coverage, and hygiene gate before the first commit.
2. **Language has no folder yet**: clone <https://github.com/PhillipChaffee/full-lint> and run `add-language` (`~/.agents/skills/add-language/SKILL.md` or `add-language/SKILL.md` in `full-lint`) to research official sources, author `<lang>/`, and prove the coverage gate fails below `95%`, then bootstrap per step 1.
3. **Set up `magic`**: install the `magic` plugin or sync `~/.agents` from <https://github.com/PhillipChaffee/magic>, then run `/setup-magic` to configure model roles and project verification skills (`/create-verification-skill` and `/create-formal-verification-skill`).

## Exceptions

- Extending existing enforcement inside a repository that is already bootstrapped.
- `full-lint` itself, which is extended with `add-language` rather than initialized from its own templates.
