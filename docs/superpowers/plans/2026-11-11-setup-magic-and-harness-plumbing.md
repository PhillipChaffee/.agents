# Setup Magic and Multi-Harness Plumbing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Overhaul `/setup-magic`, `model-roles.md`, `harness-adapter.md`, and the five harness plugins and manifests so every kit agent (`7`), operational rule (`5`), model role (`22` plus `4` tier slots), `~/.agents/models.json` tier, and repository forge tracker (`docs/agents/issue-tracker.md`) loads and resolves cleanly without manual wiring.

**Architecture:** We extend the consumer-local `magic-models` contract with `# orchestrator: thin | standard`, `# budget`, top-level `orchestrator` / `fast` / `main` / `deep` tier lines (synced into `~/.agents/models.json`), and grouped role overrides covering `/research`, `fast` miners, `arena synthesizer`, `SDD`, and `comment-sicko`. We wire `.opencode/plugins/magic.js`, `.pi/extensions/magic.ts`, `package.json`, `.claude-plugin/plugin.json`, and `hooks/session-start` to register named agents and inject rules + `magic-models` automatically, and split `/setup-magic` into Scope 1 (User & Harness Global) and Scope 2 (Repo Onboarding, including `docs/agents/issue-tracker.md` scaffolding).

**Tech Stack:** Node.js ESM (`node:test`), TypeScript (`.pi/extensions/magic.ts`), Bash (`hooks/session-start`, `scripts/install.sh`, `scripts/validate.sh`), Python 3 (`unittest`), Markdown (`SKILL.md`, `agent.md`, JSON manifests).

**Spec:** `docs/research/thin-orchestrator-and-setup-magic.md`

## Global Constraints

- Zero runtime npm dependencies (`package.json` `dependencies` and `devDependencies` must remain `undefined`; `tests/opencode-and-pi-plugins.test.mjs:274-275`).
- Zero vendor model pins, Cursor-only fields, or hardcoded forge CLIs in kit skills/agents/rules (`docs/adr/0001-no-model-pins.md`, `docs/adr/0007-forge-agnostic.md`, `scripts/validate.sh:152-158`).
- Keep `agents/<id>/agent.md` directory layout and sorted YAML frontmatter keys (`connection-type`, `description`, `enabled`, `id`, `name`, `readonly`, `role`; optional `disallowedTools` sorted alphabetically after `description`).
- Keep skill count at `75` and operational rule count at `5` (`tests/opencode-and-pi-plugins.test.mjs:157`, `tests/writing-rules.test.mjs:38-55`).
- `hooks/session-start` must spawn zero child processes (`fork`/`clone`) and survive an empty `PATH` and closed stdout (`tests/plugin-hooks-and-manifests.test.mjs:89-155`).
- Write files larger than ~300 lines in `<= 300`-line chunks and verify with `wc -l` (`rules/large-file-creation.md`).
- Zero em-dashes or en-dashes and zero mid-sentence colons in prose (`skills/technical-writing/SKILL.md`, `skills/unslop/SKILL.md`).

## Review Focus

1. **Missing or malformed consumer `magic-models` file at session start:** `.opencode/plugins/magic.js`, `.pi/extensions/magic.ts`, and `hooks/session-start` must treat missing `~/.config/opencode/rules/magic-models.md` / `~/.agents/rules/magic-models.md` / `~/.claude/rules/magic-models.md` as a clean no-op without throwing or emitting stderr warnings.
2. **OpenCode V2 `#variant` suffix parsing (`provider/model#high`):** Role parser in `lib/bootstrap-core.js` and `/setup-magic` Step 4 validation must preserve `#<variant>` suffixes on OpenCode model IDs instead of stripping `#...` as an inline comment.
3. **Child subagent bootstrap suppression:** `.opencode/plugins/magic.js` must still skip `using-magic` root bootstrap injection on child sessions (`session.parentID !== undefined`), while registered `ctx.agent.transform` subagents receive their own `agent.md` prompt cleanly.
4. **Zero-fork `hooks/session-start` rule loading:** Appending `rules/*.md` in `hooks/session-start` for Claude Code / Copilot CLI must use pure bash builtins (`for r in "${PLUGIN_ROOT}"/rules/*.md`, `read -r -d ''`), never `cat`, `ls`, or `$(...)` subshells, and must skip `rules/*.md` when `CURSOR_PLUGIN_ROOT` is set (since `.cursor-plugin/plugin.json` already loads `"rules": "./rules/"`).
5. **Read-only enforcement on `research-planner` and `research-synthesizer`:** Both `readonly: true` agents must declare `disallowedTools` in frontmatter (for Claude Code) and edit/write deny permissions in `.opencode/plugins/magic.js` `ctx.agent.transform` so neither agent can mutate repo files.

---

## File Structure

- Modify: `lib/bootstrap-core.js` to add `loadKitRules`, `loadMagicModelsRule`, `parseMagicModels`, and `loadKitAgents`.
- Modify: `.opencode/plugins/magic.js` to restore `todowrite` and `subagent` `model` guidance in `V2_MAPPING`, register all 7 `agents/*/agent.md` subagents via `ctx.agent.transform` and `config.agent`, and inject `rules/*.md` plus `magic-models.md` on root sessions.
- Modify: `.pi/extensions/magic.ts` and `package.json` to add `pi.subagents.agents` and inject `rules/*.md` plus `magic-models.md` in Pi context bootstrap.
- Modify: `.claude-plugin/plugin.json`, `hooks/session-start`, `agents/research-planner/agent.md`, and `agents/research-synthesizer/agent.md` to add explicit `"agents"` paths, add `disallowedTools` on readonly agents, and zero-fork load `rules/*.md` in `hooks/session-start`.
- Modify: `skills/magic-mode/references/harness-adapter.md`, `skills/magic-mode/references/model-roles.md`, `skills/setup-magic/SKILL.md`, and `scripts/install.sh` to add `# orchestrator: thin | standard` (default `thin`), tier-first slots (`orchestrator`, `fast`, `main`, `deep`), 22 grouped roles, real auto-load paths, `~/.agents/models.json` sync, and Scope 1 (Global) plus Scope 2 (Repo Onboarding).
- Create: `skills/setup-magic/references/issue-tracker-templates.md`, `docs/agents/issue-tracker.md`, `tests/setup-magic-and-roles.test.mjs`.

---

### Task 1: Shared Rule, Agent, and `magic-models` Loader in `lib/bootstrap-core.js`

**Files:**

- Modify: `lib/bootstrap-core.js:1-55`
- Test: `tests/opencode-and-pi-plugins.test.mjs`

**Interfaces:**

- Consumes: `node:fs`, `node:path`.
- Produces:
  - `loadKitRules(rulesDir: string): string`
  - `parseMagicModels(raw: string): { orchestratorMode: "thin" | "standard", budget: string | null, roles: Record<string, string> }`
  - `loadMagicModelsRule(candidatePaths: string[]): { path: string, raw: string, parsed: ReturnType<typeof parseMagicModels> } | null`
  - `loadKitAgents(agentsDir: string): Array<{ id: string, name: string, description: string, readonly: boolean, prompt: string, path: string }>`
  - `loadBootstrapContent(skillsDir, toolMapping, preamble, extraSections = [])`

- [ ] **Step 1: Write the failing test in `tests/opencode-and-pi-plugins.test.mjs`**

```javascript
test("lib/bootstrap-core.js loads kit rules, 7 kit agents, and parses magic-models keeping #variant suffixes", async (t) => {
	const core = await importFresh(corePath);
	assert.match(core.loadKitRules(path.join(repoDir, "rules")), /# Workflow Routing/);
	assert.equal(core.loadKitRules(path.join(repoDir, "missing-rules")), "");

	const agents = core.loadKitAgents(path.join(repoDir, "agents"));
	assert.equal(agents.length, 7);
	assert.equal(agents.find((a) => a.id === "research-planner").readonly, true);
	assert.equal(agents.find((a) => a.id === "magic-agent").readonly, false);

	const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "magic-models-"));
	t.after(() => fs.rmSync(tmp, { recursive: true, force: true }));
	const p = path.join(tmp, "magic-models.md");
	fs.writeFileSync(
		p,
		"---\nalwaysApply: true\ndescription: models\n---\n# orchestrator: thin\n# budget: large (xhigh)\nmain: provider/workhorse#medium\nresearcher-lite, collectors: fast\narena runners: a/b#high, c/d#max\n",
	);
	assert.equal(core.loadMagicModelsRule([path.join(tmp, "missing.md")]), null);
	const loaded = core.loadMagicModelsRule([p]);
	assert.equal(loaded.parsed.orchestratorMode, "thin");
	assert.equal(loaded.parsed.budget, "large (xhigh)");
	assert.equal(loaded.parsed.roles["main"], "provider/workhorse#medium");
	assert.equal(loaded.parsed.roles["arena runners"], "a/b#high, c/d#max");
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test tests/opencode-and-pi-plugins.test.mjs`
Expected: FAIL with `core.loadKitRules is not a function`

- [ ] **Step 3: Implement loaders and parser in `lib/bootstrap-core.js`**

Strip optional YAML frontmatter in `parseMagicModels` before parsing `# orchestrator:` (default `"thin"` when absent, `"standard"` when explicit) and `# budget:`, and split `<role>: <value>` on the first `:` without stripping `#variant` suffixes inside `<value>`. Keep `loadBootstrapContent` cache-hit behavior when `extraSections.length === 0`.

- [ ] **Step 4: Run test to verify it passes**

Run: `node --test tests/opencode-and-pi-plugins.test.mjs`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add lib/bootstrap-core.js tests/opencode-and-pi-plugins.test.mjs
git commit -m "feat(bootstrap): add kit rules, agents, and magic-models loaders"
```

---

### Task 2: OpenCode V1/V2 Agent Registration, `V2_MAPPING` Fix, and Rules/`magic-models` Injection

**Files:**

- Modify: `.opencode/plugins/magic.js:10-209`
- Test: `tests/opencode-and-pi-plugins.test.mjs`

**Interfaces:**

- Consumes: `loadKitRules`, `loadKitAgents`, `loadMagicModelsRule` from `lib/bootstrap-core.js`.
- Produces:
  - Updated `V2_MAPPING` restoring `todowrite` and instructing OpenCode to pass `agent: "<id>"` for registered kit subagents and `model: "providerID/modelID#variant"` from user-configured `magic-models` entries.
  - `resolveAgentModel(agentId: string, parsed: ReturnType<typeof parseMagicModels> | null): string | undefined`
  - V2 `ctx.agent.transform` registration of all 7 kit agents (`mode: "subagent"`, `permission: { edit: "deny", write: "deny" }` when `readonly`), plus V1 `config.agent` registration and root-session injection of `rules/*.md` + `magic-models.md` (`OPENCODE_CONFIG_DIR/rules/magic-models.md`, `~/.config/opencode/rules/magic-models.md`, `~/.agents/rules/magic-models.md`).

- [ ] **Step 1: Write the failing tests in `tests/opencode-and-pi-plugins.test.mjs`**

Add assertions verifying `V2_MAPPING` names `todowrite` and `model`, `ctx.agent.transform` updates all 7 kit agents with `mode: "subagent"` and readonly deny permissions, `resolveAgentModel` binds `provider/model#variant` from a temp `magic-models.md` while omitting `inherit-parent`/`auto`, and root bootstrap injects `# Workflow Routing` while child sessions still skip bootstrap.

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test tests/opencode-and-pi-plugins.test.mjs`
Expected: FAIL on `V2_MAPPING` `todowrite` check and missing `ctx.agent.transform` registration.

- [ ] **Step 3: Implement OpenCode V1/V2 agent registration and rule injection in `.opencode/plugins/magic.js`**

Keep `ctx.agent?.transform` optional so existing minimal V2 mock contexts continue passing without changes.

- [ ] **Step 4: Run test to verify it passes**

Run: `node --test tests/opencode-and-pi-plugins.test.mjs`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add .opencode/plugins/magic.js tests/opencode-and-pi-plugins.test.mjs
git commit -m "feat(opencode): register 7 kit subagents, restore todowrite, and inject rules"
```

---

### Task 3: Claude Code, Cursor, and Pi Agent Discovery & Zero-Fork Rule Injection

**Files:**

- Modify: `.claude-plugin/plugin.json:1-20`
- Modify: `agents/research-planner/agent.md:1-13`
- Modify: `agents/research-synthesizer/agent.md:1-13`
- Modify: `hooks/session-start:22-88`
- Modify: `package.json:17-24`
- Modify: `.pi/extensions/magic.ts:13-49`
- Test: `tests/plugin-hooks-and-manifests.test.mjs`, `tests/opencode-and-pi-plugins.test.mjs`

**Interfaces:**

- Consumes: `loadKitRules`, `loadMagicModelsRule` from `lib/bootstrap-core.js` (in Pi); pure bash builtins in `hooks/session-start`.
- Produces:
  - `.claude-plugin/plugin.json` `"agents"` array with sorted paths `["./agents/comment-sicko/agent.md", "./agents/magic-agent/agent.md", "./agents/research-planner/agent.md", "./agents/research-synthesizer/agent.md", "./agents/researcher-deep/agent.md", "./agents/researcher-lite/agent.md", "./agents/researcher-mid/agent.md"]`.
  - Sorted `disallowedTools` frontmatter key (`connection-type`, `description`, `disallowedTools`, `enabled`, `id`, `name`, `readonly`, `role`) on `research-planner` (blocking all tools) and `research-synthesizer` (blocking `"Edit"`, `"MultiEdit"`, `"NotebookEdit"`, `"Write"`).
  - Zero-fork `rules/*.md` injection in `hooks/session-start` when `CURSOR_PLUGIN_ROOT` is empty (also updating backslash-path symlink setup in `tests/plugin-hooks-and-manifests.test.mjs:116-119` to symlink `rules`).
  - `package.json` `"pi.subagents": { "agents": ["./agents"] }` and Pi context rule + `magic-models.md` injection (`~/.pi/agent/rules/magic-models.md`, `~/.agents/rules/magic-models.md`).

- [ ] **Step 1: Write the failing tests in `tests/plugin-hooks-and-manifests.test.mjs` and `tests/opencode-and-pi-plugins.test.mjs`**

Assert `claudePlugin.agents` has all 7 paths, `pkg.pi.subagents` equals `{ agents: ["./agents"] }`, Claude/Copilot `session-start` output contains `# Workflow Routing` while `CURSOR_PLUGIN_ROOT` output omits duplicate `rules/*.md`, and Pi context bootstrap contains `# Workflow Routing`.

- [ ] **Step 2: Run tests to verify they fail**

Run: `node --test tests/plugin-hooks-and-manifests.test.mjs tests/opencode-and-pi-plugins.test.mjs`
Expected: FAIL on missing `claudePlugin.agents`, `pkg.pi.subagents`, and `# Workflow Routing`.

- [ ] **Step 3: Implement manifest, agent frontmatter, `hooks/session-start`, and Pi extension updates**

Use pure bash `for rule_md in "${PLUGIN_ROOT}"/rules/*.md` and `IFS= read -r -d ''` in `hooks/session-start` so `strace` fork count remains zero and empty `PATH` tests pass.

- [ ] **Step 4: Run tests, shellcheck, and validator**

Run: `node --test tests/plugin-hooks-and-manifests.test.mjs tests/opencode-and-pi-plugins.test.mjs && ./scripts/validate.sh`
Expected: PASS with 0 errors and 0 new warnings.

- [ ] **Step 5: Commit**

```bash
git add .claude-plugin/plugin.json agents/research-planner/agent.md agents/research-synthesizer/agent.md hooks/session-start package.json .pi/extensions/magic.ts tests/plugin-hooks-and-manifests.test.mjs tests/opencode-and-pi-plugins.test.mjs
git commit -m "feat(plugins): wire 7 named agents and auto-load rules across Claude, Cursor, and Pi"
```

---

### Task 4: Expand `model-roles.md` and `harness-adapter.md` for Thin Orchestration and All 22 Roles

**Files:**

- Modify: `skills/magic-mode/references/harness-adapter.md:9-63`
- Modify: `skills/magic-mode/references/model-roles.md:1-71`
- Modify: `scripts/install.sh:132-158`
- Create: `tests/setup-magic-and-roles.test.mjs`

**Interfaces:**

- Produces:
  - `harness-adapter.md`: adds `Max portable subagent depth: 1 (parent -> leaf subagents; never rely on subagents spawning subagents)` row; fixes Claude Code cross-provider fallback to map tier defaults to `opus` (`deep`), `sonnet` (`main`), `haiku` (`fast`) instead of omitting `model`; fixes OpenCode `subagent`, `skill`, and `todowrite` V2 mapping and sets OpenCode `magic-models` path to `~/.config/opencode/rules/magic-models.md` (with per-profile `magic-models-<profile>.md` note), Cursor `.mdc` frontmatter note, Codex `~/.codex/config.toml` (`multi_agent = true`, `default_subagent_model`) + `~/.codex/agents/<id>.toml`, and Pi `~/.pi/agent/rules/magic-models.md` + `pi-subagents`.
  - `model-roles.md`: documents `# orchestrator: thin | standard` (default `thin`), top-level `orchestrator`, `fast`, `main`, `deep` tier lines, `~/.agents/models.json` sync, and the 22 canonical role lines (`15` existing roles plus `fast, mechanical, miners: fast`, `researcher-lite, collectors: fast`, `researcher-mid: main`, `researcher-deep, planner, synthesizer: deep`, `arena synthesizer: deep`, `sdd reviewer: main`, `comment-sicko: main`, while widening `arena cross-judge pool` to cover `/interrogate`, `eval.md`, `show-me-your-work`, `figure-it-out`, `orchestrate` and `autopilot-full` verifiers, and `PDD` spec audit).
  - `scripts/install.sh`: updates interactive `models.json` prompt copy and writes `"orchestrator"` alongside `"fast"`, `"main"`, `"deep"` when interactive.

- [ ] **Step 1: Write the failing test in `tests/setup-magic-and-roles.test.mjs`**

```javascript
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";

const repoDir = path.resolve(import.meta.dirname, "..");

test("model-roles.md and harness-adapter.md define orchestrator mode, tier-first slots, all 22 roles, depth-1 limit, and real auto-load paths", () => {
	const roles = fs.readFileSync(
		path.join(repoDir, "skills/magic-mode/references/model-roles.md"),
		"utf8",
	);
	for (const required of [
		"# orchestrator: thin",
		"orchestrator:",
		"fast:",
		"main:",
		"deep:",
		"fast, mechanical, miners",
		"researcher-lite, collectors",
		"researcher-mid",
		"researcher-deep, planner, synthesizer",
		"arena synthesizer",
		"sdd reviewer",
		"comment-sicko",
		"arena cross-judge pool",
	]) {
		assert.ok(roles.includes(required), `model-roles.md missing: ${required}`);
	}

	const adapter = fs.readFileSync(
		path.join(repoDir, "skills/magic-mode/references/harness-adapter.md"),
		"utf8",
	);
	assert.match(adapter, /depth\s*=\s*1|Max portable subagent depth/i);
	assert.ok(adapter.includes("~/.config/opencode/rules/magic-models.md"));
	assert.match(adapter, /opus.*sonnet.*haiku|haiku.*sonnet.*opus/is);
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test tests/setup-magic-and-roles.test.mjs`
Expected: FAIL on missing `# orchestrator: thin` and `researcher-lite, collectors`.

- [ ] **Step 3: Update `harness-adapter.md`, `model-roles.md`, and `scripts/install.sh`**

Apply `/technical-writing` and `/unslop` (zero em-dashes, zero mid-sentence colons). Ensure fallback rules in `model-roles.md` resolve `~/.agents/models.json` tiers before ever omitting `model`.

- [ ] **Step 4: Run tests and validator**

Run: `node --test tests/setup-magic-and-roles.test.mjs && python3 -m unittest discover -s tests && ./scripts/validate.sh`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add skills/magic-mode/references/harness-adapter.md skills/magic-mode/references/model-roles.md scripts/install.sh tests/setup-magic-and-roles.test.mjs
git commit -m "feat(models): expand model-roles and harness-adapter for thin orchestrator and all roles"
```

---

### Task 5: Overhaul `/setup-magic` into Scope 1 (Global Harness & Tier-First Models) + Scope 2 (Repo Onboarding & `issue-tracker.md`)

**Files:**

- Modify: `skills/setup-magic/SKILL.md:1-76`
- Create: `skills/setup-magic/references/issue-tracker-templates.md`
- Create: `docs/agents/issue-tracker.md`
- Modify: `rules/new-repo-setup.md:19-25`
- Modify: `docs/magic-guide/01-setup.md:1-66`
- Test: `tests/setup-magic-and-roles.test.mjs`

**Interfaces:**

- Consumes: `skills/magic-mode/references/model-roles.md`, `skills/magic-mode/references/harness-adapter.md`, `skills/magic-mode/references/forge-operations.md`.
- Produces:
  - `skills/setup-magic/SKILL.md` with sorted frontmatter (`description`, `name`) and two selectable scopes:
    - **Scope 1 (User & Harness Global):** (1) Detect harness, available models, and existing `magic-models` / `~/.agents/models.json`; on OpenCode, default to shared `~/.config/opencode/rules/magic-models.md` and note that per-profile `magic-models-<profile>.md` files can be written when profile overlays (`personal`, `work-dev`, `work-prod`) have distinct provider entitlements. (2) Ask 5 core prompts: Orchestrator mode (`thin` recommended default vs. `standard`), Reasoning budget (`unlimited`, `large`, `medium`, `small`), Core tier models (`orchestrator`, `fast`, `main`, `deep`), Optional cross-family secondary model for panels/judges, and Confirm or customize individual roles. (3) Validate base model IDs while preserving `#<variant>` (OpenCode), `[effort=...]` (Cursor), family aliases + `effort` (Claude Code), and `reasoning_effort` (Codex); warn if `thin` mode leaves `main`/`deep` roles on `inherit-parent`/`auto`. (4) Write `magic-models` at the harness's real auto-loaded path (including `alwaysApply: true` YAML frontmatter for `.mdc` / rule files), sync `~/.agents/models.json`, and run the Harness Doctor (Codex `multi_agent = true` + `~/.codex/agents/*.toml`, Claude `CLAUDE_CODE_SUBAGENT_MODEL`, Pi `pi-subagents` check).
    - **Scope 2 (Repository Onboarding, runnable standalone in new repos without re-prompting Scope 1):** (1) Auto-detect forge & tracker from `git remote -v` + installed CLIs/MCPs and offer to scaffold `docs/agents/issue-tracker.md` from `references/issue-tracker-templates.md` covering both issue operations and all 16 `forge-operations.md` PR/MR operations. (2) Offer `CONTEXT.md` + `docs/adr/` stubs if absent. (3) On greenfield repos, check `init-<lang>-repo` gates per `rules/new-repo-setup.md`. (4) Offer `/create-verification-skill` and `/create-formal-verification-skill`.
  - `docs/agents/issue-tracker.md` for this repository (`PhillipChaffee/magic`, GitHub Issues + GitHub PRs via `gh` CLI or GitHub MCP; note `scripts/validate.sh` skips `docs/` so `gh` commands are allowed in `docs/agents/issue-tracker.md` per `ADR-0007`, while `skills/setup-magic/references/issue-tracker-templates.md` must stay neutral or add `skills/setup-magic/references/issue-tracker-templates.md` to `MAPPING_DOCS` in `scripts/validate.sh:138-142`!).

- [ ] **Step 1: Extend `tests/setup-magic-and-roles.test.mjs` with failing assertions**

Assert:

1. `skills/setup-magic/SKILL.md` includes Scope 1 and Scope 2, `# orchestrator: thin`, `~/.agents/models.json` sync, shared `~/.config/opencode/rules/magic-models.md` default + per-profile note, `alwaysApply: true` header guidance, all 22 role lines (plus 4 tier lines) matching `model-roles.md`, and `docs/agents/issue-tracker.md` onboarding.
2. `skills/setup-magic/references/issue-tracker-templates.md` exists and covers all 16 forge operations from `skills/magic-mode/references/forge-operations.md`.
3. `docs/agents/issue-tracker.md` exists in this repo and names all 16 forge operations.
4. `rules/new-repo-setup.md` stays `< 250` words (`tests/writing-rules.test.mjs:36`).

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test tests/setup-magic-and-roles.test.mjs`
Expected: FAIL on missing Scope 1/2, `issue-tracker-templates.md`, and `docs/agents/issue-tracker.md`.

- [ ] **Step 3: Implement `/setup-magic`, `references/issue-tracker-templates.md` (+ `MAPPING_DOCS` whitelist in `scripts/validate.sh:138-142`), `docs/agents/issue-tracker.md`, `rules/new-repo-setup.md`, and `docs/magic-guide/01-setup.md`**

Follow `/writing-skills` TDD discipline (positive template recipe, observable predicates, zero subjective nuance clauses) and `/technical-writing` + `/unslop` (zero em-dashes, zero mid-sentence colons).

- [ ] **Step 4: Run full validation and test suites**

Run: `./scripts/validate.sh && python3 -m unittest discover -s tests && node --test tests/*.test.mjs && npx --yes markdownlint-cli2`
Expected: PASS with 0 errors.

- [ ] **Step 5: Commit**

```bash
git add skills/setup-magic/SKILL.md skills/setup-magic/references/issue-tracker-templates.md scripts/validate.sh docs/agents/issue-tracker.md rules/new-repo-setup.md docs/magic-guide/01-setup.md tests/setup-magic-and-roles.test.mjs
git commit -m "feat(setup-magic): add tier-first roles, harness doctor, models.json sync, and repo onboarding"
```
