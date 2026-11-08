import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";

const repoDir = path.resolve(import.meta.dirname, "..");

function resolveDotField(obj, fieldPath) {
	return fieldPath.split(".").reduce((acc, part) => {
		if (acc === null || acc === undefined) return undefined;
		const key = /^\d+$/.test(part) ? Number(part) : part;
		return acc[key];
	}, obj);
}

test(".version-bump.json lists all 5 plugin/package manifests and locks them to the same semver version (0.2.0)", () => {
	const versionBumpPath = path.join(repoDir, ".version-bump.json");
	const config = JSON.parse(fs.readFileSync(versionBumpPath, "utf8"));

	assert.deepEqual(config, {
		files: [
			{ path: "package.json", field: "version" },
			{ path: ".claude-plugin/plugin.json", field: "version" },
			{ path: ".claude-plugin/marketplace.json", field: "plugins.0.version" },
			{ path: ".cursor-plugin/plugin.json", field: "version" },
			{ path: ".codex-plugin/plugin.json", field: "version" },
		],
	});

	const versions = new Set();
	for (const entry of config.files) {
		const targetPath = path.join(repoDir, entry.path);
		assert.ok(fs.existsSync(targetPath), `missing manifest listed in .version-bump.json: ${entry.path}`);
		const json = JSON.parse(fs.readFileSync(targetPath, "utf8"));
		const version = resolveDotField(json, entry.field);
		assert.equal(typeof version, "string", `${entry.path} (${entry.field}) must be a string`);
		assert.match(version, /^\d+\.\d+\.\d+$/, `${entry.path} (${entry.field}) must be semver`);
		assert.equal(version, "0.2.0", `${entry.path} (${entry.field}) expected 0.2.0`);
		versions.add(version);
	}
	assert.equal(versions.size, 1, "all manifests in .version-bump.json must share the exact same version");
});

test("THIRD-PARTY-NOTICES.md documents obra/superpowers plugin and bootstrap files under MIT", () => {
	const notices = fs.readFileSync(path.join(repoDir, "THIRD-PARTY-NOTICES.md"), "utf8");
	assert.match(notices, /obra\/superpowers/);
	assert.match(notices, /22f0b463e7a5e579904dd6211a520321035526f7/);
	for (const requiredRef of [
		"hooks/run-hook.cmd",
		"hooks/session-start",
		".opencode/plugins/dot-agents.js",
		".pi/extensions/dot-agents.ts",
	]) {
		assert.ok(
			notices.includes(requiredRef),
			`THIRD-PARTY-NOTICES.md must document ${requiredRef}`,
		);
	}
});

test("README.md and .gitignore document 74 skills, 4 rules, multi-harness installation, and node_modules ignores", () => {
	const readme = fs.readFileSync(path.join(repoDir, "README.md"), "utf8");
	for (const expectedSnippet of [
		"**74 active skills**",
		"**4 operational rules**",
		"Native Plugin Installation (Superpowers-Style)",
		"/plugin marketplace add PhillipChaffee/.agents",
		"/plugin install dot-agents@dot-agents-dev",
		".cursor-plugin/plugin.json",
		".agents/plugins/marketplace.json",
		"dot-agents@git+https://github.com/PhillipChaffee/.agents.git",
		"pi install git:github.com/PhillipChaffee/.agents",
		"./scripts/install.sh --target agents",
		"skills/using-poteto/SKILL.md",
		"rules/workflow-routing.md",
	]) {
		assert.ok(readme.includes(expectedSnippet), `README.md missing: ${expectedSnippet}`);
	}

	const gitignoreLines = fs
		.readFileSync(path.join(repoDir, ".gitignore"), "utf8")
		.split(/\r?\n/)
		.map((l) => l.trim());
	assert.ok(gitignoreLines.includes("node_modules/"), ".gitignore must ignore node_modules/");
	assert.ok(gitignoreLines.includes(".opencode/node_modules/"), ".gitignore must ignore .opencode/node_modules/");
	assert.ok(!gitignoreLines.includes("package.json"), ".gitignore must not ignore root package.json");
});

