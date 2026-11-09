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
			assert.match(textOf(res.messages[0]), /## Pi tool mapping/);

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
