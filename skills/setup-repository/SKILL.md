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
   Confirm that root `AGENTS.md` is active before installing its block.
   Resolve instruction ownership and unborn-repository boundaries before edits.

2. For a new repository, select [full-lint](https://github.com/PhillipChaffee/full-lint)
   at a recorded full commit SHA.
   Read its matching initializer and templates together, comparing installed copies.
   Use canonical `add-language` for missing language support.
   Resolve sync defects or obtain explicit acceptance before initialization.
   Follow the initializer and preserve its required gates.
   For requested tracker configuration, reuse existing setup or `setup-matt-pocock-skills`.
   If a dependency is unavailable, report that step blocked.

3. Before any rule write, read [rule sources](references/rule-sources.md) and all four payloads.
   Check their SHA-256 values and preflight every destination together:

   | Payload under `templates/` | Destination |
   | --- | --- |
   | `coding.txt` | Whole `docs/agents/coding.md` |
   | `domain.txt` | Whole `docs/agents/domain.md`, only if absent |
   | `agent-rules.txt` | One marked block in root `AGENTS.md` |
   | `issue-tracker-evidence.txt` | One marked block in `docs/agents/issue-tracker.md` |

   Preserve an existing domain guide.
   Identical files or managed blocks are no-ops.
   For conflicting coding files, differing managed blocks, or same-heading sections,
   show an explicit diff and obtain approval before writing anything.
   Stop on malformed or duplicate markers.
   Surface incompatible `pyproject.toml`, `CONTEXT.md`, or other source assumptions without rewriting them for another language.

4. Use existing file tools or platform copying to install the approved bytes.
   Follow the exact marker and wrapper rules in the source record.
   Preserve unrelated prefixes and suffixes byte-for-byte.
   An absent tracker guide gets a neutral title and literal evidence block, without invented tracker identity.
   Apply writing review only to new instructions or notes outside payloads.

5. Compare installed whole files and extracted block bytes against their payloads.
   Confirm that coding links resolve and a repeated install changes no bytes.
   Run applicable target checks, including the initializer's below-floor coverage proof.
   Report source pin, destination status, approvals, preserved files, commands,
   environment, results, blockers, and next action.
   Distinguish installation from runtime readiness.
   Commit or publish only when requested.

For the maintenance rationale and evidence limits, read [research](references/research.md).
