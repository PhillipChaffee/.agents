# Working rules to adapt

Use existing files that already own these responsibilities. Add only the missing
rules required for the chosen setup scope. The [research reference](research.md)
records the source history and its limits.

## Contents

- [Assign documents and read triggers](#assign-documents-and-read-triggers)
- [Preserve the coding process](#preserve-the-coding-process)
- [Configure work ownership and tracking](#configure-work-ownership-and-tracking)
- [Record setup evidence](#record-setup-evidence)
- [Select optional research and teaching rules](#select-optional-research-and-teaching-rules)
- [Maintain the setup](#maintain-the-setup)

## Assign documents and read triggers

Record the adopted rule's source, file, read trigger, and completion evidence.
The filenames below are examples. Preserve equivalent existing files and identify
which instruction files the agent host loads.

| Responsibility | Example owner | Read trigger | Completion evidence |
| --- | --- | --- | --- |
| Goal and milestone | `README.md` | Before planning | The plan addresses the stated goal and current milestone. |
| Coding process | `docs/agents/coding.md` | Before planning, changing, reviewing, or explaining code | The owning module, affected callers, tests, and evidence are identified. |
| Shared meanings | `CONTEXT.md` and domain guide | Before introducing or changing recurring terms | Definitions and affected uses agree. |
| Tracker operations | `docs/agents/issue-tracker.md` | Before searching, creating, claiming, or resolving work | Ownership, dependencies, and resolution match the tracker. |
| Technical contracts | Existing contract or decision record | Before changing the behavior it governs | Implementation, callers, and relevant tests support the contract. |
| Lesson authoring | Existing authoring guide | Before creating or revising lessons, examples, or animations | Numerical, presentation, and learning evidence remain distinct. |

Keep the root instruction file short. Put shared definitions in one glossary.
Keep example values and derivations next to their examples. Create glossary
entries when concepts are resolved, and architectural decision records when a
costly or surprising trade-off needs a durable explanation.

Keep dated investigations separate from adopted conventions. Record active work
in the chosen tracker. A report, decision record, and issue can link to the same
evidence without repeating it.

## Preserve the coding process

Adapt these rules to the language and repository. Keep the process in one coding
guide, with conditional pointers to additional guidance. Configuration remains
the authority for exact lint rules, tool versions, and commands.

### Naming and placement

Names explain behavior at the call site. Use one name for each concept and the
same vocabulary in related code and documentation. Resolve conflicting meanings
against the implementation and its callers before renaming them.

Search existing code and inspect callers before adding functionality. Put behavior
in the module that owns it. Keep entry points focused on wiring. Put shared types
and helpers with their actual consumers, using existing modules where possible.

Finish when the implementation to reuse or the owning location is clear.
Identify affected callers, tests, fixtures, imports, exports, and configuration.
When moving a symbol, update its tests and mock targets together.

### Dependencies

Read documentation for the installed version before writing a workaround.
Check project code, the standard library, and installed dependencies first.
For a new dependency, record its concrete benefit, maintenance, compatibility,
license, and ongoing cost.

Finish when the proposed use has a source and the benefit justifies the addition.
Source revisions establish provenance. Runtime compatibility requires separate
execution evidence.

### Docstrings and comments

Explain when a caller uses the operation and what the caller receives.
Use a short docstring for simple behavior. Expand it when callers need parameter
meaning, data shapes, constraints, side effects, or errors.

Follow the configured documentation convention. If an argument section exists,
describe every parameter. Describe current behavior in comments and explain
non-obvious reasons instead of narrating the code.

Finish when the documentation agrees with the implementation and its callers.
Update affected descriptions when behavior changes.

### Simplification and evidence

First establish that the change meets the requested behavior and scope.
Remove unnecessary additions and reuse existing implementations. Consolidate
code when it shares a responsibility. Keep useful single-use functions that name
behavior or hide complexity. Preserve validation and error handling.

For runtime claims, establish the expected result independently of the code under
test. Run the smallest check that can disprove the claim. For a bug fix, reproduce
the failure before the change and run the same reproduction afterward.

Finish when the relevant checks pass and remaining limits are explicit.
Distinguish inspected source, executed checks, historical results, and assumptions.
Claim a performance improvement only when measurements support it.

## Configure work ownership and tracking

Use `setup-matt-pocock-skills` for tracker and domain conventions. Inspect existing
issues before creating work. Read discussions, record ownership, and use native
parent/blocking relationships when the tracker supports them.

Add triage labels or a decision map when the work needs them. A written label
vocabulary does not establish that labels exist remotely. Close work when its
stated criteria are met, with a resolution, evidence, and explicit closure reason.
An approved plan does not certify implementation or runtime behavior.

Apply the active worktree and ownership policy. Preserve other sessions' changes,
and identify who owns an existing branch before resuming it. Keep scratch files
outside the repository and use separate build outputs for parallel builders.
After merge or abandonment, remove only owned worktrees under the cleanup policy.

Keep platform assumptions, credential mechanisms, absolute home paths, and model
preferences in the appropriate local configuration. Read available policy files
as evidence of their contents, not proof that the host loaded them.

## Record setup evidence

Use one setup record or the repository's existing equivalent. It contains:

- The source URL, full commit SHA, initializer and template paths.
- The target package, path substitutions, ownership exclusions, and reasons.
- The gate command, threshold, scope, trigger, and failure behavior.
- The OS, architecture, runtime and tool versions, dependency lock, and revision tested.
- The command result, exit code, relevant metric, and evidence location.
- Unexecuted checks, unavailable access, unresolved deviations, and next actions.

Run the full applicable check set, not only the initializer's shortest example.
Demonstrate that coverage below the required floor fails while the selected tests
otherwise pass. Restore the passing state after controlled negative checks.
Test failure propagation through wrappers when their behavior is uncertain.

Separate local checks from remote checks. Distinguish workflow configuration,
successful execution, coverage upload, and required merge protection. Preserve
network failures and access errors as evidence rather than converting them to
successful results.

For new repositories, follow the canonical language baseline's required gates.
For existing repositories, preserve enforcement outside the requested migration.
For several languages, reconcile shared workflow and configuration destinations
before running initializers. Missing coverage support blocks a coverage claim.

## Select optional research and teaching rules

Add these branches when the project contains the corresponding work:

| Trigger | Useful rules and artifacts |
| --- | --- |
| External reference implementations | Record origins, immutable revisions, reading paths, licenses, and snapshot checksums. Separate reference files from executable dependencies. |
| Large data or model artifacts | Store them externally. Record location and distinguish listing, verified bytes, successful loading, and reproduced results. |
| Lessons and worked examples | Define the audience and learning goal. Follow one coherent example, explain purpose before mechanics, and define terms before use. |
| Repeated numerical outputs | Keep one authoritative computation. Use independent expectations and invariants, then compare rendered tables with its output. |
| Visual or interactive explanations | Preserve editable sources, exact render commands, tested versions, and delivered assets. Inspect presentation and accessibility. |
| Learner feedback | Record approved sections, unresolved understanding, and the next learning gap. Separate arithmetic validation, visual inspection, and learning evidence. |

Keep model identities, numerical dimensions, timings, and renderer choices local
to the project. Adopt an animation tool only when the project requires it.
Research checks do not establish a GPU training environment.

Use `writing-for-agents` for instruction documents. For human-facing prose,
apply `avoid-ai-writing` and `simple-english` in Plain mode under the adopted
writing policy. Preserve terminology, facts, evidence limits, code, commands,
numbers, links, and attributed text during editing.

## Maintain the setup

When updating the baseline, compare old templates, new templates, and adapted
project files. Preserve justified changes and record new deviations. Rerun
applicable checks and update the source pin with the evidence.

Maintain the skill source in version control and install the complete directory.
Keep one intended installation per host and inspect discovery precedence when
duplicates exist. Compare source and installed files after updates.
