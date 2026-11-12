---
description: "Generate a project-local verification skill that drives your app the way a user does, in any language, framework, or platform. Use for /create-verification-skill, \"make a control skill for this repo\", or when a project has no scripted way to prove UI/CLI/service behavior."
enabled: true
id: create-verification-skill
name: create-verification-skill
---

# Create a verification skill

Every serious project needs a scripted way to drive the real app and prove behavior, which means launch it, exercise a feature the way a user would, and capture evidence. This skill generates that as a project-local skill (`.agents/skills/verify-<app>/`; the harness adapter lists the other locations) tailored to the repo. You write the generator's output for the next agent, not for a human. It will be read cold, mid-task, by an agent that has never seen the app.

## How the work is dispatched

Wave 1 is the repo interview, run through the **how** skill on the `how explorer` role (`main`). It answers the surface, run, drive, observe, and isolate questions from the codebase.

Wave 2 authors the skill, as one depth-1 `magic-agent` on the `feature, refactoring` role (`main`), or on `judgment and prose` (`deep`) when the surface or evidence standard needs judgment. It writes `verify-<app>/` and its feature map from the Wave 1 answers.

Wave 3 proves the generated skill, as a fresh cold-start subagent on the `swarm workers` role that has never seen the authoring conversation. It follows the new skill exactly as the next agent would.

When the harness exposes no subagent tool, or `orchestrator` is `standard`, run the three waves inline in this session.

## 1. Interview the repo, not the user

Answer these from the codebase and only ask the user what you cannot observe.

- **Surface.** What does a user actually touch? A web UI, a CLI/TUI, a desktop app, an API, a mobile app, a library? A repo can have several; pick the primary one and note the rest.
- **Run.** How does the app start locally? Prefer the repo's own documented dev command (package scripts, Makefile, README quickstart). Note ports, env vars, seed data, auth.
- **Drive.** How can an agent interact with it programmatically? Existing harnesses first, such as Playwright/Cypress specs, expect scripts, PTY helpers, curl-able endpoints, or a debug port. Only then pick a generic recipe, such as browser/CDP for web and Electron, a tmux/PTY harness for CLI/TUI, or plain HTTP for services.
- **Observe.** What evidence can be captured? Screenshots, terminal transcripts, response bodies, logs, exit codes, DB state.
- **Isolate.** Can two instances run side by side (ports, data dirs, profiles)? If not, say so in the generated skill. Refusing to double-drive a shared instance beats corrupting the user's session.

If the checkout doesn't build or start as-is, fix that first (or report it precisely) before generating. A skill written against a broken base teaches wrong steps. When an irrelevant missing asset blocks startup (a static dir the API never serves, a sample config), the generated skill may create it, clearly marked as verification scaffolding, and remove it in cleanup.

## 2. Generate the skill

Hand Wave 2 the interview answers and have it write `.agents/skills/verify-<app>/SKILL.md` with YAML frontmatter (`name: verify-<app>` and a `description` that names the app, the surface, and when to reach for it. Without frontmatter the skill never registers) and these sections, each grounded in what the interview actually found (no placeholders left).

- **Launch.** The exact command that starts the app for verification, and how to tell it's ready (a log line, a prompt). Launch must reach a usable state from an empty data dir, including any migrations and seed data. Ready means usable, not just that a process answers. A database health check can pass while its init scripts are still running. Include teardown. For a short-lived CLI or TUI there is no server to keep alive. Launch means build the binary (or install deps) once, then start each drive in its own isolated PTY or tmux session.
- **Doctor.** One read-only check that answers "is this instance worth driving?", covering process up, right version/build, port owned by us, and auth valid. An agent runs this first whenever anything looks off.
- **Drive.** The harness recipe with real selectors/commands from this repo, not examples. Prefer stable handles (ARIA labels, data attributes, prompt strings, route paths) over coordinates and tab order.
- **Evidence.** What to capture for a proof and where it goes. State the proof standards. Exercise the real user path, not internal setters or test-only endpoints. Capture the action and the resulting state, not just the final screen. Verify side effects (files written, rows inserted, messages sent) alongside what's visible. Mocks belong only where a production boundary already isolates the external system. When the safe path is a dry-run or test mode, verify what it actually skips by observing (files, network, git refs) rather than trusting its name, since some dry-runs still touch the network or open a browser.
- **Cleanup.** How to tear down instances the run created. Never kill by process name; kill what you started. Cleanup removes instances and scratch state, never the evidence. Proof artifacts survive the teardown, in a location the skill names.
- **Helpers.** Any script the skill ships is executable and its invocation is shown in the skill body. A helper the reader has to reverse-engineer is not a helper.

## 3. Seed the feature map

Create `.agents/skills/verify-<app>/features/README.md` plus one file per user-facing feature you can identify (aim for the top 3-5 to start, from routes, commands, menus, or docs). Follow the shape in [`references/feature-map-example/`](references/feature-map-example/), with a README index and one file per feature. Each file answers, from the user's point of view, what the feature is, how to reach it, how to drive it with the harness, and what observable end state proves it works. The four H2s are `Sub-features`, `How to get to it (user POV)`, `Driving it with <harness>`, and `Gotchas`. If the seed data lacks a precondition that a journey needs, the journey reports a failure and the reason goes in that feature's `Gotchas`. Never weaken the journey to make it pass. The map is the repo's maintained verification source, and a proof that drives one convenient entry point is incomplete when the map lists others.

## 4. Prove the generated skill before handing it over

Wave 3 runs the new skill's own instructions end to end once. It launches, doctors, drives ONE mapped feature (one is enough, since the map exists so later runs can cover the rest), captures evidence, and cleans up. After cleanup, it confirms the evidence still exists at the named location. A cleanup that eats the proof fails this step. Fix what fails, and run the generated cleanup after every failed iteration too, so broken attempts don't strand processes and ports. A generated skill that was never executed is a draft, not a deliverable. If it was proved in a stand-in for the real target (a container in place of a fresh VM, a local stack in place of a remote one), list every setup step the stand-in did that the target will not. Those steps stay unverified until a run on the real target covers them.

## 5. Offer the maintenance loop

Point the user at `/maintain-verification-skill` for keeping the map honest as the app changes. Suggest a cadence only if they ask.
