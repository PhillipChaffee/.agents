# Opening a PR

Invoked at the end of every other playbook.

**Waves.** The root chat keeps this work as one depth-1 leaf. It dispatches a `magic-agent` on the `judgment and prose` line (default `deep`), or on `feature, refactoring` (default `main`) when the commit surgery needs code judgment, and that leaf owns the slop-strip, the dependency-ordered commit splitting, the `/make-pr-easy-to-review` pass, the `/technical-writing` and `/unslop` PR body, the forge open or edit call, and the final reply draft. Both role lines come from the `magic-models` role file. It returns the PR URL, the head SHA, and the draft. When a PR owner already runs as a depth-1 leaf, it executes these steps directly in its own session without spawning subagents or calling `/loop`.

The one step outside that leaf is the comment audit. The root chat dispatches `/no-comments` at depth 1 before review, which means a `comment-sicko` leaf in Wave 1 and a `bug-fix` or `feature, refactoring` leaf in Wave 2. The PR leaf never spawns `comment-sicko` itself, and the root chat relays the leaf's verified text without rewriting it.

**Worktree.** Work from a git worktree off main. Subagents inherit it. Multiple subagents on the same branch each get their own worktree, or `git fetch && git reset --hard origin/<branch>` between them. Dirty branch with unrelated work means patch it out, use a fresh worktree, and apply. Snarled worktree means reset from main and redo minimally.

**Commits.** Commit liberally. Rebase into small, ordered commits before opening PRs. Group commits in `/make-pr-easy-to-review` order, which is landable story order, data or core layer first and wiring after, and check `git rev-parse HEAD^{tree}` before and after a rewrite of an already-pushed branch so the tree is identical. Each commit is a future PR, landable and ordered to tell the story. Amend when the fix belongs in a just-made commit, and add a new commit when the work is separable. Commit bodies don't restate the subject.

**PRs.** The leaf runs `/clean-code` over the diff before commit (routing by language to strip AI code slop per the **principle-laziness-protocol** skill). It runs `/make-pr-easy-to-review` when opening a review-ready PR or MR, or right after opening or when updating an open PR or MR, so the description and reviewer guidance match the final diff, with core files separated from mechanical or generated files and the risky behavior, migration order, rollout plan, and test coverage called out. It writes every PR title, description, and commit body with `/technical-writing` (every layer except Diátaxis, and the STE vocabulary rules, one word per action, articles kept, a plain verb over `-ing` where one works), then applies `/unslop`.

**Titles.** Conventional Commits `type(scope): subject`, no trailing period. Type such as `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, or `perf`. Scope is the area, such as `magic` or `magic-mode`. Subject is short, imperative, and names a real symbol when one carries the change, for example `fix(magic): retarget opening-a-pr babysit trigger`.

**Descriptions.** The PR body is a one-minute briefing, not a lab notebook, for a reviewer who has the diff. It says why the change exists, what it leaves out, what it could break, and how you proved it works. Write short, simple sentences with few identifiers, no walls of text. The body becomes the squash commit body, so keep that commit under about 40 lines. Use `##` headings, not bold lead-ins, in this order, and drop a section with nothing to say:

- `## Why` covers the problem and approach in 1-3 short sentences, with no SHAs, rebase genealogy, or "based on main" preamble.
- `## What changed` is 1-3 short bullets. Name a real symbol or path only when it carries the change, and name both sides of a rename or retarget.
- `## Scope` is always present, 1-3 short items on what it covers and what it deliberately leaves out (a follow-up, a known gap). No symbols, paths, or file-by-file essay.
- `## Tradeoffs` covers only rejected alternatives a reviewer would otherwise ask about. Skip it when there was no real choice.
- `## Blast Radius` is 1-2 sentences on who or what it touches and why that is safe or risky. If main is red, state the cost of leaving it red.
- `## Verification` is 1-3 bullets, each a real run path and its outcome. Perf gets one primary number with its unit, `before → after`, and a link to the arena or swarm directory for the rest. No sample-size methodology, swarm recitals, or metric tables.

After the sections, attach videos or screenshots when they prove a claim. Full SHAs, swarm or arena lane recitals, lever-correction essays, file-by-file checklists, and "CLEAN" verdicts go in a linked artifact, not the body.

**Forge.** The root chat resolves the forge once from the repo's `docs/agents/issue-tracker.md` (or from `git remote -v` when that file is absent, and say which), keeps it for every PR operation, and passes it into the leaf brief.

**Size and stacks.** Prefer five narrow PRs to one large PR. A stack is a base-branch chain. The root PR targets trunk. Each child branch rebases onto its parent's exact tip and its PR targets the parent branch. As a parent merges, move its child onto trunk per `playbooks/shipping.md` step 4. Per the resolved forge, create a child against `<parent-branch>` (forge operation **open PR**), and retarget one to `<parent-branch>` (forge operation **edit PR**). Branch from trunk only for independent work. Rebase on trunk before substantial stack work.

**Readiness.** Open every PR ready, never as a draft. Pass the ready state on every creation call (forge operation **open PR**). If a PR still opens as a draft, mark it ready according to the resolved forge (forge operation **mark ready**). View the PR (forge operation **view PR**) before you refer to PR status.

**Babysit.** Opening a PR does not start a babysit. Post the URL and keep building. Finish the phase or stack first. Run a separate babysit pass only when the user asks for one after the whole stack exists. A babysit for each new PR stalls the build and spends checks on commits later waves restart. Push back when feedback drifts from intent.

A leaf that opens a PR returns to the parent without babysitting, unless it is an Autopilot-full or Autopilot-stack owner. That owner's brief assigns the babysit loop and is the ask `playbooks/babysit.md` waits for. The owner starts the loop after its code-ready report, reports merge-ready, and is exempt from the rules here and in `playbooks/babysit.md` that hold babysitting until a whole stack is built.
