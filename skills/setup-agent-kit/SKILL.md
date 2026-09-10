---
description: >-
  Configure this repo for the agent kit: issue tracker, triage labels, doc
  directories, plans directory. Run once per repo before using
  tracker-dependent skills like ship or mr-review.
enabled: true
id: setup-agent-kit
name: setup-agent-kit
---

# Setup Agent Kit

One-time per-repo configuration for the agent kit. Asks five questions — one at a time — then writes `.agents/kit.json` at the repo root (the workspace config layer) and ensures the root `AGENTS.md` points at it. Tracker-dependent skills (`ship`, `mr-review`) read this file; research and review skills work without it.

Idempotent: re-run any time. Each answer updates its key; everything else stays put.

## Scope guard

Questions and file writes only. No MCP calls, no code edits, no git commands, no directory creation.

## Inputs

- Repo root = current workspace root.
- Existing `.agents/kit.json` (optional): its values become the defaults for each question.

## Workflow

Copy this checklist and track progress:

```
Task Progress:
- [ ] Step 1: Read existing config
- [ ] Step 2: Ask the five questions
- [ ] Step 3: Write .agents/kit.json
- [ ] Step 4: Ensure the AGENTS.md pointer
- [ ] Step 5: Report
```

## Step 1: Read existing config

If `.agents/kit.json` exists at the repo root, read it and keep its values at hand — they seed the defaults in Step 2. If not, use only the built-in defaults.

## Step 2: Ask the five questions

Ask one question at a time — do not batch. Show the current default (existing config value, else the built-in default) with each question; a "default" answer keeps it.

| # | Key | Question | Options / default |
|---|-----|----------|-------------------|
| 1 | `tracker` | Which issue tracker does this repo use? | `linear` \| `github` \| `gitlab` \| `local-files` — no default, ask until picked |
| 2 | `labels` | Which tracker labels mark triage outcomes? | one label name per outcome; `{}` if none |
| 3 | `docs_dir` | Where do docs live? | default `docs/` |
| 4 | `plans_dir` | Where do plans live? | default `.agents/plans/` |
| 5 | `mr_draft_default` | Create MRs as drafts by default? | default `true` |

For `labels`: ask for one tracker label name per triage outcome (`fix-now`, `defer`, `nit`). Store `{"fix-now": ..., "defer": ..., "nit": ...}`; omit keys the user leaves blank. Repo uses no tracker labels for triage → `labels` is `{}`.

## Step 3: Write .agents/kit.json

Write `.agents/kit.json` at the repo root (workspace layer — repo-local, committed) with exactly these keys:

```json
{
  "tracker": "linear",
  "labels": {"fix-now": "...", "defer": "...", "nit": "..."},
  "docs_dir": "docs/",
  "plans_dir": ".agents/plans/",
  "mr_draft_default": true
}
```

On re-run, overwrite these five keys with the new answers and preserve any other keys already present.

## Step 4: Ensure the AGENTS.md pointer

If `AGENTS.md` exists in the repo root:

- Already contains the exact line `Agent kit config: read .agents/kit.json before running kit skills.` → do nothing (never duplicate it).
- Otherwise, append at the end of the file:

  ```markdown
  ## Agent kit

  Agent kit config: read .agents/kit.json before running kit skills.
  ```

If no root `AGENTS.md` exists, skip — do not create one.

## Step 5: Report

Print:

- The final `.agents/kit.json` contents.
- Pointer outcome: `AGENTS.md` line added / already present / skipped (no `AGENTS.md`).
- One line on what changed vs the previous config, if one existed.

## Graceful degradation

- `linear`, `gitlab`, and `github` trackers require the matching MCP. Without it configured, tracker-dependent skills (`ship`, `mr-review`) are unavailable in this workspace.
- `local-files` needs no MCP.
- Research and review skills (`deep-research`, `plan-review`, `code-review`, the looping skills, `clean-plan`) touch no tracker and work regardless of MCP availability.
- This skill makes no MCP calls and does not verify tracker connectivity; a misconfigured tracker surfaces later, in the tracker-dependent skill that needs it.

## What this skill does NOT do

- Call any MCP or tracker API (no credential checks, no label creation on the tracker).
- Edit code, run git commands, or create `docs_dir` / `plans_dir` — dependent skills create directories on demand.
- Create an `AGENTS.md` when the repo root has none.