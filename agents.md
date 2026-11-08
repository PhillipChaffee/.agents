# Repository guidance

This repository publishes the approved contents of the owner's `~/.agents`.
`agents.kit.md` is the home instruction file, installed as `~/.agents/agents.md`;
this file contains repository-only guidance.

## Sync boundaries

- Carry additions, edits, and deletions into `agents/`, `rules/`, and `skills/`.
- Keep `skills-disabled/` as an archive; do not install or activate it.
- Do not import home `scripts/`, credentials, or the generated `.kit-stamp`.
- Preserve upstream skill bytes and their notices. Check secrets in upstream
  copies even when their formatting and example links are excluded from lint.
- Retain repository documentation, installation, validation, and CI support.

## Repository tooling

- Issues: GitHub Issues through `gh`.
- Domain docs: `CONTEXT.md` and `docs/adr/`.
