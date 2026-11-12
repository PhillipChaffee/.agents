# Authoring or modifying a skill

**You own the skill's voice.** Every heavy step is a flat depth-1 wave whose model comes from a role line in the `magic-models` role file.

1. **Wave 1, author.** Dispatch one `magic-agent` on the `judgment and prose` line (default `deep`) with the skill path, the audience, and the decision the skill changes. It writes or edits `SKILL.md` per `/writing-skills`, then applies `/unslop` and `/technical-writing` so the prose is one Diátaxis mode with no restatement.
2. **Wave 2, pressure and validate.** Dispatch `arena cross-judge pool` (default `deep`) or `swarm workers` (default `main`) as depth-1 leaves to run the pressure scenarios and the structural validator. Frontmatter has `name` and `description`, referenced files exist, cross-skill links resolve. Test cases only when structural, skipped when subjective. Report each failure with the line that caused it.
3. **Wave 3, open the PR.** Run **Opening a PR**, whose commit splitting, `/make-pr-easy-to-review`, PR body, and reply draft run in one `judgment and prose` (default `deep`) `magic-agent`.

When in doubt, delete. Keep only prose that changes a decision. Tell it to do the thing and skip the reason. Explain only when the rule is confusing without one. Match tone to scope. Point at structural sources (types, READMEs, config) per the **principle-encode-lessons-in-structure** skill. Delegate to other skills by path, and don't restate them. A workflow you keep hitting but isn't captured means proposing a new skill.

**Reply.** Give a summary of the skill, the key design decisions, and the validation notes.
