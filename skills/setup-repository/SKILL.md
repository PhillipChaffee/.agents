---
description: Use when bootstrapping a new repository, adopting repository working rules, or transferring an established repository setup to another project.
enabled: true
id: setup-repository
name: setup-repository
---

# Set up a repository

Reuse a maintained baseline and give each working rule an owner, a read trigger,
and completion evidence. Keep project decisions separate from machine preferences.

## Select the scope

| Request | Apply |
| --- | --- |
| New repository | Canonical language initializer, then working rules |
| Existing repository | Requested changes within existing conventions |
| Working rules only | Instruction and documentation changes |
| Several languages | Compose shared files before applying initializers |

## Procedure

1. Read the project goal, active instructions, Git status, and existing setup.
   Identify languages, package paths, tracker, and the owned worktree.
   Resolve an unborn repository's worktree boundary before edits.
   Completion: record scope, preserved work, and unresolved choices.

2. For a new repository, resolve [full-lint](https://github.com/PhillipChaffee/full-lint)
   and record its full commit SHA. Read the matching `init-<language>-repo`
   instructions and templates together. Compare installed copies before use.
   If language support is missing, use its `add-language` skill first.
   Keep sync defects blocked until resolved or explicitly accepted by the user.
   Completion: record provenance, substitutions, and deviations without weakening gates.

3. Follow the selected initializer within the agreed scope.
   For tracker/domain setup, use `setup-matt-pocock-skills`; use `domain-modeling`
   when terms or architectural decisions need resolution.
   If a dependency skill is absent, locate its source or report that step blocked.
   Reuse existing issues. Create glossary entries and decision records when needed.
   Completion: the setup matches this project, with conditional features justified.

4. Before writing working rules, read [working rules](references/working-rules.md).
   Give every adopted rule a source, owning file, explicit read condition,
   and observable completion criterion. Link these from the active instruction file.
   Completion: preserve caller-focused docstrings and independently established
   test expectations alongside naming, placement, and reuse rules.

5. Run applicable checks in the target environment and demonstrate below-floor
   coverage failure. Record wrapper failures and restore the passing state.
   Completion: each check has a command, environment, result, and evidence location.
   Distinguish scheduled checks, execution, optional reporting, and merge protection.

6. Write the setup handoff using the required fields below.
   Apply `writing-for-agents` to instructions and Plain-mode writing review to prose.
   Completion: report remaining blockers, next actions, and exact readiness.
   Commit or publish only when requested.

## Required handoff fields

- Scope and preserved work.
- Source URL, full revision, initializer, substitutions, and unresolved deviations.
- Rule ownership: file, read trigger, content, and completion evidence.
- Validation: commands, runtime/tool versions, platform, results, and missing checks.
- Blockers, next action, and readiness.

Example rule: before changing, reviewing, or explaining code, read
`docs/agents/coding.md`. Finish when affected callers, tests, and documentation agree.
Unknown environment values remain explicitly unknown until measured.

## Common mistakes

Links without read conditions and results without environments leave the handoff
incomplete. Historical success is evidence about its recorded revision only.
For rationale, history, optional practices, and known limitations, read the
[research reference](references/research.md).
