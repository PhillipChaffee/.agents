# Eval

**You own the experiment design. Plan, blind, run, synthesize.** Every heavy step is a flat depth-1 wave whose model comes from a role line in the `magic-models` role file.

**Non-negotiables for blinding.**

- No `eval`, `test`, `judge`, `experiment`, `rubric`, `score`, `compare`, `benchmark`, `candidate`, or `arena` in any directory, file, or prompt the candidate sees.
- The candidate prompt looks like an organic user request. State the goal, not the meta.
- No chain-eliciting cues. Don't ask the candidate to list which skills, principles, or files they applied. Ask for design notes generally and grade chain-following from code shape, not self-report.
- Sanitize directory and slug names. Use project-shaped names a user might pick.
- Don't tell the candidate other candidates exist.
- The judge can know it's judging but sees outputs by sanitized label only, never by model name.
- Comparing two variants means one judge scores both sets in a single pass on one scale, blind to which set each came from.

**Waves.**

1. **Wave 1, frame and sanitize.** Dispatch one `magic-agent` on `judgment and prose` (default `deep`) with the variant under test and the behavior that counts as success. It writes the rubric (3-6 concrete criteria) for the judge only, holds it back from candidates, authors one organic prompt, and builds a sanitized working dir per candidate with the variant in place. It plants the context an organic task would have, a project skeleton and the skills the candidate would naturally read. It returns the dirs, the prompt, and the rubric path.
2. **Wave 2, candidates.** Dispatch the `arena runners` panel per the `arena` skill's Phase B, one depth-1 candidate per seat, each in its own sanitized dir with the same prompt. Pick each subagent's reasoning level and fast or standard speed for the job, per the Subagents section.
3. **Wave 3, blinded judge.** Dispatch one judge from the `arena cross-judge pool` (default `deep`) on a different model family, per the `arena` skill's Phase C. It sees outputs by sanitized label and the rubric, never a model name.
4. **Wave 4, audit and synthesize.** Dispatch one `magic-agent` on `judgment and prose` (default `deep`) as an Eval Auditor, with the rubric, the sanitized candidate dirs, and the candidate output paths. It reads every candidate output end to end, then verifies the chain from transcripts rather than self-report, reading each candidate's local transcript under the active workspace's session transcript store (the harness adapter names the path) without globbing across other workspaces. It looks at which files each candidate actually opened, compares that to the judge's verdict, and drafts the synthesis and the promotion recommendation. Disagreement means a model is biased or the rubric is ambiguous. This chat relays the verified result.

**Reply.** Give the variant under test, the rubric, per-candidate notes, the judge's verdict, your synthesis, and a recommendation for whether to promote the variant.
