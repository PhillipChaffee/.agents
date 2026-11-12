---
description: "Find what a change could break somewhere else before it ships, beyond the diff, and prove the one fact it's safe because of by running real code instead of writing it up. Use for 'blast radius of X', 'what could this break', or reviewing a small diff you don't trust."
enabled: true
id: blast-radius
name: blast-radius
---

# Blast radius

Find what a change breaks somewhere else, before it ships. Use for "blast radius of X", "what could this break", or reviewing a small diff you don't trust yet.

Companion to `how` and `why`. `how` tells you what the code does. `why` tells you why it's shaped that way. Blast radius tells you what it breaks somewhere else.

Listing the callers is not the job. The agent can grep those in a second. The job is the breakage grep won't show you.

## Don't trust your own writeup

A blast-radius writeup that sounds right is worthless. It reads as convincing whether or not it's true. So don't hand back the writeup. Find the one or two facts the whole thing depends on and prove them by running code.

### How sure are you

For each fact the change's safety depends on, get it as far down this list as is cheap, and say where it stopped.

1. You said so. Worthless on its own.
2. You pointed at the line. A real `file:line`, or the library's own source.
3. You showed the bad case can't happen. You walked the failure step by step and it doesn't reach.
4. You ran it. A script or test that calls the real code and fails loud if you're wrong.
5. You reproduced it in the running app.

Step 4 is usually one small script that imports the same library the app ships and calls the exact function you're worried about.

## Steps

In the root chat, dispatch Steps 1-5 as one depth-1 `magic-agent` on the `hardest tasks` line in the `magic-models` role file (see `model-roles.md`), whose default is `deep`, because a thin parent never traces three-hop callers, library source, and a proof script inline.

When this skill already runs inside a depth-1 leaf subagent, or on a harness with no subagent tool, execute Steps 1-5 directly in this session and spawn nothing. Never wrap a wave inside a wave.

Give the worker the diff, the scope, and Steps 1-5 below, and state in the brief that it is a depth-1 leaf that never spawns a subagent.

1. Read the change. The diff, the symbols it adds, changes, and deletes, and what it now does differently, including the part the diff doesn't spell out. Run `git blame`, `git log -S`, and `git log --follow -p` in this leaf session, then read the PR and commits they surface. Never spawn a `why` subagent for this.
2. Find the one fact it's safe because of. Most changes that look risky are safe because of a single fact, like "this call only drops already-dead cache entries and does nothing else". Find that fact. If it holds, most risky cases are cleared at once. Spend your time here, not on a long list of maybes.
3. Look where grep stops. Read the source of the library you call, and check its pinned version and any local patch. Work out when things run, including microtasks, unmount and teardown, Solid versus React. Follow what a symbol search misses, including the JSON an API returns, a DB column, a wire format, another language reading the same bytes, a feature flag, and code three hops downstream.
4. Be honest about each risk. Give it a real chance of happening and a real cost if it does. Keep the risks you confirmed. List the ones you checked and cleared separately. Same rules as `why`. Cite a real `file:line`, a search that finds nothing is still an answer, and never make up a caller or an API.
5. Prove the one fact. Write a proof script or test that runs the real code, run it, and paste what happened.
6. Wide or cross-cutting diff only. The root chat chooses this option instead of the single-worker wave and dispatches `arena` itself from the root chat, with the `arena runners` line, because more than one model catches different real bugs. A leaf worker never runs this step and never nests it.

The parent relays the returned report.

## What to hand back

Keep every prose block to **at most 1-2 sentences**, open each section with a 1-sentence framing line, and use bullets, Markdown tables, and a Mermaid diagram when the change crosses multiple callers, services, or schemas:

- **What it does.** 1-2 sentences on what changed, plus bullets for non-obvious behavior changes. Include a compact Mermaid dependency/propagation diagram when 3+ hops or boundaries are involved.
- **The one fact it's safe because of.** State it in 1-2 sentences, name the verification level (1 to 5), and show the runnable proof output. If you couldn't prove it, write `unproven`.
- **Risks & Cleared Surfaces (Table).** Open with 1 sentence and present a Markdown table (`| Surface / Caller | File:Line | Status (Risk / Cleared) | Likelihood & Impact | Proof / Check |`) covering every confirmed risk and cleared path.
- **Before you merge.** Bullet list of the cheapest test or repro that catches the real bug, including the script you wrote.
- **TL;DR.** Required at the bottom of the turn, as a `## TL;DR` section with 1-2 plain sentences stating whether the safety fact is proven, any remaining risk, and merge readiness.

Write it through `unslop`, cite real code, and strip anything private before it goes anywhere public.

**Reply.** The writeup above (1-2 sentence max prose blocks, Risk/Cleared table, propagation visual when multi-hop, and bottom `## TL;DR`), with the one safety fact either proven or marked unproven.
