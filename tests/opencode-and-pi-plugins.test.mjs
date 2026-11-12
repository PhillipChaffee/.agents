import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { pathToFileURL } from "node:url";

const repoDir = path.resolve(import.meta.dirname, "..");
const skillsDir = path.join(repoDir, "skills");
const pluginPath = path.join(repoDir, ".opencode/plugins/magic.js");
const indexPath = path.join(repoDir, "index.js");
const corePath = path.join(repoDir, "lib/bootstrap-core.js");
const piExtensionPath = path.join(repoDir, ".pi/extensions/magic.ts");
const packageJsonPath = path.join(repoDir, "package.json");

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

test("lib/bootstrap-core.js agent loader exposes prompt/path and magic-models parsing defaults", async (t) => {
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
	}
	assert.deepEqual(core.loadKitAgents(path.join(repoDir, "missing-agents")), []);

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

test("OpenCode V1: MagicPlugin registers skills path, injects V1 bootstrap idempotently, and skips child sessions", async () => {
	const canonicalMod = await import(pathToFileURL(pluginPath).href);
	const indexMod = await import(pathToFileURL(indexPath).href);
	assert.equal(indexMod.default, canonicalMod.default);

	const mod = await importFresh(pluginPath);
	assert.equal(mod.default.id, "magic");
	assert.equal(mod.default.server, mod.MagicPlugin);
	assert.equal(typeof mod.V1_MAPPING, "string");
	assert.equal(typeof mod.V2_MAPPING, "string");

	const lookups = [];
	const sessions = new Map([
		["sess-root", { data: { id: "sess-root" } }],
		["sess-child", { data: { id: "sess-child", parentID: "parent-1" } }],
	]);
	const client = {
		session: {
			get: async ({ path: { id } }) => {
				lookups.push(id);
				if (id === "sess-flaky" && lookups.filter((x) => x === "sess-flaky").length === 1) {
					return { error: { message: "503" }, response: { ok: false } };
				}
				return sessions.get(id) ?? { data: { id, parentID: "parent-1" } };
			},
		},
	};

	const plugin = await mod.DotAgentsPlugin({ client, directory: repoDir });

	const v1Config = {};
	await plugin.config(v1Config);
	await plugin.config(v1Config);
	assert.deepEqual(v1Config.skills.paths, [skillsDir]);

	const v2Config = { skills: ["existing"] };
	await plugin.config(v2Config);
	assert.deepEqual(v2Config.skills, ["existing"]);

	const transform = plugin["experimental.chat.messages.transform"];
	const rootOutput = {
		messages: [
			{
				info: { role: "user", sessionID: "sess-root" },
				parts: [{ type: "text", text: "Help me refactor this module and mention EXTREMELY_IMPORTANT" }],
			},
		],
	};

	await transform({}, rootOutput);
	assert.equal(rootOutput.messages[0].parts.length, 2);
	assert.ok(rootOutput.messages[0].parts[0].text.startsWith(expectedMarker));
	assert.ok(rootOutput.messages[0].parts[0].text.includes(mod.V1_MAPPING));
	assert.match(rootOutput.messages[0].parts[0].text, /# Using Magic/);

	await transform({}, rootOutput);
	assert.equal(rootOutput.messages[0].parts.length, 2, "repeat call on same message must be idempotent");

	const secondRootOutput = {
		messages: [
			{
				info: { role: "user", sessionID: "sess-root" },
				parts: [{ type: "text", text: "Next step" }],
			},
		],
	};
	await transform({}, secondRootOutput);
	assert.equal(secondRootOutput.messages[0].parts.length, 2);
	assert.deepEqual(
		lookups.filter((id) => id === "sess-root"),
		["sess-root"],
		"root session classification should be cached",
	);

	const childOutput = {
		messages: [
			{
				info: { role: "user", sessionID: "sess-child" },
				parts: [{ type: "text", text: "Execute leaf subtask" }],
			},
		],
	};
	await transform({}, childOutput);
	assert.equal(childOutput.messages[0].parts.length, 1, "child session with parentID must skip bootstrap");

	const flakyFirst = {
		messages: [{ info: { role: "user", sessionID: "sess-flaky" }, parts: [{ type: "text", text: "Step 1" }] }],
	};
	await transform({}, flakyFirst);
	assert.equal(flakyFirst.messages[0].parts.length, 2, "failed session lookup should fail open");

	const flakySecond = {
		messages: [{ info: { role: "user", sessionID: "sess-flaky" }, parts: [{ type: "text", text: "Step 2" }] }],
	};
	await transform({}, flakySecond);
	assert.equal(flakySecond.messages[0].parts.length, 1, "subsequent lookup should recover and skip child session");
});

test("OpenCode V2: default.setup registers all 75 skills, survives hostile draft.add, registers context/compaction/generate, and skips child sessions", async () => {
	const mod = await importFresh(pluginPath);

	await mod.default.setup({});

	const expectedSkillDirs = fs
		.readdirSync(skillsDir, { withFileTypes: true })
		.filter((e) => e.isDirectory() && !e.name.startsWith(".") && fs.existsSync(path.join(skillsDir, e.name, "SKILL.md")))
		.map((e) => e.name)
		.sort();
	assert.equal(expectedSkillDirs.length, 75, "expected 75 skills in skills/*/SKILL.md");

	const addedSkills = [];
	const hooks = new Map();
	const sessionRecords = new Map([
		["v2-root", { id: "v2-root" }],
		["v2-child", { id: "v2-child", parentID: "parent-1" }],
		["v2-compacted", { id: "v2-compacted" }],
	]);

	await mod.default.setup({
		skill: {
			transform: async (fn) => {
				await fn({ add: (s) => addedSkills.push(s) });
			},
		},
		session: {
			get: async ({ sessionID }) => sessionRecords.get(sessionID) ?? { id: sessionID },
			hook: async (name, cb) => {
				hooks.set(name, cb);
			},
		},
	});

	assert.equal(addedSkills.length, 75);
	assert.deepEqual(
		addedSkills.map((s) => s.id).sort(),
		expectedSkillDirs,
	);
	for (const skill of addedSkills) {
		assert.equal(typeof skill.id, "string");
		assert.equal(typeof skill.name, "string");
		assert.equal(typeof skill.description, "string");
		assert.equal(skill.path, path.join(skillsDir, skill.id, "SKILL.md"));
		assert.equal(typeof skill.content, "string");
		assert.ok(!skill.content.startsWith("---"), `skill ${skill.id} content must strip frontmatter`);
		assert.ok(!("location" in skill));
	}

	assert.deepEqual([...hooks.keys()].sort(), ["compaction", "context", "generate"]);
	assert.equal(hooks.get("compaction"), hooks.get("context"));
	assert.equal(hooks.get("generate"), hooks.get("context"));

	for (const hookName of ["context", "compaction", "generate"]) {
		const handler = hooks.get(hookName);
		const rootEv = {
			sessionID: "v2-root",
			messages: [{ role: "user", content: [{ type: "text", text: "Run task" }] }],
		};
		await handler(rootEv);
		assert.equal(rootEv.messages[0].content.length, 2);
		assert.ok(rootEv.messages[0].content[0].text.startsWith(expectedMarker));
		assert.ok(rootEv.messages[0].content[0].text.includes(mod.V2_MAPPING));

		await handler(rootEv);
		assert.equal(rootEv.messages[0].content.length, 2, `${hookName} handler must be idempotent`);

		const childEv = {
			sessionID: "v2-child",
			messages: [{ role: "user", content: [{ type: "text", text: "Leaf task" }] }],
		};
		await handler(childEv);
		assert.equal(childEv.messages[0].content.length, 1, `${hookName} handler must skip child sessions`);
	}

	const compactedEv = {
		sessionID: "v2-compacted",
		messages: [{ role: "assistant", content: [{ type: "compaction", encrypted: "checkpoint" }] }],
	};
	await hooks.get("compaction")(compactedEv);
	assert.equal(compactedEv.messages.length, 2);
	assert.equal(compactedEv.messages[1].role, "user");
	assert.ok(compactedEv.messages[1].content[0].text.startsWith(expectedMarker));

	const survived = [];
	const survivingHooks = new Map();
	const rejectedId = expectedSkillDirs[10];
	const origError = console.error;
	console.error = () => {};
	try {
		await mod.default.setup({
			skill: {
				transform: async (fn) => {
					await fn({
						add: (s) => {
							if (s.id === rejectedId) throw new Error("Schema rejection");
							survived.push(s.id);
						},
					});
				},
			},
			session: {
				get: async ({ sessionID }) => ({ id: sessionID }),
				hook: async (name, cb) => {
					survivingHooks.set(name, cb);
				},
			},
		});
	} finally {
		console.error = origError;
	}
	assert.equal(survived.length, 74);
	assert.ok(!survived.includes(rejectedId));
	assert.equal(survivingHooks.size, 3);
});

const KIT_AGENT_IDS = [
	"comment-sicko",
	"magic-agent",
	"research-planner",
	"research-synthesizer",
	"researcher-deep",
	"researcher-lite",
	"researcher-mid",
];

const ALLOW_ALL_RULE = { action: "*", resource: "*", effect: "allow" };
const EDIT_DENY_RULE = { action: "edit", resource: "*", effect: "deny" };
const DEFAULT_V2_REQUEST = { settings: {}, headers: {}, body: {} };

function useMagicModels(t, contents) {
	const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "magic-models-plugin-"));
	const modelsPath = path.join(tmp, "magic-models.md");
	fs.writeFileSync(modelsPath, contents);
	const previous = process.env.MAGIC_MODELS_PATH;
	process.env.MAGIC_MODELS_PATH = modelsPath;
	t.after(() => {
		fs.rmSync(tmp, { recursive: true, force: true });
		if (previous === undefined) delete process.env.MAGIC_MODELS_PATH;
		else process.env.MAGIC_MODELS_PATH = previous;
	});
	return modelsPath;
}

test("OpenCode V2_MAPPING restores todowrite and documents kit subagent model authorization", async () => {
	const mod = await importFresh(pluginPath);

	assert.match(
		mod.V2_MAPPING,
		/- Create or update todos → `todowrite` when offered; otherwise track the plan in a markdown file \(or the harness's plan facility\)/,
	);
	assert.ok(!mod.V2_MAPPING.includes("OpenCode v2 has no todo tool"));
	assert.match(mod.V2_MAPPING, /`agent: "<id>"` for registered kit subagents/);
	for (const id of KIT_AGENT_IDS) {
		assert.ok(mod.V2_MAPPING.includes(`\`${id}\``), `V2_MAPPING must name ${id}`);
	}
	assert.match(mod.V2_MAPPING, /pass it in `model`/);
	assert.match(mod.V2_MAPPING, /`providerID\/modelID#variant`/);
	assert.equal(typeof mod.V1_MAPPING, "string");
});

test("resolveAgentModel binds concrete provider/model#variant and refuses tier words", async () => {
	const mod = await importFresh(pluginPath);
	assert.equal(typeof mod.resolveAgentModel, "function");

	assert.equal(mod.resolveAgentModel("magic-agent", null), undefined);
	assert.equal(mod.resolveAgentModel("magic-agent", {}), undefined);
	assert.equal(mod.resolveAgentModel("magic-agent", { roles: {} }), undefined);
	assert.equal(mod.resolveAgentModel("unknown-agent", { roles: { main: "provider/workhorse" } }), undefined);

	const parsed = {
		roles: {
			main: "provider/workhorse#medium",
			"feature, refactoring": "inherit-parent",
			"researcher-lite, collectors": "fast",
			fast: "vendor/flash#max",
			"researcher-deep, planner, synthesizer": "auto",
			deep: "vendor/deep#high",
			"comment-sicko": "fast",
		},
	};

	assert.equal(mod.resolveAgentModel("magic-agent", parsed), undefined, "inherit-parent must not resolve");
	assert.equal(mod.resolveAgentModel("researcher-lite", parsed), "vendor/flash#max", "fast tier dereferences once");
	assert.equal(mod.resolveAgentModel("researcher-mid", parsed), "provider/workhorse#medium", "main tier dereferences");
	assert.equal(mod.resolveAgentModel("researcher-deep", parsed), undefined, "auto must not resolve");
	assert.equal(mod.resolveAgentModel("research-planner", parsed), undefined, "auto must not resolve");
	assert.equal(mod.resolveAgentModel("research-synthesizer", parsed), undefined, "auto must not resolve");
	assert.equal(mod.resolveAgentModel("comment-sicko", parsed), "vendor/flash#max");

	assert.equal(
		mod.resolveAgentModel("magic-agent", { roles: { "feature, refactoring": "a/b#high, c/d#max" } }),
		"a/b#high",
		"only the first comma-separated entry is used",
	);
	assert.equal(
		mod.resolveAgentModel("researcher-deep", {
			roles: { "researcher-deep, planner, synthesizer": "deep", deep: "vendor/deep#high" },
		}),
		"vendor/deep#high",
		"deep tier dereferences once",
	);
	assert.equal(
		mod.resolveAgentModel("researcher-deep", { roles: { "researcher-deep, planner, synthesizer": "deep" } }),
		undefined,
		"an unresolved tier name must never reach the host",
	);
	assert.equal(
		mod.resolveAgentModel("researcher-mid", { roles: { main: "" } }),
		undefined,
	);
	assert.equal(
		mod.resolveAgentModel("researcher-mid", { roles: { main: "provider/workhorse#medium # weekly pick" } }),
		"provider/workhorse#medium",
		"an inline comment must be stripped while #variant survives",
	);
	assert.equal(
		mod.resolveAgentModel("researcher-mid", { roles: { main: "a/b, c/d#max # comment" } }),
		"a/b",
		"only the first comma-separated entry is used, after comment stripping",
	);
});

test("parseModelRef mirrors OpenCode V2 Model.Ref.parse and refuses malformed role strings", async () => {
	const mod = await importFresh(pluginPath);
	assert.equal(typeof mod.parseModelRef, "function");

	assert.deepEqual(mod.parseModelRef("provider/workhorse"), { providerID: "provider", id: "workhorse" });
	assert.deepEqual(mod.parseModelRef("provider/workhorse#medium"), {
		providerID: "provider",
		id: "workhorse",
		variant: "medium",
	});
	assert.deepEqual(mod.parseModelRef("togetherai/moonshotai/Kimi-K3.1-Pro#max"), {
		providerID: "togetherai",
		id: "moonshotai/Kimi-K3.1-Pro",
		variant: "max",
	});

	assert.equal(mod.parseModelRef(undefined), undefined);
	assert.equal(mod.parseModelRef(null), undefined);
	assert.equal(mod.parseModelRef(42), undefined);
	assert.equal(mod.parseModelRef("/no-provider"), undefined);
	assert.equal(mod.parseModelRef("noid/"), undefined);
	assert.equal(mod.parseModelRef("pro#vider/id"), undefined);
	assert.equal(mod.parseModelRef("provider/model#"), undefined);
	assert.equal(mod.parseModelRef("provider/model#two#variants"), undefined);
	assert.equal(mod.parseModelRef("no-slash"), undefined);
});

test("OpenCode V2 setup registers all 7 kit subagents as Agent.Info records with Model.Ref models and deny permission rules", async (t) => {
	const mod = await importFresh(pluginPath);
	useMagicModels(
		t,
		"main: provider/workhorse#medium\nfeature, refactoring: inherit-parent\ncomment-sicko: fast\nfast: vendor/flash#max\n",
	);

	const registered = [];
	const drafts = new Map();
	const hooks = new Map();
	const draftFor = (id) => {
		if (id === "research-planner") {
			return { permissions: [{ action: "bash", resource: "*", effect: "allow" }], hidden: true };
		}
		if (id === "comment-sicko") {
			return { model: { providerID: "user", id: "choice", variant: "high" } };
		}
		return {};
	};
	await mod.default.setup({
		agent: {
			transform: async (fn) => {
				await fn({
					update: (id, cb) => {
						const draft = draftFor(id);
						const result = cb(draft);
						registered.push(result);
						drafts.set(id, draft);
					},
				});
			},
		},
		skill: { transform: async (fn) => fn({ add: () => {} }) },
		session: {
			get: async ({ sessionID }) => ({ id: sessionID }),
			hook: async (name, cb) => {
				hooks.set(name, cb);
			},
		},
	});

	assert.equal(registered.length, 7);
	assert.deepEqual(
		registered.map((agent) => agent.id).sort(),
		KIT_AGENT_IDS,
	);
	for (const agent of registered) {
		assert.equal(agent.name, agent.id);
		assert.equal(agent.mode, "subagent");
		assert.ok(agent.description.length > 0, `${agent.id} description must be non-empty`);
		assert.ok(agent.system.length > 0, `${agent.id} system prompt must be non-empty`);
		assert.ok(!agent.system.startsWith("---"), `${agent.id} system prompt must strip frontmatter`);
		assert.ok(!("prompt" in agent), `${agent.id} must use Agent.Info.system, not the V1 prompt field`);
		assert.equal(typeof agent.hidden, "boolean");
		assert.deepEqual(agent.request, DEFAULT_V2_REQUEST);
		assert.ok(Array.isArray(agent.permissions), `${agent.id} permissions must be a Ruleset array`);
		for (const rule of agent.permissions) {
			assert.deepEqual(Object.keys(rule).sort(), ["action", "effect", "resource"]);
		}
		const draft = drafts.get(agent.id);
		assert.equal(draft.mode, "subagent", `${agent.id} must also land via in-place draft mutation`);
		assert.equal(draft.system, agent.system);
		assert.deepEqual(draft.permissions, agent.permissions);
	}

	const byId = new Map(registered.map((agent) => [agent.id, agent]));
	assert.deepEqual(byId.get("researcher-mid").model, { providerID: "provider", id: "workhorse", variant: "medium" });
	assert.deepEqual(
		byId.get("researcher-lite").model,
		{ providerID: "vendor", id: "flash", variant: "max" },
		"fast tier feeds researcher-lite",
	);
	assert.deepEqual(
		byId.get("comment-sicko").model,
		{ providerID: "user", id: "choice", variant: "high" },
		"an existing draft Model.Ref wins over the role-file binding",
	);
	assert.ok(!("model" in byId.get("magic-agent")), "inherit-parent must not be passed as a model");

	assert.deepEqual(byId.get("research-planner").permissions, [
		{ action: "bash", resource: "*", effect: "allow" },
		EDIT_DENY_RULE,
	]);
	assert.deepEqual(byId.get("research-planner").hidden, true, "an existing hidden flag is preserved");
	assert.deepEqual(byId.get("research-synthesizer").permissions, [ALLOW_ALL_RULE, EDIT_DENY_RULE]);
	assert.deepEqual(byId.get("research-synthesizer").hidden, false);
	assert.deepEqual(
		byId.get("magic-agent").permissions,
		[ALLOW_ALL_RULE],
		"writable agents keep default permissions",
	);
	assert.deepEqual([...hooks.keys()].sort(), ["compaction", "context", "generate"]);
});

test("OpenCode V2 setup falls back to editor.add when the host has no update", async (t) => {
	const mod = await importFresh(pluginPath);
	useMagicModels(t, "main: provider/workhorse#medium\n");

	const added = [];
	const origConsoleError = console.error;
	console.error = () => {};
	try {
		await mod.default.setup({
			agent: {
				transform: async (fn) => {
					await fn({ add: (agent) => added.push(agent) });
				},
			},
			skill: { transform: async (fn) => fn({ add: () => {} }) },
			session: {
				get: async ({ sessionID }) => ({ id: sessionID }),
				hook: async () => {},
			},
		});
	} finally {
		console.error = origConsoleError;
	}

	assert.equal(added.length, 7);
	assert.deepEqual(
		added.map((agent) => agent.id).sort(),
		KIT_AGENT_IDS,
	);
	assert.equal(added.find((agent) => agent.id === "magic-agent").mode, "subagent");
	assert.ok(added.every((agent) => typeof agent.system === "string" && agent.system.length > 0));
	assert.deepEqual(added.find((agent) => agent.id === "researcher-mid").model, {
		providerID: "provider",
		id: "workhorse",
		variant: "medium",
	});
});

test("OpenCode V2 setup retries with editor.add when update throws, and survives frozen drafts", async (t) => {
	const mod = await importFresh(pluginPath);
	useMagicModels(t, "main: provider/workhorse#medium\n");

	const updateAttempts = [];
	const added = [];
	const updated = [];
	const origConsoleError = console.error;
	console.error = () => {};
	try {
		await mod.default.setup({
			agent: {
				transform: async (fn) => {
					await fn({
						update: (id) => {
							updateAttempts.push(id);
							throw new Error(`unknown agent: ${id}`);
						},
						add: (agent) => added.push(agent),
					});
				},
			},
			skill: { transform: async (fn) => fn({ add: () => {} }) },
			session: {
				get: async ({ sessionID }) => ({ id: sessionID }),
				hook: async () => {},
			},
		});

		await mod.default.setup({
			agent: {
				transform: async (fn) => {
					await fn({
						update: (id, cb) => {
							updated.push(cb(Object.freeze({})));
						},
					});
				},
			},
			skill: { transform: async (fn) => fn({ add: () => {} }) },
			session: {
				get: async ({ sessionID }) => ({ id: sessionID }),
				hook: async () => {},
			},
		});
	} finally {
		console.error = origConsoleError;
	}

	assert.deepEqual([...updateAttempts].sort(), KIT_AGENT_IDS, "every kit agent must be attempted through update");
	assert.deepEqual(
		added.map((agent) => agent.id).sort(),
		KIT_AGENT_IDS,
		"a rejected update must fall back to add for every agent",
	);
	assert.deepEqual(added.find((agent) => agent.id === "research-planner").permissions, [
		ALLOW_ALL_RULE,
		EDIT_DENY_RULE,
	]);

	assert.deepEqual(
		updated.map((agent) => agent.id).sort(),
		KIT_AGENT_IDS,
		"a frozen draft must still yield the merged registration",
	);
	assert.equal(updated.find((agent) => agent.id === "magic-agent").mode, "subagent");
	assert.deepEqual(updated.find((agent) => agent.id === "magic-agent").model, {
		providerID: "provider",
		id: "workhorse",
		variant: "medium",
	});
	assert.deepEqual(updated.find((agent) => agent.id === "research-planner").permissions, [
		ALLOW_ALL_RULE,
		EDIT_DENY_RULE,
	]);
});

test("OpenCode V2 setup registers every agent when the host calls the transform callback synchronously", async (t) => {
	const mod = await importFresh(pluginPath);
	useMagicModels(t, "main: provider/workhorse#medium\n");

	const registered = [];
	const drafts = new Map();
	const draftFor = (id) => {
		if (id === "research-planner") {
			return { model: "vendor/draft#high", permissions: [{ action: "edit", resource: "*", effect: "allow" }] };
		}
		if (id === "research-synthesizer") return { model: null };
		if (id === "researcher-deep") return { model: { providerID: "user" } };
		return {};
	};

	let countWhenCallbackReturned;
	let returned;
	await mod.default.setup({
		agent: {
			// @opencode/plugin's adapter invokes `fn(editor)` and ignores the
			// return value, so registration must finish before `fn` returns.
			transform: (fn) => {
				returned = fn({
					update: (id, cb) => {
						const draft = draftFor(id);
						drafts.set(id, draft);
						registered.push(cb(draft));
					},
				});
				countWhenCallbackReturned = registered.length;
			},
		},
		skill: { transform: (fn) => fn({ add: () => {} }) },
		session: {
			get: async ({ sessionID }) => ({ id: sessionID }),
			hook: async () => {},
		},
	});

	assert.equal(
		countWhenCallbackReturned,
		7,
		"all 7 agents must be registered before the synchronous callback returns",
	);
	assert.ok(
		!(returned && typeof returned.then === "function"),
		"the transform callback must not return a promise the host would ignore",
	);
	assert.deepEqual(
		registered.map((agent) => agent.id).sort(),
		KIT_AGENT_IDS,
	);

	const byId = new Map(registered.map((agent) => [agent.id, agent]));

	// A parseable draft string becomes a Model.Ref rather than leaking through.
	assert.deepEqual(byId.get("research-planner").model, { providerID: "vendor", id: "draft", variant: "high" });
	// Unusable draft models are stripped, not passed to the schema.
	assert.ok(!("model" in byId.get("research-synthesizer")), "a null draft model must be dropped");
	assert.ok(!("model" in byId.get("researcher-deep")), "an incomplete draft Model.Ref must be dropped");
	assert.ok(!("model" in drafts.get("research-synthesizer")), "the draft mutation must not resurrect a bad model");

	// Rulesets are last-match-wins: the deny has to land after the draft allow.
	assert.deepEqual(byId.get("research-planner").permissions, [
		{ action: "edit", resource: "*", effect: "allow" },
		EDIT_DENY_RULE,
	]);
	assert.deepEqual(byId.get("research-synthesizer").permissions, [ALLOW_ALL_RULE, EDIT_DENY_RULE]);

	// Every agent gets its own request object, never a shared nested default.
	const firstRequest = byId.get("magic-agent").request;
	const secondRequest = byId.get("comment-sicko").request;
	assert.deepEqual(firstRequest, DEFAULT_V2_REQUEST);
	assert.notEqual(firstRequest, secondRequest);
	assert.notEqual(firstRequest.settings, secondRequest.settings);
});

test("OpenCode V2 keeps an existing tail edit-deny rule and still denies through the last rule", async (t) => {
	const mod = await importFresh(pluginPath);
	useMagicModels(t, "main: provider/workhorse#medium\n");

	const registered = [];
	const draftFor = (id) => {
		if (id === "research-planner") return { permissions: [EDIT_DENY_RULE] };
		if (id === "research-synthesizer") {
			return { permissions: [{ action: "*", resource: "*", effect: "allow" }, EDIT_DENY_RULE] };
		}
		return {};
	};
	await mod.default.setup({
		agent: {
			transform: (fn) => {
				fn({ update: (id, cb) => registered.push(cb(draftFor(id))) });
			},
		},
		skill: { transform: (fn) => fn({ add: () => {} }) },
		session: {
			get: async ({ sessionID }) => ({ id: sessionID }),
			hook: async () => {},
		},
	});

	const byId = new Map(registered.map((agent) => [agent.id, agent]));
	assert.deepEqual(byId.get("research-planner").permissions, [EDIT_DENY_RULE], "a tail deny is not duplicated");
	assert.deepEqual(byId.get("research-synthesizer").permissions, [ALLOW_ALL_RULE, EDIT_DENY_RULE]);
	assert.deepEqual(byId.get("research-synthesizer").permissions.at(-1), EDIT_DENY_RULE);
});

test("OpenCode V1 config registers kit subagents, honours user overrides, and injects rules plus magic-models", async (t) => {
	const mod = await importFresh(pluginPath);
	useMagicModels(
		t,
		"---\nalwaysApply: true\ndescription: models\n---\n# orchestrator: thin\nmain: provider/workhorse#medium\ncomment-sicko: fast\nfast: vendor/flash#max\n",
	);

	const lookups = [];
	const client = {
		session: {
			get: async ({ path: { id } }) => {
				lookups.push(id);
				return id === "rules-v1-child"
					? { data: { id, parentID: "parent-1" } }
					: { data: { id } };
			},
		},
	};
	const plugin = await mod.DotAgentsPlugin({ client, directory: repoDir });

	const config = {
		agent: {
			"comment-sicko": { model: "user/choice", temperature: 0.2 },
			"research-planner": { permission: { bash: "allow" } },
		},
	};
	await plugin.config(config);
	assert.deepEqual(config.skills.paths, [skillsDir]);
	assert.equal(Object.keys(config.agent).length, 7);
	assert.equal(config.agent["comment-sicko"].model, "user/choice", "user overrides win");
	assert.equal(config.agent["comment-sicko"].temperature, 0.2);
	assert.equal(config.agent["comment-sicko"].mode, "subagent");
	assert.equal(config.agent["researcher-mid"].model, "provider/workhorse#medium", "V1 model stays a string");
	assert.equal(config.agent["magic-agent"].model, "provider/workhorse#medium", "main tier feeds magic-agent");
	assert.equal(typeof config.agent["researcher-mid"].prompt, "string");
	assert.ok(config.agent["researcher-mid"].prompt.length > 0, "V1 config.agent uses the prompt field");
	assert.ok(!("system" in config.agent["researcher-mid"]), "V1 config.agent must not carry the V2 system field");
	assert.deepEqual(config.agent["research-synthesizer"].permission, { edit: "deny" });
	assert.deepEqual(
		config.agent["research-planner"].permission,
		{ bash: "allow", edit: "deny" },
		"a user permission override must not drop readonly enforcement",
	);
	assert.ok(!("permission" in config.agent["comment-sicko"]), "writable agents keep default permissions");

	const rootOutput = {
		messages: [{ info: { role: "user", sessionID: "rules-v1-root" }, parts: [{ type: "text", text: "go" }] }],
	};
	await plugin["experimental.chat.messages.transform"]({}, rootOutput);
	assert.equal(rootOutput.messages[0].parts.length, 2);
	const injected = rootOutput.messages[0].parts[0].text;
	assert.match(injected, /# Workflow Routing/);
	assert.match(injected, /main: provider\/workhorse#medium/);
	assert.ok(injected.indexOf("# Workflow Routing") < injected.indexOf(mod.V1_MAPPING));
	assert.ok(injected.endsWith(`${mod.V1_MAPPING}\n</EXTREMELY_IMPORTANT>`));

	const childOutput = {
		messages: [
			{
				info: { role: "user", sessionID: "rules-v1-child" },
				parts: [{ type: "text", text: "leaf" }],
			},
		],
	};
	await plugin["experimental.chat.messages.transform"]({}, childOutput);
	assert.equal(childOutput.messages[0].parts.length, 1);
	assert.deepEqual(lookups, ["rules-v1-root", "rules-v1-child"]);
});

test("OpenCode V2 root bootstrap injects rules and magic-models while child sessions still skip", async (t) => {
	const mod = await importFresh(pluginPath);
	useMagicModels(t, "---\nalwaysApply: true\n---\n# orchestrator: thin\n# budget: large\nmain: provider/workhorse#medium\n");

	const hooks = new Map();
	await mod.default.setup({
		skill: { transform: async (fn) => fn({ add: () => {} }) },
		session: {
			get: async ({ sessionID }) =>
				sessionID === "rules-v2-child" ? { id: sessionID, parentID: "parent-1" } : { id: sessionID },
			hook: async (name, cb) => {
				hooks.set(name, cb);
			},
		},
	});

	const handler = hooks.get("context");
	const rootEv = {
		sessionID: "rules-v2-root",
		messages: [{ role: "user", content: [{ type: "text", text: "Run task" }] }],
	};
	await handler(rootEv);
	assert.equal(rootEv.messages[0].content.length, 2);
	const injected = rootEv.messages[0].content[0].text;
	assert.match(injected, /# Workflow Routing/);
	assert.match(injected, /# orchestrator: thin/);
	assert.ok(injected.indexOf("# Using Magic") < injected.indexOf("# Workflow Routing"));
	assert.ok(injected.indexOf("# Workflow Routing") < injected.indexOf(mod.V2_MAPPING));

	await handler(rootEv);
	assert.equal(rootEv.messages[0].content.length, 2, "rules injection must stay idempotent");

	const childEv = {
		sessionID: "rules-v2-child",
		messages: [{ role: "user", content: [{ type: "text", text: "Leaf task" }] }],
	};
	await handler(childEv);
	assert.equal(childEv.messages[0].content.length, 1, "child sessions must not receive rules or magic-models");
});

test("OpenCode plugin prefers a profile magic-models file named by OPENCODE_CONFIG for model binding and root bootstrap", async (t) => {
	const mod = await importFresh(pluginPath);

	const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "magic-models-profile-"));
	const savedEnv = new Map(
		["HOME", "OPENCODE_CONFIG", "MAGIC_MODELS_PATH", "OPENCODE_CONFIG_DIR"].map((key) => [key, process.env[key]]),
	);
	t.after(() => {
		fs.rmSync(tmp, { recursive: true, force: true });
		for (const [key, value] of savedEnv) {
			if (value === undefined) delete process.env[key];
			else process.env[key] = value;
		}
	});

	process.env.HOME = tmp;
	delete process.env.MAGIC_MODELS_PATH;
	delete process.env.OPENCODE_CONFIG_DIR;

	const rulesDir = path.join(tmp, ".config/opencode/rules");
	const profileDir = path.join(tmp, "profile-models");
	fs.mkdirSync(rulesDir, { recursive: true });
	fs.mkdirSync(profileDir, { recursive: true });
	fs.writeFileSync(path.join(rulesDir, "magic-models.md"), "# orchestrator: thin\nmain: global/workhorse#medium\n");

	const configPath = path.join(tmp, "work-dev.json");
	fs.writeFileSync(
		configPath,
		JSON.stringify({ instructions: ["~/profile-models/magic-models-work-dev.md"] }),
	);
	fs.writeFileSync(
		path.join(profileDir, "magic-models-work-dev.md"),
		"# orchestrator: thin\n# budget: large\nmain: profile/strong#high\n",
	);
	process.env.OPENCODE_CONFIG = configPath;

	const plugin = await mod.DotAgentsPlugin({ directory: repoDir });
	const config = {};
	await plugin.config(config);
	assert.equal(
		config.agent["researcher-mid"].model,
		"profile/strong#high",
		"the profile role file must win over the shared global file",
	);
	assert.equal(config.agent["magic-agent"].model, "profile/strong#high", "main tier feeds magic-agent from the profile");

	const output = {
		messages: [{ info: { role: "user", sessionID: "profile-root" }, parts: [{ type: "text", text: "go" }] }],
	};
	await plugin["experimental.chat.messages.transform"]({}, output);
	const injected = output.messages[0].parts[0].text;
	assert.match(injected, /main: profile\/strong#high/);
	assert.match(injected, /# budget: large/);
	assert.doesNotMatch(injected, /global\/workhorse/, "the shared global file must not win the bootstrap");

	// The profile basename resolves the file even when no instruction entry names it.
	fs.writeFileSync(configPath, JSON.stringify({ instructions: [] }));
	fs.writeFileSync(
		path.join(rulesDir, "magic-models-work-dev.md"),
		"# orchestrator: thin\nmain: basename/two#medium\n",
	);
	const byName = await mod.DotAgentsPlugin({ directory: repoDir });
	const byNameConfig = {};
	await byName.config(byNameConfig);
	assert.equal(byNameConfig.agent["researcher-mid"].model, "basename/two#medium");

	// An unreadable profile config must fall through to the shared file.
	fs.writeFileSync(configPath, "{ not json");
	const origConsoleError = console.error;
	console.error = () => {};
	try {
		const broken = await mod.DotAgentsPlugin({ directory: repoDir });
		const brokenConfig = {};
		await broken.config(brokenConfig);
		assert.equal(
			brokenConfig.agent["researcher-mid"].model,
			"basename/two#medium",
			"a malformed OPENCODE_CONFIG must not throw or drop the profile-name candidate",
		);
	} finally {
		console.error = origConsoleError;
	}
});

test("OpenCode root bootstrap skips a stub magic-models candidate and falls through to a usable rule file", async (t) => {
	const mod = await importFresh(pluginPath);
	useMagicModels(t, "just prose with no role lines\n");

	const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "magic-models-stub-home-"));
	const saved = new Map(
		["HOME", "OPENCODE_CONFIG", "OPENCODE_CONFIG_DIR"].map((key) => [key, process.env[key]]),
	);
	process.env.HOME = tmp;
	delete process.env.OPENCODE_CONFIG;
	process.env.OPENCODE_CONFIG_DIR = path.join(tmp, ".config/opencode");
	fs.mkdirSync(path.join(tmp, ".config/opencode/rules"), { recursive: true });
	fs.writeFileSync(
		path.join(tmp, ".config/opencode/rules/magic-models.md"),
		"# orchestrator: standard\n# budget: large\nmain: fallback/strong#high\n",
	);
	t.after(() => {
		fs.rmSync(tmp, { recursive: true, force: true });
		for (const [key, value] of saved) {
			if (value === undefined) delete process.env[key];
			else process.env[key] = value;
		}
	});

	const plugin = await mod.DotAgentsPlugin({ directory: repoDir });
	const output = {
		messages: [{ info: { role: "user", sessionID: "guard-root" }, parts: [{ type: "text", text: "go" }] }],
	};
	await plugin["experimental.chat.messages.transform"]({}, output);
	const injected = output.messages[0].parts[0].text;
	assert.match(injected, /# Workflow Routing/);
	assert.doesNotMatch(injected, /just prose with no role lines/);
	assert.match(
		injected,
		/main: fallback\/strong#high/,
		"the unusable MAGIC_MODELS_PATH stub must not shadow a usable lower-priority file",
	);
	assert.match(injected, /# orchestrator: standard/);

	const config = {};
	await plugin.config(config);
	assert.equal(
		config.agent["researcher-mid"].model,
		"fallback/strong#high",
		"model binding must read the same non-shadowed rule file",
	);
});

test("Pi Extension & package.json: manifest contract, lifecycle hooks, multi-prompt injection, and compactionSummary ordering", async () => {
	const pkg = JSON.parse(fs.readFileSync(packageJsonPath, "utf8"));
	assert.equal(pkg.name, "magic");
	assert.equal(pkg.version, "0.2.0");
	assert.equal(pkg.type, "module");
	assert.equal(pkg.main, ".opencode/plugins/magic.js");
	assert.ok(Array.isArray(pkg.keywords) && pkg.keywords.includes("pi-package"));
	assert.deepEqual(pkg.pi, {
		extensions: ["./.pi/extensions/magic.ts"],
		skills: ["./skills"],
		subagents: { agents: ["./agents"] },
	});
	assert.equal(pkg.dependencies, undefined);
	assert.equal(pkg.devDependencies, undefined);

	const handlers = new Map();
	const pi = {
		on(event, handler) {
			if (!handlers.has(event)) handlers.set(event, []);
			handlers.get(event).push(handler);
		},
	};
	const extMod = await importFresh(piExtensionPath);
	extMod.default(pi);

	assert.equal((handlers.get("resources_discover") ?? []).length, 0);
	assert.equal((handlers.get("session_before_compact") ?? []).length, 0);
	for (const event of ["session_start", "session_compact", "context"]) {
		assert.equal((handlers.get(event) ?? []).length, 1, `expected one ${event} handler`);
	}

	const emit = async (event, payload = {}) => {
		for (const handler of handlers.get(event) ?? []) {
			await handler({ type: event, ...payload }, {});
		}
	};
	const contextHandler = handlers.get("context")[0];
	const textOf = (msg) =>
		typeof msg.content === "string"
			? msg.content
			: msg.content
					.filter((p) => p.type === "text")
					.map((p) => p.text)
					.join("\n");

	await emit("session_start", { reason: "startup" });

	const history = [];
	const prompts = [
		{ text: "first prompt", providerRequests: 1 },
		{ text: "second prompt with tool loop", providerRequests: 2 },
		{ text: "third prompt", providerRequests: 1 },
	];
	for (const [promptIdx, prompt] of prompts.entries()) {
		history.push({ role: "user", content: [{ type: "text", text: prompt.text }], timestamp: promptIdx });
		for (let req = 1; req <= prompt.providerRequests; req += 1) {
			const res = await contextHandler({ type: "context", messages: structuredClone(history) }, {});
			assert.ok(res, `prompt ${promptIdx + 1} req ${req} must return injected messages`);
			assert.equal(res.messages.length, history.length + 1);
			assert.equal(res.messages[0].role, "user");
			assert.match(textOf(res.messages[0]), /You have magic\./);
			assert.match(textOf(res.messages[0]), /# Using Magic/);
			assert.match(textOf(res.messages[0]), /# Workflow Routing/);
			assert.match(textOf(res.messages[0]), /## Pi tool mapping/);
			assert.ok(
				textOf(res.messages[0]).indexOf("# Using Magic") <
					textOf(res.messages[0]).indexOf("# Workflow Routing"),
				"rules must follow the using-magic content",
			);
			assert.ok(
				textOf(res.messages[0]).indexOf("# Workflow Routing") <
					textOf(res.messages[0]).indexOf("## Pi tool mapping"),
				"rules must precede the Pi tool mapping",
			);
			assert.doesNotMatch(textOf(res.messages[0]), /alwaysApply:/, "rules must arrive without frontmatter");

			const duplicateCheck = await contextHandler({ type: "context", messages: res.messages }, {});
			assert.equal(duplicateCheck, undefined, "must not duplicate when bootstrap is already present");

			history.push({ role: "assistant", content: [{ type: "text", text: "ok" }], timestamp: promptIdx });
		}
	}

	await emit("session_compact", { compactionEntry: {}, fromExtension: false });
	const summary1 = { role: "compactionSummary", summary: "Summary 1", tokensBefore: 100, timestamp: 1 };
	const summary2 = { role: "compactionSummary", summary: "Summary 2", tokensBefore: 200, timestamp: 2 };
	const nextUser = { role: "user", content: [{ type: "text", text: "Continue" }], timestamp: 3 };
	const compactedRes = await contextHandler({ type: "context", messages: [summary1, summary2, nextUser] }, {});
	assert.equal(compactedRes.messages.length, 4);
	assert.equal(compactedRes.messages[0], summary1);
	assert.equal(compactedRes.messages[1], summary2);
	assert.equal(compactedRes.messages[2].role, "user");
	assert.match(textOf(compactedRes.messages[2]), /You have magic\./);
	assert.equal(compactedRes.messages[3], nextUser);
});

async function piBootstrapText(t, modelsContents) {
	useMagicModels(t, modelsContents);

	const handlers = new Map();
	const pi = {
		on(event, handler) {
			handlers.set(event, handler);
		},
	};
	const extMod = await importFresh(piExtensionPath);
	extMod.default(pi);

	const res = await handlers.get("context")(
		{ type: "context", messages: [{ role: "user", content: [{ type: "text", text: "go" }] }] },
		{},
	);
	return res.messages[0].content.map((part) => part.text).join("\n");
}

test("Pi extension injects the consumer magic-models rule between kit rules and the Pi tool mapping", async (t) => {
	const injected = await piBootstrapText(
		t,
		"---\nalwaysApply: true\ndescription: models\n---\n# orchestrator: thin\n# budget: large (xhigh)\nmain: provider/workhorse#medium\n",
	);

	assert.match(injected, /# Workflow Routing/);
	assert.match(injected, /# orchestrator: thin/);
	assert.match(injected, /# budget: large \(xhigh\)/);
	assert.match(injected, /main: provider\/workhorse#medium/);
	assert.doesNotMatch(injected, /alwaysApply:/, "magic-models frontmatter must be stripped");
	assert.ok(
		injected.indexOf("# Workflow Routing") < injected.indexOf("# orchestrator: thin"),
		"magic-models must follow the kit rules",
	);
	assert.ok(
		injected.indexOf("# orchestrator: thin") < injected.indexOf("## Pi tool mapping"),
		"magic-models must precede the Pi tool mapping",
	);
});

test("Pi extension ignores a stub magic-models candidate and falls through to a usable rule file", async (t) => {
	const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "magic-models-pi-home-"));
	const savedHome = process.env.HOME;
	process.env.HOME = tmp;
	fs.mkdirSync(path.join(tmp, ".agents/rules"), { recursive: true });
	fs.writeFileSync(
		path.join(tmp, ".agents/rules/magic-models.md"),
		"# orchestrator: standard\n# budget: large\nmain: fallback/strong#high\n",
	);
	t.after(() => {
		fs.rmSync(tmp, { recursive: true, force: true });
		if (savedHome === undefined) delete process.env.HOME;
		else process.env.HOME = savedHome;
	});

	const injected = await piBootstrapText(t, "just prose with no role lines\n");

	assert.match(injected, /# Workflow Routing/);
	assert.doesNotMatch(injected, /just prose with no role lines/);
	assert.match(
		injected,
		/main: fallback\/strong#high/,
		"the unusable MAGIC_MODELS_PATH stub must not shadow a usable lower-priority file",
	);
	assert.match(injected, /# orchestrator: standard/);
});
