import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { pathToFileURL } from "node:url";

const repoDir = path.resolve(import.meta.dirname, "..");
const piExtensionPath = path.join(repoDir, ".pi/extensions/magic.ts");
const packageJsonPath = path.join(repoDir, "package.json");

let importCounter = 0;

async function importFresh(filePath) {
	const url = pathToFileURL(filePath).href;
	return import(`${url}?t=${++importCounter}`);
}

function useMagicModels(t, contents) {
	const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "magic-models-pi-"));
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
