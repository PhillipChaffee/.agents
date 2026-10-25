# Setup skill literal-installation validation

The current requirement is to install the maintained source rules word for word.
The handoff-only evidence in commit `0df209a` is superseded for this requirement.
That commit retains the historical record. Its planning scores do not establish
literal installation, repeat-install behavior, or conflict handling.

## Independent source expectations

The source revision is `5905904e02de887dde3d4de3d7b83313ffc38c5e` in
`glm-5.3-flash-drafter`. An independent agent calculated expected SHA-256 values
from that revision before implementation. Current source files also match the
pin, confirmed by `git diff` with no output.

The [source record](../../skills/setup-repository/references/rule-sources.md)
specifies the four selections, byte lengths, hashes, destinations, and block
boundaries. The tests retain those independent hashes. Only the expected payload
filenames `coding.md` and `domain.md` changed to `coding.txt` and `domain.txt`.
The payloads preserve final newlines as well as visible text.

## Red before payload implementation

The initial application baseline, reported by the parent session, could not
install literal rules because the skill supplied rewritten summaries only.
The independent tests first reported two tests with eight failures.
After the TXT filename correction and before adding payloads, this session reran:

```sh
python3 -m unittest discover -s tests -v
```

Result: exit 1, `Ran 2 tests`, `FAILED (failures=8)`.
Four packaged payloads and four installed payloads were missing.
The sandbox installer itself exited 0, so successful execution alone did not
establish delivery of the required content.

## Green source and kit-install checks

After adding the exact payloads and extending skill support-file selection to TXT,
the same unittest command exited 0 with `Ran 2 tests` and `OK`.
The tests independently hash all four source payloads and all four installed
copies after running the existing installer in a temporary home.
`shasum -a 256 skills/setup-repository/templates/*.txt` also matched every expected hash.

These runs used macOS arm64, Python 3.14.7, and Bash 5.3.20.
`PYTHONDONTWRITEBYTECODE=1` prevented test cache files, and `TMPDIR` selected
session scratch space. The installer used a temporary `HOME`.
The main skill contains 470 whitespace-delimited words, including frontmatter.

The following local checks also exited 0:

| Command or check | Result |
| --- | --- |
| `./scripts/validate.sh` | 3 skills, 16 agents, 7 rules, 7 skill Markdown files, installer syntax passed |
| Existing sandbox smoke block with updated comparisons | Main skill, both references, and all four TXT payloads matched installed bytes |
| `cmp` for coding and domain payloads against current source files | Both whole-file comparisons passed |
| `markdownlint-cli2 "**/*.md"` | Version 0.23.2, no findings |
| `typos` | Version 1.50.1, no findings |
| `git diff --check` | No whitespace findings |
| `shellcheck scripts/install.sh` | Version 0.11.0, no findings |
| `shfmt -d scripts/install.sh` | Local version 3.14.1, no formatting differences |

### TXT link handling

With lychee 0.24.2, `lychee --dump-inputs .` included all four TXT payloads.
`lychee --dump skills/setup-repository/templates` emitted no links.
`lychee --offline --no-progress .` exited 0 with zero errors.
This establishes directory-wide local link behavior without changing the link
configuration or adding wrapper documents. Remote links were excluded by the
offline command, so that result is not a full network link check.

## Executed target scenarios

Three agents applied the corrected skill to synthetic existing-Python fixtures.
The agent that calculated the independent hashes then inspected all three targets.
It compared their bytes with the fixed hashes and original pinned Git blobs.
All four bundled payloads matched both sources of expected bytes.
All four current source files also matched the pinned blobs directly.

| Fixture | Final inventory | Independent result |
| --- | --- | --- |
| `verbatim-baseline` | 6 files, 8519 bytes, 2 directories | Both whole guides and both extracted blocks match the pinned source. |
| `verbatim-conflict` | 3 files, 166 bytes, 0 directories | Every original byte and path remains unchanged. The `docs/` directory is absent. |
| `verbatim-update` | 6 files, 7731 bytes, 2 directories | Coding and both blocks match the pinned source. Existing project content remains intact. |

The baseline retains the original 54 AGENTS bytes, followed by one separator LF
outside the managed block. Its README and Python configuration retain their original hashes.
The tracker uses the specified neutral wrapper.
Each managed block has one valid marker pair and unique payload headings.

The conflict report records an unmanaged `## Comments` section and no approval
to replace, remove, or adopt it. The agent stopped before writing any rules.
The independent comparison matched every file against the saved original contents,
byte counts, and hashes. This establishes preservation for this conflict scenario.

The update retains the exact AGENTS prefix and suffix around the approved block.
Reconstructing the old block produces the original whole-file hash.
The existing 46-byte domain guide remains unchanged and differs from the default payload.
The tracker retains its complete original prefix, with one separator LF outside
the appended evidence block. README and Python configuration hashes remain unchanged.

In both installed fixtures, the coding links resolve to `domain.md` and
`issue-tracker.md#evidence-and-completion`. Each tracker contains exactly one
`## Evidence and completion` heading. Neither fixture contains an invented glossary.

### Fresh repeat evaluation

Before reading the scenario reports, the independent agent read the current skill,
source record, payloads, and baseline project files.
It assumed active root AGENTS instructions and worktree ownership as the fixture request specified.
It inspected every destination together and found no conflicting headings or markers.

Coding and both managed blocks were identical, so the repeat required no writes.
The existing domain guide was preserved. A Python comparison retained every file's
bytes and every directory path before applying those decisions, then compared the final snapshot.
All 6 files, 8519 bytes, and 2 directories were unchanged.
Files created, modified, or deleted: 0.
This was an independent agent evaluation of the skill's instructions, not an executable project installer.

### Failures, commands, and evidence limits

The update agent reported one copying error: its first coding comparison found
an altered question and indentation. It corrected that copy before its final pass.
The independent comparison confirms that the final coding bytes match the pinned source.
It does not erase or independently replay that earlier failure.

The independent verifier also made one incorrect expectation about the baseline README's final newline.
That assertion failed. Inspection showed that the actual file matched the original manifest hash.
The verifier used the recorded README and Python configuration hashes on rerun.
The complete comparison then exited 0, without changing any fixture.

The independent checks used read-only `python3 - <<'PY'` commands on Python 3.14.7
and macOS 26.6.1 arm64. They read file bytes, calculated SHA-256, inspected complete
path sets, and extracted pinned blobs with `git show <revision>:<path>`.
The fresh repeat command and corrected three-fixture comparison both exited 0.
The complete inventory covered 15 files and 16416 bytes across the three fixtures.

Session evidence consists of `verbatim-install-result.md`, `verbatim-conflict-result.md`,
`verbatim-update-result.md`, and `verbatim-independent-result.md`.
The independent record retains raw results and the repeat manifest outside the fixtures.
The conflict and update comparisons also used their saved `*-before.json` records.
These scratch artifacts are session-local and are not repository links.

The complete local CI check set subsequently passed on macOS arm64 with Python
3.12.13 and the pinned tool versions, including shfmt 3.14.0. All 12 check groups
passed, including both unittests and all seven installer comparisons. Public link
checking ran without authentication: 40 checks, 27 unique URLs, zero errors.
History and working-tree secret scans passed, as did all 29 artifact checks.

These rules-only fixtures do not establish runtime readiness, language initialization,
or below-floor coverage enforcement. Malformed markers, other languages, and repeated
agent trials beyond the recorded scenarios remain untested.
No claim of application success follows from the earlier handoff-only scorecard.
