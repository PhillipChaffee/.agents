import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { typographyViolations } from "./helpers/markdown-checks.mjs";

const repoDir = path.resolve(import.meta.dirname, "..");
const rolesPath = path.join(repoDir, "skills/magic-mode/references/model-roles.md");
const adapterPath = path.join(repoDir, "skills/magic-mode/references/harness-adapter.md");
const installPath = path.join(repoDir, "scripts/install.sh");
const rolesText = fs.readFileSync(rolesPath, "utf8");
const adapterText = fs.readFileSync(adapterPath, "utf8");
const installText = fs.readFileSync(installPath, "utf8");

// The 17 role lines that predate thin orchestration. Every one must survive
// verbatim so consumer role files keep resolving.
const ORIGINAL_ROLES = [
	"feature, refactoring",
	"bug-fix",
	"perf-issue",
	"hillclimb",
	"hardest tasks",
	"judgment and prose",
	"how explorer",
	"how explainer",
	"why investigators",
	"why synthesizer",
	"reflect tooling",
	"reflect judgment, divergent, synthesizer",
	"swarm workers",
	"arena runners",
	"arena cross-judge pool",
	"architect runners",
	"interrogate reviewers",
];

// The 7 grouped role lines thin orchestration adds.
const NEW_ROLES = [
	"fast, mechanical, miners",
	"researcher-lite, collectors",
	"researcher-mid",
	"researcher-deep, planner, synthesizer",
	"arena synthesizer",
	"sdd reviewer",
	"comment-sicko",
];

const TIER_KEYS = new Set(["orchestrator", "fast", "main", "deep"]);

function fencedBlock(text, language) {
	const lines = text.split("\n");
	const start = lines.findIndex((line) => line.trim() === `\`\`\`${language}`);
	assert.notEqual(start, -1, `missing \`\`\`${language} block`);
	const end = lines.indexOf("```", start + 1);
	assert.notEqual(end, -1, `unterminated \`\`\`${language} block`);
	return lines.slice(start + 1, end);
}

function roleLines(text) {
	const directives = [];
	const roles = [];
	for (const line of fencedBlock(text, "text")) {
		const trimmed = line.trim();
		if (trimmed === "" || trimmed.startsWith("#")) continue;
		const colon = trimmed.indexOf(":");
		assert.notEqual(colon, -1, `role file line without a colon: ${trimmed}`);
		const key = trimmed.slice(0, colon).trim();
		if (TIER_KEYS.has(key)) directives.push(key);
		else roles.push(key);
	}
	return { directives, roles };
}

test("model-roles.md defines orchestrator mode, four tier slots, and all 24 role lines", () => {
	for (const required of [
		"# orchestrator: thin",
		"# budget: large (xhigh)",
		"flat depth-1 wave dispatcher",
		"single-fact lookups",
		"`standard`",
	]) {
		assert.ok(rolesText.includes(required), `model-roles.md missing: ${required}`);
	}

	const { directives, roles } = roleLines(rolesText);
	assert.deepEqual(directives, ["orchestrator", "fast", "main", "deep"], "role file must declare exactly the four tier slots");
	assert.equal(roles.length, 24, "role file must declare 24 role lines");
	for (const role of [...ORIGINAL_ROLES, ...NEW_ROLES]) {
		assert.ok(roles.includes(role), `role file missing role line: ${role}`);
	}
	assert.deepEqual(new Set(roles), new Set([...ORIGINAL_ROLES, ...NEW_ROLES]), "role file declares an unexpected role line");
});

test("model-roles.md routes every new thin-orchestration slot to its tier and documents cross-family judges", () => {
	const tableRows = rolesText
		.split("\n")
		.filter((line) => line.startsWith("|"));
	const rowFor = (role) => tableRows.find((line) => line.startsWith(`| \`${role}\``));
	const expectations = new Map([
		["fast, mechanical, miners", "`fast`"],
		["researcher-lite, collectors", "`fast`"],
		["researcher-mid", "`main`"],
		["researcher-deep, planner, synthesizer", "`deep`"],
		["arena synthesizer", "`deep`"],
		["sdd reviewer", "`main`"],
		["comment-sicko", "`main`"],
	]);
	for (const [role, tier] of expectations) {
		const row = rowFor(role);
		assert.ok(row, `role table missing row for ${role}`);
		assert.ok(row.endsWith(`| ${tier} |`), `role ${role} must default to ${tier}, got ${row}`);
	}

	assert.ok(rolesText.includes("`orchestrator:` tier line names the model the parent chat"), "orchestrator tier purpose");
	assert.ok(rolesText.includes("hides the parent model ID"), "hidden parent model fallback");
	assert.ok(rolesText.includes("~/.agents/models.json"), "models.json tier fallback");
	assert.ok(rolesText.includes("`opus` for `deep`"), "Claude deep alias");
	assert.ok(rolesText.includes("`sonnet` for `main`"), "Claude main alias");
	assert.ok(rolesText.includes("`haiku` for `fast`"), "Claude fast alias");
});

test("harness-adapter.md records portable depth 1, real auto-load paths, and per-harness model passing", () => {
	for (const required of [
		"| Max portable subagent depth |",
		"1 (parent dispatches leaf subagents; never rely on subagents spawning subagents)",
		"IDE depth 2 is not portable",
		"~/.config/opencode/rules/magic-models.md",
		"magic-models-<profile>.md",
		"~/.claude/rules/magic-models.md",
		"~/.pi/agent/rules/magic-models.md",
		"~/.cursor/rules/magic-models.mdc",
		"alwaysApply: true",
		"multi_agent = true",
		"default_subagent_model",
		"~/.codex/agents/<id>.toml",
		"CLAUDE_CODE_SUBAGENT_MODEL",
		"pi-subagents",
		"`subagent` (V2) or `task` (V1)",
		"`skill` with `id` in V2 or `name` in V1",
		"`todowrite` when offered; otherwise a plan file",
		'`model: "providerID/modelID#variant"` on `subagent`',
		"`model` takes `opus`, `sonnet`, `haiku`, or `fable`",
		"`opus` for `deep`, `sonnet` for `main`, `haiku` for `fast`",
		"instead of omitting `model`",
	]) {
		assert.ok(adapterText.includes(required), `harness-adapter.md missing: ${required}`);
	}
});

test("model-roles.md and harness-adapter.md carry zero dashes and zero mid-sentence colons", () => {
	assert.deepEqual(typographyViolations(rolesText, "model-roles.md"), []);
	assert.deepEqual(typographyViolations(adapterText, "harness-adapter.md"), []);
});

test("scripts/install.sh prompts for the orchestrator model and keeps the non-interactive skip", () => {
	assert.ok(installText.includes("if [ ! -t 0 ]; then"), "non-interactive skip must stay");
	assert.ok(installText.includes('read -rp "orchestrator model (the parent chat'), "orchestrator prompt");
	assert.ok(installText.includes('"orchestrator": "$orchestrator"'), "models.json orchestrator key");
	const presets = installText.slice(installText.indexOf('"presets"'));
	for (const tier of ["orchestrator", "fast", "main", "deep"]) {
		assert.ok(presets.includes(`"${tier}"`), `models.json must keep the ${tier} tier`);
	}
});

// The 16 forge operations every tracker template and repo tracker must name.
const FORGE_OPERATIONS = [
	"open PR",
	"view PR",
	"PR for branch",
	"list PRs",
	"list checks",
	"watch checks",
	"job log",
	"rerun checks",
	"list review threads",
	"reply to thread",
	"resolve thread",
	"edit PR",
	"mark ready",
	"merge PR",
	"arm auto-merge",
	"PR history",
];

const ISSUE_OPERATIONS = ["list", "view", "create", "edit", "comment", "label", "close"];

function textFenceContaining(text, needle) {
	const lines = text.split("\n");
	let start = -1;
	for (let index = 0; index < lines.length; index += 1) {
		if (lines[index].trim() !== "```text") continue;
		const end = lines.indexOf("```", index + 1);
		assert.notEqual(end, -1, "unterminated ```text block");
		if (lines.slice(index + 1, end).some((line) => line.includes(needle))) {
			start = index;
			break;
		}
		index = end;
	}
	assert.notEqual(start, -1, `missing \`\`\`text block containing ${needle}`);
	const end = lines.indexOf("```", start + 1);
	return lines.slice(start + 1, end);
}

function fenceRoleLines(lines) {
	const directives = [];
	const roles = [];
	for (const line of lines) {
		const trimmed = line.trim();
		if (trimmed === "" || trimmed.startsWith("#")) continue;
		const colon = trimmed.indexOf(":");
		assert.notEqual(colon, -1, `role file line without a colon: ${trimmed}`);
		const key = trimmed.slice(0, colon).trim();
		if (TIER_KEYS.has(key)) directives.push(key);
		else roles.push(key);
	}
	return { directives, roles };
}

test("setup-magic SKILL.md offers Scope 1 and Scope 2 with the same tier and role lines as model-roles.md", () => {
	const skillPath = path.join(repoDir, "skills/setup-magic/SKILL.md");
	const skillText = fs.readFileSync(skillPath, "utf8");

	const fmEnd = skillText.indexOf("\n---", 4);
	assert.notEqual(fmEnd, -1, "setup-magic SKILL.md frontmatter is malformed");
	const frontmatter = skillText.slice(4, fmEnd);
	const fmKeys = frontmatter
		.split("\n")
		.filter((line) => /^[A-Za-z][A-Za-z0-9-]*:/.test(line))
		.map((line) => line.slice(0, line.indexOf(":")));
	assert.deepEqual([...fmKeys].sort(), fmKeys, "frontmatter keys must stay sorted");
	assert.match(frontmatter, /^description: "?Use when /m, 'description must start with "Use when"');

	for (const required of [
		"## Step 0. Select scope",
		"Scope 1",
		"Scope 2",
		"~/.agents/models.json",
		"~/.config/opencode/rules/magic-models.md",
		"magic-models-<profile>.md",
		"`personal`, `work-dev`, `work-prod`",
		"alwaysApply: true",
		"# orchestrator: thin",
		"# budget: large (xhigh)",
		"`#<variant>`",
		"`[effort=...]`",
		"`reasoning_effort`",
		"`inherit-parent`",
		"`auto`",
		"unlimited (max reasoning)",
		"large (xhigh reasoning)",
		"medium (high reasoning)",
		"small (medium reasoning)",
		"multi_agent = true",
		"default_subagent_model",
		"~/.codex/agents/<id>.toml",
		"CLAUDE_CODE_SUBAGENT_MODEL",
		"pi-subagents",
		"docs/agents/issue-tracker.md",
		"references/issue-tracker-templates.md",
		"CONTEXT.md",
		"docs/adr/",
		"init-<lang>-repo",
		"`/create-verification-skill`",
		"`/create-formal-verification-skill`",
	]) {
		assert.ok(skillText.includes(required), `setup-magic SKILL.md missing: ${required}`);
	}

	const roleBlock = textFenceContaining(skillText, "# orchestrator: thin");
	assert.ok(roleBlock.some((line) => line.trim() === "# budget: large (xhigh)"), "role block budget line");
	const skillRoles = fenceRoleLines(roleBlock);
	const canonical = roleLines(rolesText);
	assert.deepEqual(skillRoles.directives, canonical.directives, "setup-magic must mirror the four tier lines");
	assert.deepEqual(skillRoles.roles, canonical.roles, "setup-magic must mirror all 24 role lines in order");
});

test("setup-magic SKILL.md and the repo tracker templates stay free of dashes and mid-sentence colons", () => {
	for (const rel of [
		"skills/setup-magic/SKILL.md",
		"skills/setup-magic/references/issue-tracker-templates.md",
		"docs/agents/issue-tracker.md",
		"rules/new-repo-setup.md",
		"docs/magic-guide/01-setup.md",
	]) {
		const text = fs.readFileSync(path.join(repoDir, rel), "utf8");
		assert.deepEqual(typographyViolations(text, rel), []);
	}
});

test("issue-tracker-templates.md covers issue operations and all 16 forge operations for every tracker", () => {
	assert.equal(FORGE_OPERATIONS.length, 16, "forge operation list must hold exactly 16 entries");
	const templatesPath = path.join(
		repoDir,
		"skills/setup-magic/references/issue-tracker-templates.md",
	);
	assert.ok(fs.existsSync(templatesPath), "missing issue-tracker-templates.md");
	const templates = fs.readFileSync(templatesPath, "utf8");

	for (const operation of FORGE_OPERATIONS) {
		assert.ok(templates.includes(operation), `issue-tracker-templates.md missing forge operation: ${operation}`);
	}
	for (const operation of ISSUE_OPERATIONS) {
		assert.match(
			templates,
			new RegExp(`\\| ${operation} \\|`),
			`issue-tracker-templates.md missing issue operation row: ${operation}`,
		);
	}
	for (const tracker of ["GitHub", "GitLab", "Linear", "Local Markdown"]) {
		assert.ok(templates.includes(tracker), `issue-tracker-templates.md missing tracker: ${tracker}`);
	}
	for (const command of ["gh", "glab", "docs/issues/", "ticket ID", "issues and PRs"]) {
		assert.ok(templates.includes(command), `issue-tracker-templates.md missing: ${command}`);
	}
});

test("this repository records its own GitHub tracker with all 16 forge operations", () => {
	const trackerPath = path.join(repoDir, "docs/agents/issue-tracker.md");
	assert.ok(fs.existsSync(trackerPath), "missing docs/agents/issue-tracker.md");
	const tracker = fs.readFileSync(trackerPath, "utf8");

	assert.ok(tracker.includes("PhillipChaffee/magic"), "tracker must name the repository");
	for (const operation of ISSUE_OPERATIONS) {
		assert.match(
			tracker,
			new RegExp(`\\| ${operation} \\|`),
			`docs/agents/issue-tracker.md missing issue operation row: ${operation}`,
		);
	}
	for (const operation of FORGE_OPERATIONS) {
		assert.ok(tracker.includes(operation), `docs/agents/issue-tracker.md missing forge operation: ${operation}`);
	}
	for (const command of ["gh issue", "gh pr", "gh api", "gh run", "GitHub MCP", "credential.helper"]) {
		assert.ok(tracker.includes(command), `docs/agents/issue-tracker.md missing: ${command}`);
	}
});

test("research-planner and research-synthesizer pin their read-only tool denials", () => {
	for (const id of ["research-planner", "research-synthesizer"]) {
		const agent = fs.readFileSync(path.join(repoDir, `agents/${id}/agent.md`), "utf8");
		const end = agent.indexOf("\n---", 4);
		const frontmatter = agent.slice(4, end);
		const denial = frontmatter
			.split("\n")
			.find((line) => line.startsWith("disallowedTools:"));
		assert.ok(denial, `${id}: missing disallowedTools`);
		assert.ok(denial.includes('"Agent"'), `${id}: must deny Agent to stay depth 1`);
		assert.ok(denial.includes('"Edit"'), `${id}: must deny Edit`);
	}
	const planner = fs.readFileSync(path.join(repoDir, "agents/research-planner/agent.md"), "utf8");
	assert.ok(planner.includes('"Write"'), "research-planner: must deny Write");
});
