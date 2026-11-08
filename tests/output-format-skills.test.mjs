import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";

const repoRoot = path.resolve(import.meta.dirname, "..");

const OUTPUT_FORMAT_FILES = [
	"skills/magic-mode/SKILL.md",
	"skills/how/SKILL.md",
	"skills/how/references/explainer-prompt.md",
	"skills/why/SKILL.md",
	"skills/why/references/synthesizer-prompt.md",
	"skills/teach/SKILL.md",
	"skills/interrogate/SKILL.md",
	"skills/blast-radius/SKILL.md",
	"skills/research-summary/SKILL.md",
	"skills/research/SKILL.md",
	"skills/recall/SKILL.md",
	"skills/benchmark-checklist/SKILL.md",
	"skills/arena/SKILL.md",
	"skills/swarm/SKILL.md",
	"skills/magic-help/SKILL.md",
	"skills/autopilot/SKILL.md",
	"skills/correct/SKILL.md",
	"skills/reflect/SKILL.md",
	"skills/figure-it-out/SKILL.md",
	"skills/tdd/SKILL.md",
	"skills/writing-rules/SKILL.md",
	"agents/research-synthesizer/agent.md",
];

test("output-formatting skills enforce Variant C (1-2 sentence prose cap, section-framed tables/diagrams, and plain bottom ## TL;DR)", () => {
	for (const rel of OUTPUT_FORMAT_FILES) {
		const full = path.join(repoRoot, rel);
		assert.ok(fs.existsSync(full), `missing ${rel}`);
		const content = fs.readFileSync(full, "utf8");
		assert.match(
			content,
			/1-2 sentences?|One or two (?:plain )?sentences/i,
			`${rel} must enforce the 1-2 sentence prose block rule`,
		);
		assert.match(
			content,
			/###? TL;DR/,
			`${rel} must require a bottom ## TL;DR or ### TL;DR section`,
		);
		assert.match(
			content,
			/table/i,
			`${rel} must reference Markdown tables for structured output`,
		);
	}
});

test("how explainer-prompt enforces Variant C section framing, diagrams, and bottom ### TL;DR", () => {
	const explainer = fs.readFileSync(
		path.join(repoRoot, "skills/how/references/explainer-prompt.md"),
		"utf8",
	);
	assert.doesNotMatch(explainer, /1-2 paragraphs/i);
	assert.doesNotMatch(explainer, /If prose covers the flow, skip the diagram/i);
	assert.match(explainer, /### TL;DR/);
	assert.match(explainer, /1-sentence framing line/);
});
