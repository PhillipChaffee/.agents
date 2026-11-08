import { spawnSync } from "node:child_process";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";

const repoDir = path.resolve(import.meta.dirname, "..");
const renderGraphsScript = path.join(repoDir, "skills/writing-skills/render-graphs.js");

test("writing-rules skill satisfies SDO frontmatter, triage gates, and TDD contract", () => {
	const skillFile = path.join(repoDir, "skills/writing-rules/SKILL.md");
	assert.ok(fs.existsSync(skillFile), "missing skills/writing-rules/SKILL.md");
	const content = fs.readFileSync(skillFile, "utf8");
	assert.ok(content.startsWith("---\n"), "missing frontmatter start");
	const fmEnd = content.indexOf("\n---", 4);
	assert.notEqual(fmEnd, -1, "missing frontmatter end");

	const fm = content.slice(4, fmEnd);
	assert.ok(fm.length <= 1024, "frontmatter exceeds 1024 chars");
	assert.match(fm, /^description: "Use when /m, "description must start with 'Use when '");
	assert.match(fm, /^enabled: true$/m, "enabled must be true");
	assert.match(fm, /^id: writing-rules$/m, "id must match directory");
	assert.match(fm, /^name: writing-rules$/m, "name must match directory");

	const topKeys = fm
		.split("\n")
		.filter((line) => /^[a-z]+:/.test(line))
		.map((line) => line.split(":")[0]);
	assert.deepEqual(topKeys, [...topKeys].sort(), "frontmatter keys must be sorted alphabetically");

	assert.match(content, /NO RULE WITHOUT A FAILING BASELINE AND A STRUCTURAL-ENFORCEMENT CHECK FIRST/);
	assert.match(content, /digraph rule_triage/);
	assert.match(content, /## Common Mistakes & Rationalizations/);
	assert.match(content, /## Red Flags - STOP and Fix Properly/);
});

test("all repository rules in rules/ and agents.kit.md satisfy writing-rules packaging contract", () => {
	const rulesDir = path.join(repoDir, "rules");
	const ruleEntries = fs.readdirSync(rulesDir).filter((f) => f.endsWith(".md"));
	assert.ok(ruleEntries.length >= 3, "expected at least 3 rules in rules/");

	for (const entry of ruleEntries) {
		const text = fs.readFileSync(path.join(rulesDir, entry), "utf8");
		assert.ok(text.startsWith("---\n"), `${entry}: missing frontmatter`);
		const end = text.indexOf("\n---", 4);
		assert.notEqual(end, -1, `${entry}: malformed frontmatter`);
		const fm = text.slice(4, end);
		const keys = fm
			.split("\n")
			.filter((line) => /^[A-Za-z][A-Za-z0-9-]*:/.test(line))
			.map((line) => line.split(":")[0]);
		assert.ok(keys.includes("alwaysApply"), `${entry}: missing alwaysApply`);
		assert.ok(keys.includes("description"), `${entry}: missing description`);
		assert.deepEqual(keys, [...keys].sort(), `${entry}: frontmatter keys not sorted`);
	}

	const kitLines = fs
		.readFileSync(path.join(repoDir, "agents.kit.md"), "utf8")
		.trim()
		.split("\n");
	for (const line of kitLines) {
		assert.match(line, /^- /, `agents.kit.md line must be a single bullet: ${line}`);
	}
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

test("workflow-routing rule, agents.kit.md pointer, using-magic bootstrap skill, and magic-mode SDO trigger satisfy routing contract", () => {
	const routingFile = path.join(repoDir, "rules/workflow-routing.md");
	const routingText = fs.readFileSync(routingFile, "utf8");
	assert.ok(routingText.startsWith("---\n"), "workflow-routing.md: missing frontmatter start");
	const routingFmEnd = routingText.indexOf("\n---", 4);
	assert.notEqual(routingFmEnd, -1, "workflow-routing.md: missing frontmatter end");
	const routingFm = routingText.slice(4, routingFmEnd);
	const routingKeys = routingFm
		.split("\n")
		.filter((line) => /^[A-Za-z][A-Za-z0-9-]*:/.test(line))
		.map((line) => line.split(":")[0]);
	assert.deepEqual(routingKeys, ["alwaysApply", "description"]);

	const routingBody = routingText.slice(routingFmEnd + 4).trim();
	const bodyWordCount = routingBody.split(/\s+/).filter(Boolean).length;
	assert.ok(bodyWordCount < 150, `workflow-routing.md body has ${bodyWordCount} words (expected < 150)`);
	assert.match(routingBody, /\/magic-mode/);
	assert.match(routingBody, /\/research/);
	assert.match(routingBody, /\/proof-driven-development/);

	const kitLines = fs
		.readFileSync(path.join(repoDir, "agents.kit.md"), "utf8")
		.trim()
		.split("\n");
	assert.ok(
		kitLines.some((line) => line.startsWith("- ") && line.includes("rules/workflow-routing.md")),
		"agents.kit.md must contain a bullet linking to rules/workflow-routing.md",
	);
	for (const line of kitLines) {
		const words = line.trim().split(/\s+/).filter(Boolean);
		assert.ok(words.length <= 25, `agents.kit.md line exceeds 25 words (${words.length}): ${line}`);
	}

	const usingMagicFile = path.join(repoDir, "skills/using-magic/SKILL.md");
	assert.ok(fs.existsSync(usingMagicFile), "missing skills/using-magic/SKILL.md");
	const usingMagicText = fs.readFileSync(usingMagicFile, "utf8");
	assert.ok(usingMagicText.startsWith("---\n"), "using-magic: missing frontmatter start");
	const upFmEnd = usingMagicText.indexOf("\n---", 4);
	assert.notEqual(upFmEnd, -1, "using-magic: missing frontmatter end");
	const upFm = usingMagicText.slice(4, upFmEnd);
	const upKeys = upFm
		.split("\n")
		.filter((line) => /^[A-Za-z][A-Za-z0-9-]*:/.test(line))
		.map((line) => line.split(":")[0]);
	assert.deepEqual(upKeys, ["description", "enabled", "id", "name"]);
	assert.match(usingMagicText, /<SUBAGENT-STOP>/);
	assert.match(usingMagicText, /<EXTREMELY-IMPORTANT>/);
	assert.match(usingMagicText, /\.\.\/magic-mode\/references\/harness-adapter\.md/);

	const magicModeText = fs.readFileSync(path.join(repoDir, "skills/magic-mode/SKILL.md"), "utf8");
	const pmFmEnd = magicModeText.indexOf("\n---", 4);
	const pmFm = magicModeText.slice(4, pmFmEnd);
	assert.match(pmFm, /^description: ["']?Use when /m, "magic-mode description must start with 'Use when'");

	const harnessAdapterText = fs.readFileSync(
		path.join(repoDir, "skills/magic-mode/references/harness-adapter.md"),
		"utf8",
	);
	assert.match(harnessAdapterText, /spawn_agent \{fork_turns: "none"\}/);
	assert.match(harnessAdapterText, /followup_task/);
	assert.match(harnessAdapterText, /wait_agent/);
	assert.match(harnessAdapterText, /pi-subagents/);
	assert.match(harnessAdapterText, /TODO\.md/);
});

test("large-file-creation rule satisfies frontmatter, word budget, and agents.kit.md link", () => {
	const largeFile = path.join(repoDir, "rules/large-file-creation.md");
	assert.ok(fs.existsSync(largeFile), "missing rules/large-file-creation.md");
	const text = fs.readFileSync(largeFile, "utf8");
	assert.ok(text.startsWith("---\n"), "large-file-creation.md: missing frontmatter start");
	const fmEnd = text.indexOf("\n---", 4);
	assert.notEqual(fmEnd, -1, "large-file-creation.md: missing frontmatter end");
	const fm = text.slice(4, fmEnd);
	const keys = fm
		.split("\n")
		.filter((line) => /^[A-Za-z][A-Za-z0-9-]*:/.test(line))
		.map((line) => line.split(":")[0]);
	assert.deepEqual(keys, ["alwaysApply", "description"]);

	const body = text.slice(fmEnd + 4).trim();
	const bodyWordCount = body.split(/\s+/).filter(Boolean).length;
	assert.ok(bodyWordCount < 150, `large-file-creation.md body has ${bodyWordCount} words (expected < 150)`);

	const kitLines = fs
		.readFileSync(path.join(repoDir, "agents.kit.md"), "utf8")
		.trim()
		.split("\n");
	assert.ok(
		kitLines.some((line) => line.startsWith("- ") && line.includes("rules/large-file-creation.md")),
		"agents.kit.md must contain a bullet linking to rules/large-file-creation.md",
	);
});

