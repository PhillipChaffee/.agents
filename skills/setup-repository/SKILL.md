---
description: Use when bootstrapping a new repository, installing repository working rules, or transferring an established repository setup to another project.
enabled: true
id: setup-repository
name: setup-repository
---

# Set up a repository

Install the maintained rule payloads word for word. Payloads are authoritative
data: never summarize, reflow, rename, path-substitute, or pass them through prose
rewriting. Changes belong in reviewed payload updates, not individual installs.

## Select the scope

| Request | Apply |
| --- | --- |
| New repository | Canonical language initializer, then literal rules |
| Existing repository | Requested changes within existing conventions |
| Rules only | Literal rule installation without replacing enforcement |
| Several languages | Reconcile shared destinations before initialization |

## Install

1. Read the project goal, active instructions, Git status, and existing setup.
   Confirm worktree ownership and preserve other work.
   Confirm that root instruction file (`AGENTS.md` or `agents.md`) is active before installing its block.

2. For a new repository, select [full-lint](https://github.com/PhillipChaffee/full-lint)
   at a recorded full commit SHA.
   Follow its matching initializer and preserve its required gates.
   Use canonical `/add-language` for missing language support.
   When tracker/domain setup is requested via `/setup-matt-pocock-skills`, run that setup
   before rule preflight so tracker configuration and domain modeling are established first.

3. Preflight all rule destinations together with the deterministic installer helper:

   ```sh
   python3 <skill_dir>/install_rules.py --check <target_repo>
   ```

   The helper inspects all four destinations:
   - `docs/agents/coding.md` (whole file from `coding.txt`)
   - `docs/agents/domain.md` (whole file from `domain.txt`, preserved if already present)
   - Root `AGENTS.md` or `agents.md` (`<!-- setup-repository:agent-rules:start/end -->` block)
   - `docs/agents/issue-tracker.md` (`<!-- setup-repository:issue-tracker-evidence:start/end -->` block)

   Identical files or managed blocks are no-ops.
   If conflicting files, differing blocks, or unmanaged heading collisions exist,
   inspect the displayed diff and obtain user approval before writing anything.
   Surface any incompatible `pyproject.toml` or `CONTEXT.md` assumptions.

4. Apply the approved rule bytes:

   ```sh
   python3 <skill_dir>/install_rules.py --apply <target_repo> [--approve-conflicts]
   ```

   The helper writes approved bytes verbatim, preserves prefixes and suffixes,
   and verifies installed bytes and relative Markdown link targets.

5. Run applicable target checks, including the initializer's below-floor coverage proof.
   Report source pin, destination statuses, approvals, preserved files, commands,
   and verification results. Distinguish installation from runtime readiness.
