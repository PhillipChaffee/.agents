import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import test from "node:test";

const repoDir = path.resolve(import.meta.dirname, "..");

const THIN_FILES = [
	"skills/using-magic/SKILL.md",
	"rules/workflow-routing.md",
	"skills/magic-mode/SKILL.md",
	"agents/magic-agent/agent.md",
	"agents/comment-sicko/agent.md",
	"skills/magic-help/SKILL.md",
];

const read = (rel) => fs.readFileSync(path.join(repoDir, rel), "utf8");

const TASK2_FILES = [
	"skills/research/SKILL.md",
	"agents/research-planner/agent.md",
	"agents/research-synthesizer/agent.md",
	"agents/researcher-deep/agent.md",
	"skills/research-summary/SKILL.md",
	"skills/why/SKILL.md",
	"skills/arena/SKILL.md",
	"skills/architect/SKILL.md",
	"skills/no-comments/SKILL.md",
	"skills/interrogate/SKILL.md",
	"skills/blast-radius/SKILL.md",
];

const TASK3_PLAYBOOKS = [
	"feature",
	"bug-fix",
	"perf-issue",
	"hillclimb",
	"refactoring",
	"prototype",
	"visual-parity",
	"authoring-a-skill",
	"eval",
	"runtime-forensics",
	"trace-forensics",
	"investigation",
	"babysit",
	"shipping",
	"autonomous-run",
	"multi-phase-plan",
	"orchestrate",
	"autopilot-full",
	"autopilot-stack",
	"session-pickup",
	"opening-a-pr",
].map((name) => `skills/magic-mode/playbooks/${name}.md`);

const TASK3_FILES = [...TASK3_PLAYBOOKS, "skills/autopilot/SKILL.md"];

const playbook = (name) => read(`skills/magic-mode/playbooks/${name}.md`);

function typographyViolations(text, file) {
	const violations = [];
	const lines = text.split("\n");
	// YAML frontmatter carries configuration colons by design.
	const frontmatterEndLine = text.startsWith("---\n")
		? lines.findIndex((line, index) => index > 0 && line.trim() === "---")
		: -1;
	let inFence = false;
	lines.forEach((line, index) => {
		const trimmed = line.trim();
		if (index <= frontmatterEndLine) return;
		if (trimmed.startsWith("```")) {
			inFence = !inFence;
			return;
		}
		if (/[\u2013\u2014]/.test(line)) {
			violations.push(`${file}:${index + 1}: dash character ${trimmed}`);
		}
		if (inFence || trimmed === "" || trimmed.startsWith("|") || trimmed.startsWith("#")) return;
		const prose = line
			.replace(/`[^`]*`/g, "")
			.replace(/https?:\/\/\S+/g, "")
			.replace(/\([^)]*\)/g, "");
		if (!prose.includes(":")) return;
		// A colon may end a lead-in before a list, table, or code block.
		if (prose.trimEnd().endsWith(":")) return;
		violations.push(`${file}:${index + 1}: mid-sentence colon ${trimmed}`);
	});
	return violations;
}

test("using-magic, workflow-routing, magic-mode, magic-agent, and comment-sicko enforce flat depth-1 thin orchestration", () => {
	const usingMagic = read("skills/using-magic/SKILL.md");
	assert.match(usingMagic, /orchestrator:\s*thin/i);
	assert.match(usingMagic, /magic-agent/);

	const routing = read("rules/workflow-routing.md");
	assert.match(routing, /orchestrator:\s*thin|subagent tool/i);

	const magicMode = read("skills/magic-mode/SKILL.md");
	assert.match(magicMode, /depth\s*1|depth-1/i);
	assert.match(magicMode, /models\.json/);
	assert.doesNotMatch(magicMode, /\bcreate-skill\b/);

	const sicko = read("agents/comment-sicko/agent.md");
	assert.doesNotMatch(sicko, /run `\/how`, `\/why`, or both/i);
	assert.match(sicko, /NEEDS-GROUNDING/);
});

test("workflow-routing.md keeps its routing contract inside the 250-word budget with a thin-mode leaf wrap", () => {
	const text = read("rules/workflow-routing.md");
	assert.ok(text.startsWith("---\n"), "workflow-routing.md must open with frontmatter");
	const end = text.indexOf("\n---", 4);
	assert.notEqual(end, -1, "workflow-routing.md frontmatter must close");
	const frontmatter = text.slice(4, end);
	const keys = frontmatter
		.split("\n")
		.map((line) => line.split(":")[0])
		.filter(Boolean);
	assert.deepEqual(keys, ["alwaysApply", "description"], "frontmatter keys must stay sorted");

	const words = text
		.slice(end + 4)
		.trim()
		.split(/\s+/)
		.filter(Boolean).length;
	assert.ok(words < 250, `workflow-routing.md body has ${words} words (budget < 250)`);

	assert.match(text, /\/make-pr-easy-to-review/);
	assert.match(text, /pull request or merge request/i);
	assert.match(text, /subtask that does not open or update a pull request or merge request/i);
	assert.match(text, /orchestrator:\s*thin/);
	assert.match(text, /subagent tool/);
	assert.match(text, /magic-agent/);
	assert.match(text, /Route before you explore|before you explore|multi-file exploration/i);
	assert.doesNotMatch(text, /# orchestrator: thin/, "rules must not shadow the injected magic-models header");
});

test("using-magic gates the leaf wrap on thin mode plus a subagent tool and keeps the stop from recursing", () => {
	const text = read("skills/using-magic/SKILL.md");
	assert.match(text, /# Using Magic/);
	assert.match(text, /\/make-pr-easy-to-review/);
	assert.match(text, /subtask that does not open or update a pull request or merge request/i);

	assert.match(text, /<SUBAGENT-STOP>/);
	assert.match(text, /never spawn a subagent/i);

	assert.match(text, /orchestrator: thin/);
	assert.match(text, /harness exposes a subagent tool/);
	assert.match(text, /pi-subagents/);
	assert.match(text, /sequentially/);
	assert.doesNotMatch(
		text,
		/# orchestrator: thin/,
		"the bootstrap text must not shadow the injected magic-models header",
	);
	for (const leaf of ["/tdd", "/technical-writing", "/sharpen", "/make-bot-ui", "/benchmark-checklist"]) {
		assert.ok(text.includes(leaf), `using-magic must name the heavy leaf skill ${leaf}`);
	}
	const wrapStart = text.indexOf("The heavy leaf skills are");
	const wrapParagraph = text.slice(wrapStart, text.indexOf("\n\n", wrapStart));
	assert.doesNotMatch(
		wrapParagraph,
		/`\/blast-radius`/,
		"blast-radius dispatches its own wave, so it must stay out of the external wrap list",
	);
	assert.match(text, /dispatch their own depth-1 waves stay out of this list/);
	assert.match(text, /`\/blast-radius`/);
	assert.match(text, /Pre-Routing Guard/);
});

test("magic-mode adds the depth-1 leaf rule, the models.json tier fallback, and thin-mode judgment delegation", () => {
	const text = read("skills/magic-mode/SKILL.md");
	assert.match(text, /Depth-1 Leaf Subagent Rule/);
	assert.match(text, /depth 0/);
	assert.match(text, /depth 1/);
	assert.match(text, /never spawn/i);
	assert.match(text, /fast, mechanical, miners/);
	assert.match(text, /judgment and prose/);
	assert.match(text, /deep/);
	assert.match(text, /models\.json/);
	assert.match(text, /opus/);
	assert.match(text, /sonnet/);
	assert.match(text, /haiku/);
	assert.match(text, /weak-parent/i);

	assert.match(text, /\/make-pr-easy-to-review/);
	assert.match(text, /take-a-step-back/);
	assert.match(text, /1-2 sentences?/i);
	assert.match(text, /###? TL;DR/);
	assert.match(text, /table/i);

	assert.match(text, /the \*\*writing-skills\*\* skill \(`\/writing-skills`\)/);
});

test("magic-help explains thin orchestration at setup and cost time and routes skill authoring to /writing-skills", () => {
	const text = read("skills/magic-help/SKILL.md");
	assert.match(text, /# orchestrator: thin/);
	assert.match(text, /dispatcher/i);
	assert.match(text, /subagent/i);
	assert.match(text, /\/setup-magic/);
	assert.doesNotMatch(text, /create-skill/);
	assert.match(text, /\/writing-skills/);
	for (const skill of ["/tdd", "/thermo-nuclear-code-quality-review", "/make-bot-ui", "/proving-with-hoare-logic"]) {
		assert.ok(text.includes(skill), `magic-help must keep routing to ${skill}`);
	}
});

test("magic-agent and comment-sicko execute as depth-1 leaves and carry no long dashes", () => {
	const magicAgent = read("agents/magic-agent/agent.md");
	assert.match(magicAgent, /depth-1 leaf/i);
	assert.match(magicAgent, /never spawn/i);

	const sicko = read("agents/comment-sicko/agent.md");
	assert.match(sicko, /NEEDS-GROUNDING/);
	assert.match(sicko, /git log -S/);
	assert.match(sicko, /git blame/);
	assert.match(sicko, /depth-1 leaf/i);

	for (const rel of THIN_FILES) {
		const text = read(rel);
		assert.doesNotMatch(text, /[\u2013\u2014]/, `${rel} must carry no en dash or em dash`);
	}
});

test("research binds every subagent to a magic-models role and routes each tier through a wave", () => {
	const text = read("skills/research/SKILL.md");
	for (const role of [
		"researcher-lite, collectors",
		"researcher-mid",
		"researcher-deep, planner, synthesizer",
	]) {
		assert.ok(text.includes(role), `research must bind the ${role} role`);
	}
	assert.match(text, /research-planner/);
	assert.match(text, /research-synthesizer/);
	assert.match(text, /orchestrator: thin/);

	const tierOne = text.slice(text.indexOf("## Tier 1"), text.indexOf("## Tier 2"));
	assert.match(tierOne, /researcher-lite, collectors/, "Tier 1 confirms facts through the collector role");
	assert.match(tierOne, /already in context|inline/i, "Tier 1 keeps in-context facts inline");

	const tierTwo = text.slice(text.indexOf("## Tier 2"), text.indexOf("## Tier 3"));
	assert.match(tierTwo, /research-synthesizer/, "Tier 2 dispatch must name the synthesizer");
	assert.match(tierTwo, /docs\/research\/<topic>\.md/, "Tier 2 keeps the cited file deliverable");
	assert.doesNotMatch(tierTwo, /synthesize them yourself/i, "Tier 2 must not synthesize on the main chat");

	const tierThree = text.slice(text.indexOf("## Tier 3"));
	assert.match(tierThree, /\*\*Plan\b[^\n]*research-planner/, "Tier 3 Step 3 names research-planner by id");
	assert.match(tierThree, /take-a-step-back/, "Tier 3 keeps take-a-step-back");
	assert.doesNotMatch(
		text,
		/Upgrade prompts must forbid tools and source lookups/,
		"the stale thinking-only contradiction must be gone",
	);
	assert.doesNotMatch(text, /upgrade criteria/, "Step 3 must point at the role table, not a removed heading");
	assert.match(tierThree, /`### When each role runs` table/);
});

test("research agents declare their roles and reconcile tool access", () => {
	const planner = read("agents/research-planner/agent.md");
	assert.match(planner, /researcher-deep, planner, synthesizer/);
	assert.match(planner, /thinking-only/i);
	assert.match(planner, /## Missing evidence/);
	assert.match(planner, /disallowedTools:/);

	const synthesizer = read("agents/research-synthesizer/agent.md");
	assert.match(synthesizer, /researcher-deep, planner, synthesizer/);
	assert.match(synthesizer, /re-read/i);
	assert.match(synthesizer, /take-a-step-back/);
	assert.match(synthesizer, /disallowedTools:/);

	const deep = read("agents/researcher-deep/agent.md");
	assert.match(deep, /researcher-deep, planner, synthesizer/);
	assert.match(deep, /MCP/);
	const contradictions = deep.match(/must not use tools|tools are forbidden/i);
	assert.equal(contradictions, null, "researcher-deep must not forbid the tools it needs");
});

test("research-summary routes its formatted summary through the synthesizer and drops simple-english", () => {
	const text = read("skills/research-summary/SKILL.md");
	assert.doesNotMatch(text, /simple-english/i);
	assert.match(text, /\/technical-writing/);
	assert.match(text, /\/unslop/);
	assert.match(text, /research-synthesizer/);
	assert.match(text, /researcher-deep, planner, synthesizer/);
	assert.match(text, /60 lines/);
});

test("why moves the code anchor into a Wave 1 collector and passes it by path", () => {
	const text = read("skills/why/SKILL.md");
	assert.match(text, /researcher-lite, collectors/);
	assert.match(text, /code-anchor\.md/);
	assert.match(text, /Anchor Collector/i);
	assert.match(text, /scratch|store directory/i);
	assert.doesNotMatch(text, /build the seed context inline/i);
	assert.match(text, /git blame/, "the collector brief still names the git commands");
	assert.match(text, /Step 4[\s\S]{0,600}code-anchor\.md/, "the synthesizer receives the anchor by path");
});

test("arena runs base selection and grafting as one mandatory arena synthesizer wave", () => {
	const text = read("skills/arena/SKILL.md");
	assert.match(text, /arena synthesizer/);
	assert.match(text, /orchestrator:/);
	assert.match(text, /magic-agent/);
	assert.match(text, /Phase D and Phase E|Phase D \+ E/);
	assert.match(text, /redesign-from-first-principles/);
	assert.match(text, /swarm workers/);
	assert.match(text, /## Outputs[\s\S]*table/i);
});

test("architect screens red flags on deep and implements through a role-routed wave", () => {
	const text = read("skills/architect/SKILL.md");
	assert.match(text, /arena synthesizer/);
	assert.match(text, /design-red-flags\.md/);
	assert.match(text, /rationale-template\.md/);
	assert.match(text, /take-a-step-back/);

	const phaseD = text.slice(text.indexOf("## Phase D"), text.indexOf("## Phase E"));
	assert.match(phaseD, /magic-agent/, "Phase D dispatches a depth-1 delegate");
	assert.match(phaseD, /feature, refactoring/);
	assert.match(phaseD, /hardest tasks/);
	assert.match(phaseD, /not implemented/);
});

test("no-comments names the comment-sicko role and delegates its fix rounds", () => {
	const text = read("skills/no-comments/SKILL.md");
	assert.match(text, /`comment-sicko` line/, "Step 1 binds the spawn to the role line");
	assert.match(text, /magic-models/);
	assert.match(text, /NEEDS-GROUNDING/);
	assert.match(text, /Steps 2-4/);
	assert.match(text, /magic-agent/);
	assert.match(text, /feature, refactoring/);
	assert.match(text, /judgment and prose/);
	assert.match(text, /This chat then reruns Wave 1 once at depth 1/, "the parent reruns the audit wave");
	assert.match(text, /Wave 2 never spawns `comment-sicko`/, "the fix wave never spawns the auditor");
	assert.match(text, /Yes\.\.\. Ha ha ha\.\.\. Yes!/, "the audit contract names the required first line");
});

test("interrogate reruns and merges reports through one judgment and prose wave", () => {
	const text = read("skills/interrogate/SKILL.md");
	assert.match(text, /judgment and prose/);
	assert.match(text, /magic-agent/);
	const verify = text.slice(text.indexOf("## Verify"), text.indexOf("## Output"));
	assert.match(verify, /judgment and prose/, "Step 3 of the run is a delegated wave");
	assert.match(verify, /repro|rerun/i);
});

test("blast-radius traces and proves through a hardest tasks wave", () => {
	const text = read("skills/blast-radius/SKILL.md");
	assert.match(text, /hardest tasks/);
	assert.match(text, /magic-agent/);
	assert.match(text, /arena/);
	const steps = text.slice(text.indexOf("## Steps"), text.indexOf("## What to hand back"));
	assert.match(steps, /magic-agent/, "Steps 1 through 5 dispatch a depth-1 delegate");
	assert.match(steps, /proof script|prove the one fact/i);
	assert.match(
		steps,
		/already runs inside a depth-1 leaf subagent[\s\S]*?execute Steps 1-5 directly in this session/,
		"a leaf runs the steps itself instead of nesting another wave",
	);
	assert.match(steps, /git blame|git log -S/, "the leaf collects its own anchor inline");
	assert.doesNotMatch(steps, /Use `why` step 2/, "the leaf must not delegate to a why subagent");
	assert.match(
		steps,
		/root chat chooses this option[\s\S]*?dispatches `arena` itself from the root chat/,
		"the arena option belongs to the root chat",
	);
});

test("the Task 2 files carry no long dashes and no mid-sentence colons", () => {
	for (const rel of TASK2_FILES) {
		assert.deepEqual(typographyViolations(read(rel), rel), [], `${rel} must stay typographically clean`);
	}
});

test("every Task 3 playbook keeps one depth-1 wave per heavy step with an explicit magic-models role", () => {
	for (const rel of TASK3_PLAYBOOKS) {
		const text = read(rel);
		assert.match(text, /magic-models/, `${rel} must resolve its subagents through the role file`);
		assert.doesNotMatch(text, /\bowner\b[^.\n]*spawns? (?:another|a nested) (?:subagent|coordinator)/i);
	}
	const feature = playbook("feature");
	assert.match(feature, /how explorer|the `how` skill/, "Wave 1 grounds through how");
	assert.match(feature, /arena synthesizer/, "Wave 2 adds the arena synthesizer check");
	assert.match(feature, /feature, refactoring/);
	assert.match(feature, /hardest tasks/);
	assert.match(feature, /swarm workers/);
	assert.match(feature, /judgment and prose/);
	assert.match(feature, /comment-sicko/);

	const bugFix = playbook("bug-fix");
	for (const role of ["bug-fix", "how explorer", "why investigators", "architect", "swarm workers", "tdd"]) {
		assert.ok(bugFix.includes(role), `bug-fix must name ${role}`);
	}
	assert.match(bugFix, /take-a-step-back/);

	const perfIssue = playbook("perf-issue");
	for (const role of ["perf-issue", "how explorer", "hardest tasks", "swarm workers", "benchmark-checklist"]) {
		assert.ok(perfIssue.includes(role), `perf-issue must name ${role}`);
	}

	const hillclimb = playbook("hillclimb");
	for (const role of ["hillclimb", "judgment and prose", "hardest tasks", "benchmark-checklist", "decision.tsv"]) {
		assert.ok(hillclimb.includes(role), `hillclimb must name ${role}`);
	}

	const refactoring = playbook("refactoring");
	for (const role of ["feature, refactoring", "architect", "swarm workers", "judgment and prose", "take-a-step-back"]) {
		assert.ok(refactoring.includes(role), `refactoring must name ${role}`);
	}

	const prototype = playbook("prototype");
	assert.match(prototype, /feature, refactoring/);
	assert.match(prototype, /swarm|arena/);

	const visualParity = playbook("visual-parity");
	for (const role of ["feature, refactoring", "swarm workers"]) {
		assert.ok(visualParity.includes(role), `visual-parity must name ${role}`);
	}

	const authoring = playbook("authoring-a-skill");
	assert.match(authoring, /writing-skills/);
	assert.doesNotMatch(authoring, /\bcreate-skill\b/);
	assert.match(authoring, /arena cross-judge pool|swarm workers/);
	assert.match(authoring, /judgment and prose/);

	const evalPlaybook = playbook("eval");
	for (const role of ["judgment and prose", "arena runners", "arena cross-judge pool"]) {
		assert.ok(evalPlaybook.includes(role), `eval must name ${role}`);
	}

	const runtime = playbook("runtime-forensics");
	assert.match(runtime, /fast, mechanical, miners/);
	assert.match(runtime, /bug-fix|hardest tasks/);

	const trace = playbook("trace-forensics");
	assert.match(trace, /fast, mechanical, miners/);
	assert.match(trace, /bug-fix|hardest tasks/);

	const investigation = playbook("investigation");
	assert.match(investigation, /how explainer/);
	assert.match(investigation, /why synthesizer/);
	assert.match(investigation, /take-a-step-back/);

	const babysit = playbook("babysit");
	assert.match(babysit, /judgment and prose/);
	assert.match(babysit, /bug-fix/);
	assert.match(babysit, /review-bot-triage\.md/);
	assert.match(babysit, /NEEDS-GROUNDING|grounding wave/i, "a triage leaf reports a grounding need instead of nesting");

	const shipping = playbook("shipping");
	assert.match(shipping, /swarm workers/);
	assert.match(shipping, /feature, refactoring/);
	assert.match(shipping, /patch-id/);

	const autonomous = playbook("autonomous-run");
	assert.match(autonomous, /fast, mechanical, miners/);
	assert.match(autonomous, /judgment and prose/);
	assert.match(autonomous, /take-a-step-back/);
	assert.match(autonomous, /feature, refactoring/);

	const multiPhase = playbook("multi-phase-plan");
	for (const role of ["how explorer", "fast, mechanical, miners", "hardest tasks", "judgment and prose"]) {
		assert.ok(multiPhase.includes(role), `multi-phase-plan must name ${role}`);
	}
	assert.match(multiPhase, /check-plan\.mjs/);
	assert.match(multiPhase, /take-a-step-back/);

	const orchestrate = playbook("orchestrate");
	assert.match(orchestrate, /## Topology/);
	assert.match(orchestrate, /## Supervision/);
	assert.match(orchestrate, /isolated-worktree subagents/);
	assert.match(orchestrate, /depth >= 2/);
	assert.match(orchestrate, /feature, refactoring/);
	assert.match(orchestrate, /arena cross-judge pool/);
	assert.match(orchestrate, /swarm workers/);

	const autopilotFull = playbook("autopilot-full");
	assert.match(autopilotFull, /feature, refactoring/);
	assert.match(autopilotFull, /swarm workers/);
	assert.match(autopilotFull, /comment-sicko/);
	assert.match(autopilotFull, /arena cross-judge pool/);
	assert.match(autopilotFull, /make-pr-easy-to-review/);
	assert.match(
		autopilotFull,
		/root (?:coordinator|chat) dispatches `comment-sicko`[\s\S]*?depth 1/,
		"the root dispatches the comment audit flat at code-ready",
	);
	assert.doesNotMatch(autopilotFull, /owner spawns `comment-sicko`/, "a PR owner never nests the comment audit");

	const stack = playbook("autopilot-stack");
	assert.match(stack, /feature, refactoring|autopilot-full/);

	const pickup = playbook("session-pickup");
	assert.match(pickup, /fast, mechanical, miners/);
	assert.match(pickup, /judgment and prose/);
	assert.match(pickup, /swarm workers/);

	const opening = playbook("opening-a-pr");
	assert.match(opening, /judgment and prose/);
	assert.match(opening, /comment-sicko/);
	assert.match(opening, /HEAD\^\{tree\}/);
	assert.match(opening, /make-pr-easy-to-review/);
	assert.match(
		opening,
		/root (?:chat|coordinator) (?:runs|dispatches) `?\/no-comments`?/,
		"the root chat runs the comment audit flat for a PR leaf",
	);
});

test("feature, autopilot-full, and opening-a-pr carry no nested owner fan-out", () => {
	const feature = playbook("feature");
	assert.doesNotMatch(feature, /fans out internally/, "the feature owner must not fan out internally");
	assert.match(feature, /Wave 3a/);
	assert.match(feature, /Wave 3b/);
	assert.match(feature, /root chat fans out/, "the root chat dispatches the parallel implementation wave");

	const full = playbook("autopilot-full");
	assert.doesNotMatch(full, /owner[^\n]*runs `\/no-comments`/, "the PR owner never runs /no-comments itself");

	const opening = playbook("opening-a-pr");
	assert.doesNotMatch(opening, /subagent[^\n]*spawns `comment-sicko`/);
	assert.match(opening, /depth 1/);
});

test("autopilot drops the leaked model name and the deleted rule names for depth-1 waves", () => {
	const text = read("skills/autopilot/SKILL.md");
	assert.doesNotMatch(text, /Claude Opus|python-docstrings-google|minimal-changes/);
	assert.doesNotMatch(text, /comment-style|`engineering`|code-organization/);
	assert.match(text, /magic-models/);
	assert.match(text, /judgment and prose/);
	assert.match(text, /bug-fix/);
	assert.match(text, /Conflict-Resolver/);
	assert.match(text, /depth-1|depth 1/);
	assert.match(text, /baseline_changed_lines/);
	assert.match(text, /growth_budget/);
	assert.match(text, /1-2 sentences?/i);
	assert.match(text, /###? TL;DR/);
	assert.match(text, /table/i);
});

test("the validator BANNED regex rejects capitalized vendor model prose", () => {
	const source = read("scripts/validate.sh");
	const block = source.match(/BANNED = re\.compile\(\n([\s\S]*?)\n\)/);
	assert.ok(block, "scripts/validate.sh must define the BANNED regex");
	const pattern = block[1];
	for (const fragment of ["Claude (?:Opus|Sonnet|Haiku)", "GPT-[0-9]", "Gemini [0-9]", "Grok [0-9]"]) {
		assert.ok(pattern.includes(fragment), `BANNED must include ${fragment}`);
	}
	const script = [
		"import os, re, sys",
		"pattern = re.compile(eval('(' + os.environ['BANNED_SRC'] + ')'))",
		"text = os.environ['BANNED_TEXT']",
		"sys.exit(0 if pattern.search(text) else 1)",
	].join("\n");
	const rejects = (text) =>
		spawnSync("python3", ["-c", script], {
			env: { ...process.env, BANNED_SRC: block[1], BANNED_TEXT: text },
		}).status === 0;
	for (const text of [
		"Claude Opus 5.5 xhigh",
		"Claude Sonnet 4",
		"Claude Haiku",
		"GPT-5",
		"Gemini 3",
		"Grok 4",
	]) {
		assert.ok(rejects(text), `BANNED must reject ${text}`);
	}
	for (const text of ["Claude Code", "the deep tier", "a judgment and prose wave"]) {
		assert.ok(!rejects(text), `BANNED must allow ${text}`);
	}
});

test("the Task 3 files carry no long dashes and no mid-sentence colons", () => {
	for (const rel of TASK3_FILES) {
		assert.deepEqual(typographyViolations(read(rel), rel), [], `${rel} must stay typographically clean`);
	}
});

const TASK4_SKILLS = [
	"skills/make-pr-easy-to-review/SKILL.md",
	"skills/subagent-driven-development/SKILL.md",
	"skills/thermo-nuclear-code-quality-review/SKILL.md",
	"skills/writing-plans/SKILL.md",
	"skills/writing-skills/SKILL.md",
];

const UPSTREAM_DIRS = [
	"skills/writing-plans",
	"skills/subagent-driven-development",
	"skills/writing-skills",
];

function markdownFilesUnder(dir) {
	const files = [];
	for (const entry of fs.readdirSync(path.join(repoDir, dir), { withFileTypes: true })) {
		const rel = `${dir}/${entry.name}`;
		if (entry.isDirectory()) files.push(...markdownFilesUnder(rel));
		else if (entry.name.endsWith(".md")) files.push(rel);
	}
	return files;
}

// A fence opens with an info string and closes bare. A shorter fence inside a
// longer block is literal content, and a closing fence that carries an info
// string silently swallows everything after it.
function fenceProblems(rel) {
	const problems = [];
	let open = null;
	read(rel)
		.split("\n")
		.forEach((line, index) => {
			const match = line.match(/^[ \t]*(`{3,}|~{3,})(.*)$/);
			if (!match) return;
			const fence = match[1];
			const info = match[2].trim();
			const lineNo = index + 1;
			if (open === null) {
				open = { char: fence[0], length: fence.length, line: lineNo };
				if (!info) problems.push(`${rel}:${lineNo}: opening fence needs an info string`);
				return;
			}
			if (fence[0] !== open.char || fence.length < open.length) return;
			if (info) {
				problems.push(`${rel}:${lineNo}: closing fence must be bare (opened on line ${open.line})`);
			}
			open = null;
		});
	if (open !== null) problems.push(`${rel}:${open.line}: fence never closes`);
	return problems;
}

test("every adapted skill fence opens with an info string and closes bare", () => {
	const problems = [];
	for (const dir of [
		...UPSTREAM_DIRS,
		"skills/make-pr-easy-to-review",
		"skills/thermo-nuclear-code-quality-review",
	]) {
		for (const rel of markdownFilesUnder(dir)) problems.push(...fenceProblems(rel));
	}
	assert.deepEqual(problems, [], "an info string on a closing fence hides the markdown after it");
});

// Links inside fenced code blocks are illustrative, and lychee skips them.
function markdownLinks(rel) {
	const links = [];
	let fence = null;
	for (const line of read(rel).split("\n")) {
		const trimmed = line.trim();
		const marker = trimmed.match(/^(`{3,}|~{3,})/);
		if (marker) {
			if (fence === null) fence = marker[1][0];
			else if (marker[1][0] === fence) fence = null;
			continue;
		}
		if (fence !== null) continue;
		for (const match of line.matchAll(/\]\(([^)\s]+)\)/g)) links.push(match[1]);
	}
	return links;
}

test("the validator reports zero FAIL and zero WARN lines with the adapted upstream skills un-ignored", () => {
	const source = read("scripts/validate.sh");
	assert.doesNotMatch(
		source,
		/rel\.startswith\(\("skills\/writing-skills\/"/,
		"validate.sh must not skip the adapted upstream skills",
	);

	const result = spawnSync("./scripts/validate.sh", { cwd: repoDir, encoding: "utf8" });
	assert.equal(result.status, 0, `validate.sh exited ${result.status}:\n${result.stdout}${result.stderr}`);
	const lines = result.stdout.split("\n");
	assert.deepEqual(
		lines.filter((line) => line.startsWith("WARN ")),
		[],
		"validate.sh must report no WARN lines",
	);
	assert.deepEqual(
		lines.filter((line) => line.startsWith("FAIL ")),
		[],
		"validate.sh must report no FAIL lines",
	);
});

test("the five adapted SKILL.md files sort their frontmatter keys", () => {
	for (const rel of TASK4_SKILLS) {
		const text = read(rel);
		assert.ok(text.startsWith("---\n"), `${rel} must open with frontmatter`);
		const end = text.indexOf("\n---", 4);
		assert.notEqual(end, -1, `${rel} frontmatter must close`);
		const keys = text
			.slice(4, end)
			.split("\n")
			.map((line) => line.split(":")[0].trim())
			.filter((key) => /^[A-Za-z][A-Za-z0-9-]*$/.test(key));
		assert.deepEqual(keys, [...keys].sort(), `${rel} frontmatter keys must stay sorted`);
	}
});

test("the lint configs and the verbatim list stop exempting the adapted upstream skills", () => {
	const verbatim = read("scripts/magic-verbatim.txt");
	assert.doesNotMatch(verbatim, /^skills\//m, "magic-verbatim.txt holds no skill path");
	assert.match(verbatim, /^#/m, "magic-verbatim.txt keeps a comment header explaining why it is empty");

	const markdownlint = read(".markdownlint-cli2.jsonc");
	for (const dir of ["writing-skills", "writing-plans", "subagent-driven-development"]) {
		assert.ok(
			!markdownlint.includes(`!skills/${dir}/**`),
			`.markdownlint-cli2.jsonc must lint skills/${dir}`,
		);
	}
	assert.match(
		markdownlint,
		/\.superpowers\/\*\*/,
		".markdownlint-cli2.jsonc must ignore the gitignored .superpowers scratch tree",
	);
	assert.doesNotMatch(
		markdownlint,
		/"!\S+"/,
		'an ignores entry starting with "!" cancels the glob set and lints nothing',
	);

	const lychee = read("lychee.toml");
	for (const dir of ["writing-skills", "writing-plans", "subagent-driven-development"]) {
		assert.ok(!lychee.includes(`./skills/${dir}`), `lychee.toml must check skills/${dir}`);
	}

	const typos = read(".typos.toml");
	for (const dir of ["writing-skills", "writing-plans", "subagent-driven-development"]) {
		assert.ok(!typos.includes(`"skills/${dir}"`), `.typos.toml must spell-check skills/${dir}`);
	}
});

test("THIRD-PARTY-NOTICES records the adapted upstream skills and keeps their provenance", () => {
	const text = read("THIRD-PARTY-NOTICES.md");
	assert.match(text, /are adapted from/, "the notices must say the skills are adapted, not copied");
	assert.doesNotMatch(
		text,
		/copied without content changes from\s*\n?\[obra\/superpowers\]/,
		"the superpowers skills are adapted, so the copied-verbatim claim is gone",
	);
	for (const path of [
		"skills/writing-skills/",
		"skills/writing-plans/",
		"skills/subagent-driven-development/",
		"skills/make-pr-easy-to-review/",
		"skills/thermo-nuclear-code-quality-review/",
	]) {
		assert.ok(text.includes(path), `THIRD-PARTY-NOTICES.md must name ${path}`);
	}
	for (const ref of [
		"obra/superpowers",
		"22f0b463e7a5e579904dd6211a520321035526f7",
		"hooks/run-hook.cmd",
		"hooks/session-start",
		"lib/bootstrap-core.js",
		".opencode/plugins/magic.js",
		".pi/extensions/magic.ts",
	]) {
		assert.ok(text.includes(ref), `THIRD-PARTY-NOTICES.md must keep ${ref}`);
	}
});

test("the adapted references keep valid code spans, tier names, and explicit final-review placeholders", () => {
	const discovery = read("skills/writing-skills/references/discovery.md");
	assert.match(discovery, /`\*\*REQUIRED SUB-SKILL:\*\* Use \/tdd`/, "the exemplar is one code span");
	assert.doesNotMatch(discovery, /`Use`\/tdd``/, "a code span must not be split by its own backtick");

	for (const rel of markdownFilesUnder("skills/writing-skills/references")) {
		assert.doesNotMatch(
			read(rel),
			/\b(?:Haiku|Sonnet|Opus)\b/,
			`${rel} must name the fast, main, and deep tiers instead of vendor models`,
		);
	}

	const finalReview = read("skills/subagent-driven-development/references/final-review.md");
	for (const placeholder of [
		"**Framing.**",
		"`[BRIEF_FILE]`",
		"`[REPORT_FILE]`",
		"pre-merge whole-branch review",
		"progress.md",
	]) {
		assert.ok(
			finalReview.includes(placeholder),
			`final-review.md must spell out ${placeholder} for the reused reviewer template`,
		);
	}

	const writingPlans = read("skills/writing-plans/SKILL.md");
	assert.match(
		writingPlans,
		/Under `orchestrator: thin`, when the harness exposes a subagent tool:[\s\S]{0,400}recommend Subagent-driven/,
		"thin mode recommends subagent-driven execution",
	);
	assert.match(
		writingPlans,
		/Under `orchestrator: standard`, inline is the default/,
		"standard mode makes the recommendation a per-plan choice",
	);
});

test("the adapted upstream skills carry no superpowers references and no broken relative links", () => {
	const broken = [];
	for (const dir of UPSTREAM_DIRS) {
		for (const rel of markdownFilesUnder(dir)) {
			const text = read(rel);
			assert.doesNotMatch(text, /superpowers:/, `${rel} must not reference an external skill namespace`);
			const base = path.dirname(path.join(repoDir, rel));
			for (const link of markdownLinks(rel)) {
				if (/^[a-z]+:/i.test(link) || link.startsWith("#")) continue;
				const target = link.split("#")[0];
				if (!target) continue;
				if (!fs.existsSync(path.resolve(base, target))) broken.push(`${rel}: ${link}`);
			}
		}
	}
	assert.deepEqual(broken, [], "every relative link in the adapted skills must resolve");
});

test("subagent-driven-development binds every seat to a magic-models role and delegates adjudication", () => {
	const skill = read("skills/subagent-driven-development/SKILL.md");
	for (const role of [
		"fast, mechanical, miners",
		"feature, refactoring",
		"sdd reviewer",
		"hardest tasks",
		"judgment and prose",
		"arena cross-judge pool",
	]) {
		assert.ok(skill.includes(role), `SKILL.md must bind the ${role} role`);
	}
	assert.match(skill, /model-roles\.md/, "Model Selection resolves through the role file");
	assert.match(skill, /orchestrator: thin/, "the preflight ruling runs under thin mode");
	assert.match(skill, /orchestrator: standard/, "inline execution stays named");
	assert.match(skill, /harness-adapter\.md/);
	assert.match(skill, /opening-a-pr\.md/);
	assert.doesNotMatch(skill, /executing-plans/, "inline execution is /magic-mode now");
	assert.doesNotMatch(skill, /finishing-a-development-branch/);

	for (const rel of [
		"skills/subagent-driven-development/implementer-prompt.md",
		"skills/subagent-driven-development/task-reviewer-prompt.md",
		"skills/subagent-driven-development/re-review-prompt.md",
	]) {
		const text = read(rel);
		assert.match(text, /magic-models/, `${rel} names the role file`);
		assert.doesNotMatch(text, /\[MODEL/, `${rel} names a role instead of a model placeholder`);
	}
	assert.match(read("skills/subagent-driven-development/implementer-prompt.md"), /fast, mechanical, miners/);
	assert.match(read("skills/subagent-driven-development/task-reviewer-prompt.md"), /sdd reviewer/);
	assert.match(read("skills/subagent-driven-development/re-review-prompt.md"), /sdd reviewer/);

	const preflight = read("skills/subagent-driven-development/references/preflight.md");
	assert.match(preflight, /judgment and prose/, "the preflight scan runs on the deep judgment role");
	assert.match(preflight, /Adjudicator/i);
	assert.match(preflight, /progress\.md/, "the ruling lands in the ledger");
	assert.match(preflight, /Ruling:/);

	const fixLoop = read("skills/subagent-driven-development/references/fix-loop.md");
	assert.match(fixLoop, /judgment and prose/, "round-5 breaker rulings run on the deep judgment role");
	assert.match(fixLoop, /Adjudicator/i);

	const finalReview = read("skills/subagent-driven-development/references/final-review.md");
	assert.match(finalReview, /task-reviewer-prompt\.md/, "the final review reuses the task reviewer template");
	assert.doesNotMatch(finalReview, /requesting-code-review/);
	assert.match(finalReview, /arena cross-judge pool/);
	assert.match(finalReview, /deferred minor/i);
	assert.match(finalReview, /opening-a-pr\.md/);
});

test("writing-plans dispatches a plan-author wave and recommends subagent-driven execution", () => {
	const text = read("skills/writing-plans/SKILL.md");
	assert.match(text, /orchestrator: thin/);
	assert.match(text, /orchestrator: standard/);
	assert.match(text, /harness-adapter\.md/);
	assert.match(text, /how explorer/, "Wave 1 grounds the target files through how");
	assert.match(text, /hardest tasks/);
	assert.match(text, /judgment and prose/);
	assert.match(text, /magic-agent/);
	assert.match(text, /docs\/superpowers\/plans\/YYYY-MM-DD-<feature-name>\.md/);
	for (const check of ["Spec coverage", "Step scan", "Type consistency", "Review Focus", "Proportion"]) {
		assert.ok(text.includes(check), `the plan-author self-review keeps ${check}`);
	}
	assert.match(text, /\/subagent-driven-development/);
	assert.match(text, /inline/, "inline execution is the /magic-mode fallback");
	assert.match(text, /depth-1/);
	assert.doesNotMatch(text, /using-git-worktrees/);
	assert.doesNotMatch(text, /executing-plans/);
});

test("writing-skills links the harness adapter and /tdd and delegates its drafting wave", () => {
	const text = read("skills/writing-skills/SKILL.md");
	assert.match(text, /\.\.\/magic-mode\/references\/harness-adapter\.md/);
	assert.match(text, /\.\.\/tdd\/SKILL\.md/);
	assert.match(text, /arena cross-judge pool/, "pressure-test seats come from the cross-family pool");
	assert.match(text, /judgment and prose/);
	assert.match(text, /magic-agent/);
	assert.match(text, /orchestrator: thin/);
	assert.match(text, /depth-1/);
	assert.doesNotMatch(text, /using-superpowers/);
	assert.doesNotMatch(text, /test-driven-development/, "the background skill is /tdd now");
});

test("make-pr-easy-to-review resolves forge operations and dispatches one history-cleanup wave", () => {
	const text = read("skills/make-pr-easy-to-review/SKILL.md");
	assert.doesNotMatch(text, /\bgh pr\b/);
	assert.doesNotMatch(text, /\borigin pr\b/);
	assert.match(text, /forge-operations\.md/);
	assert.match(text, /issue-tracker\.md/);
	assert.match(text, /view PR/);
	assert.match(text, /edit PR/);
	assert.match(text, /open PR/);
	assert.match(text, /HEAD\^\{tree\}/);
	assert.match(text, /judgment and prose/);
	assert.match(text, /feature, refactoring/);
	assert.match(text, /depth-1/);
	assert.match(text, /subagent tool/);
	assert.match(text, /inside a depth-1 leaf subagent/i, "a leaf runs the cleanup itself");
});

test("thermo-nuclear-code-quality-review dispatches one depth-1 review wave", () => {
	const text = read("skills/thermo-nuclear-code-quality-review/SKILL.md");
	assert.match(text, /depth-1/);
	assert.match(text, /magic-agent/);
	assert.match(text, /hardest tasks/);
	assert.match(text, /judgment and prose/);
	assert.match(text, /interrogate reviewers/);
	assert.match(text, /inside a depth-1 leaf subagent/i);
	assert.match(text, /structured report/i);
	assert.match(text, /subagent tool/);
});

test("using-magic keeps the adapted skills out of the wrap list and names their own dispatch", () => {
	const text = read("skills/using-magic/SKILL.md");
	const wrapStart = text.indexOf("The heavy leaf skills are");
	const wrapParagraph = text.slice(wrapStart, text.indexOf("\n\n", wrapStart));
	for (const selfDispatching of [
		"/make-pr-easy-to-review",
		"/thermo-nuclear-code-quality-review",
		"/writing-plans",
		"/subagent-driven-development",
		"/writing-skills",
	]) {
		assert.ok(
			text.includes(selfDispatching),
			`using-magic must name ${selfDispatching} so routing stays unambiguous`,
		);
		assert.ok(
			!wrapParagraph.includes(`\`${selfDispatching}\``),
			`${selfDispatching} dispatches its own wave, so it stays out of the external wrap list`,
		);
	}
	const selfDispatchStart = text.indexOf("Skills that dispatch their own depth-1 waves stay out of this list");
	const selfDispatchParagraph = text.slice(selfDispatchStart, text.indexOf("\n\n", selfDispatchStart));
	assert.match(selfDispatchParagraph, /\/writing-plans/);
	assert.match(selfDispatchParagraph, /\/subagent-driven-development/);
});

const TASK5_SKILLS = [
	"skills/recall/SKILL.md",
	"skills/automate-me/SKILL.md",
	"skills/reflect/SKILL.md",
	"skills/teach/SKILL.md",
	"skills/ketchup/SKILL.md",
	"skills/ketchup-video/SKILL.md",
	"skills/show-me-your-work/SKILL.md",
	"skills/figure-it-out/SKILL.md",
	"skills/correct/SKILL.md",
	"skills/writing-rules/SKILL.md",
	"skills/create-verification-skill/SKILL.md",
	"skills/maintain-verification-skill/SKILL.md",
	"skills/create-formal-verification-skill/SKILL.md",
	"skills/maintain-formal-verification-skill/SKILL.md",
	"skills/proof-driven-development/SKILL.md",
	"skills/proving-with-hoare-logic/SKILL.md",
	"skills/proving-with-dependent-types/SKILL.md",
	"skills/model-checking-protocols-and-code/SKILL.md",
	"skills/analyzing-with-abstract-interpretation/SKILL.md",
	"skills/auditing-proof-specifications/SKILL.md",
	"skills/statechart/SKILL.md",
];

test("the Task 5 standalone skills bind every wave to a magic-models role", () => {
	const expects = {
		"skills/recall/SKILL.md": ["fast, mechanical, miners", "why investigators", "why synthesizer", "orchestrator: thin"],
		"skills/automate-me/SKILL.md": ["fast, mechanical, miners", "judgment and prose", "/writing-skills"],
		"skills/reflect/SKILL.md": ["/writing-skills", "judgment and prose"],
		"skills/teach/SKILL.md": ["judgment and prose", "Wave 3"],
		"skills/ketchup/SKILL.md": ["judgment and prose", "orchestrator: thin"],
		"skills/ketchup-video/SKILL.md": [
			"magic-agent",
			"feature, refactoring",
			"judgment and prose",
			"## Subtitles",
		],
		"skills/show-me-your-work/SKILL.md": ["fast, mechanical, miners", "arena cross-judge pool"],
		"skills/figure-it-out/SKILL.md": [
			"hardest tasks",
			"arena cross-judge pool",
			"feature, refactoring",
			"take-a-step-back",
		],
		"skills/correct/SKILL.md": ["why investigators", "hardest tasks", "feature, refactoring"],
		"skills/writing-rules/SKILL.md": [
			"arena cross-judge pool",
			"judgment and prose",
			"feature, refactoring",
		],
		"skills/create-verification-skill/SKILL.md": [
			"how explorer",
			"feature, refactoring",
			"swarm workers",
			"magic-agent",
		],
		"skills/maintain-verification-skill/SKILL.md": [
			"fast, mechanical, miners",
			"swarm workers",
			"feature, refactoring",
			"opening-a-pr.md",
		],
		"skills/create-formal-verification-skill/SKILL.md": ["hardest tasks", "swarm workers"],
		"skills/maintain-formal-verification-skill/SKILL.md": ["hardest tasks", "swarm workers"],
	};
	for (const [rel, needles] of Object.entries(expects)) {
		const text = read(rel);
		for (const needle of needles) {
			assert.ok(text.includes(needle), `${rel} must bind ${needle}`);
		}
	}
});

test("no active skill and no magic-guide page sends authors to the retired create-skill name", () => {
	const offenders = [];
	for (const rel of markdownFilesUnder("skills")) {
		if (/\bcreate-skill\b/.test(read(rel))) offenders.push(rel);
	}
	for (const entry of fs.readdirSync(path.join(repoDir, "docs/magic-guide"))) {
		if (!entry.endsWith(".md")) continue;
		const rel = `docs/magic-guide/${entry}`;
		const text = read(rel);
		if (/\bcreate-skill\b/.test(text)) offenders.push(`${rel} (create-skill)`);
		if (/installed separately with the main flow/i.test(text)) offenders.push(`${rel} (external /tdd)`);
	}
	assert.deepEqual(offenders, [], "skill authoring routes through /writing-skills and /tdd ships in the kit");
});

test("the superseded ADRs are marked and the pstack ADR records the current names", () => {
	const adr4 = read("docs/adr/0004-mattpocock-main-flow.md");
	const adr5 = read("docs/adr/0005-combined-two-tier-code-review.md");
	for (const [rel, text] of [
		["docs/adr/0004-mattpocock-main-flow.md", adr4],
		["docs/adr/0005-combined-two-tier-code-review.md", adr5],
	]) {
		assert.match(text, /Status: Superseded/, `${rel} must open with a superseded notice`);
		assert.match(text, /magic-mode/, `${rel} names the replacement entry point`);
	}
	assert.match(adr5, /code-review/, "the notice names the retired suite");
	assert.match(adr4, /interrogate|thermo-nuclear-code-quality-review/);

	const adr8 = read("docs/adr/0008-pstack-port.md");
	assert.match(adr8, /`magic-mode`|magic-mode/);
	assert.match(adr8, /`magic-agent`/);
	assert.match(adr8, /`magic-models`/);
	assert.match(adr8, /\/setup-magic/);
	assert.match(adr8, /renam/i, "the port records the rename from the upstream names");
	assert.match(adr8, /`poteto-mode`/, "the rename note keeps the old name for history");
	assert.match(adr8, /25 one-principle skills/);
	assert.match(adr8, /0\.15\.36/);
	assert.match(adr8, /`tdd`, `typescript-best-practices`, and `make-bot-ui`/);
});

// The standalone skills are prose shaped, so they take the full Variant C rule.
const TASK5_PROSE_SKILLS = TASK5_SKILLS.filter(
	(rel) => !/writing-rules|proof-driven-development|proving-with|model-checking-protocols|analyzing-with-abstract|auditing-proof/.test(rel),
);

// The proof and rule-authoring references keep label lead-ins such as
// "Gate A (trace validation)" and "Step 3 (GREEN)" in their requirement lists,
// so their gate covers the long-dash ban and the prose blocks those edits touch.
const TASK5_DASH_ONLY_SKILLS = TASK5_SKILLS.filter((rel) => !TASK5_PROSE_SKILLS.includes(rel));

test("the Task 5 prose skills carry no long dashes and no mid-sentence colons", () => {
	for (const rel of TASK5_PROSE_SKILLS) {
		assert.deepEqual(typographyViolations(read(rel), rel), [], `${rel} must stay typographically clean`);
	}
});

test("every Task 5 skill carries no long dashes", () => {
	for (const rel of TASK5_DASH_ONLY_SKILLS) {
		assert.doesNotMatch(read(rel), /[\u2013\u2014]/, `${rel} must carry no en dash or em dash`);
	}
});
