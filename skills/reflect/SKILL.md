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

Each reviewer and the synthesizer name a role line in the `magic-models` role file (see `model-roles.md`) and a default. Set `model` to that line's value, or to the default if the role file or the line is missing. Leave `model` unset when the value is `auto` or `inherit-parent`. If the harness rejects the resolved model, fall back to the role's default tier and say so. Pick each subagent's reasoning level and fast or standard speed for the job, per the Subagents section of the **magic-mode** skill.

| Lens | Role line | Default `model` | Prompt template |
| --- | --- | --- | --- |
| Judgment | `reflect judgment, divergent, synthesizer` | `deep` | `references/judgment-reviewer.md` |
| Tooling | `reflect tooling` | `main` | `references/tooling-reviewer.md` |
| Divergent | `reflect judgment, divergent, synthesizer` | `deep` | `references/divergent-reviewer.md` |

Pass each template verbatim, substituting the transcript path or digest where marked. Reviewers return findings in the subagent response body.

## 3. Synthesize

One subagent spawn, general-purpose, `model` from the `reflect judgment, divergent, synthesizer` line (default `deep`), read-write. It spot-verifies citations through MCP, and read-only types drop MCP access in some harnesses. Pass `references/synthesizer.md` verbatim, with each reviewer's full output inlined where marked. It returns an Accepted / Rejected / Backlog list.

That template also runs the structural-enforcement check. Any Accepted item that a lint rule, script, metadata flag, or runtime check would enforce more reliably moves to Backlog (the **encode-lessons-in-structure** principle skill). Keep that check inside the synthesizer prompt so one subagent owns both the routing and the enforcement test.

## 4. Apply

Present the synthesizer's full Accepted / Rejected / Backlog output and wait for explicit approval before applying any Accepted edit. The user picks the subset and may redirect routings. Skill changes affect every future agent in the org. Do not auto-apply.

File each Backlog item to your team's devex or backlog tracker without waiting. Only the Accepted list waits for approval.

Never edit a skill in an installed kit copy. Before approval, show its destination, the project's skills directory (`.agents/skills/<skill>/`) or the user's (`~/.agents/skills/<skill>/`). The harness adapter lists the others. After approval, copy the skill folder there and edit the copy. Never open a PR or push.

Under `orchestrator: thin`, when the harness exposes a subagent tool, Wave 4a dispatches one depth-1 `magic-agent` on the `judgment and prose` role (`deep`) with the approved rows and their destinations. It applies the approved trivial existing-skill edits and drafts any substantive or new-skill `SKILL.md` change per `/writing-skills`, then applies `/unslop`. For a substantive or new-skill row, the root chat dispatches Wave 4b pressure-test and validator leaves at depth 1 on the `arena cross-judge pool` role, and on `swarm workers` for the validator seats, before iterating. The root chat relays the leaf summary.

Under `orchestrator: standard`, or when the harness exposes no subagent tool, apply trivial edits inline in this session and run `/writing-skills` from the root chat.

Follow each approved row's Routing exactly.

- Trivial existing-skill edit (a one-line bullet, a tightened sentence, a stale fact corrected). Wave 4a applies it, or this session applies it inline.
- Substantive existing-skill edit (a new section, a new pattern table, more than ~10 lines). Wave 4a drafts it per `/writing-skills`, then Wave 4b runs the draft / test / iterate loop before the root chat applies it.
- `tune description: <skill path>` (the skill exists but didn't trigger when it should have). Same waves, with the `/writing-skills` description-optimization loop.
- `new skill via /writing-skills: <kebab-name>`. Same waves. Do not invent the shape ad hoc.

If your environment ships a SKILL.md validator, Wave 4b runs it on every touched skill before declaring done.

## 5. Summarize for the user

Keep prose blocks to at most 1-2 sentences, present Accepted / Backlog / Dropped items as a Markdown table or concise bullets, and end with a 1-2 sentence `## TL;DR` section at the bottom.

- Edits applied. `<skill path>`. What changed, one line each.
- New skills created. `<skill path>`. One line each (rare).
- Backlog filed to the devex tracker. `<issue title>` (`<tags>`). One line each.
- Dropped. One line per rejected finding + reason from the synthesizer.
- `## TL;DR`. 1-2 plain sentences stating what landed or awaits approval.
