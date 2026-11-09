import { spawnSync } from "node:child_process";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";

const repoDir = path.resolve(import.meta.dirname, "..");
const renderGraphsScript = path.join(repoDir, "skills/writing-skills/render-graphs.js");

test("rules/, agents.kit.md, README.md, and docs/CATALOG.md satisfy the universal rule packaging contract", () => {
	const rulesDir = path.join(repoDir, "rules");
	const ruleEntries = fs
		.readdirSync(rulesDir)
		.filter((f) => f.endsWith(".md"))
		.sort();
	assert.ok(ruleEntries.length > 0, "expected at least one rule in rules/");

	const catalogText = fs.readFileSync(path.join(repoDir, "docs/CATALOG.md"), "utf8");
	const readmeText = fs.readFileSync(path.join(repoDir, "README.md"), "utf8");

	for (const entry of ruleEntries) {
		const text = fs.readFileSync(path.join(rulesDir, entry), "utf8");
		assert.ok(text.startsWith("---\n"), `${entry}: missing frontmatter`);
		const end = text.indexOf("\n---", 4);
		assert.notEqual(end, -1, `${entry}: malformed frontmatter`);

		const fm = text.slice(4, end);
		const globsLine = fm.split("\n").find((line) => line.startsWith("globs:"));
		if (globsLine) {
			const rawGlobs = globsLine.slice("globs:".length).trim();
			assert.doesNotMatch(rawGlobs, /^\*/, `${entry}: unquoted '*' in globs is invalid YAML`);
		}

		const body = text.slice(end + 4).trim();
		const bodyWords = body.split(/\s+/).filter(Boolean).length;
		assert.ok(bodyWords < 250, `${entry}: body has ${bodyWords} words (budget < 250)`);
		assert.ok(catalogText.includes(`rules/${entry}`), `docs/CATALOG.md is missing an entry for rules/${entry}`);
	}

	assert.match(
		readmeText,
		new RegExp(`\\*\\*${ruleEntries.length} operational rules\\*\\*`),
		`README.md operational rule count must match rules/ count (${ruleEntries.length})`,
	);
	assert.match(
		catalogText,
		new RegExp(`\\*\\*${ruleEntries.length} operational rules\\*\\*`),
		`docs/CATALOG.md header operational rule count must match rules/ count (${ruleEntries.length})`,
	);
	assert.match(
		catalogText,
		new RegExp(`^## ${ruleEntries.length} Operational Rules`, "m"),
		`docs/CATALOG.md section heading count must match rules/ count (${ruleEntries.length})`,
	);

	const kitLines = fs
		.readFileSync(path.join(repoDir, "agents.kit.md"), "utf8")
		.trim()
		.split("\n");
	for (const line of kitLines) {
		assert.match(line, /^- /, `agents.kit.md line must be a single bullet: ${line}`);
		assert.doesNotMatch(line, /—/, `agents.kit.md line must not contain em dashes: ${line}`);
		const words = line.trim().split(/\s+/).filter(Boolean).length;
		assert.ok(words <= 25, `agents.kit.md bullet has ${words} words (budget <= 25): ${line}`);
	}
});

test("workflow-routing.md, agents.kit.md, and using-magic route PR/MR creation and updates to /make-pr-easy-to-review", () => {
	const routingRule = fs.readFileSync(path.join(repoDir, "rules/workflow-routing.md"), "utf8");
	assert.match(routingRule, /\/make-pr-easy-to-review/);
	assert.match(routingRule, /pull request or merge request/i);
	assert.match(
		routingRule,
		/subtask that does not open or update a pull request or merge request/i,
	);

	const kitText = fs.readFileSync(path.join(repoDir, "agents.kit.md"), "utf8");
	assert.match(kitText, /\/make-pr-easy-to-review/);

	const usingMagic = fs.readFileSync(path.join(repoDir, "skills/using-magic/SKILL.md"), "utf8");
	assert.match(usingMagic, /\/make-pr-easy-to-review/);
	assert.match(
		usingMagic,
		/subtask that does not open or update a pull request or merge request/i,
	);
});

test("writing-rules rule_triage flowchart renders cleanly with render-graphs.js", (t) => {
	const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "writing-rules-graph-"));
	t.after(() => fs.rmSync(tmpDir, { recursive: true, force: true }));

	const dotStub = path.join(tmpDir, "dot");
	fs.writeFileSync(dotStub, "#!/bin/sh\ncat >/dev/null\nprintf '<svg/>\\n'\n", { mode: 0o755 });
	const env = { ...process.env, PATH: `${tmpDir}${path.delimiter}${process.env.PATH}` };

	const skillCopyDir = path.join(tmpDir, "writing-rules");
	fs.mkdirSync(skillCopyDir);
	fs.copyFileSync(path.join(repoDir, "skills/writing-rules/SKILL.md"), path.join(skillCopyDir, "SKILL.md"));

	const res = spawnSync(process.execPath, [renderGraphsScript, skillCopyDir], { env, encoding: "utf8" });
	assert.equal(res.status, 0, res.stderr);
	assert.ok(fs.existsSync(path.join(skillCopyDir, "diagrams/rule_triage.svg")));
});
