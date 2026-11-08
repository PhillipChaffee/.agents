import { spawnSync } from "node:child_process";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";

const root = path.resolve(import.meta.dirname, "..");
const cheatChecker = path.join(root, "skills/auditing-proof-specifications/scripts/check-proof-cheats.mjs");
const renderGraphs = path.join(root, "skills/writing-skills/render-graphs.js");

const PROOF_SKILLS = [
	"proof-driven-development",
	"proving-with-hoare-logic",
	"proving-with-dependent-types",
	"model-checking-protocols-and-code",
	"analyzing-with-abstract-interpretation",
	"auditing-proof-specifications",
];

test("all proof-driven development skills exist and satisfy SDO frontmatter contract", () => {
	for (const skill of PROOF_SKILLS) {
		const skillPath = path.join(root, "skills", skill, "SKILL.md");
		assert.ok(fs.existsSync(skillPath), `missing ${skillPath}`);
		const text = fs.readFileSync(skillPath, "utf8");
		assert.ok(text.startsWith("---\n"), `${skill}: missing frontmatter start`);
		const end = text.indexOf("\n---", 4);
		assert.notEqual(end, -1, `${skill}: missing frontmatter end`);
		const fm = text.slice(4, end);
		assert.ok(fm.length <= 1024, `${skill}: frontmatter exceeds 1024 chars`);
		assert.match(fm, /^description: "Use when /m, `${skill}: description must start with 'Use when '`);
		assert.match(fm, new RegExp(`^id: ${skill}$`, "m"), `${skill}: id must match directory`);
		assert.match(fm, new RegExp(`^name: ${skill}$`, "m"), `${skill}: name must match directory`);
	}
});

test("check-proof-cheats detects escape hatches across proof languages and passes clean files", (t) => {
	const dir = fs.mkdtempSync(path.join(os.tmpdir(), "proof-cheats-"));
	t.after(() => fs.rmSync(dir, { recursive: true, force: true }));

	const cleanDir = path.join(dir, "clean");
	fs.mkdirSync(cleanDir);
	fs.writeFileSync(
		path.join(cleanDir, "clean.rs"),
		"// comment mentioning assume(false) and #[verifier::external_body]\npub fn add(a: u32, b: u32) -> u32 { a + b }\n",
	);
	fs.writeFileSync(
		path.join(cleanDir, "Clean.lean"),
		"-- comment mentioning sorry and axiom\ntheorem refl_nat (n : Nat) : n = n := rfl\n",
	);
	const cleanRes = spawnSync(process.execPath, [cheatChecker, cleanDir], { encoding: "utf8" });
	assert.equal(cleanRes.status, 0, cleanRes.stderr);
	assert.match(cleanRes.stdout, /OK: 2 file\(s\) scanned, 0 proof escape hatches found/);

	const dirtyDir = path.join(dir, "dirty");
	fs.mkdirSync(dirtyDir);
	fs.writeFileSync(path.join(dirtyDir, "bad.rs"), "#[verifier::external_body]\npub fn f() { assume(false); }\n");
	fs.writeFileSync(path.join(dirtyDir, "Bad.lean"), "axiom fake : False\ntheorem t : False := by sorry\n");
	fs.writeFileSync(path.join(dirtyDir, "bad.dfy"), "method M() { assume false; }\n");
	fs.writeFileSync(path.join(dirtyDir, "bad.c"), "/*@ admit foo; */\n");
	fs.writeFileSync(path.join(dirtyDir, "ci.sh"), "cargo kani --no-unwinding-assertions\nframa-c -eva -no-warn-signed-overflow\n");

	const dirtyRes = spawnSync(process.execPath, [cheatChecker, dirtyDir], { encoding: "utf8" });
	assert.equal(dirtyRes.status, 1);
	for (const expectedId of [
		"verus-external-body",
		"smt-assume-call",
		"lean-axiom",
		"lean-sorry",
		"dafny-assume",
		"acsl-admit",
		"kani-no-unwinding-asserts",
		"eva-disable-rte-flag",
	]) {
		assert.match(dirtyRes.stderr, new RegExp(`\\[${expectedId}\\]`), `missing ${expectedId} in ${dirtyRes.stderr}`);
	}
});

test("graphviz flowcharts in proof skills extract and render cleanly with stub dot", (t) => {
	const dir = fs.mkdtempSync(path.join(os.tmpdir(), "proof-graphs-"));
	t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
	const dot = path.join(dir, "dot");
	fs.writeFileSync(dot, "#!/bin/sh\ncat >/dev/null\nprintf '<svg/>\\n'\n", { mode: 0o755 });
	const env = { ...process.env, PATH: `${dir}${path.delimiter}${process.env.PATH}` };

	for (const [skill, graphName] of [
		["proof-driven-development", "proof_orchestrator"],
		["proving-with-hoare-logic", "smt_failure"],
		["model-checking-protocols-and-code", "mc_choice"],
		["analyzing-with-abstract-interpretation", "abstract_alarm"],
		["autopilot", "autopilot_loop"],
	]) {
		const targetSkillDir = path.join(dir, skill);
		fs.mkdirSync(targetSkillDir);
		fs.copyFileSync(path.join(root, "skills", skill, "SKILL.md"), path.join(targetSkillDir, "SKILL.md"));
		const res = spawnSync(process.execPath, [renderGraphs, targetSkillDir], { env, encoding: "utf8" });
		assert.equal(res.status, 0, `${skill}: ${res.stderr}`);
		assert.ok(fs.existsSync(path.join(targetSkillDir, "diagrams", `${graphName}.svg`)), `${skill}: diagrams/${graphName}.svg not rendered`);
	}
});
