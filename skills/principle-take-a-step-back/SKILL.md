---
description: "Use when starting any task, receiving grounding or research findings, crossing a phase boundary, or when tempted to execute a literal mechanism request, compare narrow options, or offer a fallback diff that may not serve the user's underlying goal."
enabled: true
id: principle-take-a-step-back
name: principle-take-a-step-back
---

# Take a Step Back

At the start of a task, after grounding or research findings return, and at every phase transition, step back from the immediate mechanics and check whether the current path actually serves the user's goal.

Fast execution on the wrong problem wastes the whole run. Users often ask for a specific mechanism to solve an unstated goal, or frame a request around an incomplete mental model of the system.

## Ask the six diagnostic questions

Ask these six questions at task entry and whenever new evidence arrives:

1. **Why is the user asking this?** Identify the concrete pain, failure, or decision that prompted the request.
2. **What is the goal?** State the end-to-end outcome that must hold when the work finishes.
3. **What do they actually want?** Separate the outcome the user needs from the specific mechanism, file, flag, or option list they named.
4. **Are they off track?** Check whether the request is an XY problem, targets the wrong layer, optimizes a negligible path, or chases a symptom.
5. **Is what we are doing actually going to serve that goal?** Check the codebase, runtime topology, and system limits to verify that completing the literal step will achieve the real outcome in production.
6. **Is there something they do not understand that I should flag?** If a system constraint, caller behavior, multi-replica topology, or existing mechanism means the thing you are investigating, researching, or building will not serve their goal, flag it clearly with evidence before going further.

```dot
digraph take_a_step_back {
    "Task start, grounding findings,\nor phase boundary" [shape=ellipse];
    "Does the requested path\nactually serve the user's goal?" [shape=diamond];
    "Proceed with execution" [shape=box];
    "Is the right fix clear,\nreversible, and in scope?" [shape=diamond];
    "Flag the mismatch with evidence,\nomit the broken diff, and ship the real fix" [shape=box];
    "STOP: Flag what the user missed with evidence,\nomit the broken diff, and present viable options" [shape=octagon, style=filled, fillcolor=red, fontcolor=white];

    "Task start, grounding findings,\nor phase boundary" -> "Does the requested path\nactually serve the user's goal?";
    "Does the requested path\nactually serve the user's goal?" -> "Proceed with execution" [label="yes"];
    "Does the requested path\nactually serve the user's goal?" -> "Is the right fix clear,\nreversible, and in scope?" [label="no (off track)"];
    "Is the right fix clear,\nreversible, and in scope?" -> "Flag the mismatch with evidence,\nomit the broken diff, and ship the real fix" [label="yes"];
    "Is the right fix clear,\nreversible, and in scope?" -> "STOP: Flag what the user missed with evidence,\nomit the broken diff, and present viable options" [label="no (needs product or threat-model choice)"];
}
```

## Redirect when the path is off track

1. **Lead with the mismatch and the evidence.** State plainly in the first paragraph why the requested mechanism, research comparison, or proof target will not achieve the user's goal. Cite the exact files, lines, numbers, or docs that prove it.
2. **Explain what the user could not see.** Name the hidden constraint, such as multi-pod state, an upstream proxy, a build behavior, or an existing database constraint, that invalidates the literal request.
3. **Redirect to what actually serves the goal.**
   - If the right fix is clear, reversible, and in scope, implement or research the approach that actually solves the goal.
   - If the right fix requires a product, architecture, or threat-model decision that only the human can make, stop before writing broken code and present the viable options.
4. **Never include an appeasement diff or broken config.** Do not bolt a dead mechanism onto the real fix just because the prompt named it. Do not provide a ready-to-paste "Option B" diff or config snippet for an approach you just proved is broken, unsafe, or a no-op.

## Check alignment at three points

| Checkpoint | Trigger | Required action |
| --- | --- | --- |
| **Task start** | User names a specific mechanism, flag, tool, or narrow option list | Separate the underlying goal from the named mechanism before executing |
| **Post-grounding** | `how`, `why`, reproduction, or collector research returns | Re-check whether the requested path still serves the goal given the real system shape |
| **Mid-run and pre-ship** | A test or proxy predicate turns green, or scope grows | Verify that passing the check actually solves the user's production problem |

## Example of catching a multi-pod blind spot

A user asks to add a 60-second in-memory `Map` cache to `getUserPermissions(userId)` in `src/auth/permissions.ts`.

- **Without this principle.** The agent writes the `Map` cache, adds unit tests, and adds a footnote at the bottom noting that `deploy/k8s.yaml` runs 8 replicas so `revokeUserAccess(userId)` will leave revoked users active on the other 7 pods for 60 seconds.
- **With this principle.** Stepping back after reading `src/auth/revoke.ts` and `deploy/k8s.yaml` shows that a process-local cache breaks access revocation across the 8 pods. The agent stops before shipping the broken in-memory cache, flags the 8-replica revocation hazard up front with `file:line` citations, and presents the real options, such as a shared Redis cache with eviction on revoke or keeping the indexed database read.

## Common rationalizations

| Excuse | Reality |
| --- | --- |
| "The user asked to compare or configure these exact files, so I should answer literally first." | Writing 200 lines of configuration for an approach that breaks the system is malicious compliance. Flag the flawed premise first and redirect. |
| "I will ship the requested diff and mention the multi-pod or scale failure in a caveat." | Burying a fatal flaw in a footnote while handing over a broken diff causes the user to merge broken code. Stop and surface the blocker at the top. |
| "I will provide Option A with the real fix and Option B with the literal broken diff they asked for." | Offering a ready-to-copy diff that you just proved fails, corrupts data, or does nothing at runtime invites the user to ship a bug. Omit the broken diff. |
| "`Never Block on the Human` says to proceed and let the human course-correct." | [Never Block on the Human](../principle-never-block-on-the-human/SKILL.md) governs reversible implementation choices when the goal is sound. It never authorizes building a mechanism that fails the user's goal. |

## Red flags that mean stop and step back

- You are writing code or configuration that you already know will fail in production, break another harness, or do nothing at runtime.
- You are drafting an "Option B" fallback diff for a mechanism the evidence ruled out.
- You are burying an architectural blocker under "Gotchas", "Open questions", or "Gaps" at the bottom of the reply.
- A local test predicate passed, but production scale, deployment topology, or an upstream limit means the user's problem is still broken.

## Boundaries with related principles

- Distinct from [Never Block on the Human](../principle-never-block-on-the-human/SKILL.md), which says not to pause on reversible implementation details when the approach serves the goal. When the premise itself is off track, flagging the mismatch is mandatory.
- Distinct from [Attack the Premise](../principle-attack-the-premise/SKILL.md), which tests a technical hypothesis after two fixes fail a gate. This principle runs from turn one and at every phase transition, even when every gate is green.
- Distinct from [Redesign from First Principles](../principle-redesign-from-first-principles/SKILL.md), which reshapes code around a valid requirement. This principle questions whether the requirement or investigation itself serves the user's goal.
