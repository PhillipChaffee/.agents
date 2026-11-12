import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { pathToFileURL } from "node:url";

const repoDir = path.resolve(import.meta.dirname, "..");
const skillsDir = path.join(repoDir, "skills");
const corePath = path.join(repoDir, "lib/bootstrap-core.js");

const expectedMarker = "<EXTREMELY_IMPORTANT>\nYou have magic.";
let importCounter = 0;

async function importFresh(filePath) {
	const url = pathToFileURL(filePath).href;
	return import(`${url}?t=${++importCounter}`);
}

test("lib/bootstrap-core.js parses frontmatter variants and loads cached using-magic bootstrap", async () => {
	const core = await importFresh(corePath);
	assert.equal(core.BOOTSTRAP_MARKER, expectedMarker);

	const parsed = core.extractAndStripFrontmatter(
		'---\r\ndescription: "Multi-line\r\n  quoted description"\r\nname: sample\r\nsummary: >\r\n  Folded line one\r\n  line two\r\n---\r\n# Heading\r\n\r\nBody text.\n',
	);
	assert.equal(parsed.frontmatter.description, "Multi-line quoted description");
	assert.equal(parsed.frontmatter.name, "sample");
	assert.equal(parsed.frontmatter.summary, "Folded line one line two");
	assert.equal(parsed.content, "# Heading\r\n\r\nBody text.\n");

	const noFm = core.extractAndStripFrontmatter("# Plain markdown\n");
	assert.deepEqual(noFm.frontmatter, {});
	assert.equal(noFm.content, "# Plain markdown\n");

	const missing = core.loadBootstrapContent(path.join(repoDir, "nonexistent-skills"), "TOOLS");
	assert.equal(missing, null);

	const bootstrap = core.loadBootstrapContent(skillsDir, "CUSTOM_TOOL_MAPPING");
	assert.ok(bootstrap?.startsWith(expectedMarker));
	assert.match(bootstrap, /# Using Magic/);
	assert.match(bootstrap, /CUSTOM_TOOL_MAPPING/);
});

test("lib/bootstrap-core.js handles empty frontmatter without eating body horizontal rules", async () => {
	const core = await importFresh(corePath);
	const sample = "---\n---\n# Heading\n\n---\n\nBody paragraph.\n";
	const { frontmatter, content } = core.extractAndStripFrontmatter(sample);
	assert.deepEqual(frontmatter, {});
	assert.match(content, /^# Heading\n\n---\n\nBody paragraph\./);

	const emptyNoRule = "---\n---\n# Heading\nBody text.\n";
	const stripped = core.extractAndStripFrontmatter(emptyNoRule);
	assert.deepEqual(stripped.frontmatter, {});
	assert.equal(stripped.content, "# Heading\nBody text.\n");
});

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
	assert.equal(loaded.parsed.hasDirectives, true);
	assert.equal(loaded.parsed.roles["main"], "provider/workhorse#medium");
	assert.equal(loaded.parsed.roles["arena runners"], "a/b#high, c/d#max");
	assert.equal(core.isUsableMagicModels(loaded.parsed), true);
});

test("lib/bootstrap-core.js agent loader exposes prompt/path, disallowedTools, and magic-models parsing defaults", async (t) => {
	const core = await importFresh(corePath);
	const agents = core.loadKitAgents(path.join(repoDir, "agents"));
	assert.deepEqual(
		agents.map((a) => a.id),
		[
			"comment-sicko",
			"magic-agent",
			"research-planner",
			"research-synthesizer",
			"researcher-deep",
			"researcher-lite",
			"researcher-mid",
		],
	);
	for (const agent of agents) {
		assert.equal(typeof agent.name, "string");
		assert.equal(typeof agent.description, "string");
		assert.equal(agent.path, path.join(repoDir, "agents", agent.id, "agent.md"));
		assert.ok(agent.prompt.length > 0, `${agent.id} prompt must be non-empty`);
		assert.ok(!agent.prompt.startsWith("---"), `${agent.id} prompt must strip frontmatter`);
		assert.ok(Array.isArray(agent.disallowedTools), `${agent.id} must expose disallowedTools array`);
	}
	assert.deepEqual(core.loadKitAgents(path.join(repoDir, "missing-agents")), []);

	const planner = agents.find((a) => a.id === "research-planner");
	assert.ok(planner.disallowedTools.includes("Agent"));
	assert.ok(planner.disallowedTools.includes("Write"));

	const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "magic-models-defaults-"));
	t.after(() => fs.rmSync(tmp, { recursive: true, force: true }));
	const p = path.join(tmp, "magic-models.md");
	fs.writeFileSync(p, "main: provider/workhorse\n");
	const parsed = core.loadMagicModelsRule([p]).parsed;
	assert.equal(parsed.orchestratorMode, "thin");
	assert.equal(parsed.budget, null);
	assert.equal(parsed.hasDirectives, false);
	assert.deepEqual(parsed.roles, { main: "provider/workhorse" });
	assert.equal(core.isUsableMagicModels(parsed), true, "roles alone make a file usable");

	fs.writeFileSync(p, "# orchestrator: standard\n# budget: medium\n");
	const standard = core.loadMagicModelsRule([p]).parsed;
	assert.equal(standard.orchestratorMode, "standard");
	assert.equal(standard.budget, "medium");
	assert.equal(standard.hasDirectives, true);
	assert.deepEqual(standard.roles, {});
	assert.equal(core.isUsableMagicModels(standard), true, "directives alone make a file usable");
});

test("lib/bootstrap-core.js falls through a stub magic-models candidate to a usable file lower in the list", async (t) => {
	const core = await importFresh(corePath);
	const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "magic-models-fallthrough-"));
	t.after(() => fs.rmSync(tmp, { recursive: true, force: true }));

	const empty = path.join(tmp, "empty.md");
	fs.writeFileSync(empty, "");
	const stub = path.join(tmp, "magic-models.md");
	fs.writeFileSync(
		stub,
		"---\nalwaysApply: true\ndescription: stub\n---\nJust prose about which models to pick.\n# budget:\n# orchestrator: see the harness docs\n",
	);
	const fallback = path.join(tmp, "magic-models-fallback.md");
	fs.writeFileSync(fallback, "# orchestrator: standard\nmain: provider/workhorse#medium\n");

	const stubParsed = core.parseMagicModels(fs.readFileSync(stub, "utf8"));
	assert.equal(stubParsed.budget, null, "an empty # budget: directive must normalize to null");
	assert.equal(stubParsed.hasDirectives, false, "an empty directive is not configuration");
	assert.equal(stubParsed.orchestratorMode, "thin", "an unrelated # orchestrator: note must not set a mode");
	assert.equal(core.isUsableMagicModels(stubParsed), false);
	assert.equal(core.isUsableMagicModels(null), false);
	assert.equal(core.isUsableMagicModels(undefined), false);

	assert.equal(core.loadMagicModelsRule([stub]), null, "a lone stub yields no rule");
	const loaded = core.loadMagicModelsRule([empty, stub, fallback]);
	assert.equal(loaded.path, fallback, "a higher-priority stub must not shadow a usable file");
	assert.equal(loaded.parsed.orchestratorMode, "standard");
	assert.equal(loaded.raw.includes("provider/workhorse#medium"), true);
});

test("lib/bootstrap-core.js appends extra sections between skill content and tool mapping without poisoning the cache", async () => {
	const core = await importFresh(corePath);
	const plain = core.loadBootstrapContent(skillsDir, "TOOLS");
	assert.ok(plain.endsWith("TOOLS\n</EXTREMELY_IMPORTANT>"));

	const sectioned = core.loadBootstrapContent(skillsDir, "TOOLS", undefined, ["# Rules", "", "# Magic Models"]);
	assert.ok(sectioned.includes("# Rules\n\n# Magic Models\n\nTOOLS\n</EXTREMELY_IMPORTANT>"));
	assert.ok(sectioned.indexOf("# Using Magic") < sectioned.indexOf("# Rules"));
	assert.equal(core.loadBootstrapContent(skillsDir, "TOOLS", undefined, []), plain);
	assert.equal(core.loadBootstrapContent(skillsDir, "TOOLS", undefined, ["", "  "]), plain);
});

test("lib/bootstrap-core.js loads skills and models.json presets", async (t) => {
	const core = await importFresh(corePath);
	const skills = core.loadKitSkills(skillsDir);
	assert.equal(skills.length, 75);
	assert.ok(skills.some((s) => s.id === "magic-mode"));

	const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "models-json-"));
	t.after(() => fs.rmSync(tmp, { recursive: true, force: true }));
	const p = path.join(tmp, "models.json");
	fs.writeFileSync(p, JSON.stringify({ presets: { fast: "vendor/fast", main: "vendor/main", deep: "vendor/deep" } }));
	const presets = core.loadModelsJsonPresets(p);
	assert.deepEqual(presets, { fast: "vendor/fast", main: "vendor/main", deep: "vendor/deep" });
	assert.equal(core.loadModelsJsonPresets(path.join(tmp, "missing.json")), null);
});
