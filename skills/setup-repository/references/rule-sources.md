# Literal rule sources

The four TXT payloads contain the maintained rule text. Treat them as bytes,
including their final newlines. Their Markdown links resolve at the destination
paths after installation. This record defines ownership and placement, not
replacement wording.

## Source identity and destinations

Source repository: `glm-5.3-flash-drafter`.
Source revision: `5905904e02de887dde3d4de3d7b83313ffc38c5e`.
Line numbers below are one-based and inclusive at that revision.
Extract with line endings retained, without decoding or newline normalization.

| Payload | Source selection | Destination and ownership |
| --- | --- | --- |
| [coding.txt](../templates/coding.txt) | Entire `docs/agents/coding.md` | Whole `docs/agents/coding.md` |
| [domain.txt](../templates/domain.txt) | Entire `docs/agents/domain.md` | Whole `docs/agents/domain.md` only when absent. Preserve an existing project-specific guide. |
| [agent-rules.txt](../templates/agent-rules.txt) | `AGENTS.md` lines 6–23, one blank line, then lines 56–73 | One managed block in the active root `AGENTS.md` |
| [issue-tracker-evidence.txt](../templates/issue-tracker-evidence.txt) | `docs/agents/issue-tracker.md` lines 43–49 | One managed block in `docs/agents/issue-tracker.md` |

| Payload | Bytes | SHA-256 |
| --- | --- | --- |
| `coding.txt` | 5595 | `e583fe3c0b1cb25be5b3dafdc6b0fe94c9b8e3c9bdbfdc2f9b87d1728111ae7c` |
| `domain.txt` | 870 | `4f9c0172770fcad1374ec7bfee22502a06f0f61d52ae741d30fb8862ed087cf2` |
| `agent-rules.txt` | 1329 | `7731c884c94de49adcf30b337f3ab33a010e0b280cd4910f7b9ff06ae5213e21` |
| `issue-tracker-evidence.txt` | 352 | `564cf08b9274732fd74db87d66dd4b4260fe4b8be6c72f93b9dcbc15633c2f5d` |

The source record deliberately contains no private repository URL.
The kit distributes the selected text, so installation needs no source-repository access.
Hashes identify the payload bytes and include their terminal newlines.

## Block boundaries and preflight

Use these exact marker pairs on separate lines:

```text
<!-- setup-repository:agent-rules:start -->
<!-- setup-repository:agent-rules:end -->

<!-- setup-repository:issue-tracker-evidence:start -->
<!-- setup-repository:issue-tracker-evidence:end -->
```

LF means a single line-feed byte (`0x0a`).
A block consists of the start marker, one LF, the complete payload bytes,
the end marker, and one LF. The payload already ends with LF.
Add no blank lines inside this boundary. For comparison, extract all bytes
after the start marker's LF and before the end marker.

Before any rule write, inspect all destination files and headings together.
Treat identical whole files and managed blocks as no-ops.
Preserve an existing domain guide, even when it differs from the payload.
For a differing coding file or managed block, show a diff and obtain explicit
approval before any write. For unmanaged sections with payload headings, show
their proposed treatment and obtain approval before adopting, replacing, or removing them.
Never silently merge those sections or create duplicate headings.
Malformed, partial, or duplicate marker pairs block installation.

Keep unrelated prefix and suffix bytes unchanged, including when replacing an
approved managed block. If appending a new block needs a separator, place it
outside the markers. If a whole-file replacement contains unrelated material,
resolve its preservation with the user before approval.

For a missing root file, use `# Agent guidelines` followed by two LF bytes,
then the agent-rules block. For a missing tracker guide, use `# Issue tracker`
followed by two LF bytes, then the evidence block. These titles are wrappers,
outside the payload. Existing project configuration or the setup skill owns
tracker identity. The evidence fragment supplies `#evidence-and-completion`
without choosing a tracker.

Keep literal source paths and language assumptions, including `pyproject.toml`
and `CONTEXT.md`. Report incompatibilities before installation rather than
substituting paths or inventing project files. After installation, compare
whole files and extracted blocks with the payloads. An existing domain guide
is reported as preserved, not as an installed copy. Repeat installation must
leave all target bytes unchanged.

## Reviewed updates

The payload files are the editable, versioned rules after this import.
For a source refresh, review the revision and extraction ranges, then copy the
selected bytes without prose editing. For an intentional rule change, edit the
payload itself and review its exact diff. Record the new origin or rule revision
instead of claiming that changed bytes still match the original source.
Update this record, payload hashes, and test expectations together after approval.
Rerun fidelity and installation checks.
Installation always uses the reviewed bundled revision, never an unrecorded
live source. Writing-style review applies only to new instructions and notes
outside payloads.
