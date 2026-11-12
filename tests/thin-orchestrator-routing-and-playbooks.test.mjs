import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import test from "node:test";
import { typographyViolations } from "./helpers/markdown-checks.mjs";

const repoDir = path.resolve(import.meta.dirname, "..");
const read = (rel) => fs.readFileSync(path.join(repoDir, rel), "utf8");

const THIN_FILES = [
	"skills/using-magic/SKILL.md",
	"rules/workflow-routing.md",
	"skills/magic-mode/SKILL.md",
	"agents/magic-agent/agent.md",
	"agents/comment-sicko/agent.md",
	"skills/magic-help/SKILL.md",
];

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
	assert.match(text, /orchestrator:\s*thin/i);
	assert.match(text, /pull request or merge request/i);
	assert.match(text, /subtask that does not open or update a pull request or merge request/i);
});

test("using-magic wraps only heavy leaves and keeps self-dispatching skills flat in the root chat", () => {
	const usingMagic = read("skills/using-magic/SKILL.md");
	const wrapStart = usingMagic.indexOf("The heavy leaf skills are");
	assert.ok(wrapStart !== -1, "must define heavy leaf wrap paragraph");
	const wrapEnd = usingMagic.indexOf("Skills that dispatch their own depth-1 waves stay out of this list");
	assert.ok(wrapEnd > wrapStart, "must define wave-skill exclusion paragraph");
	const wrapPara = usingMagic.slice(wrapStart, wrapEnd);

	assert.doesNotMatch(wrapPara, /\/blast-radius\b/, "blast-radius dispatches its own wave");
	assert.match(wrapPara, /\/tdd\b/);
	assert.match(wrapPara, /\/technical-writing\b/);
	assert.match(wrapPara, /\/sharpen\b/);
	assert.match(wrapPara, /\/proving-\*/);
	assert.match(wrapPara, /\/auditing-proof-specifications\b/);
	assert.match(wrapPara, /\/statechart\b/);

	const wavePara = usingMagic.slice(wrapEnd);
	assert.match(wavePara, /\/blast-radius\b/);
	assert.match(wavePara, /\/arena\b/);
	assert.match(wavePara, /\/architect\b/);
	assert.match(wavePara, /\/research\b/);
	assert.match(wavePara, /\/why\b/);
	assert.match(wavePara, /\/no-comments\b/);
	assert.match(wavePara, /\/interrogate\b/);

	assert.match(usingMagic, /# Using Magic/);
	assert.match(usingMagic, /\/make-pr-easy-to-review/);
	assert.match(usingMagic, /Pre-Routing Guard/);
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
test("research binds every subagent to magic-models, runs Tier 2 through the synthesizer, and names research-planner", () => {
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
