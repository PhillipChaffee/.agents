#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import process from "node:process";

const IGNORED_DIRS = new Set([".git", ".lake", "node_modules", "states", "target", ".venv", "__pycache__"]);

function sha256Hex(content) {
	return crypto.createHash("sha256").update(content).digest("hex");
}

function normalizeWs(text) {
	return text.trim().split(/\s+/).join(" ");
}

function stripCStyleComments(src) {
	return src
		.replace(/\/\*[\s\S]*?\*\//g, " ")
		.replace(/\/\/.*$/gm, "");
}

function findMatchingBrace(text, openPos) {
	let depth = 0;
	for (let i = openPos; i < text.length; i++) {
		const ch = text[i];
		if (ch === "{") {
			depth += 1;
		} else if (ch === "}") {
			depth -= 1;
			if (depth === 0) return i;
		}
	}
	return -1;
}

function extractContractAst(src) {
	const clean = stripCStyleComments(src);
	const blocks = [];
	let cursor = 0;

	const blockPatterns = [
		{ tag: "KANI_HARNESS", prefixes: ["#[kani::proof]"] },
		{ tag: "TYPE_DEF", prefixes: ["pub struct ", "struct ", "pub enum ", "enum "] },
		{
			tag: "SPEC_FN",
			prefixes: [
				"pub open spec fn ",
				"open spec fn ",
				"pub closed spec fn ",
				"closed spec fn ",
				"pub spec fn ",
				"spec fn ",
				"function ",
				"predicate ",
				"twostate predicate ",
			],
		},
		{
			tag: "VACUITY_PROOF",
			prefixes: ["pub proof fn verify_spec_not_vacuous", "proof fn verify_spec_not_vacuous", "lemma verify_spec_not_vacuous"],
		},
	];

	const execPrefixes = ["pub fn ", "pub exec fn ", "fn ", "exec fn ", "method "];

	while (cursor < clean.length) {
		const slice = clean.slice(cursor);
		let matched = false;

		for (const group of blockPatterns) {
			for (const prefix of group.prefixes) {
				if (slice.startsWith(prefix)) {
					const relOpen = slice.indexOf("{");
					if (relOpen !== -1) {
						const absOpen = cursor + relOpen;
						const absClose = findMatchingBrace(clean, absOpen);
						if (absClose !== -1) {
							blocks.push(`${group.tag}: ${normalizeWs(clean.slice(cursor, absClose + 1))}`);
							cursor = absClose + 1;
							matched = true;
							break;
						}
					}
				}
			}
			if (matched) break;
		}
		if (matched) continue;

		for (const prefix of execPrefixes) {
			if (slice.startsWith(prefix)) {
				const relOpen = slice.indexOf("{");
				if (relOpen !== -1) {
					const header = slice.slice(0, relOpen);
					const absOpen = cursor + relOpen;
					const absClose = findMatchingBrace(clean, absOpen);
					if (absClose !== -1) {
						blocks.push(`EXEC_CONTRACT: ${normalizeWs(header)}`);
						cursor = absClose + 1;
						matched = true;
						break;
					}
				}
			}
		}
		if (matched) continue;

		cursor += 1;
	}

	return blocks.join("\n");
}

function walkTree(dir, results) {
	if (!fs.existsSync(dir)) return;
	const entries = fs.readdirSync(dir, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name));
	for (const entry of entries) {
		if (entry.name.startsWith(".") || IGNORED_DIRS.has(entry.name)) continue;
		const fullPath = path.join(dir, entry.name);
		if (entry.isDirectory()) {
			walkTree(fullPath, results);
		} else if (entry.isFile() && !entry.name.includes("_TTrace_")) {
			results.push(fullPath);
		}
	}
}

function buildLockSnapshot(rootDir, whitelistedUnsafe) {
	const allFiles = [];
	walkTree(rootDir, allFiles);

	const tlaFiles = {};
	const leanFiles = {};
	const contractAsts = {};

	for (const absPath of allFiles) {
		const relPath = path.relative(rootDir, absPath).split(path.sep).join("/");
		const ext = path.extname(absPath);
		if (ext === ".tla" || ext === ".cfg") {
			tlaFiles[relPath] = sha256Hex(fs.readFileSync(absPath));
		} else if (ext === ".lean" || ext === ".v") {
			leanFiles[relPath] = sha256Hex(fs.readFileSync(absPath));
		} else if (ext === ".rs" || ext === ".dfy") {
			const src = fs.readFileSync(absPath, "utf8");
			const extracted = extractContractAst(src);
			if (extracted.length > 0) {
				contractAsts[relPath] = sha256Hex(extracted);
			}
		}
	}

	return {
		version: 1,
		tla_files: tlaFiles,
		lean_files: leanFiles,
		contract_asts: contractAsts,
		whitelisted_unsafe_files: [...whitelistedUnsafe].sort(),
	};
}

function scanUnsafeViolations(rootDir, whitelistedUnsafe) {
	const allFiles = [];
	walkTree(rootDir, allFiles);
	const allowed = new Set(whitelistedUnsafe);
	const violations = [];

	for (const absPath of allFiles) {
		if (path.extname(absPath) !== ".rs") continue;
		const relPath = path.relative(rootDir, absPath).split(path.sep).join("/");
		if (allowed.has(relPath)) continue;
		const clean = stripCStyleComments(fs.readFileSync(absPath, "utf8")).replace(/#!\s*\[\s*forbid\s*\(\s*unsafe_code\s*\)\s*\]/g, "");
		if (/\bunsafe\s*\{|\bunsafe\s+fn\b|\bunsafe\s+impl\b/.test(clean)) {
			violations.push(`Unauthorized \`unsafe\` block found in non-whitelisted file ${relPath}`);
		}
	}
	return violations;
}

function parseCliArgs(argv) {
	let mode = "--check";
	let rootDir = ".";
	let lockFile = null;
	const allowUnsafe = [];

	for (let i = 0; i < argv.length; i++) {
		const arg = argv[i];
		if (arg === "--generate" || arg === "--check") {
			mode = arg;
			if (i + 1 < argv.length && !argv[i + 1].startsWith("-")) {
				rootDir = argv[i + 1];
				i += 1;
			}
		} else if (arg === "--lock-file" && i + 1 < argv.length) {
			lockFile = argv[i + 1];
			i += 1;
		} else if (arg === "--allow-unsafe" && i + 1 < argv.length) {
			allowUnsafe.push(argv[i + 1]);
			i += 1;
		} else if (arg === "-h" || arg === "--help") {
			console.log("Usage: node verify-spec-lock.mjs [--generate | --check] [root-dir] [--lock-file <path>] [--allow-unsafe <rel-path>]");
			process.exit(0);
		} else if (!arg.startsWith("-")) {
			rootDir = arg;
		}
	}

	const resolvedRoot = path.resolve(rootDir);
	const resolvedLock = lockFile ? path.resolve(lockFile) : path.join(resolvedRoot, "spec.lock");
	return { mode, resolvedRoot, resolvedLock, allowUnsafe };
}

const { mode, resolvedRoot, resolvedLock, allowUnsafe } = parseCliArgs(process.argv.slice(2));

if (!fs.existsSync(resolvedRoot)) {
	console.error(`verify-spec-lock: root directory not found: ${resolvedRoot}`);
	process.exit(2);
}

if (mode === "--generate") {
	const unsafeErrors = scanUnsafeViolations(resolvedRoot, allowUnsafe);
	if (unsafeErrors.length > 0) {
		for (const err of unsafeErrors) console.error(`verify-spec-lock: ${err}`);
		process.exit(1);
	}
	const snapshot = buildLockSnapshot(resolvedRoot, allowUnsafe);
	fs.writeFileSync(resolvedLock, `${JSON.stringify(snapshot, null, 2)}\n`, "utf8");
	console.log(
		`verify-spec-lock: generated ${resolvedLock} (${Object.keys(snapshot.tla_files).length} TLA+ files, ${Object.keys(snapshot.lean_files).length} Lean/Rocq files, ${Object.keys(snapshot.contract_asts).length} contract AST modules)`,
	);
	process.exit(0);
}

if (!fs.existsSync(resolvedLock)) {
	console.error(`verify-spec-lock: ${resolvedLock} does not exist. Run with --generate first.`);
	process.exit(1);
}

const expected = JSON.parse(fs.readFileSync(resolvedLock, "utf8"));
const actual = buildLockSnapshot(resolvedRoot, expected.whitelisted_unsafe_files || []);
const mismatches = [];

if (JSON.stringify(expected.tla_files) !== JSON.stringify(actual.tla_files)) {
	mismatches.push("TLA+ specification hashes do not match spec.lock");
}
if (JSON.stringify(expected.lean_files) !== JSON.stringify(actual.lean_files)) {
	mismatches.push("Lean/Rocq specification hashes do not match spec.lock");
}
for (const [modPath, expHash] of Object.entries(expected.contract_asts || {})) {
	const actHash = actual.contract_asts[modPath];
	if (!actHash) {
		mismatches.push(`Locked contract module missing: ${modPath}`);
	} else if (actHash !== expHash) {
		mismatches.push(`contract AST hash modified in locked module: ${modPath}`);
	}
}
if (Object.keys(actual.contract_asts).length !== Object.keys(expected.contract_asts || {}).length) {
	mismatches.push("Number of contract AST modules changed vs spec.lock");
}

const unsafeErrors = scanUnsafeViolations(resolvedRoot, expected.whitelisted_unsafe_files || []);
mismatches.push(...unsafeErrors);

if (mismatches.length > 0) {
	console.error("verify-spec-lock: FAILED spec lock check:");
	for (const m of mismatches) console.error(`  - ${m}`);
	process.exit(1);
}

console.log(
	`verify-spec-lock: OK (${Object.keys(expected.tla_files).length} TLA+ files, ${Object.keys(expected.lean_files).length} Lean/Rocq files, ${Object.keys(expected.contract_asts).length} contract AST modules verified)`,
);
