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

const expectedMarker = "<EXTREMELY_IMPORTANT>\nYou have magic.";
let importCounter = 0;

async function importFresh(filePath) {
	const url = pathToFileURL(filePath).href;
	return import(`${url}?t=${++importCounter}`);
}

const KIT_AGENT_IDS = [
	"comment-sicko",
	"magic-agent",
	"research-planner",
	"research-synthesizer",
	"researcher-deep",
	"researcher-lite",
	"researcher-mid",
];

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

test("OpenCode V1: MagicPlugin registers skills path, injects V1 bootstrap idempotently, and skips child sessions", async () => {
	const canonicalMod = await import(pathToFileURL(pluginPath).href);
	const indexMod = await import(pathToFileURL(indexPath).href);
	assert.equal(indexMod.default, canonicalMod.default);

	const mod = await importFresh(pluginPath);
	assert.equal(mod.default.id, "magic");
	assert.equal(mod.default.server, mod.MagicPlugin);

	const lookups = [];
	const sessions = new Map([
		["sess-root", { data: { id: "sess-root" } }],
		["sess-child", { data: { id: "sess-child", parentID: "parent-1" } }],
	]);
	const client = {
		session: {
			get: async ({ path: { id } }) => {
				lookups.push(id);
				return sessions.get(id) ?? { data: { id, parentID: "parent-1" } };
			},
		},
	};

	const plugin = await mod.DotAgentsPlugin({ client, directory: repoDir });
	const v1Config = {};
	await plugin.config(v1Config);
	assert.deepEqual(v1Config.skills.paths, [skillsDir]);

	const transform = plugin["experimental.chat.messages.transform"];
	const rootOutput = {
		messages: [{ info: { role: "user", sessionID: "sess-root" }, parts: [{ type: "text", text: "Task" }] }],
	};
	await transform({}, rootOutput);
	assert.equal(rootOutput.messages[0].parts.length, 2);
	assert.ok(rootOutput.messages[0].parts[0].text.startsWith(expectedMarker));

	await transform({}, rootOutput);
	assert.equal(rootOutput.messages[0].parts.length, 2, "repeat call must be idempotent");

	const childOutput = {
		messages: [{ info: { role: "user", sessionID: "sess-child" }, parts: [{ type: "text", text: "Child" }] }],
	};
	await transform({}, childOutput);
	assert.equal(childOutput.messages[0].parts.length, 1, "child session must skip bootstrap");
});

test("OpenCode V2: default.setup registers 75 skills, hooks context/compaction/generate, and skips child sessions", async () => {
	const mod = await importFresh(pluginPath);
	await mod.default.setup({});

	const addedSkills = [];
	const hooks = new Map();
	const sessionRecords = new Map([
		["v2-root", { id: "v2-root" }],
		["v2-child", { id: "v2-child", parentID: "parent-1" }],
		["v2-compacted", { id: "v2-compacted" }],
	]);

	await mod.default.setup({
		skill: { transform: async (fn) => fn({ add: (s) => addedSkills.push(s) }) },
		session: {
			get: async ({ sessionID }) => sessionRecords.get(sessionID) ?? { id: sessionID },
			hook: async (name, cb) => hooks.set(name, cb),
		},
	});

	assert.equal(addedSkills.length, 75);
	assert.deepEqual([...hooks.keys()].sort(), ["compaction", "context", "generate"]);

	const handler = hooks.get("context");
	const rootEv = { sessionID: "v2-root", messages: [{ role: "user", content: [{ type: "text", text: "Run" }] }] };
	await handler(rootEv);
	assert.equal(rootEv.messages[0].content.length, 2);
	assert.ok(rootEv.messages[0].content[0].text.startsWith(expectedMarker));

	const childEv = { sessionID: "v2-child", messages: [{ role: "user", content: [{ type: "text", text: "Leaf" }] }] };
	await handler(childEv);
	assert.equal(childEv.messages[0].content.length, 1);
});

test("OpenCode V2_MAPPING restores todowrite and documents kit subagent model authorization", async () => {
	const mod = await importFresh(pluginPath);
	assert.match(mod.V2_MAPPING, /todowrite/);
	assert.doesNotMatch(mod.V2_MAPPING, /OpenCode v2 has no todo tool/);
	assert.match(mod.V2_MAPPING, /entries in `magic-models` are explicit user model selections/);
});

test("OpenCode resolveAgentModel dereferences tier names, strips comments, and falls back to models.json", async () => {
	const mod = await importFresh(pluginPath);
	const parsed = {
		roles: {
			"fast, mechanical, miners": "fast",
			"researcher-lite, collectors": "fast",
			"researcher-mid": "main",
			"researcher-deep, planner, synthesizer": "deep",
			"comment-sicko": "main",
			"feature, refactoring": "main",
			main: "provider/workhorse#medium # inline comment",
			deep: "provider/frontier#high",
		},
	};
	const presets = { fast: "provider/flash#low", main: "fallback/main", deep: "fallback/deep" };

	assert.equal(mod.resolveAgentModel("researcher-lite", parsed, presets), "provider/flash#low");
	assert.equal(mod.resolveAgentModel("researcher-mid", parsed, presets), "provider/workhorse#medium");
	assert.equal(mod.resolveAgentModel("magic-agent", parsed, presets), "provider/workhorse#medium");
	assert.equal(mod.resolveAgentModel("researcher-deep", parsed, presets), "provider/frontier#high");

	const inheritParsed = { roles: { "feature, refactoring": "inherit-parent", main: "provider/main" } };
	assert.equal(mod.resolveAgentModel("magic-agent", inheritParsed, presets), undefined);
});

test("OpenCode V2 parseModelRef splits provider, model id, and variant cleanly", async () => {
	const mod = await importFresh(pluginPath);
	assert.deepEqual(mod.parseModelRef("google/gemini-4-carbon#high"), {
		providerID: "google",
		id: "gemini-4-carbon",
		variant: "high",
	});
	assert.deepEqual(mod.parseModelRef("anthropic/claude-3-7-sonnet"), {
		providerID: "anthropic",
		id: "claude-3-7-sonnet",
	});
	assert.equal(mod.parseModelRef("invalid"), undefined);
	assert.equal(mod.parseModelRef(""), undefined);
});
test("OpenCode V2 setup registers all 7 kit subagents with mode: 'subagent', system prompt, and depth-1 leaf permissions", async (t) => {
	const mod = await importFresh(pluginPath);
	useMagicModels(
		t,
		"---\nalwaysApply: true\ndescription: models\n---\n# orchestrator: thin\n# budget: large (xhigh)\nmain: provider/workhorse#medium\nresearcher-lite, collectors: provider/flash#low\n",
	);

	const byId = new Map();
	await mod.default.setup({
		agent: {
			transform: (fn) => {
				fn({
					update: (id, updateFn) => {
						const draft = {};
						const res = updateFn(draft);
						byId.set(id, res);
					},
				});
			},
		},
		skill: { transform: (fn) => fn({ add: () => {} }) },
		session: { get: async ({ sessionID }) => ({ id: sessionID }), hook: async () => {} },
	});

	assert.equal(byId.size, 7);
	for (const id of KIT_AGENT_IDS) {
		const agent = byId.get(id);
		assert.ok(agent, `missing agent ${id}`);
		assert.equal(agent.mode, "subagent");
		assert.ok(typeof agent.system === "string" && agent.system.length > 0);
		// All kit agents must deny subagent and question
		assert.ok(agent.permissions.some((p) => (p.action === "subagent" || p.action === "*") && p.effect === "deny"));
		assert.ok(agent.permissions.some((p) => (p.action === "question" || p.action === "*") && p.effect === "deny"));
	}

	const planner = byId.get("research-planner");
	assert.deepEqual(planner.permissions, [{ action: "*", resource: "*", effect: "deny" }]);

	const synth = byId.get("research-synthesizer");
	assert.ok(synth.permissions.some((p) => p.action === "edit" && p.resource === "*" && p.effect === "deny"));
	assert.ok(synth.permissions.some((p) => p.action === "edit" && p.resource === "docs/research/*" && p.effect === "allow"));
});

test("OpenCode V1 config registers all 7 kit agents with subagent mode, prompt, and leaf permissions", async (t) => {
	const mod = await importFresh(pluginPath);
	useMagicModels(t, "main: provider/workhorse#medium\n");

	const plugin = await mod.MagicPlugin({});
	const config = { agent: { "research-planner": { custom: true } } };
	await plugin.config(config);

	for (const id of KIT_AGENT_IDS) {
		const a = config.agent[id];
		assert.ok(a);
		assert.equal(a.mode, "subagent");
		assert.equal(a.permission.subagent, "deny");
		assert.equal(a.permission.question, "deny");
	}
	assert.equal(config.agent["research-planner"].permission["*"], "deny");
	assert.equal(config.agent["research-planner"].custom, true);
});

test("OpenCode plugin prioritizes OPENCODE_CONFIG profile instructions over global fallback", async (t) => {
	const mod = await importFresh(pluginPath);
	const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "opencode-profile-test-"));
	t.after(() => fs.rmSync(tmp, { recursive: true, force: true }));

	const profileRolePath = path.join(tmp, "magic-models-work.md");
	fs.writeFileSync(profileRolePath, "# orchestrator: thin\nmain: profile/workhorse#high\n");

	const profileConfigPath = path.join(tmp, "work.json");
	fs.writeFileSync(profileConfigPath, JSON.stringify({ instructions: [profileRolePath] }));

	const prevConfig = process.env.OPENCODE_CONFIG;
	const prevMagic = process.env.MAGIC_MODELS_PATH;
	delete process.env.MAGIC_MODELS_PATH;
	process.env.OPENCODE_CONFIG = profileConfigPath;
	t.after(() => {
		if (prevConfig === undefined) delete process.env.OPENCODE_CONFIG;
		else process.env.OPENCODE_CONFIG = prevConfig;
		if (prevMagic === undefined) delete process.env.MAGIC_MODELS_PATH;
		else process.env.MAGIC_MODELS_PATH = prevMagic;
	});

	const plugin = await mod.MagicPlugin({});
	const config = {};
	await plugin.config(config);

	assert.equal(config.agent["researcher-mid"].model, "profile/workhorse#high");
});
