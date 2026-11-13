---
description: "Use for \"interrogate\", \"adversarial review\", \"multi-model review\", \"challenge this\", \"stress test this code\", \"find blind spots\", or \"tear this apart\". Adversaries try to break a change or design, and only findings proven by a run or cited design contradiction survive."
disable-model-invocation: true
enabled: true
id: interrogate
name: interrogate
---

# Interrogate

Adversaries try to break a change or a design. A finding survives only when verified. Report the findings. Do not apply fixes.

## Frame

The scope is what the user names. Otherwise it is the branch diff from its merge base with the base branch, through the working tree. State the intent with the **in-your-own-words** skill, from the user's message, the commits, and the PR description. Ask the user when the intent is unclear.

Classify the scope as **Code Diff Mode** (when reviewing a code change or branch diff) or **Pre-Code Design Mode** (when reviewing a design doc, architecture sketch, or plan before code exists).

## Fan out

Run **arena** Phase A steps 3 and 4 and Phase B, with these adjustments. Read `interrogate reviewers` in place of `arena runners`, and spawn each adversary as a general-purpose subagent.

- **Code Diff Mode:** Copy the scope's uncommitted changes into each worktree and give each adversary this brief:

> Break this change. Prove each finding with a run against the real code, such as a failing test, a repro script, or command output that shows the wrong behavior. Keep repros in your own worktree. Report each finding with a title, the exact command, the output it printed, and the output the intent requires. Leave out anything you did not run, including style, naming, and hypothetical risks. No findings is a valid result.

- **Pre-Code Design Mode:** Pass the design document, sketch, or plan path alongside [`references/postmortem-corpus.md`](references/postmortem-corpus.md) and give each adversary this brief:

> Stress-test this design against [`references/postmortem-corpus.md`](references/postmortem-corpus.md). Prove each finding with either (1) a runnable quantitative or state-machine counterexample script in your worktree showing the design's stated math, pools, concurrency, or state invariants fail, or (2) a cited `section:line` contradiction or missing boundary defense against the DFMEA table or an applicable postmortem class. Never write dummy scripts; leave out ungrounded speculation. No findings is a valid result.

## Verify

Verify every finding before keeping it, then drop the rest and merge findings sharing one root cause.

- In **Code Diff Mode**, rerun the adversary's command per **arena** Phase F and keep the finding only when the output proves a failure breaking the intent.
- In **Pre-Code Design Mode**, keep a finding only when either (1) rerunning its math or state-machine script reproduces the failure, or (2) inspecting the cited `section:line` confirms a real DFMEA boundary gap or missing defense from `references/postmortem-corpus.md`.

Skip **arena** Phases C, D, and E. Adversaries find different failures, so the verdict keeps every verified finding rather than one adversary's list.

## Output

Keep every prose block to **at most 1-2 sentences**, open each section with a 1-sentence framing line, and use Markdown tables and bullets:

- **Intent**: 1-2 sentences restating the change's or design's intent.
- **Findings**: a Markdown summary table (`| Finding | Proof or Citation | Adversaries | How It Breaks Intent |`) plus 1-sentence bullets with the printed output vs. required output (or cited `section:line` gap) for each verified finding. Say "no verified findings" when none survive.
- **Dropped**: a Markdown table (`| Adversary | Dropped Count | Reason |`) listing each adversary's dropped findings and why.
- **TL;DR**: a `## TL;DR` section at the bottom with 1-2 plain sentences stating how many verified findings survived and the overall verdict.
