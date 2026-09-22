# Changelog

## Unreleased

Adopted the reference repo's hygiene gates and retired the `67-sus-95-clean` name (ADR-0006).

- The repo now self-lints: full-lint's repo-wide hygiene configs copied
  byte-for-byte (`.typos.toml`, `.markdownlint-cli2.jsonc`, `.jscpd.json`,
  `.gitleaks.toml`, `.yamllint.yaml`, `lychee.toml`, `.github/dependabot.yml`)
  and a `hygiene` job added to `validate.yml` beside the existing
  kit-structure `validate` job — spell, markdown, link, secret, copy-paste,
  shell lint/format, and workflow YAML gates, with Dependabot on the
  SHA-pinned Actions
- The reference repo is named `full-lint` everywhere: the domain glossary,
  ADR-0002, and the README reference link updated from the old
  `67-sus-95-clean` name and URL

Realigned to the personal workflow only (ADR-0003) and the Matt Pocock main flow (ADR-0004).

- Skills cut from 13 to 4: threw `ship`, `plan-review`, `looping-plan-review`,
  `looping-code-review`, `clean-plan`, `ultracode`, `mr-review`,
  `setup-agent-kit`, `refactor-planner`; renamed `deep-research` → `research`
  with a cited `docs/research/<topic>.md` output mode; rewrote `code-review`
  as one two-tier skill (ADR-0005); GitHub Actions support in `ci-lint-test`;
  `pre-mr-checklist` reworded forge-neutral
- Sub-agents cut from 30 to 16: threw the 12 `pr-*` and the two refactor
  scouts; stripped every vendor model pin (ADR-0001)
- Rules cut from 20 to 10: threw the Python stack, Django/work conventions,
  Linear, dual-forge routing, `autopilot`, `plan-steps`; `merge-requests`
  rewritten as forge-neutral `pull-requests`; `subagents` rewritten
  harness-neutral; added `git-worktrees` (mutating agent sessions work in a
  worktree under `~/worktrees/`, removed after merge or abandonment)
- `mcp.json`/`models.json` templates deleted; the installer now prompts for
  model tiers and writes a consumer-local `models.json`; cursor target and
  `agents.md` mapping removed
- Added `CONTEXT.md` and ADRs 0001–0005; `docs/agents/` (tracker, labels,
  domain docs); README rewritten to match

## 0.1.0

Initial release: the agent kit published as an .agents Protocol repo.

- 13 skills (research, code/plan review, MR review, planning, shipping,
  CI hygiene, setup): 12 migrated from the .cursor kit with portable paths,
  plus the new setup-agent-kit
- 30 sub-agents in protocol layout (`agents/<id>/agent.md`), ids unchanged
- 20 rules at `rules/<id>.md` plus a distilled `agents.md` instruction layer
- `scripts/install.sh`: non-destructive installer for `~/.agents/`
  (protocol layout) and `~/.cursor/` (Cursor layout), with stamp-manifest
  safety, `--adopt`, `--force`, `--dry-run`, `--prune`, `--uninstall`,
  `--pull`
- `scripts/validate.sh`: frontmatter, cross-reference, and install checks
- `mcp.json` / `models.json` templates; GitHub Actions validation
