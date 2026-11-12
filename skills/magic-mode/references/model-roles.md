# Model roles

The kit pins no models (ADR-0001). magic skills never name a model. They name a **role**, and the role resolves to a model when the subagent is spawned:

1. The role line in the consumer's `magic-models` role file, when it has one.
2. The tier line for the role's tier in the same file.
3. The tier recorded in `~/.agents/models.json`.
4. The harness's own default for subagents, or the agent file the harness exposes.

Where the harness exposes no model field for subagents, every role runs on the parent chat's model. Say so in the reply when a skill expected a diverse panel.

## Orchestrator mode

The role file opens with `# orchestrator: thin` or `# orchestrator: standard`. `thin` is the default.

- `thin` treats the parent chat as a flat depth-1 wave dispatcher. It routes waves, tracks state, and keeps the user in the loop while it delegates scoping, planning, coding, Arena grafting, verification, diff review, and PR or reply prose to role-routed subagents. Pure chat and single-fact lookups stay inline.
- `standard` lets a frontier parent chat run framing, diff review, and leaf prose inline. Code changes and panels still route to subagents.

Both modes stop at depth 1. A subagent never spawns a subagent, because the supported harnesses do not offer portable nesting. The [harness adapter](harness-adapter.md) records the per-harness limit.

The `orchestrator:` tier line names the model the parent chat runs on. magic uses it as the cross-family comparison baseline when a judge panel must avoid the parent's family and the harness hides the parent model ID. It never spawns the parent chat.

## Tiers

Four tier slots shape the file. `orchestrator` holds the parent chat model, `fast` holds the cheapest capable model, `main` holds the everyday model, and `deep` holds the strongest model. A role line may name a tier or a model the harness accepts.

| Slot | What it holds |
| --- | --- |
| `orchestrator` | The parent chat model, used as the cross-family baseline |
| `fast` | Cheap mechanical edits, miners, collectors, and event watchers |
| `main` | Everyday implementation, research, and review |
| `deep` | Design, synthesis, grafting, and adversarial judgment |

The installer and `/setup-magic` record the same four choices under `presets` in `~/.agents/models.json`. A harness that reads neither the role file nor a tier line still resolves through that file.

## Roles

| Role | Who uses it | Default tier |
| --- | --- | --- |
| `feature, refactoring` | The Feature and Refactoring playbooks' code delegates. | `main` |
| `bug-fix` | The Bug fix playbook's code delegate. | `main` |
| `perf-issue` | The Perf issue playbook's code delegate. | `main` |
| `hillclimb` | The Hillclimb playbook's code delegate. | `main` |
| `hardest tasks` | Cross-cutting design, gnarly concurrency, subtle algorithms, and precisely specified long step sequences. | `deep` |
| `judgment and prose` | Replies, docs, reviews of intent, synthesis. | `deep` |
| `how explorer` | The **how** skill's explorers. | `main` |
| `how explainer` | The **how** skill's explainer. | `deep` |
| `why investigators` | The **why** skill's investigators. | `main` |
| `why synthesizer` | The **why** skill's synthesizer. | `deep` |
| `reflect tooling` | The **reflect** skill's tooling reviewer. | `main` |
| `reflect judgment, divergent, synthesizer` | The **reflect** skill's judgment and divergent reviewers and its synthesizer. | `deep` |
| `swarm workers` | Every **swarm** worker, and the verification lanes other playbooks run through it. | `main` |
| `arena runners` | The **arena** skill's candidates. A panel. | `deep, main` |
| `arena cross-judge pool` | The cross-family judge pool. It covers the **arena** cross-judge, the **interrogate** reviewers, the **eval** playbook judges, the **show-me-your-work** trail reviewer, the **figure-it-out** unit judges, the **orchestrate** and **autopilot-full** verifiers, the **writing-skills** and **writing-rules** pressure testers, and the **proof-driven-development** spec audit. One seat is chosen from the pool, preferring a family different from the parent chat's. | `deep, main` |
| `architect runners` | The **architect** skill's runners, in place of `arena runners`. A panel. | `deep, main` |
| `interrogate reviewers` | The **interrogate** skill's reviewers. A panel. | `deep, main` |
| `fast, mechanical, miners` | Trivial mechanical edits, `subagent-driven-development` mechanical tasks, transcript and artifact miners (`recall`, `automate-me`, `session-pickup`, `worktree-cleanup`, `runtime-forensics`, `trace-forensics`, `show-me-your-work`), event watchers (`autonomous-run`), and the **maintain-verification-skill** source wave. | `fast` |
| `researcher-lite, collectors` | `researcher-lite`, the **research** skill's Tier 1 to Tier 3 collectors, and the **why** skill's Wave 1 git and PR anchor collector. | `fast` |
| `researcher-mid` | `researcher-mid` standard subsystem and multi-source investigation. | `main` |
| `researcher-deep, planner, synthesizer` | `researcher-deep`, `research-planner`, and `research-synthesizer`, which also serves the **research-summary** skill. | `deep` |
| `arena synthesizer` | The **arena** skill's Phase D and Phase E base selection and code or design grafting, plus the **architect** skill's red-flag screening. | `deep` |
| `sdd reviewer` | The `subagent-driven-development` task reviewer and scoped re-reviewer. The escalated implementer and the final whole-branch reviewer use `hardest tasks` and `judgment and prose`. | `main` |
| `comment-sicko` | The `comment-sicko` agent's comment and workaround audit in the **no-comments** skill. | `main` |

A panel role's value is a list. One subagent runs per entry, alias entries included, so the list length sets the fan-out.

## Upstream model names

Upstream skills restored to verbatim wording may write Cursor model slugs. If a skill you restored to upstream wording names one, read it as a tier. `claude-opus-5-5-xhigh` is the `deep` tier, `grok-4.7-xhigh-fast` is the `main` tier, and the `magic-models.mdc` rule is the role file below.

## Reasoning level and speed

Where the harness exposes a reasoning-effort setting, the ladder is `max` > `xhigh` > `high` > `medium` > `low`. The role file's `# budget` line sets every role's starting level. The default budget is `large`, which is `xhigh`. Before each spawn, start from the role's level, raise it one step for the hardest or subtlest work, lower it one step for judgment and two or more for routine work. Where the harness exposes a fast speed variant, use it only when the job is urgent (CI or trunk is red, or a person is blocked on the result right now). Verification stays on the `swarm workers` role at its configured level and speed. Where the harness exposes neither setting, ignore this section.

## The role file

`/setup-magic` writes the role file. It is an always-applied rule, so its lines are normally already in context. If they are not, read the file. The [harness adapter](harness-adapter.md) names where it lives. The fallback copy in the protocol layout is `~/.agents/rules/magic-models.md`. The shape below spells out every role line, the four tier slots, and both directives.

```text
# magic model configuration. One line per role. Delete a line to fall back to the default tier.
# `inherit-parent` or `auto` leaves the model field out, so the role runs on the parent chat model.
# orchestrator: thin
# budget: large (xhigh)
orchestrator: <the parent chat model>
fast: <a fast model>
main: <a main model>
deep: <a deep model>
feature, refactoring: main
bug-fix: main
perf-issue: main
hillclimb: main
hardest tasks: deep
judgment and prose: deep
how explorer: main
how explainer: deep
why investigators: main
why synthesizer: deep
reflect tooling: main
reflect judgment, divergent, synthesizer: deep
swarm workers: main
arena runners: deep, <a model from another family>
arena cross-judge pool: deep, <a model from another family>
architect runners: deep, main
interrogate reviewers: deep, main
fast, mechanical, miners: fast
researcher-lite, collectors: fast
researcher-mid: main
researcher-deep, planner, synthesizer: deep
arena synthesizer: deep
sdd reviewer: main
comment-sicko: main
```

A value is one of:

- A tier name, `fast`, `main`, or `deep`.
- A model identifier the harness accepts for a subagent, exactly as the harness spells it.
- `inherit-parent` or `auto`.

A role with no line keeps its default tier. A line whose role is not in the table is from a retired role. Ignore it.

## Diversity

A panel is diverse only when its seats resolve to different model families. When the consumer's `deep` and `main` tiers are the same family, pin one seat of each panel to another family in the role file, or accept a same-family panel and say so in the reply. Agreement between two models of one family is weaker evidence than agreement across families. Judge selection compares against the `orchestrator:` line when the harness hides the parent model ID.

## Fallback

Never drop the model field as a first resort. A missing model runs a deep role on the parent chat's model, which is the weak-parent failure thin mode exists to avoid. Resolve the role's tier first, through its tier line, then `~/.agents/models.json`, then the harness's subagent default. Omit the model field only when the role resolves to `inherit-parent` or `auto`, or when the harness exposes no model field for subagents at all.

If the harness rejects the resolved model, fall back to the role's default tier and say so in the reply. Do not try other guesses. Never treat `inherit-parent` or `auto` as a rejected model.

On Claude Code, a model from another provider cannot be passed. Map the role's default tier to a Claude family before falling back to the parent model, with `opus` for `deep`, `sonnet` for `main`, and `haiku` for `fast`. A same-provider family alias such as `fable` passes through unchanged. `CLAUDE_CODE_SUBAGENT_MODEL` is the environment backstop for a spawn that carries no model field.
