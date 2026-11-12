# Repository guidance

This repository publishes the approved contents of the owner's `~/.agents`.
`agents.kit.md` is the home instruction file, installed as `~/.agents/agents.md`;
this file contains repository-only guidance.

## Sync boundaries

- Carry additions, edits, and deletions into `agents/`, `rules/`, and `skills/`.
- Keep `skills-disabled/` as an archive; do not install or activate it.
- Do not import home `scripts/`, credentials, or the generated `.kit-stamp`.
- Preserve upstream notices and the disabled archive's bytes. Adapted skills
  keep their upstream structure and credit while naming the kit's roles,
  adapters, and forge operations; check secrets in archived copies even though
  their formatting and example links are excluded from lint.
- Retain repository documentation, installation, validation, and CI support.
- When adding a new rule via `/writing-rules`:
  - Add `rules/<name>.md` (sorted `alwaysApply` and `description` frontmatter) and a `<= 25`-word single-bullet pointer in `agents.kit.md`.
  - Update the rule count in `README.md` and the count and table in `docs/CATALOG.md`.
  - Run `./scripts/validate.sh`, `python3 -m unittest discover -s tests`, and `node --test tests/*.test.mjs`.

## Repository tooling

- Issues: GitHub Issues through `gh`.
- Domain docs: `CONTEXT.md` and `docs/adr/`.
