---
description: When to delegate work to subagents and how to choose among them.
alwaysApply: true
---

# Subagent Use

Keep the main chat focused on orchestration, decisions, edits, and user communication. Delegate work that benefits from isolated context, parallel collection, or a specialized rubric.

## Decide Whether to Delegate

Work inline only when the task is a user-specified file read, one quick symbol lookup, a known fact, or a narrow check needed while actively editing.

Delegate unfamiliar code or architecture, multi-file tracing, debugging and root-cause analysis, code or plan review, tradeoff analysis, and web/MCP/external research. Split independent threads across subagents and launch them in parallel.

## Choose the Subagent

Choose by the work the agent must actually perform, not by the overall complexity of the parent task.

- `researcher-lite`: mechanical retrieval from known sources, one-fact confirmation, or a small bounded read.
- Harness-native search and command carriers (read-only explorers, shell runners): repository search, file discovery, symbol tracing, command output collection.
- `researcher-mid`: normal multi-file or multi-source gathering, call-flow tracing, evidence comparison, and research summaries.
- `researcher-deep`: broad, ambiguous, high-stakes, security-sensitive, or novel evidence gathering.
- Named kit specialists (`cr-*`, `research-*`): use when their rubric matches the task; they are defined in `agents/`.
- Generic fallback: use only as a carrier when a required named type is unavailable. Inline the highest-priority agent definition in its prompt.

## Model Selection

The kit pins no models (ADR-0001). Run subagents on the harness's configured subagent model; the consumer configures fast/main/deep tiers in their harness, not here. If a deep-thinking tier is configured, reserve it for rare, bounded, thinking-only work on a complete evidence packet: one discrete question, tools forbidden in the prompt, exact missing evidence reported rather than gathered. Complexity alone never justifies the deep tier, and it never gathers its own evidence — collectors gather first.

## Dispatch Requirements

- Make prompts self-contained with the goal, sources, constraints, known facts, and output format.
- Launch independent work in parallel. Run dependent stages sequentially and pass forward curated evidence.
- Do not pass `readonly: true` when a researcher needs web or MCP access. Forbid edits in its prompt instead.
- Never paste raw subagent output. Curate, deduplicate, resolve conflicts, preserve source references, and surface gaps.

Skills own workflow-specific pipelines, rosters, rubrics, and exit criteria. This rule owns shared delegation and tier-selection policy.