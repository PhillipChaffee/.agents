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
	assert.match(notices, /22f0b463e7a5e579904dd6211a5e579904dd6211a520321035526f7|22f0b463e7a5e579904dd6211a520321035526f7/);
	for (const requiredRef of [
		"hooks/run-hook.cmd",
		"hooks/session-start",
		"lib/bootstrap-core.js",
		".opencode/plugins/magic.js",
		".pi/extensions/magic.ts",
	]) {
		assert.ok(
			notices.includes(requiredRef),
			`THIRD-PARTY-NOTICES.md must document ${requiredRef}`,
		);
	}
});

test("README.md and .gitignore document magic quote, SVG workflow diagram, section order (Installation -> The Basic Workflow -> Acknowledgments -> Catalog Reference), and node_modules ignores", () => {
	const readme = fs.readFileSync(path.join(repoDir, "README.md"), "utf8");
	for (const expectedSnippet of [
		"# magic",
		"assets/magic-banner.png",
		"assets/workflow-diagram.svg",
		"Any sufficiently advanced technology is indistinguishable from magic.",
		"Arthur C. Clarke",
		"## Installation",
		"### 1. Native Plugin Installation (Superpowers-Style)",
		"### 2. Use as a `.agents` Directory (`~/.agents` or `.agents/`)",
		"#### What Works vs. What Does Not Work in `.agents` Directory Mode",
		"You never need to invoke `/using-poteto` yourself",
		"## The Basic Workflow",
		"## Acknowledgments",
		"Native Plugin Installation (Superpowers-Style)",
		"/plugin marketplace add PhillipChaffee/magic",
		"/plugin install magic@magic-dev",
		".cursor-plugin/plugin.json",
		".agents/plugins/marketplace.json",
		"magic@git+https://github.com/PhillipChaffee/magic.git",
		"pi install git:github.com/PhillipChaffee/magic",
		"./scripts/install.sh --target agents",
		"skills/using-poteto/SKILL.md",
		"rules/workflow-routing.md",
	]) {
		assert.ok(readme.includes(expectedSnippet), `README.md missing: ${expectedSnippet}`);
	}

	assert.ok(
		!readme.includes("Vendor-neutral AI coding kit"),
		"Vendor-neutral prose line must be removed",
	);
	assert.ok(!readme.includes("[![validate]("), "Badges must be removed");
	assert.ok(!readme.includes("## How to Use It"), "## How to Use It section must be removed");
	assert.ok(
		fs.existsSync(path.join(repoDir, "assets/magic-banner.png")),
		"assets/magic-banner.png must exist",
	);
	assert.ok(
		fs.existsSync(path.join(repoDir, "assets/workflow-diagram.svg")),
		"assets/workflow-diagram.svg must exist",
	);

	const headingIdx = readme.indexOf("# magic");
	const bannerIdx = readme.indexOf("assets/magic-banner.png");
	const quoteIdx = readme.indexOf("Any sufficiently advanced technology is indistinguishable from magic.");
	const installIdx = readme.indexOf("## Installation");
	const workflowIdx = readme.indexOf("## The Basic Workflow");
	const ackIdx = readme.indexOf("## Acknowledgments");
	const catalogIdx = readme.indexOf("## Catalog Reference");
	assert.ok(headingIdx === 0 && bannerIdx > headingIdx && bannerIdx < quoteIdx, "Banner must appear right under # magic");
	assert.ok(quoteIdx < installIdx, "Quote must appear before ## Installation");
	assert.ok(installIdx < workflowIdx, "## Installation must appear before ## The Basic Workflow");
	assert.ok(workflowIdx < ackIdx, "## The Basic Workflow must appear before ## Acknowledgments");
	assert.ok(ackIdx < catalogIdx, "## Acknowledgments must appear before ## Catalog Reference");

	const gitignoreLines = fs
		.readFileSync(path.join(repoDir, ".gitignore"), "utf8")
		.split(/\r?\n/)
		.map((l) => l.trim());
	assert.ok(gitignoreLines.includes("node_modules/"), ".gitignore must ignore node_modules/");
	assert.ok(gitignoreLines.includes(".opencode/node_modules/"), ".gitignore must ignore .opencode/node_modules/");
	assert.ok(!gitignoreLines.includes("package.json"), ".gitignore must not ignore root package.json");
});

