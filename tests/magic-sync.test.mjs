import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";

const repoDir = path.resolve(import.meta.dirname, "..");

const ALL_58_MAGIC_SKILLS = [
	"architect",
	"arena",
	"automate-me",
	"benchmark-checklist",
	"blast-radius",
	"bro",
	"clean-code",
	"correct",
	"create-formal-verification-skill",
	"create-verification-skill",
	"figure-it-out",
	"how",
	"in-your-own-words",
	"interrogate",
	"ketchup",
	"ketchup-video",
	"magic-help",
	"magic-mode",
	"maintain-formal-verification-skill",
	"maintain-verification-skill",
	"make-bot-ui",
	"no-comments",
	"principle-attack-the-premise",
	"principle-boundary-discipline",
	"principle-build-the-lever",
	"principle-encode-lessons-in-structure",
	"principle-exhaust-the-design-space",
	"principle-experience-first",
	"principle-explain-the-number",
	"principle-fix-root-causes",
	"principle-foundational-thinking",
	"principle-guard-the-context-window",
	"principle-laziness-protocol",
	"principle-make-operations-idempotent",
	"principle-migrate-callers-then-delete-legacy-apis",
	"principle-minimize-reader-load",
	"principle-model-the-domain",
	"principle-never-block-on-the-human",
	"principle-outcome-oriented-execution",
	"principle-prove-it-works",
	"principle-redesign-from-first-principles",
	"principle-separate-before-serializing-shared-state",
	"principle-sequence-verifiable-units",
	"principle-subtract-before-you-add",
	"principle-test-behavior-not-implementation",
	"principle-type-system-discipline",
	"recall",
	"reflect",
	"setup-magic",
	"sharpen",
	"show-me-your-work",
	"statechart",
	"swarm",
	"tdd",
	"teach",
	"technical-writing",
	"unslop",
	"why",
];

test("all 58 core magic skills are present including make-bot-ui, tdd, and clean-code", () => {
	assert.equal(ALL_58_MAGIC_SKILLS.length, 58);
	for (const skill of ALL_58_MAGIC_SKILLS) {
		const entry = path.join(repoDir, "skills", skill, "SKILL.md");
		assert.ok(fs.existsSync(entry), `missing magic skill: ${skill}`);
	}
	assert.ok(
		fs.existsSync(path.join(repoDir, "skills/clean-code/references/python.md")),
		"missing python reference in clean-code",
	);
	assert.ok(
		fs.existsSync(path.join(repoDir, "skills/clean-code/references/typescript.md")),
		"missing typescript reference in clean-code",
	);
	assert.ok(
		!fs.existsSync(path.join(repoDir, "skills/typescript-best-practices")),
		"typescript-best-practices should be retired into clean-code",
	);
});

test("synced magic skill updates and local customizations are preserved", () => {
	const interrogate = fs.readFileSync(path.join(repoDir, "skills/interrogate/SKILL.md"), "utf8");
	assert.match(interrogate, /Adversaries try to break a change or a design/);
	for (const retired of ["code-quality-review.md", "lead-judgment.md", "reviewer-prompt.md", "rubric.md"]) {
		assert.ok(
			!fs.existsSync(path.join(repoDir, "skills/interrogate/references", retired)),
			`retired reference should be deleted: ${retired}`,
		);
	}

	const ketchupVideo = fs.readFileSync(path.join(repoDir, "skills/ketchup-video/SKILL.md"), "utf8");
	assert.match(ketchupVideo, /## Subtitles/);

	const explainNum = fs.readFileSync(
		path.join(repoDir, "skills/principle-explain-the-number/SKILL.md"),
		"utf8",
	);
	assert.match(explainNum, /Write the decision before you run\./);

	const orchestrate = fs.readFileSync(
		path.join(repoDir, "skills/magic-mode/playbooks/orchestrate.md"),
		"utf8",
	);
	assert.match(orchestrate, /## Topology/);
	assert.match(orchestrate, /## Supervision/);
	assert.match(orchestrate, /isolated-worktree subagents/);

	assert.ok(fs.existsSync(path.join(repoDir, "skills/statechart/references/render.md")));
	assert.ok(fs.existsSync(path.join(repoDir, "skills/statechart/scripts/statechart.ts")));
	assert.ok(fs.existsSync(path.join(repoDir, "skills/statechart/scripts/statechart.mjs")));

	const magicHelp = fs.readFileSync(path.join(repoDir, "skills/magic-help/SKILL.md"), "utf8");
	for (const customSkill of [
		"/proof-driven-development",
		"/proving-with-hoare-logic",
		"/proving-with-dependent-types",
		"/model-checking-protocols-and-code",
		"/analyzing-with-abstract-interpretation",
		"/auditing-proof-specifications",
		"/research",
		"/research-summary",
		"/autopilot",
		"/make-pr-easy-to-review",
		"/thermo-nuclear-code-quality-review",
		"/tdd",
		"/clean-code",
		"/make-bot-ui",
		"/simple-english",
	]) {
		assert.ok(magicHelp.includes(customSkill), `magic-help missing ${customSkill}`);
	}
	assert.ok(
		!magicHelp.includes("/typescript-best-practices"),
		"magic-help should not reference retired typescript-best-practices",
	);
});

test("magic-mode and PR playbooks wire /make-pr-easy-to-review when opening or updating a PR/MR while preserving upstream make-pr-easy-to-review bytes", () => {
	const magicMode = fs.readFileSync(path.join(repoDir, "skills/magic-mode/SKILL.md"), "utf8");
	assert.match(magicMode, /\/make-pr-easy-to-review/);

	const openingPr = fs.readFileSync(
		path.join(repoDir, "skills/magic-mode/playbooks/opening-a-pr.md"),
		"utf8",
	);
	assert.match(openingPr, /\/make-pr-easy-to-review/);
	assert.match(openingPr, /right after opening|when updating an open PR/i);

	const autopilotFull = fs.readFileSync(
		path.join(repoDir, "skills/magic-mode/playbooks/autopilot-full.md"),
		"utf8",
	);
	assert.match(autopilotFull, /\/make-pr-easy-to-review/);

	const multiPhasePlan = fs.readFileSync(
		path.join(repoDir, "skills/magic-mode/playbooks/multi-phase-plan.md"),
		"utf8",
	);
	assert.match(multiPhasePlan, /make-pr-easy-to-review/);
	for (const line of multiPhasePlan.split(/\r?\n/)) {
		if (line.includes("make-pr-easy-to-review")) {
			assert.doesNotMatch(line, /[\u2013\u2014]/, `long dash in multi-phase-plan.md: ${line}`);
			assert.doesNotMatch(line, /: \S/, `mid-sentence colon in multi-phase-plan.md: ${line}`);
		}
	}

	const verbatimList = fs.readFileSync(path.join(repoDir, "scripts/magic-verbatim.txt"), "utf8");
	assert.match(verbatimList, /^skills\/make-pr-easy-to-review\/SKILL\.md$/m);
});

test("clean-code skill routes by language, enforces pre-PR/MR cleanup contract, and is wired across PR/MR entry points", () => {
	const cleanCodePath = path.join(repoDir, "skills/clean-code/SKILL.md");
	assert.ok(fs.existsSync(cleanCodePath), "missing skills/clean-code/SKILL.md");
	const cleanCodeText = fs.readFileSync(cleanCodePath, "utf8");
	assert.match(cleanCodeText, /^description:\s*["']?Use when/m);
	assert.match(cleanCodeText, /references\/python\.md/);
	assert.match(cleanCodeText, /references\/typescript\.md/);
	assert.match(cleanCodeText, /Universal AI Slop Checklist/);
	assert.match(cleanCodeText, /## TL;DR/);

	const pyRefPath = path.join(repoDir, "skills/clean-code/references/python.md");
	assert.ok(fs.existsSync(pyRefPath), "missing python reference");
	const pyRefText = fs.readFileSync(pyRefPath, "utf8");
	assert.match(pyRefText, /getattr/i);
	assert.match(pyRefText, /OneToOne/);
	assert.match(pyRefText, /inline import/i);
	assert.match(pyRefText, /SimpleNamespace/);
	assert.match(pyRefText, /dataclasses\.fields/);
	assert.match(pyRefText, /TYPE_CHECKING/);
	assert.doesNotMatch(pyRefText, /sela-ai/, "references/python.md must not contain private repo names");

	const tsRefPath = path.join(repoDir, "skills/clean-code/references/typescript.md");
	assert.ok(fs.existsSync(tsRefPath), "missing typescript reference");
	const tsRefText = fs.readFileSync(tsRefPath, "utf8");
	assert.match(tsRefText, /discriminated union/i);
	assert.match(tsRefText, /branded/i);
	assert.match(tsRefText, /unknown/i);
	assert.match(tsRefText, /as/i);

	const magicMode = fs.readFileSync(path.join(repoDir, "skills/magic-mode/SKILL.md"), "utf8");
	assert.match(magicMode, /\/clean-code/);

	const openingPr = fs.readFileSync(
		path.join(repoDir, "skills/magic-mode/playbooks/opening-a-pr.md"),
		"utf8",
	);
	assert.match(openingPr, /\/clean-code/);

	const autopilotFull = fs.readFileSync(
		path.join(repoDir, "skills/magic-mode/playbooks/autopilot-full.md"),
		"utf8",
	);
	assert.match(autopilotFull, /\/clean-code/);

	const multiPhasePlan = fs.readFileSync(
		path.join(repoDir, "skills/magic-mode/playbooks/multi-phase-plan.md"),
		"utf8",
	);
	assert.match(multiPhasePlan, /clean-code/);
	for (const line of multiPhasePlan.split(/\r?\n/)) {
		if (line.includes("clean-code")) {
			assert.doesNotMatch(line, /[\u2013\u2014]/, `long dash in multi-phase-plan.md: ${line}`);
			assert.doesNotMatch(line, /: \S/, `mid-sentence colon in multi-phase-plan.md: ${line}`);
		}
	}
});

test("principle-take-a-step-back satisfies skill contract and is wired into Layer 2 checkpoints", () => {
	const skillPath = path.join(repoDir, "skills/principle-take-a-step-back/SKILL.md");
	assert.ok(fs.existsSync(skillPath), "missing skills/principle-take-a-step-back/SKILL.md");
	const text = fs.readFileSync(skillPath, "utf8");
	assert.match(text, /^description: "Use when /m);
	assert.match(text, /Why is the user asking this\?/);
	assert.match(text, /Is there something they do not understand that I should flag\?/);

	for (const rel of [
		"skills/magic-mode/SKILL.md",
		"skills/research/SKILL.md",
		"skills/architect/SKILL.md",
		"skills/figure-it-out/SKILL.md",
		"skills/proof-driven-development/SKILL.md",
		"skills/magic-mode/playbooks/feature.md",
		"skills/magic-mode/playbooks/bug-fix.md",
		"skills/magic-mode/playbooks/investigation.md",
		"skills/magic-mode/playbooks/refactoring.md",
		"skills/magic-mode/playbooks/autonomous-run.md",
		"skills/magic-mode/playbooks/multi-phase-plan.md",
	]) {
		const targetText = fs.readFileSync(path.join(repoDir, rel), "utf8");
		assert.match(targetText, /take-a-step-back/, `${rel} should reference take-a-step-back`);
	}
});

test("simple-english skill and references exist, parse folded frontmatter cleanly, and satisfy markdownlint", async () => {
	const { extractAndStripFrontmatter } = await import("../lib/bootstrap-core.js");
	const skillDir = path.join(repoDir, "skills/simple-english");
	const skillText = fs.readFileSync(path.join(skillDir, "SKILL.md"), "utf8");
	const { frontmatter, content } = extractAndStripFrontmatter(skillText);

	assert.equal(frontmatter.id, "simple-english");
	assert.equal(frontmatter.name, "simple-english");
	assert.equal(frontmatter.enabled, "true");
	assert.match(frontmatter.description, /^Write or rewrite text in plain, layman-readable English/);
	assert.match(frontmatter.description, /answer first, prose by default\.$/);
	assert.ok(!content.startsWith("---"));
	assert.match(content, /^# Simple English/m);

	for (const ref of ["rule-catalog.md", "strict-vocabulary.md", "use-cases.md", "word-swaps.md"]) {
		const refPath = path.join(skillDir, "references", ref);
		assert.ok(fs.existsSync(refPath), `missing skills/simple-english/references/${ref}`);
		const refText = fs.readFileSync(refPath, "utf8");
		assert.doesNotMatch(refText, /^\|---\|/m, `${ref} must space table delimiter pipes (MD060)`);
		assert.doesNotMatch(refText, /\n\n\n/, `${ref} must not contain consecutive blank lines (MD012)`);
	}
	const catalog = fs.readFileSync(path.join(skillDir, "references/rule-catalog.md"), "utf8");
	assert.match(catalog, /^## Rules\n\n### Section 1: Words \(Rules 1\.1-1\.14\)/m);
});
