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
	"typescript-best-practices",
	"unslop",
	"why",
];

test("all 58 core magic skills are present including make-bot-ui, tdd, and typescript-best-practices", () => {
	assert.equal(ALL_58_MAGIC_SKILLS.length, 58);
	for (const skill of ALL_58_MAGIC_SKILLS) {
		const entry = path.join(repoDir, "skills", skill, "SKILL.md");
		assert.ok(fs.existsSync(entry), `missing magic skill: ${skill}`);
	}
	assert.ok(
		fs.existsSync(path.join(repoDir, "skills/typescript-best-practices/references/patterns.md")),
	);
});

test("synced magic skill updates and local customizations are preserved", () => {
	// 1. interrogate updated to run-proven adversaries & retired references removed
	const interrogate = fs.readFileSync(path.join(repoDir, "skills/interrogate/SKILL.md"), "utf8");
	assert.match(interrogate, /Adversaries try to break a change or a design/);
	for (const retired of ["code-quality-review.md", "lead-judgment.md", "reviewer-prompt.md", "rubric.md"]) {
		assert.ok(
			!fs.existsSync(path.join(repoDir, "skills/interrogate/references", retired)),
			`retired reference should be deleted: ${retired}`,
		);
	}

	// 2. ketchup-video has Subtitles section
	const ketchupVideo = fs.readFileSync(path.join(repoDir, "skills/ketchup-video/SKILL.md"), "utf8");
	assert.match(ketchupVideo, /## Subtitles/);

	// 3. principle-explain-the-number has Write the decision before you run
	const explainNum = fs.readFileSync(
		path.join(repoDir, "skills/principle-explain-the-number/SKILL.md"),
		"utf8",
	);
	assert.match(explainNum, /Write the decision before you run\./);

	// 4. orchestrate has agentic Topology & Supervision sections with neutral vocabulary
	const orchestrate = fs.readFileSync(
		path.join(repoDir, "skills/magic-mode/playbooks/orchestrate.md"),
		"utf8",
	);
	assert.match(orchestrate, /## Topology/);
	assert.match(orchestrate, /## Supervision/);
	assert.match(orchestrate, /isolated-worktree subagents/);

	// 5. statechart has both the new TS compiler + render.md and the preserved statechart.mjs
	assert.ok(fs.existsSync(path.join(repoDir, "skills/statechart/references/render.md")));
	assert.ok(fs.existsSync(path.join(repoDir, "skills/statechart/scripts/statechart.ts")));
	assert.ok(fs.existsSync(path.join(repoDir, "skills/statechart/scripts/statechart.mjs")));

	// 6. magic-help preserves local custom skill rows while adding synced updates
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
		"/typescript-best-practices",
		"/make-bot-ui",
	]) {
		assert.ok(magicHelp.includes(customSkill), `magic-help missing ${customSkill}`);
	}
});
