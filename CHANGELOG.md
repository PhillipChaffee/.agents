# Changelog

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