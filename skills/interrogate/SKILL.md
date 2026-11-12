---
description: "Use for \"interrogate\", \"adversarial review\", \"multi-model review\", \"challenge this\", \"stress test this code\", \"find blind spots\", or \"tear this apart\". Adversaries try to break a change or design, and only findings proven by a run survive."
disable-model-invocation: true
enabled: true
id: interrogate
name: interrogate
---

# Interrogate

Adversaries try to break a change or a design. A finding survives only when a run proves it. Report the findings. Do not apply fixes.

## Frame

The scope is what the user names. Otherwise it is the branch diff from its merge base with the base branch, through the working tree. State the intent with the **in-your-own-words** skill, from the user's message, the commits, and the PR description. Ask the user when the intent is unclear.

## Fan out

Run Phase A steps 3 and 4 and Phase B of the **arena** skill, with four changes. Read the `interrogate reviewers` line in place of `arena runners`. Copy the scope's uncommitted changes into each worktree. Spawn each adversary as a general-purpose subagent. In place of the arena task and rationale, give each adversary the scope, the intent, and this brief:

> Break this change. Prove each finding with a run against the real code, such as a failing test, a repro script, or command output that shows the wrong behavior. For a design or plan, run a prototype or probe the current tree. Keep repros in your own worktree. Report each finding with a title, the exact command, the output it printed, and the output the intent requires. Leave out anything you did not run. That covers style, naming, structure, and risks that need a future change to matter. No findings is a valid result.

## Verify

Spawn one depth-1 `magic-agent` on the `judgment and prose` line in the `magic-models` role file (see `model-roles.md`), whose default is `deep`. Its brief carries the scope, the intent, every adversary's report and repro command, and the work below.

> Rerun each repro command against the real code in an isolated worktree. Keep a finding when the printed output shows the failure and the failure breaks the intent. Drop the rest, and merge findings that share a root cause. Then format the `## Output` sections below, with the summary table, the dropped table, and a bottom `## TL;DR`. You are a depth-1 leaf, so never spawn a subagent.

Skip arena Phases C, D, and E. Adversaries find different failures, so the verdict keeps every verified finding, not one adversary's list. The parent relays the verified report without rewriting it.

## Output

Keep every prose block to **at most 1-2 sentences**, open each section with a 1-sentence framing line, and use Markdown tables and bullets:

- **Intent.** 1-2 sentences restating the change's intent.
- **Findings.** A Markdown summary table (`| Finding | Command | Adversaries | How It Breaks Intent |`) plus 1-sentence bullets with the printed output vs. required output for each verified finding. Say "no verified findings" when none survive.
- **Dropped.** A Markdown table (`| Adversary | Dropped Count | Reason |`) listing each adversary's dropped findings and why.
- **TL;DR.** A `## TL;DR` section at the bottom with 1-2 plain sentences stating how many verified findings survived and the overall verdict.
