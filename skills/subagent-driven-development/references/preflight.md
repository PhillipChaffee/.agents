# The Pre-flight Scan

Part of `/subagent-driven-development`. Run it once, before dispatching Task 1.

## Who runs it

Under `orchestrator: thin`, when the harness exposes a subagent tool, the scan
and its rulings are one depth-1 Adjudicator `magic-agent` on the
`judgment and prose` role (default `deep`) from the `magic-models` role file
(see `model-roles.md`). Give the Adjudicator this file, the plan, the spec
path, and the plan's `## Global Constraints`, and tell it to write the table
and its rulings into `<workspace>/progress.md`.

Run the scan yourself in this session when you are already inside a depth-1
leaf subagent, or when the harness exposes no subagent tool, or under
`orchestrator: standard`.

## The scan

Scan the plan once for conflicts, writing down what you checked as you check
it:

- tasks that contradict each other or the plan's Global Constraints
- anything the plan explicitly mandates that the review rules below treat as
  a defect (a test that asserts nothing, verbatim duplication of a logic
  block)

The scan returns a table, not a verdict. One row for every pair of tasks that
share a file or an interface: the two tasks, what one produces against what
the other consumes, and what you found. One row for every task: whether its
own text agrees with itself, the tests it specifies against the code it
specifies, the files it creates against the files it later touches. "The scan
is clean" without those rows is not a scan you ran.

## The rulings

Rule on everything the scan finds before execution begins, each finding
against the plan text that mandates it. The spec is the binding authority and
the plan is its argument. Record each ruling beside its row in
`<workspace>/progress.md` as

`Preflight: Ruling: <what you decided> — <why> — <what it costs if wrong>`

If the scan is clean, proceed without comment. The review loop remains the net
for conflicts that only emerge from implementation.
