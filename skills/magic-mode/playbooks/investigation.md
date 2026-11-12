# Investigation

**You own the answer. Plan, route, write.** Each heavy step is a flat depth-1 wave whose model comes from a role line in the `magic-models` role file.

Investigation requests are read-only. They produce a cited explanation or a recommendation, not a code change.

1. **Wave 1, ground.** Route through the `how` skill, whose `how explorer` and `how explainer` lines come from the `magic-models` role file. For motivation questions, also route through the `why` skill, whose `why investigators` and `why synthesizer` lines come from the same file. Pass `take-a-step-back` into the wave brief, so the explainer checks why the user is asking, whether the premise is off track, and what hidden constraint to flag.
2. **Wave 1 brief, the answer shape.** Pass these requirements into the same brief, so the explainer returns a ready-to-relay answer. Produce the `how`-shaped output (Overview / Key Concepts / How It Works / Where Things Live / Gotchas), or a recommendation with a tradeoffs table if the request is a decision between alternatives. If the evidence shows the user's premise is flawed, lead with that mismatch and redirect to what serves their goal. Apply `/unslop`, and use a table for any set of two or more parallel items.
3. When the question spans both mechanics and motivation, dispatch one `magic-agent` on `judgment and prose` (default `deep`) to synthesize the `how` and `why` reports instead of relaying two partial answers.
4. Throughput checkpoint stays one line, `throughput checkpoint: n/a, read-only investigation`.

No PR, no babysit, and no `architect` unless the investigation precedes a code change. If it does, hand back to the user and re-route to Bug fix or Feature.

**Reply.** Give the investigation output. For "are we sure?" answers, include your real judgment with reasons, and push back if the premise is wrong (see Autonomy).
