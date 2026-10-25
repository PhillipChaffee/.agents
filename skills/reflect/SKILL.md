---
description: Spawn three parallel review subagents over the active transcript, surface learnings, and route each to a concrete edit on an existing skill. Use when the user says reflect.
enabled: true
id: reflect
name: reflect
---

# Reflect

Mine the current conversation for durable learnings, then route them into skill edits.

Invoke when the user says "reflect" or "/reflect". Skip when the conversation is trivial, off-topic, or already covered by an existing skill the parent followed correctly. One-offs are not learnings.

## 1. Locate the active transcript

Before fanning out, find this conversation's transcript in the session transcript store (the harness adapter names the path). Do not glob across other workspaces' transcript stores. That crosses workspace boundaries and reads private chats from unrelated projects.

List the ten newest transcripts, subagent transcripts included, in the layout the harness adapter names. For each candidate, read the first JSONL line. Take the file whose `message.content[0].text` contains the conversation's opening user prompt. If none matches, pass a tight digest of the session instead.

## 2. Spawn three reviewers in parallel

One message, three subagent spawns, each general-purpose and read-write. Reviewers need MCP access to look up the tickets, chat threads, and observability traces the transcript references, and read-only types drop MCP access in some harnesses, so a subagent that needs MCP tools is read-write with edits forbidden in the brief.

Each reviewer and the synthesizer name a role line in the `pstack-models` role file (see `model-roles.md`) and a default. Set `model` to that line's value, or to the default if the role file or the line is missing. Leave `model` unset when the value is `auto` or `inherit-parent`. If the harness rejects the resolved model, fall back to the role's default tier and say so. Pick each subagent's reasoning level and fast or standard speed for the job, per the Subagents section of the **poteto-mode** skill.

| Lens | Role line | Default `model` | Prompt template |
| --- | --- | --- | --- |
| Judgment | `reflect judgment, divergent, synthesizer` | `deep` | `references/judgment-reviewer.md` |
| Tooling | `reflect tooling` | `main` | `references/tooling-reviewer.md` |
| Divergent | `reflect judgment, divergent, synthesizer` | `deep` | `references/divergent-reviewer.md` |

Pass each template verbatim, substituting the transcript path or digest where marked. Reviewers return findings in the subagent response body.

## 3. Synthesize

One subagent spawn, general-purpose, `model` from the `reflect judgment, divergent, synthesizer` line (default `deep`), read-write. It spot-verifies citations through MCP, and read-only types drop MCP access in some harnesses. Pass `references/synthesizer.md` verbatim, with each reviewer's full output inlined where marked. It returns an Accepted / Rejected / Backlog list.

## 4. Structural enforcement check

Move any Accepted item that a lint rule, script, metadata flag, or runtime check would enforce more reliably to Backlog. See the **encode-lessons-in-structure** principle skill.

## 5. Apply

Present the synthesizer's full Accepted / Rejected / Backlog output and wait for explicit approval before applying any Accepted edit. The user picks the subset and may redirect routings. Skill changes affect every future agent in the org. Do not auto-apply.

File each Backlog item to your team's devex or backlog tracker without waiting. Only the Accepted list waits for approval.

Never edit a skill in an installed kit copy. Before approval, show its destination, the project's skills directory (`.agents/skills/<skill>/`) or the user's (`~/.agents/skills/<skill>/`). The harness adapter lists the others. After approval, copy the skill folder there and edit the copy. Never open a PR or push.

Follow each approved row's Routing exactly:

- Trivial existing-skill edit (a one-line bullet, a tightened sentence, a stale fact corrected): the parent does it directly.
- Substantive existing-skill edit (a new section, a new pattern table, more than ~10 lines): hand to the **create-skill** skill (installed separately with the main flow) and run its draft / test / iterate loop.
- `tune description: <skill path>` (the skill exists but didn't trigger when it should have): hand to `create-skill` and run its description-optimization loop.
- `new skill via create-skill: <kebab-name>`: hand creation to `create-skill`. Do not invent the shape ad hoc.

If your environment ships a SKILL.md validator, run it on every touched skill before declaring done.

## 6. Summarize for the user

Short list, no preamble:

- Edits applied: `<skill path>`. What changed, one line each.
- New skills created: `<skill path>`. One line each (rare).
- Backlog filed to the devex tracker: `<issue title>` (`<tags>`). One line each.
- Dropped: one line per rejected finding + reason from the synthesizer.
