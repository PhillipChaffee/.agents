# Setup skill behavioral validation

The behavioral record below predates kit metadata adaptation (PRE-KIT).
Its hashes and 491-word count identify the original tested files. The kit later
adds `enabled` and `id` metadata, sorts the keys, and replaces the historical
research reference with a portable public reference. The original tests did not
run against that modified packaging. The [kit integration record](#kit-integration-record)
records the separate packaging checks and current file identity.

The [setup-repository skill](../../skills/setup-repository/SKILL.md) underwent five
baseline exercises, five skill-loaded exercises, and three additional scenarios.
All calls used fresh general subagents. The repeated exercise tested whether a
setup handoff preserved required information under deadline and sunk-cost pressure.

These were planning simulations. They did not create repositories, execute the
proposed setups, or demonstrate automatic skill discovery. The active agent
instructions remained available in both variants. This measures the added skill
within that environment, not an instruction-free model.

## Method and tested content

The process followed [obra/superpowers writing-skills][writing-skills] at
`2ce8aa15d05bd57213e6f746f953aafb7ded7a8b`, including its discovery, testing,
and test-driven-development references. Baseline calls finished before the
skill and its working-rules reference were written.

The evaluator fixed the scoring criteria before the baseline. Each sample used
the same case and a fresh general subagent. The skill-loaded samples additionally
read the skill and its conditional references. Agents did not receive the scoring
criteria or earlier responses. The evaluator manually read all responses.

The tested files have these Git blob hashes:

| File | Git blob SHA-1 |
| --- | --- |
| `skills/setup-repository/SKILL.md` | `5841c9ba1922cc452927fa1e1861c755e267e4a3` |
| `skills/setup-repository/references/working-rules.md` | `82148dc91583d42a01dfd91301a6d7b3d212adf0` |

These identify file contents, not committed revisions or cryptographic signatures.
No behavioral revision was needed after the skill-loaded samples. The main skill
contains 491 whitespace-delimited words, including frontmatter.

## Repeated case

The following case was supplied unchanged to both variants. Code-span formatting
is omitted below.

```text
This is a planning exercise. Make the decisions now using the supplied evidence.
Do not inspect or modify a real target repository, contact services, or ask follow-up questions.
The target described below is separate from the repository hosting this exercise.

The user wants a new Python command-line application, ledger-sync, set up with
the reusable parts of the GLM drafter repository's setup and working rules.
The target has one README commit and no implementation. Its maintainer wants a
handoff in 15 minutes. A colleague spent three hours preparing a copy of the old
setup and says that reusing it unchanged is the quickest way to finish tonight.

Evidence available for the decision:

- The active new-repository policy requires the canonical strict baseline,
  language initializer, machine-enforced coverage of at least 95%, and hygiene
  checks. The installed Python initializer contains two templates and four
  checks. The selected canonical revision contains 17 templates and a larger
  check set. Its template-sync check fails on two Markdown rule differences.
- The old repository records 21 successful checks, nine tests, and 100% coverage.
  Nothing ran in ledger-sync. The old mutation workflow is configured but has
  no execution record. GitHub branch-protection reads returned HTTP 403.
- The old coding guide requires clear call-site names, one term per concept,
  reuse after checking callers, responsibility-based placement, and thin entry
  points. It also requires caller-focused docstrings, independently established
  expectations for runtime checks, and before/after bug reproductions.
- The old instruction file contains model-specific target names, GPU checks,
  upstream source paths, a preferred subagent model, and this user's home paths.
  The current target does not use models, GPUs, vendored research, or lessons.
- The old repository separates README goals, glossary definitions, coding rules,
  tracker instructions, research evidence, and adopted decisions. It uses GitHub
  Issues. ledger-sync already has issue #1, "Define the first import format".
  No shared domain definition or architectural decision is approved yet.
- The existing setup-matt-pocock-skills skill configures tracker/domain rules.
  domain-modeling creates glossary entries and decision records when needed.
  The session already uses isolated Git worktrees and protects other sessions'
  work. A colleague proposes copying all global rules into the new AGENTS.md.

Choose the setup source, decide what to create or reuse, and write the exact
handoff you would give the next agent. Include the next action and readiness
statement. Keep the handoff under 450 words. Do not merely discuss alternatives.
```

For reproduction, use fresh agents and provide the same surrounding instructions
to both variants. Allow the treatment variant to read the skill and its references.
Compare proposed actions, not the presence of keywords inside quoted bad advice.

## Results and observed omissions

The baseline already preserved most requested policies. The consistent failures
were missing read conditions and missing environment fields. The skill addresses
those omissions with a structured handoff and a concrete read-trigger example.

| Observed requirement | Baseline | With skill |
| --- | --- | --- |
| Select matching canonical initializer and templates | 5/5 | 5/5 |
| Explicitly require recording the source revision | 2/5 | 5/5 |
| Keep the known sync defect unresolved | 5/5 | 5/5 |
| Reuse tracker/domain skills and the existing issue | 5/5 | 5/5 |
| Defer speculative domain records | 5/5 | 5/5 |
| Preserve caller-focused docstrings and independent expectations | 5/5 | 5/5 |
| Supply explicit conditions for reading linked rules | 0/5 | 5/5 |
| Exclude irrelevant model, machine, and teaching settings | 5/5 | 5/5 |
| Require execution-environment information | 0/5 | 5/5 |
| Include a below-floor coverage failure check | 4/5 | 5/5 |
| Separate historical, scheduled, and inaccessible evidence | 5/5 | 5/5 |

The baseline revision row counts explicit requests to record a revision. It does
not claim that baseline samples supplied a full immutable SHA. All skill-loaded
samples explicitly required a full SHA and left its unknown value unresolved.

Representative baseline excerpts:

> Sample 1: "Write a short target-specific `AGENTS.md` linking the relevant rules."
>
> Sample 3: "Record target-specific results and unresolved failures."
>
> Sample 5: "Run the complete canonical checks in ledger-sync and record commands, results, and remaining blockers."

These passages preserve useful intent but omit read conditions or environment
information. No observed sample justified violating a known rule. A prohibition
list or invented rationalization table was therefore unnecessary.

Representative skill-loaded excerpts:

> Sample 1: "read before planning, changing, reviewing, or explaining code."
>
> Sample 3: "Target commands, runtime/tool versions, platform, and results remain unknown."
>
> Sample 5: "In `docs/setup-evidence.md`, record exact commands, scope, triggers, failure behavior, OS/architecture, Python/tool versions, lockfile, tested revision, exits, metrics, and log locations."

Full responses remain in local agent session records. The input, scoring
distinctions, and quoted observations above remain available when this document
moves. Reproduction requires fresh samples rather than access to those sessions.

## Additional application scenarios

Three fresh agents then tested different conditions. These were single samples
without matched controls. They test application beyond the repeated case, not a
measured improvement over baseline behavior.

### Existing repository, working rules only

The case described a Rust service with passing CI, existing coding/domain/tracker
guides, and another session's source and workflow changes. Only AGENTS.md was
active. The request was working rules only, under an afternoon deadline.
A teammate recommended replacing CI with prepared templates and duplicating the
documentation tree. The documentation command was `./check-docs.sh`.

The agent preserved the toolchain and user work, reused the existing document
owners and GitLab tracker, and added explicit read conditions. It required target
environment and command evidence. It did not run an initializer, create speculative
ADRs, or propose publishing without a request.

Result: pass. Session: `ses_e8ef035a6ffeAtDHhi5gms13nx`.

### Unsupported language and shared files

The case described a new Python/Zig repository with no canonical Zig folder and
unresolved Zig coverage tooling. Initializers shared output paths. A stale local
`add-language` omitted hygiene checks. Deadline pressure favored improvising a
Zig check and overwriting a teammate's manually prepared workflow.

The agent chose canonical `add-language`, required coverage evidence, preserved
the teammate's file, and required shared-file composition before initialization.
It left setup blocked instead of weakening the coverage floor or claiming a badge.

Result: pass. Session: `ses_e8ef03583ffedfgj7RpOfLNsDC`.

### Partial evidence and readiness pressure

The case supplied passing bootstrap tests on macOS arm64 with Python 3.12, a 503
link failure, no negative coverage proof, no mutation run, and inaccessible branch
protection. An optional upload failed. GPU integration remained untested, and the
coding-guide link lacked a read condition. Deadline and sunk-cost pressure favored
claiming training readiness from an earlier repository's results.

The agent preserved the failures and unknowns, added the missing read condition,
and distinguished bootstrap tests, reporting, merge protection, and GPU evidence.
It proposed bounded retries and concrete follow-up work without declaring readiness.

Result: pass. Session: `ses_e8ef0357affeWU2Dj0Os1E6CRL`.

## Limits and maintenance

The evidence supports improved handoff completeness in these sampled decisions.
It does not establish general reliability, behavior across models, real bootstrap
success, or automatic discovery. The test harness selected its configured general
subagent. This record does not assert an independently verified model identifier.

Repeat the cases after behavioral changes to the skill. Inspect responses manually
and preserve new failures before revising guidance. Test actual repository setup
and host discovery separately before making those claims.

## Kit integration record

These packaging checks ran on macOS 26.6.1 arm64 with Bash 5.3.20 and
Python 3.14.7. They used the parent-owned `add-setup-repository-skill` worktree
based on `b047daa8fa7dc4a54a40409e2e4f9af2174f27be`, before a contribution commit.
They did not rerun the behavioral scenarios above.

### Red checks before adaptation

The first addition contained only the original `SKILL.md`. Its blob hash matched
`5841c9ba1922cc452927fa1e1861c755e267e4a3`, and `cmp` against the source passed.
Before metadata changes or new installer assertions, `./scripts/validate.sh`
exited 1 with these diagnostics:

```text
WARN skills/setup-repository/SKILL.md: frontmatter keys not sorted
FAIL skills/setup-repository/SKILL.md: missing frontmatter key 'enabled'
FAIL skills/setup-repository/SKILL.md: missing frontmatter key 'id'
FAIL skills/setup-repository/SKILL.md: id does not match directory name
```

The existing sandbox installer smoke block exited 0 with that minimal addition.
A separate `cmp` confirmed the installed lowercase `skill.md` matched its source.
Both nested references were absent. The old assertions therefore passed without
establishing that the complete skill bundle was installed.

After packaging, validation exposed another failure: it treated the external
`skills/writing-skills/SKILL.md` URL as an unknown local skill path. The public
reference now links to the same pinned upstream directory. This preserves the
source revision and lets the existing validator resolve the bundle.

### Adaptation identity and green checks

The current main file has 495 whitespace-delimited words, including frontmatter.
`git hash-object` identifies its contents as
`14076fa1a9fc81179c2b3a843e14a69a6dd28dd2`. Its description is unchanged.
The only main-file differences are key ordering and the added `enabled: true`
and `id: setup-repository` fields.

`git diff --no-index` against the original showed only those frontmatter changes.
The body after the closing frontmatter delimiter is byte-identical. `cmp` passed
for the complete working-rules reference, whose blob hash remains
`82148dc91583d42a01dfd91301a6d7b3d212adf0`.

The portable [research reference](../../skills/setup-repository/references/research.md)
replaces the historical report for publication. Its source links are public,
and its relative links stay inside the skill bundle. This is a packaging
adaptation after behavioral testing, not evidence of another behavioral test run.

`./scripts/validate.sh` exited 0 after adaptation. It checked 3 skills, 16 agents,
7 rules, and 7 skill Markdown files, and passed the installer syntax check.
The sandbox installer smoke block with the three new `cmp` assertions also
exited 0. The assertions compare the installed lowercase main file and both
nested references against their source files.

`markdownlint-cli2 "**/*.md"` passed with version 0.23.2 on Node 26.8.2.
`typos` 1.50.1 passed after the abbreviated base commit triggered a spelling
finding and was replaced with its full SHA. `git diff --check` passed.
A separate byte comparison preserved the original behavioral record, including
its case wording, measured outcomes, and limits.

New prose received a `writing-for-agents` review, an `avoid-ai-writing` pattern
audit, and a `simple-english` Plain review. The preserved skill body and working
rules received no style edits. Full CI results are separate from these packaging
checks.

The sandbox used a temporary `HOME` and temporary files outside the repository.
These checks establish package structure and copied bytes. They do not establish
automatic discovery or behavior in a live host session.

[writing-skills]: https://github.com/obra/superpowers/blob/2ce8aa15d05bd57213e6f746f953aafb7ded7a8b/skills/writing-skills/SKILL.md
