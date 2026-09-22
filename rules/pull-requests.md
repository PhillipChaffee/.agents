---
description: "Pull request conventions: titles, descriptions, and when to ask for clarification."
alwaysApply: true
---

# Pull Requests

Conventions for PRs on any forge (GitHub today; the contract is forge-neutral).

- **Title must include the issue reference** formatted as `#123: Short description`.
  - If no issue exists for the work, ask the user whether to create one or proceed without.
  - Never drop an existing issue reference when updating a title.

```
# ✅ Good
#42: Add retry logic for webhook delivery

# ❌ Bad — missing issue
Add retry logic for webhook delivery
```

- **Description must have `## Problem`, `## Fix` (with `### Changes`), `## Impact`, and `## Test Plan` sections.**
  - `## Problem` describes the problem with concrete symptoms and real-world impact.
  - `## Fix` explains the solution approach at a high level, then lists specific changes under a `### Changes` sub-heading. Each bullet carries a **bold scope label** (file, module, or component) followed by the change in that scope.
  - `## Impact` states the consequences — what improves, what trade-offs exist, any residual risks.
  - `## Test Plan` lists concrete verification steps (lint, type checks, tests, manual verification).
  - If there isn't enough context to write a section, ask before writing the description.

```markdown
# ✅ Good
## Problem

Importing the config module on a machine without a config file crashes with a
bare traceback instead of a readable message, and `--help` still exits 1.

## Fix

Give the config loader an explicit missing-file path that emits a friendly
message and exits 0 for `--help` regardless of config state.

### Changes

- **config.py** (`load_config`): return defaults with a warning when the file
  is absent instead of raising.
- **cli.py**: bind `--help` before config loading so it never touches the loader.

## Impact

- First-run experience no longer crashes; defaults apply until the user runs `init`.
- Residual risk: a typo'd config path now warns instead of failing loudly.

## Test Plan

- [ ] `pytest tests/test_config.py` — missing-file and valid-file cases
- [ ] `--help` exits 0 with no config file present
- [ ] Manual: delete config, run the CLI, confirm the warning text

# ❌ Bad — vague problem, no changes list, no impact
## Problem

CLI crashes sometimes.

## Fix

Changed the config loader.

## Impact

Should fix the issue.
```

## Self-Improvement

After writing a PR description, reflect on whether this rule should be updated: missing conventions (migration notes, deploy order, rollback plans), unclear guidance, or new patterns worth capturing. If so, ask the user before changing this rule — do not apply changes automatically.