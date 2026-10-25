# Model roles

The kit pins no models (ADR-0001). pstack skills never name a model. They name a **role**, and the role resolves to a model when the subagent is spawned:

1. The consumer's `pstack-models` role file, when it has a line for the role.
2. Otherwise the role's default tier in the table below.
3. A tier resolves through the harness's own configuration. The kit's installer records the consumer's `fast`, `main`, and `deep` choices in `~/.agents/models.json`, and the [harness adapter](harness-adapter.md) says how each harness takes a model for a subagent.

Where the harness exposes no model field for subagents, every role runs on the parent chat's model. Say so in the reply when a skill expected a diverse panel.

## Roles

| Role | Who uses it | Default tier |
| --- | --- | --- |
| `code` | Code-writing delegates in **poteto-mode**. The role lines `feature, refactoring`, `bug-fix`, `perf-issue`, and `hillclimb` split it per playbook; each defaults to `code`. | `main` |
| `hardest tasks` | Cross-cutting design, gnarly concurrency, subtle algorithms, and precisely specified long step sequences. | `deep` |
| `judgment and prose` | Replies, docs, reviews of intent, synthesis. | `deep` |
| `trivial edits` | Mechanical one-line edits and renames. | `fast` |
| `how explorer` | The **how** skill's explorers. | `main` |
| `how explainer` | The **how** skill's explainer. | `deep` |
| `why investigators` | The **why** skill's investigators. | `main` |
| `why synthesizer` | The **why** skill's synthesizer. | `deep` |
| `reflect tooling` | The **reflect** skill's tooling reviewer. | `main` |
| `reflect judgment, divergent, synthesizer` | The **reflect** skill's judgment and divergent reviewers and its synthesizer. | `deep` |
| `swarm workers` | Every **swarm** worker, and the verification lanes other playbooks run through it. | `main` |
| `arena runners` | The **arena** skill's candidates. A panel. | `deep, main` |
| `arena cross-judge pool` | The **arena** skill's cross-judge. One seat is chosen from the pool, preferring a family different from the parent chat's. | `deep, main` |
| `architect runners` | The **architect** skill's runners, in place of `arena runners`. A panel. | `deep, main` |
| `interrogate reviewers` | The **interrogate** skill's reviewers. A panel. | `deep, main` |

A panel role's value is a list. One subagent runs per entry, alias entries included, so the list length sets the fan-out.

## Reasoning level and speed

Where the harness exposes a reasoning-effort setting, the ladder is `max` > `xhigh` > `high` > `medium` > `low`. The role file's `# budget` line sets every role's starting level. The default budget is `large`, which is `xhigh`. Before each spawn, start from the role's level, raise it one step for the hardest or subtlest work, lower it one step for judgment and two or more for routine work. Where the harness exposes a fast speed variant, use it only when the job is urgent (CI or trunk is red, or a person is blocked on the result right now). Verification stays on the `swarm workers` role at its configured level and speed. Where the harness exposes neither setting, ignore this section.

## The role file

`/setup-pstack` writes the role file. It is an always-applied rule, so its lines are normally already in context. If they are not, read the file. The [harness adapter](harness-adapter.md) names where it lives; in the protocol layout it is `~/.agents/rules/pstack-models.md`. Its shape:

```text
# pstack model configuration. One line per role. Delete a line to fall back to the default tier.
# `inherit-parent` or `auto` as a value: the role runs on the parent chat model (omit the model field).
# budget: large (xhigh)
code: main
judgment and prose: deep
arena runners: deep, <a model from another family>
swarm workers: inherit-parent
```

A value is one of:

- A tier name, `fast`, `main`, or `deep`.
- A model identifier the harness accepts for a subagent, exactly as the harness spells it.
- `inherit-parent` or `auto`. The role runs on the parent chat's model. Omit the model field.

A role with no line keeps its default tier. A line whose role is not in the table is from a retired role; ignore it.

## Diversity

A panel is diverse only when its seats resolve to different model families. When the consumer's `deep` and `main` tiers are the same family, pin one seat of each panel to another family in the role file, or accept a same-family panel and say so in the reply. Agreement between two models of one family is weaker evidence than agreement across families.

## Fallback

If the harness rejects the resolved model, fall back to the role's default tier and say so. Do not try other guesses. Never treat `inherit-parent` or `auto` as a rejected model.
