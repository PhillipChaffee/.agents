# Investigation

**You own the answer. Plan, route, write.**

Investigation requests are read-only. They produce a cited explanation or a recommendation, not a code change.

1. Route through the **how** skill. For motivation questions, also route through the **why** skill. Apply the **take-a-step-back** principle skill to check why the user is asking, whether their premise is off track, and what hidden constraint you should flag so the investigation serves their real goal.
2. Throughput checkpoint stays one line: `throughput checkpoint: n/a, read-only investigation`.
3. Produce the `how`-shaped output (Overview / Key Concepts / How It Works / Where Things Live / Gotchas), or a recommendation with a tradeoffs table if the request is a decision between alternatives. If the evidence shows the user's premise is flawed, lead with that mismatch and redirect to what serves their goal.
4. Apply the **unslop** skill to the reply.

No PR, no babysit, no `architect` unless the investigation precedes a code change. If it does, hand back to the user and re-route to Bug fix or Feature.

**Reply:** the investigation output. For "are we sure?" answers, include your real judgment with reasons. Push back if the premise is wrong (see Autonomy). When the investigation surfaces 2 or more findings, alternatives, or open questions for the user to decide on, mention `/one-at-a-time` so they can step through them one by one.
