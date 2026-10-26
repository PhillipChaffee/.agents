# OpenCode Config Profiles

Several OpenCode configs exist on this machine. Identify the right one before
editing anything:

- **Global**: `~/.config/opencode/opencode.json` — the shared baseline every
  launch merges over. It is not "the personal profile".
- **Profile overlays**: `~/.config/opencode/profiles/personal.json`,
  `work-dev.json`, `work-prod.json`. The `oc <profile>` shell function picks
  one at launch by setting `OPENCODE_CONFIG`; opencode deep-merges the global
  baseline with it. Bare `oc` runs the global file alone.
- When the user says "my personal Open Code profile" — including MCP client
  edits — edit `~/.config/opencode/profiles/personal.json`. Never assume the
  global file, and never a project `.opencode/` directory, for that request.
- Credential values in these files use `{env:VAR}` or `{file:path}`
  substitution only: no plaintext tokens, no shell-style `${VAR}` (opencode
  does not substitute that form).
- After editing any of these files, validate with
  `python3 -m json.tool <file>` and tell the user to restart opencode —
  running sessions keep the already-loaded config.
