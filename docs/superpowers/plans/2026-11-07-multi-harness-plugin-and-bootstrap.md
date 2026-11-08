# Multi-Harness Plugin Packaging and Always-Active Bootstrap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `.agents` natively installable and automatically active at session start across Claude Code, Codex, Cursor, OpenCode, and Pi using the `superpowers` multi-harness plugin architecture while preserving `./scripts/install.sh --target agents`.

**Architecture:** Add a lightweight bootstrap skill (`skills/using-poteto/SKILL.md`) paired with an always-applied routing rule (`rules/workflow-routing.md`), a 1-bullet pointer in `agents.kit.md`, and updated SDO (`"Use when..."`) triggers on `skills/poteto-mode/SKILL.md`. Deliver the bootstrap and skill catalog natively to all five harnesses via root plugin manifests (`.claude-plugin/`, `.cursor-plugin/`, `.codex-plugin/`, `.agents/plugins/`, `package.json`), a zero-fork polyglot `SessionStart` hook (`hooks/run-hook.cmd` + `hooks/session-start`), an OpenCode V1/V2 plugin (`.opencode/plugins/dot-agents.js` + `index.js`), and a Pi extension (`.pi/extensions/dot-agents.ts`).

**Tech Stack:** Bash (POSIX/Bash 3.2+ builtins, polyglot `.cmd`/`.sh`), Node.js ESM (`.js`/`.mjs` `node:test`), TypeScript (Pi extension API), Python 3 (`unittest` and `scripts/validate.sh`).

**Spec:** [Always-active kit research summary](../../research/always-active-kit.md)

## Global Constraints

- Zero third-party runtime dependencies in `package.json`; OpenCode and Pi plugins use only Node.js built-ins (`node:fs`, `node:path`, `node:url`).
- Preserve `./scripts/install.sh --target agents` behavior and `tests/test_install.py` expectations: `install.sh` copies only `skills/`, `agents/`, `rules/`, `agents.kit.md`, `LICENSE`, and `THIRD-PARTY-NOTICES.md` into `~/.agents/`.
- Every skill in `skills/<name>/SKILL.md` must have alphabetically sorted YAML frontmatter keys (`description`, `enabled`, `id`, `name`) and pass `./scripts/validate.sh`.
- Every rule in `rules/<name>.md` must have alphabetically sorted YAML frontmatter keys (`alwaysApply`, `description`), stay under 150 body words, and pass `tests/writing-rules.test.mjs`.
- Every line in `agents.kit.md` must be a single bullet (`- ...`) of at most 25 words with no headings, tables, or em dashes.
- No vendor model slugs, Cursor-specific subagent fields, or hardcoded forge CLIs may appear in `skills/`, `agents/`, `rules/`, or `agents.kit.md` outside the allowlisted `MAPPING_DOCS` in `scripts/validate.sh`.
- `hooks/run-hook.cmd` and `hooks/session-start` must execute with zero child-process forks on Unix, survive an empty `PATH=""`, ignore `SIGPIPE` on early-closed stdout, and emit only the active harness's JSON field (`additional_context` for Cursor, `hookSpecificOutput.additionalContext` for Claude Code, `additionalContext` for SDK/Copilot).
- `.codex-plugin/plugin.json` must set `"hooks": {}` (an empty object) so Codex does not fall back to auto-discovering `hooks/hooks.json` and prompting for hook approval on install.
- All repo hygiene gates (`./scripts/validate.sh`, `python3 -m unittest discover -s tests`, `node --test tests/*.test.mjs`, `typos`, `markdownlint-cli2`, `lychee`, `jscpd` `< 5%` duplication, `shellcheck`, `shfmt`) must pass.

## Review Focus

- **Child subagent recursion:** Delegated subagents (`poteto-agent`, `researcher-*`, SDD implementers/reviewers) receiving the controller bootstrap can restart design/planning loops instead of executing their assigned leaf task; mitigated via `<SUBAGENT-STOP>` in `skills/using-poteto/SKILL.md` and structural `session.parentID !== undefined` suppression in `.opencode/plugins/dot-agents.js` (tested in Task 3).
- **Claude Code double-injection:** Emitting both `additional_context` and `hookSpecificOutput.additionalContext` in `hooks/session-start` causes Claude Code to inject the bootstrap twice; pinned by mutually exclusive shape assertions in Task 2.
- **Broken or empty `PATH` on hook startup:** Claude Code can spawn `SessionStart` hooks with an empty `PATH` (`PATH=""`), breaking scripts that call `dirname` or `cat`; pinned by the `PATH=""` and `zsh`-fallback tests in Task 2.
- **OpenCode V2 single-skill schema rejection or prompt-cache invalidation:** One malformed skill throwing inside `ctx.skill.transform` disables the entire OpenCode V2 plugin if uncontained, and registering only `context` (omitting `compaction` or `generate`) invalidates the prompt cache prefix; pinned by tests in Task 3.
- **Pi stateless `context` handler dropping bootstrap after Turn 1:** Pi does not persist messages returned from `context` handlers into session history, so clearing an injection flag after Turn 1 drops the bootstrap on Turn 2+; pinned by the multi-prompt provider-request loop test in Task 3.

---

### Task 1: Always-Active Bootstrap Skill, Routing Rule, and SDO Triggers

**Files:**

- Create: `skills/using-poteto/SKILL.md`
- Create: `rules/workflow-routing.md`
- Modify: `agents.kit.md:1-4`
- Modify: `skills/poteto-mode/SKILL.md:1-6`
- Modify: `skills/poteto-mode/references/harness-adapter.md:1-63`
- Modify: `scripts/validate.sh:162-168`
- Modify: `tests/writing-rules.test.mjs:1-65`

**Interfaces:**

- Consumes: `scripts/validate.sh` frontmatter and cross-reference rules; `tests/writing-rules.test.mjs` rule and `agents.kit.md` assertions.
- Produces:
  - `skills/using-poteto/SKILL.md` (read by `hooks/session-start` in Task 2, `.opencode/plugins/dot-agents.js` and `.pi/extensions/dot-agents.ts` in Task 3)
  - `rules/workflow-routing.md` (`alwaysApply: true` rule for harnesses loading `rules/`)
  - Updated `skills/poteto-mode/references/harness-adapter.md` with `Cursor`, `Claude Code`, `Codex`, `OpenCode`, and `Pi` mappings.

- [ ] **Step 1: Add failing routing tests to `tests/writing-rules.test.mjs`**

Append a new `test(...)` block in `tests/writing-rules.test.mjs` asserting:

1. `rules/workflow-routing.md` exists, has sorted frontmatter keys `["alwaysApply", "description"]`, has `< 150` body words, and references `/poteto-mode`, `/research`, and `/proof-driven-development`.
2. `agents.kit.md` contains a bullet linking to `rules/workflow-routing.md` and every line in `agents.kit.md` is `<= 25` words.
3. `skills/using-poteto/SKILL.md` exists, has sorted frontmatter keys `["description", "enabled", "id", "name"]`, contains `<SUBAGENT-STOP>` and `<EXTREMELY-IMPORTANT>`, and links to `../poteto-mode/references/harness-adapter.md`.
4. `skills/poteto-mode/SKILL.md` frontmatter `description` starts with `"Use when"`.

- [ ] **Step 2: Run the test to verify it fails**

Run: `node --test tests/writing-rules.test.mjs`
Expected: FAIL with `ENOENT: no such file or directory, open '.../rules/workflow-routing.md'`

- [ ] **Step 3: Create `rules/workflow-routing.md`, `skills/using-poteto/SKILL.md`, and update `agents.kit.md`, `skills/poteto-mode/SKILL.md`, `skills/poteto-mode/references/harness-adapter.md`, and `scripts/validate.sh`**

- Write `rules/workflow-routing.md` (`< 150` body words):

```markdown
---
alwaysApply: true
description: Route engineering, research, and formal-proof tasks to /poteto-mode, /research, or /proof-driven-development before acting
---

# Workflow Routing

Before taking action on a task, load and follow the matching entry-point skill:

| Observable task signal | Entry-point skill |
| --- | --- |
| Writing, editing, debugging, refactoring, testing, reviewing, or shipping code, docs, or configuration | `/poteto-mode` |
| Investigating a codebase, comparing options, or answering how, why, or where questions across files, web, or MCP | `/research` |
| Writing or auditing formal proofs, loop invariants, state machines, or model-checked specifications | `/proof-driven-development` |
| Unsure which skill, playbook, or principle fits the request | `/poteto-help` |

## Exceptions (skip entry-point routing)

- The user explicitly names a narrower skill (load that skill instead).
- You were spawned as a subagent to execute a scoped subtask.
- The prompt is pure conversation with no repository, tool, or code action.
- The prompt is a single-fact lookup answerable in one file read or search call.
```

- Append to `agents.kit.md` (19 words, single bullet):

```markdown
- Route every task to its entry-point skill before acting; see [workflow-routing.md](rules/workflow-routing.md) for triggers and exceptions.
```

- Update `skills/poteto-mode/SKILL.md` line 2 `description`:

```yaml
description: Use when writing, editing, debugging, refactoring, reviewing, or shipping code, tests, docs, or config, or when running multi-step engineering workflows. Applies poteto's style for concise responses, deliberate subagents, unslopped prose, simple code, and verified work.
```

- Create `skills/using-poteto/SKILL.md` with sorted frontmatter (`description`, `enabled: true`, `id: using-poteto`, `name: using-poteto`), `<SUBAGENT-STOP>`, `<EXTREMELY-IMPORTANT>`, the routing table for `/poteto-mode`, `/research`, `/research-summary`, `/proof-driven-development`, and `/poteto-help`, the observable exceptions list, a Red Flags anti-rationalization table, and a Platform Adaptation section pointing to `../poteto-mode/references/harness-adapter.md`.
- Update `skills/poteto-mode/references/harness-adapter.md` to document **Codex** (`spawn_agent {fork_turns: "none"}`, `followup_task`, `wait_agent`) and **Pi** (load skills by reading `SKILL.md` with `read`, use `subagent` from `pi-subagents` when installed, track tasks in plan files or `TODO.md`).
- In `scripts/validate.sh:162-163`, add `rule_files` and `Path("agents.kit.md")` (when present) to `md_files` so step 3–6 link and banned-term checks also guard `rules/*.md` and `agents.kit.md`.

- [ ] **Step 4: Run validation and unit tests to verify they pass**

Run: `./scripts/validate.sh && node --test tests/writing-rules.test.mjs && python3 -m unittest discover -s tests`
Expected: PASS (`OK validation passed`, all node and python tests pass)

- [ ] **Step 5: Commit**

```bash
git add skills/using-poteto/SKILL.md rules/workflow-routing.md agents.kit.md skills/poteto-mode/SKILL.md skills/poteto-mode/references/harness-adapter.md scripts/validate.sh tests/writing-rules.test.mjs
git commit -m "feat(routing): add using-poteto bootstrap skill and workflow-routing rule"
```

---

### Task 2: Cross-Platform `SessionStart` Hook and Manifests for Claude Code, Cursor, and Codex

**Files:**

- Create: `hooks/run-hook.cmd`
- Create: `hooks/session-start`
- Create: `hooks/hooks.json`
- Create: `hooks/hooks-cursor.json`
- Create: `.claude-plugin/plugin.json`
- Create: `.claude-plugin/marketplace.json`
- Create: `.cursor-plugin/plugin.json`
- Create: `.codex-plugin/plugin.json`
- Create: `.agents/plugins/marketplace.json`
- Create: `tests/plugin-hooks-and-manifests.test.mjs`

**Interfaces:**

- Consumes: `skills/using-poteto/SKILL.md` from Task 1.
- Produces:
  - `hooks/run-hook.cmd` and `hooks/session-start` (executable `0755`)
  - `hooks/hooks.json` (Claude Code) and `hooks/hooks-cursor.json` (Cursor)
  - `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.cursor-plugin/plugin.json`, `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`.

- [ ] **Step 1: Write the failing test `tests/plugin-hooks-and-manifests.test.mjs`**

Create `tests/plugin-hooks-and-manifests.test.mjs` using `node:test` and `node:child_process` to assert:

1. `hooks/hooks.json` declares `SessionStart[0].hooks[0]` with `shell: "bash"`, `async: false`, `command: "\"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd\" session-start"`, and `powershell: "& \"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd\" session-start"`.
2. `hooks/hooks-cursor.json` declares `version: 1` and `hooks.sessionStart[0].command: "./hooks/run-hook.cmd session-start"`.
3. Running `hooks/session-start` and `hooks/run-hook.cmd session-start` with:
   - `CLAUDE_PLUGIN_ROOT=<repo>` emits **only** `{ hookSpecificOutput: { hookEventName: "SessionStart", additionalContext: "<EXTREMELY_IMPORTANT>..." } }` containing `using-poteto` content.
   - `CURSOR_PLUGIN_ROOT=<repo>` (even when `CLAUDE_PLUGIN_ROOT` is also set) emits **only** `{ additional_context: "<EXTREMELY_IMPORTANT>..." }`.
   - `COPILOT_CLI=1 CLAUDE_PLUGIN_ROOT=<repo>` emits **only** `{ additionalContext: "<EXTREMELY_IMPORTANT>..." }`.
   - `PATH=""` (empty `PATH`) still succeeds and emits valid JSON.
   - Bare filename invocation (`cd hooks && bash session-start` and `cd hooks && bash run-hook.cmd session-start`) and backslash path (`hooks\session-start`) resolve `skills/using-poteto/SKILL.md` without `"Error reading using-poteto skill"`.
   - Early-closed stdout (`bash hooks/session-start | :`) exits `0` with empty stderr.
4. `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.cursor-plugin/plugin.json`, `.codex-plugin/plugin.json`, and `.agents/plugins/marketplace.json` exist, parse as valid JSON, use `"name": "dot-agents"`, and `.codex-plugin/plugin.json` sets `"hooks": {}` (deepEqual to `{}`).

- [ ] **Step 2: Run the test to verify it fails**

Run: `node --test tests/plugin-hooks-and-manifests.test.mjs`
Expected: FAIL with `ENOENT: no such file or directory, open '.../hooks/hooks.json'`

- [ ] **Step 3: Implement `hooks/` and the Claude, Cursor, and Codex plugin manifests**

1. Create `hooks/run-hook.cmd` (`chmod +x`) using the polyglot batch/shell wrapper from `superpowers/hooks/run-hook.cmd` (locates Git for Windows `bash.exe` on Windows, uses `${BASH}` or falls back to `bash`/`zsh` on Unix with no subshell forks).
2. Create `hooks/session-start` (`chmod +x`) using pure bash builtins (`read -r -d ''`, `${s//old/new}` JSON escaping, `trap '' PIPE` `printf`) to read `${PLUGIN_ROOT}/skills/using-poteto/SKILL.md` and wrap it in:
   `<EXTREMELY_IMPORTANT>\nYou have dot-agents.\n\n**Below is the full content of your 'dot-agents:using-poteto' bootstrap skill. Follow it to route every task. For all other skills, use your platform's skill tool or read the skill's SKILL.md:**\n\n${using_poteto_escaped}\n</EXTREMELY_IMPORTANT>`
3. Create `hooks/hooks.json` and `hooks/hooks-cursor.json`.
4. Create `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` (`name: "dot-agents"`, `version: "0.2.0"`, `repository: "https://github.com/PhillipChaffee/.agents"`).
5. Create `.cursor-plugin/plugin.json` (`name: "dot-agents"`, `displayName: "dot-agents"`, `version: "0.2.0"`, `skills: "./skills/"`, `agents: "./agents/"`, `rules: "./rules/"`, `hooks: "./hooks/hooks-cursor.json"`).
6. Create `.codex-plugin/plugin.json` (`name: "dot-agents"`, `version: "0.2.0"`, `skills: "./skills/"`, `hooks: {}`, plus `interface` metadata) and `.agents/plugins/marketplace.json` (`name: "dot-agents-dev"`, `plugins: [{ name: "dot-agents", source: { source: "url", url: "./" }, policy: { installation: "AVAILABLE", authentication: "ON_INSTALL" }, category: "Developer Tools" }]`).

- [ ] **Step 4: Run tests to verify they pass**

Run: `node --test tests/plugin-hooks-and-manifests.test.mjs && python3 -m unittest discover -s tests && ./scripts/validate.sh`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add hooks/ .claude-plugin/ .cursor-plugin/ .codex-plugin/ .agents/plugins/marketplace.json tests/plugin-hooks-and-manifests.test.mjs
git commit -m "feat(plugins): add SessionStart hooks and Claude, Cursor, and Codex manifests"
```

---

### Task 3: OpenCode (V1 & V2) Plugin and Pi Package Extension

**Files:**

- Create: `lib/bootstrap-core.js`
- Create: `.opencode/plugins/dot-agents.js`
- Create: `index.js`
- Create: `.pi/extensions/dot-agents.ts`
- Create: `package.json`
- Create: `tests/opencode-and-pi-plugins.test.mjs`

**Interfaces:**

- Consumes: `skills/using-poteto/SKILL.md` from Task 1.
- Produces:
  - `lib/bootstrap-core.js` exporting `BOOTSTRAP_MARKER`, `extractAndStripFrontmatter(content)`, and `loadBootstrapContent(skillsDir, toolMapping, headerLine)` (shared so `.opencode/plugins/dot-agents.js` stays concise and `jscpd` duplication stays `< 5%`).
  - `.opencode/plugins/dot-agents.js` exporting `V1_MAPPING`, `V2_MAPPING`, `DotAgentsPlugin`, and `default { id: "dot-agents", server: DotAgentsPlugin, setup }`.
  - `index.js` re-exporting `default` from `./.opencode/plugins/dot-agents.js`.
  - `.pi/extensions/dot-agents.ts` exporting `default function dotAgentsPiExtension(pi: ExtensionAPI)`.
  - `package.json` declaring `"main": ".opencode/plugins/dot-agents.js"` and `"pi": { "extensions": ["./.pi/extensions/dot-agents.ts"], "skills": ["./skills"] }`.

- [ ] **Step 1: Write the failing test `tests/opencode-and-pi-plugins.test.mjs`**

Create `tests/opencode-and-pi-plugins.test.mjs` asserting:

1. **OpenCode V1:** `DotAgentsPlugin({ client, directory })` pushes `skills/` to `config.skills.paths` (and is a no-op when `config.skills` is an array), injects `BOOTSTRAP_MARKER` (`<EXTREMELY_IMPORTANT>\nYou have dot-agents.`) + `V1_MAPPING` into the first user message once, is idempotent on repeat calls, and skips injection when `client.session.get` returns a session with `parentID: "parent-1"`.
2. **OpenCode V2:** `default.setup(ctx)` registers all 74 skills via `ctx.skill.transform` with `{ id, name, description, path, content }`, survives a single rejected skill inside `draft.add` without aborting remaining skills or hook registration, registers the same handler on `context`, `compaction`, and `generate`, injects `BOOTSTRAP_MARKER` + `V2_MAPPING` once per root session, and skips child sessions (`parentID` set).
3. **Pi Extension & `package.json`:** `package.json` includes `"pi-package"` in `keywords`, `pi.skills: ["./skills"]`, and `pi.extensions: ["./.pi/extensions/dot-agents.ts"]`. Loading `.pi/extensions/dot-agents.ts` registers `session_start`, `session_compact`, and `context` (and zero `resources_discover` handlers), injects the bootstrap user message on every provider request across multiple prompts when history is not mutated in place, avoids duplicating when already present, and inserts after leading `compactionSummary` messages.

- [ ] **Step 2: Run the test to verify it fails**

Run: `node --test tests/opencode-and-pi-plugins.test.mjs`
Expected: FAIL with `ERR_MODULE_NOT_FOUND` for `.opencode/plugins/dot-agents.js`

- [ ] **Step 3: Implement `lib/bootstrap-core.js`, `.opencode/plugins/dot-agents.js`, `index.js`, `.pi/extensions/dot-agents.ts`, and `package.json`**

1. Implement `lib/bootstrap-core.js` with `BOOTSTRAP_MARKER = "<EXTREMELY_IMPORTANT>\nYou have dot-agents."`, `extractAndStripFrontmatter(content)`, and `loadBootstrapContent(skillsDir, toolMapping, preamble)`.
2. Implement `.opencode/plugins/dot-agents.js` importing `lib/bootstrap-core.js`, defining `V1_MAPPING` and `V2_MAPPING`, `isChildSession` with `CHILD_SESSION_CACHE_MAX = 512`, `DotAgentsPlugin` (V1), and `setup(ctx)` (V2).
3. Implement `index.js` (`export { default } from "./.opencode/plugins/dot-agents.js";`).
4. Implement `.pi/extensions/dot-agents.ts` with `session_start`, `session_compact`, and `context` handlers injecting the `using-poteto` bootstrap + `piToolMapping()` after any `compactionSummary` messages.
5. Create `package.json` (`name: "dot-agents"`, `version: "0.2.0"`, `type: "module"`, `main: ".opencode/plugins/dot-agents.js"`, `pi` field).

- [ ] **Step 4: Run unit tests and copy-paste check to verify they pass**

Run: `node --test tests/opencode-and-pi-plugins.test.mjs && python3 -m unittest discover -s tests`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add lib/bootstrap-core.js .opencode/plugins/dot-agents.js index.js .pi/extensions/dot-agents.ts package.json tests/opencode-and-pi-plugins.test.mjs
git commit -m "feat(plugins): add OpenCode V1/V2 plugin and Pi package extension"
```

---

### Task 4: Version Lockstep, Third-Party Attribution, Docs, and Hygiene Gate Verification

**Files:**

- Create: `.version-bump.json`
- Create: `tests/version-sync.test.mjs`
- Modify: `THIRD-PARTY-NOTICES.md:1-35`
- Modify: `README.md:1-100,260-310`
- Modify: `.gitignore:1-20`

**Interfaces:**

- Consumes: Manifests from Tasks 2 and 3 (`package.json`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.cursor-plugin/plugin.json`, `.codex-plugin/plugin.json`).
- Produces: `.version-bump.json`, `tests/version-sync.test.mjs`, updated `README.md` and `THIRD-PARTY-NOTICES.md`.

- [ ] **Step 1: Write the failing test `tests/version-sync.test.mjs`**

Create `tests/version-sync.test.mjs` asserting:

1. `.version-bump.json` exists and lists `package.json`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` (`plugins.0.version`), `.cursor-plugin/plugin.json`, and `.codex-plugin/plugin.json`.
2. Every file listed in `.version-bump.json` exists and carries the exact same semantic version string (`0.2.0`).
3. `THIRD-PARTY-NOTICES.md` documents the `obra/superpowers` plugin/bootstrap files (`hooks/`, `.opencode/`, `.pi/`).

- [ ] **Step 2: Run the test to verify it fails**

Run: `node --test tests/version-sync.test.mjs`
Expected: FAIL with `ENOENT: no such file or directory, open '.../.version-bump.json'`

- [ ] **Step 3: Create `.version-bump.json` and update `THIRD-PARTY-NOTICES.md`, `README.md`, and `.gitignore`**

- Create `.version-bump.json`:

```json
{
  "files": [
    { "path": "package.json", "field": "version" },
    { "path": ".claude-plugin/plugin.json", "field": "version" },
    { "path": ".claude-plugin/marketplace.json", "field": "plugins.0.version" },
    { "path": ".cursor-plugin/plugin.json", "field": "version" },
    { "path": ".codex-plugin/plugin.json", "field": "version" }
  ]
}
```

- Update `THIRD-PARTY-NOTICES.md` under the `Superpowers` section to include `hooks/run-hook.cmd`, `hooks/session-start`, `.opencode/plugins/dot-agents.js`, and `.pi/extensions/dot-agents.ts` adapted from `obra/superpowers` commit `22f0b463e7a5e579904dd6211a520321035526f7`.
- Update `README.md`:
  - Update top-level counts (`74 active skills`, `4 operational rules`).
  - Add a **Native Plugin Installation (Superpowers-Style)** table under Quick Start covering:
    - **Claude Code:** `/plugin marketplace add PhillipChaffee/.agents` then `/plugin install dot-agents@dot-agents-dev`
    - **Cursor:** `/add-plugin` from the repository (or `.cursor-plugin/plugin.json`)
    - **Codex CLI / App:** `/plugins` via `.agents/plugins/marketplace.json` (or `~/.agents/skills`)
    - **OpenCode (V1 & V2):** `"plugins": ["dot-agents@git+https://github.com/PhillipChaffee/.agents.git"]` in `opencode.json`
    - **Pi:** `pi install git:github.com/PhillipChaffee/.agents` (or `pi -e /path/to/.agents`)
    - **Raw `.agents` Protocol Home:** `./scripts/install.sh --target agents`
- Ensure `.gitignore` ignores `node_modules/` and `.opencode/node_modules/` without ignoring root `package.json`.

- [ ] **Step 4: Run the full validation and test suites**

Run: `./scripts/validate.sh && python3 -m unittest discover -s tests && node --test tests/*.test.mjs`
Expected: PASS across all validators, Python installer sandbox tests, and Node test suites.

- [ ] **Step 5: Commit**

```bash
git add .version-bump.json tests/version-sync.test.mjs THIRD-PARTY-NOTICES.md README.md .gitignore
git commit -m "docs(plugins): document multi-harness installation and lock manifest versions"
```
