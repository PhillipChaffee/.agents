#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import process from "node:process";

const RULES = [
	{
		exts: [".rs"],
		checks: [
			{ id: "verus-external-body", re: /#\s*\[\s*verifier\s*::\s*external_body\s*\]/, msg: "unverified function body (#[verifier::external_body])" },
			{ id: "verus-external", re: /#\s*\[\s*verifier\s*::\s*external(?:_fn_specification)?\s*\]/, msg: "external verifier bypass (#[verifier::external*])" },
			{ id: "verus-trusted", re: /#\s*\[\s*verifier\s*::\s*trusted\s*\]/, msg: "trusted verifier bypass (#[verifier::trusted])" },
			{ id: "verus-no-decreases", re: /#\s*\[\s*verifier\s*::\s*exec_allows_no_decreases_clause\s*\]/, msg: "termination bypass (#[verifier::exec_allows_no_decreases_clause])" },
			{ id: "verus-admit-attr", re: /#\s*\[\s*verifier\s*::\s*admit\s*\]/, msg: "admitted proof obligation (#[verifier::admit])" },
			{ id: "verus-truncate", re: /#\s*\[\s*verifier\s*::\s*truncate\s*\]/, msg: "unchecked integer truncation (#[verifier::truncate])" },
			{ id: "creusot-trusted", re: /#\s*\[\s*trusted\s*\]/, msg: "trusted bypass (#[trusted])" },
			{ id: "smt-admit-call", re: /\badmit\s*\(\s*\)/, msg: "unproved admit() call" },
			{ id: "smt-assume-call", re: /(?<!::)\bassume\s*\(/, msg: "unproved assume(...) statement" },
			{ id: "kani-assume-false", re: /\bkani\s*::\s*assume\s*\(\s*false\s*\)/, msg: "vacuous kani::assume(false)" },
			{ id: "kani-stub-verified", re: /#\s*\[\s*kani\s*::\s*stub_verified\b/, msg: "unverified stub replacement (#[kani::stub_verified])" },
			{ id: "kani-stub", re: /#\s*\[\s*kani\s*::\s*stub(?!_verified)\b/, msg: "unverified Kani stub (#[kani::stub])" },
		],
	},
	{
		exts: [".lean"],
		checks: [
			{ id: "lean-sorry", re: /\b(?:sorry|sorryAx)\b/, msg: "incomplete proof token (sorry / sorryAx)" },
			{ id: "lean-admit", re: /\badmit\b/, msg: "incomplete proof token (admit)" },
			{ id: "lean-axiom", re: /^\s*axiom\s+\S+/, msg: "custom axiom declaration bypassing kernel" },
			{ id: "lean-unsafe", re: /^\s*unsafe\s+/, msg: "unsafe definition bypassing kernel soundness" },
			{ id: "lean-implemented-by", re: /@\[\s*implemented_by\b/, msg: "unverified runtime replacement (@[implemented_by])" },
			{ id: "lean-extern", re: /@\[\s*extern\b/, msg: "unverified FFI binding (@[extern])" },
			{ id: "lean-native-decide", re: /\b(?:native_decide|Lean\.ofReduceBool)\b/, msg: "unverified native compiler evaluation (native_decide / ofReduceBool)" },
		],
	},
	{
		exts: [".v"],
		checks: [
			{ id: "rocq-admitted", re: /\b(?:Admitted|admit)\b/, msg: "incomplete Rocq proof (Admitted / admit)" },
			{ id: "rocq-axiom", re: /^\s*(?:Axiom|Parameter|Conjecture|Hypothesis)\s+\S+/, msg: "unproved Rocq axiom/parameter" },
		],
	},
	{
		exts: [".dfy"],
		checks: [
			{ id: "dafny-assume", re: /\bassume\b/, msg: "unproved Dafny assume statement" },
			{ id: "dafny-axiom", re: /\{\s*:axiom\s*\}/, msg: "unproved Dafny {:axiom} attribute" },
			{ id: "dafny-verify-false", re: /\{\s*:verify\s+false\s*\}/, msg: "verification disabled ({:verify false})" },
		],
	},
	{
		exts: [".c", ".h"],
		checks: [
			{ id: "acsl-admit", re: /\/\*@[\s\S]*?\badmit\b/, msg: "unproved ACSL admit clause" },
			{ id: "eva-suppress", re: /-eva-no-warn-key\b/, msg: "suppressed Frama-C EVA alarm category" },
			{ id: "eva-disable-rte", re: /-no-warn-(?:signed-overflow|unsigned-overflow|special-float|invalid-bool|pointer-downcast|left-shift-negative|right-shift-negative)\b/, msg: "disabled Frama-C runtime error check (-no-warn-*)" },
		],
	},
	{
		exts: [".sh", ".yml", ".yaml", ".toml"],
		checks: [
			{ id: "kani-no-unwinding-asserts", re: /--no-unwinding-assertions\b/, msg: "disabled loop unwinding assertions (--no-unwinding-assertions)" },
			{ id: "kani-no-default-checks", re: /--no-default-checks\b/, msg: "disabled default safety checks (--no-default-checks)" },
			{ id: "dafny-allow-axioms", re: /--allow-axioms\s*=\s*true\b/, msg: "permitted unproved axioms (--allow-axioms=true)" },
			{ id: "eva-suppress-flag", re: /-eva-no-warn-key\b/, msg: "suppressed Frama-C EVA alarm category (-eva-no-warn-key)" },
			{ id: "eva-disable-rte-flag", re: /-no-warn-(?:signed-overflow|unsigned-overflow|special-float|invalid-bool|pointer-downcast|left-shift-negative|right-shift-negative)\b/, msg: "disabled Frama-C runtime error check (-no-warn-*)" },
		],
	},
];

function stripLineComment(line, ext) {
	if (ext === ".lean") return line.replace(/--.*$/, "");
	if (ext === ".rs" || ext === ".dfy") return line.replace(/\/\/.*$/, "");
	return line;
}

function collectFiles(target, out) {
	const stat = fs.statSync(target);
	if (stat.isFile()) {
		out.push(target);
		return;
	}
	if (!stat.isDirectory()) return;
	for (const entry of fs.readdirSync(target, { withFileTypes: true })) {
		if (entry.name === ".git" || entry.name === "node_modules" || entry.name === "target") continue;
		collectFiles(path.join(target, entry.name), out);
	}
}

const args = process.argv.slice(2);
if (args.length === 0 || args.includes("-h") || args.includes("--help")) {
	console.log("Usage: node check-proof-cheats.mjs <file-or-dir> [...]");
	process.exit(args.length === 0 ? 2 : 0);
}

const files = [];
for (const arg of args) {
	if (!fs.existsSync(arg)) {
		console.error(`error: path not found: ${arg}`);
		process.exit(2);
	}
	collectFiles(arg, files);
}

const findings = [];
for (const file of files.sort()) {
	const ext = path.extname(file);
	const ruleGroup = RULES.find((r) => r.exts.includes(ext));
	if (!ruleGroup) continue;
	const lines = fs.readFileSync(file, "utf8").split(/\r?\n/);
	for (let i = 0; i < lines.length; i++) {
		const cleaned = stripLineComment(lines[i], ext);
		for (const check of ruleGroup.checks) {
			if (check.re.test(cleaned)) {
				findings.push(`${file}:${i + 1}: [${check.id}] ${check.msg}`);
			}
		}
	}
}

for (const f of findings) {
	console.error(f);
}
if (findings.length > 0) {
	console.error(`FAIL: ${findings.length} proof escape-hatch violation(s) found`);
	process.exit(1);
}
console.log(`OK: ${files.length} file(s) scanned, 0 proof escape hatches found`);
