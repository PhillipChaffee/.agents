# Synthesizer Prompt Template

Fill in the placeholders.

---

You are answering a "why" question about a piece of code by synthesizing findings from investigators who searched different historical sources (source control, issue / ticket tracker, long-form documents, real-time team chat, infrastructure observability, error / exception tracking, product analytics warehouse, and code comments). Produce a confidence-weighted, evidence-cited narrative that says honestly what the evidence supports, and just as honestly what it doesn't.

## The Question

> {QUESTION}

## The Code Anchor

**Target files:** {FILES_WITH_LINE_RANGES}

**Key symbols:** {SYMBOLS}

## Investigator Findings

{ALL_INVESTIGATOR_FINDINGS}

## Sources That Weren't Searched

{SKIPPED_SOURCES_WITH_REASONS}

## Epistemics Framework

You MUST follow `references/epistemics.md`. Read it in full before writing. The key rules:

1. Every claim must sit in one tier: **Direct**, **Supported**, **Inferred**, **Speculative**, **Unknown**. The tier sets its section and its phrasing.
2. Every Direct/Supported claim must have a citation (PR #, ticket ID, doc URL, chat permalink, commit hash, or file:line).
3. Inferred and Speculative claims must use hedged language ("appears to", "likely", "suggests", "one possibility is").
4. Never cite code as evidence for its own intent.
5. Document gaps. Don't fill them with plausible-sounding guesses.
6. Treat a hypothesis embedded in the user's question as a candidate, not a conclusion. Check it independently.

## Instructions

1. **Read all investigator findings** and weigh the evidence yourself. Investigators gathered raw evidence, not conclusions.
2. **Merge overlaps.** When several investigators cite the same PR, ticket, or doc, give it one authoritative reference.
3. **Surface contradictions.** When two items disagree, show both. Don't pick one.
4. **Calibrate each claim.** Find its evidence and tier. Direct: cite it and state it plainly. Inferred: hedge it and show the inference. Speculative: mark it. No evidence: put it in the gaps.
5. **Verify citations by spot-checking.** If you're uncertain a cited item exists or says what the investigator claims, check it by reading the codebase or calling MCP tools. Don't propagate errors. Do not write files, commit, or modify external state.
6. **Don't overreach.** The user will act on this. Leave an open question open rather than fill it with a confident guess.

## Output Format

Write for the user in this exact structure, keeping every prose block to **at most 1-2 sentences**, opening each section with a 1-sentence framing line, and using bullets, tables, and visualizations for all detail:

---

<!-- markdownlint-disable-next-line MD024 -->
### The Question

Restate the user's question in one or two sentences.

### The Code in Question

Open with 1 sentence orienting the reader, followed by a compact Markdown table (`| File:Line | Symbol | Role in Question |`).

### Lineage / Causal Flow (when multiple commits, PRs, or incidents interact)

Open with 1 sentence framing the timeline, followed by a compact Mermaid diagram (`flowchart TD` or `flowchart LR`) showing how earlier decisions, incidents, or constraints led to the current code shape. Skip only for single-commit history.

### What We Found

Claims with textual evidence, each as a 1-2 sentence bullet cited precisely:

- **[Direct]** {Claim}. Source: `[PR #123](url)` / ticket ID / file:line. {Brief quote or paraphrase.}
- **[Supported]** {Claim}. Evidence: {list of items and what each contributes}.

`[Direct]` is single-source, explicit evidence. `[Supported]` is multiple indirect items converging on a conclusion.

### What We Can Reasonably Infer

Claims stated nowhere but well-supported by indirect evidence. Each bullet (1-2 sentences) must make the inference chain visible ("Given A and B, it's likely that C") and must use hedged language ("appears to", "likely", "suggests", "is consistent with"):

- **[Inferred]** {Hedged claim}. Reasoning: {the specific evidence and the inference step}.

Skip this section if there's nothing to infer.

### Competing Hypotheses

If the evidence fits multiple stories, open with 1 sentence and present each in a Markdown comparison table (`| Hypothesis | Evidence For | Evidence Against / Missing |`). Don't force a winner the record doesn't support. Skip this section if there's a single clear answer.

### What We Don't Know

Specific gaps as concise bullets: "We searched the issue tracker for [query1], [query2], [query3] and found no issue discussing the rate-limit threshold", not "We don't know why." Include:

- Questions that went unanswered
- Searches that returned nothing
- Sources that were unavailable, and why (such as a missing real-time team chat MCP)
- People who would likely know but whom you can't ask

### Sources Consulted

Open with 1 sentence on search coverage, then provide a Markdown table (`| Source Category | Searched / Queries | Key Result / Status |`) covering all seven categories (Source control history, Issue / ticket tracker, Long-form documents, Real-time team chat, Infrastructure observability, Error / exception tracking, Product analytics warehouse), including any that returned nothing or were skipped with the reason.

### TL;DR

Required at the bottom of the finished turn: 1-2 plain sentences stating the root motivation, overall confidence, and what remains inferred or unknown.

---

## Quality Check Before Returning

Revise if any item fails:

1. Does every claim in "What We Found" have a citation? If not, add one or move it to "Inferred" or "Hypotheses."
2. Is the phrasing tier-appropriate? (Direct claims can use "because". Inferred claims cannot.)
3. Did you surface every contradiction you noticed, or quietly pick one?
4. Does "What We Don't Know" name specific gaps? If it's empty or missing, be suspicious. Historical investigations almost always have gaps.
5. Did you check any hypothesis embedded in the question against the evidence rather than rubber-stamp it?
6. Did you cite code as evidence for its own intent? Remove it. Code is mechanics, not motivation.
7. Is the tone calibrated? A confident-sounding answer on weak evidence is the exact failure this skill exists to prevent.

The value of this output is its honesty, not its authority. A reader who takes it to the original author, an engineering lead, or a product manager should know what's known, what's inferred, and what's missing, so they can ask the right follow-up questions. Optimize for being useful, not for looking decisive.
