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
	fs.writeFileSync(
		path.join(dirtyDir, "bad.rs"),
		[
			"#[verifier::external_body]",
			"#[verifier::trusted]",
			"#[verifier::exec_allows_no_decreases_clause]",
			"#[kani::stub_verified(foo)]",
			"pub fn f() { assume(false); }",
		].join("\n"),
	);
	fs.writeFileSync(path.join(dirtyDir, "Bad.lean"), "axiom fake : False\ntheorem t : False := by sorry\n");
	fs.writeFileSync(path.join(dirtyDir, "bad.dfy"), "method M() { assume false; }\n");
	fs.writeFileSync(path.join(dirtyDir, "bad.c"), "/*@ admit foo; */\n");
	fs.writeFileSync(path.join(dirtyDir, "ci.sh"), "cargo kani --no-unwinding-assertions\nframa-c -eva -no-warn-signed-overflow\n");

	const dirtyRes = spawnSync(process.execPath, [cheatChecker, dirtyDir], { encoding: "utf8" });
	assert.equal(dirtyRes.status, 1);
	for (const expectedId of [
		"verus-external-body",
		"verus-trusted",
		"verus-no-decreases",
		"kani-stub-verified",
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

test("verify-spec-lock allows exec body synthesis but rejects contract or unwhitelisted unsafe edits", (t) => {
	const verifySpecLock = path.join(root, "skills/auditing-proof-specifications/scripts/verify-spec-lock.mjs");
	const dir = fs.mkdtempSync(path.join(os.tmpdir(), "spec-lock-"));
	t.after(() => fs.rmSync(dir, { recursive: true, force: true }));

	fs.mkdirSync(path.join(dir, "specs/tla"), { recursive: true });
	fs.mkdirSync(path.join(dir, "specs/lean"), { recursive: true });
	fs.mkdirSync(path.join(dir, "crates/core/src"), { recursive: true });

	fs.writeFileSync(path.join(dir, "specs/tla/Proc.tla"), "---- MODULE Proc ----\nInit == TRUE\n====\n");
	fs.writeFileSync(path.join(dir, "specs/lean/Model.lean"), "theorem t1 (n : Nat) : n = n := rfl\n");
	const rsFile = path.join(dir, "crates/core/src/lib.rs");
	fs.writeFileSync(
		rsFile,
		[
			"#![forbid(unsafe_code)]",
			"pub struct Counter { pub val: u64 }",
			"pub open spec fn inv_val(v: u64) -> bool { v <= 100 }",
			"pub proof fn verify_spec_not_vacuous() ensures inv_val(0) {}",
			"pub fn inc(c: &mut Counter) -> (res: u64)",
			"    requires old(c).val < 100,",
			"    ensures c.val == old(c).val + 1, res == c.val,",
			"{",
			"    todo!()",
			"}",
		].join("\n"),
	);

	const genRes = spawnSync(process.execPath, [verifySpecLock, "--generate", dir], { encoding: "utf8" });
	assert.equal(genRes.status, 0, genRes.stderr);
	assert.ok(fs.existsSync(path.join(dir, "spec.lock")));

	fs.writeFileSync(
		rsFile,
		[
			"#![forbid(unsafe_code)]",
			"pub struct Counter { pub val: u64 }",
			"pub open spec fn inv_val(v: u64) -> bool { v <= 100 }",
			"pub proof fn verify_spec_not_vacuous() ensures inv_val(0) {}",
			"pub fn inc(c: &mut Counter) -> (res: u64)",
			"    requires old(c).val < 100,",
			"    ensures c.val == old(c).val + 1, res == c.val,",
			"{",
			"    c.val = c.val + 1;",
			"    c.val",
			"}",
		].join("\n"),
	);
	const okCheck = spawnSync(process.execPath, [verifySpecLock, "--check", dir], { encoding: "utf8" });
	assert.equal(okCheck.status, 0, okCheck.stderr);

	fs.writeFileSync(
		rsFile,
		[
			"#![forbid(unsafe_code)]",
			"pub struct Counter { pub val: u64 }",
			"pub open spec fn inv_val(v: u64) -> bool { true }",
			"pub proof fn verify_spec_not_vacuous() ensures inv_val(0) {}",
			"pub fn inc(c: &mut Counter) -> (res: u64)",
			"    requires old(c).val < 10,",
			"    ensures c.val == old(c).val + 1, res == c.val,",
			"{",
			"    c.val = c.val + 1;",
			"    c.val",
			"}",
		].join("\n"),
	);
	const badContractCheck = spawnSync(process.execPath, [verifySpecLock, "--check", dir], { encoding: "utf8" });
	assert.equal(badContractCheck.status, 1);
	assert.match(badContractCheck.stderr, /contract AST hash modified/);

	fs.writeFileSync(
		rsFile,
		[
			"pub struct Counter { pub val: u64 }",
			"pub open spec fn inv_val(v: u64) -> bool { v <= 100 }",
			"pub proof fn verify_spec_not_vacuous() ensures inv_val(0) {}",
			"pub fn inc(c: &mut Counter) -> (res: u64)",
			"    requires old(c).val < 100,",
			"    ensures c.val == old(c).val + 1, res == c.val,",
			"{",
			"    unsafe { c.val = c.val + 1; }",
			"    c.val",
			"}",
		].join("\n"),
	);
	const badUnsafeCheck = spawnSync(process.execPath, [verifySpecLock, "--check", dir], { encoding: "utf8" });
	assert.equal(badUnsafeCheck.status, 1);
	assert.match(badUnsafeCheck.stderr, /Unauthorized `unsafe` block/);
});

const PROOF_LEAVES = [
	"proving-with-hoare-logic",
	"proving-with-dependent-types",
	"model-checking-protocols-and-code",
	"analyzing-with-abstract-interpretation",
	"auditing-proof-specifications",
	"statechart",
];

test("proof-driven-development runs the four-wave PDD pipeline and locks the spec before synthesis", () => {
	const text = fs.readFileSync(path.join(root, "skills/proof-driven-development/SKILL.md"), "utf8");
	assert.match(text, /## The Four-Wave PDD Pipeline/);
	for (const wave of ["Wave 1", "Wave 2", "Wave 3", "Wave 4"]) {
		assert.ok(text.includes(wave), `the pipeline must name ${wave}`);
	}
	for (const role of ["hardest tasks", "arena cross-judge pool", "swarm workers"]) {
		assert.ok(text.includes(role), `the pipeline must bind the ${role} role`);
	}
	assert.match(text, /orchestrator: thin/);
	assert.match(text, /magic-agent/);
	assert.match(text, /sequentially/, "a harness with no subagent tool falls back to inline execution");
	assert.match(text, /verify-spec-lock\.mjs --generate/);
	assert.match(text, /verify-spec-lock\.mjs --check/);
	assert.match(text, /check-proof-cheats\.mjs/);
	assert.match(text, /#print axioms/);
	assert.match(text, /take-a-step-back/);

	const lockAt = text.indexOf("Deterministic Lock Gate");
	const wave3At = text.indexOf("**Wave 3");
	assert.ok(lockAt !== -1, "the pipeline names the deterministic lock gate");
	assert.ok(wave3At !== -1, "the pipeline names Wave 3");
	assert.ok(lockAt < wave3At, "the root chat locks the spec before the proof synthesizer runs");
	const gate = text.slice(lockAt, wave3At);
	assert.match(gate, /depth = 0/, "the lock gate runs in the root chat, not a subagent");
	assert.match(gate, /--generate/);

	const wave4At = text.indexOf("**Wave 4");
	assert.ok(wave4At !== -1, "the pipeline names Wave 4");
	assert.ok(wave3At < wave4At, "Wave 3 synthesizes before Wave 4 audits");
	const wave4 = text.slice(wave4At, text.indexOf("\n\n", wave4At));
	assert.match(wave4, /verify-spec-lock\.mjs --check/, "Wave 4 rechecks the locked spec");
});

test("the proof leaf skills execute at depth 1 under the role that dispatches them", () => {
	for (const skill of PROOF_LEAVES) {
		const text = fs.readFileSync(path.join(root, "skills", skill, "SKILL.md"), "utf8");
		assert.match(text, /depth-1 leaf/, `${skill} must name the depth-1 leaf rule`);
		assert.match(text, /orchestrator: thin/, `${skill} must name the thin orchestrator mode`);
		assert.match(
			text,
			/spawns? no subagent|never spawn|without spawning/i,
			`${skill} must not spawn a sub-subagent`,
		);
		assert.match(
			text,
			/executes? (?:it|this skill) directly|executes directly in this/i,
			`${skill} runs inline`,
		);
	}
	const hoare = fs.readFileSync(path.join(root, "skills/proving-with-hoare-logic/SKILL.md"), "utf8");
	const dependent = fs.readFileSync(path.join(root, "skills/proving-with-dependent-types/SKILL.md"), "utf8");
	const modelChecking = fs.readFileSync(path.join(root, "skills/model-checking-protocols-and-code/SKILL.md"), "utf8");
	const abstract = fs.readFileSync(path.join(root, "skills/analyzing-with-abstract-interpretation/SKILL.md"), "utf8");
	const statechart = fs.readFileSync(path.join(root, "skills/statechart/SKILL.md"), "utf8");
	for (const [skill, text] of [
		["proving-with-hoare-logic", hoare],
		["proving-with-dependent-types", dependent],
		["model-checking-protocols-and-code", modelChecking],
		["analyzing-with-abstract-interpretation", abstract],
		["statechart", statechart],
	]) {
		assert.match(text, /hardest tasks/, `${skill} runs on the hardest tasks role`);
	}

	const audit = fs.readFileSync(
		path.join(root, "skills/auditing-proof-specifications/SKILL.md"),
		"utf8",
	);
	assert.match(abstract, /Wave 3/, "the abstract-interpretation leaf names its pipeline wave");
	assert.match(modelChecking, /Wave 3/, "the model-checking leaf names its pipeline wave");
	assert.match(dependent, /Wave 3/, "the dependent-types leaf names its pipeline wave");
	assert.match(hoare, /Wave 3/, "the Hoare-logic leaf names its pipeline wave");
	assert.match(statechart, /Wave 1/, "the statechart leaf serves the Wave 1 spec author");
	assert.match(audit, /arena cross-judge pool/, "the spec audit seat comes from the cross-family pool");
	assert.match(audit, /Wave 4/, "the audit leaf names its pipeline wave");
	assert.match(audit, /verify-spec-lock\.mjs --check/);
	assert.match(audit, /check-proof-cheats\.mjs/);
	assert.match(audit, /#print axioms/);
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
		["principle-take-a-step-back", "take_a_step_back"],
	]) {
		const targetSkillDir = path.join(dir, skill);
		fs.mkdirSync(targetSkillDir);
		fs.copyFileSync(path.join(root, "skills", skill, "SKILL.md"), path.join(targetSkillDir, "SKILL.md"));
		const res = spawnSync(process.execPath, [renderGraphs, targetSkillDir], { env, encoding: "utf8" });
		assert.equal(res.status, 0, `${skill}: ${res.stderr}`);
		assert.ok(fs.existsSync(path.join(targetSkillDir, "diagrams", `${graphName}.svg`)), `${skill}: diagrams/${graphName}.svg not rendered`);
	}
});
