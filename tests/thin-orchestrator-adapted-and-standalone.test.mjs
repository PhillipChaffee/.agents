import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import test from "node:test";
import { typographyViolations } from "./helpers/markdown-checks.mjs";

const repoDir = path.resolve(import.meta.dirname, "..");
const read = (rel) => fs.readFileSync(path.join(repoDir, rel), "utf8");

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
	assert.doesNotMatch(typos, /skills\/writing-skills/, ".typos.toml must check writing-skills");
});

test("THIRD-PARTY-NOTICES.md documents adapted skills rather than copied without changes", () => {
	const notices = read("THIRD-PARTY-NOTICES.md");
	assert.match(
		notices,
		/skills\/writing-skills\/[\s\S]*?are adapted from/,
		"Superpowers notice must declare the skills adapted",
	);
	assert.doesNotMatch(
		notices,
		/skills\/writing-skills\/[\s\S]*?are copied without content changes/,
		"stale copied without changes claim must be gone",
	);
	assert.match(
		notices,
		/skills\/make-pr-easy-to-review\/[\s\S]*?are adapted from/,
		"cursor-team-kit notice must declare the skills adapted",
	);
	assert.match(notices, /obra\/superpowers/);
	assert.match(notices, /22f0b463e7a5e579904dd6211a520321035526f7/);
});

test("writing-plans delegates under thin mode and recommends subagent-driven execution", () => {
	const text = read("skills/writing-plans/SKILL.md");
	assert.match(text, /how explorer/);
	assert.match(text, /Plan Author/);
	assert.match(text, /hardest tasks/);
	assert.match(text, /judgment and prose/);
	assert.match(text, /\/subagent-driven-development/);
	assert.match(text, /docs\/plans\//);
	assert.doesNotMatch(text, /superpowers:subagent-driven-development/);
	assert.doesNotMatch(text, /superpowers:using-git-worktrees/);
	assert.doesNotMatch(text, /superpowers:executing-plans/);
	assert.match(text, /under `orchestrator: thin`, when the harness exposes a subagent tool/i);
});

test("subagent-driven-development binds its prompt templates to magic-models roles", () => {
	const text = read("skills/subagent-driven-development/SKILL.md");
	assert.match(text, /`fast, mechanical, miners`/);
	assert.match(text, /`feature, refactoring`/);
	assert.match(text, /`sdd reviewer`/);
	assert.match(text, /`hardest tasks`/);
	assert.match(text, /`judgment and prose`/);
	assert.match(text, /`arena cross-judge pool`/);
	assert.doesNotMatch(text, /superpowers:using-git-worktrees/);
	assert.doesNotMatch(text, /superpowers:finishing-a-development-branch/);
	assert.doesNotMatch(text, /superpowers:executing-plans/);

	const implementer = read("skills/subagent-driven-development/implementer-prompt.md");
	assert.match(implementer, /fast, mechanical, miners/);
	assert.match(implementer, /feature, refactoring/);
	assert.match(implementer, /hardest tasks/);

	const reviewer = read("skills/subagent-driven-development/task-reviewer-prompt.md");
	assert.match(reviewer, /sdd reviewer/);

	const reReviewer = read("skills/subagent-driven-development/re-review-prompt.md");
	assert.match(reReviewer, /sdd reviewer/);

	const finalReview = read("skills/subagent-driven-development/references/final-review.md");
	assert.match(finalReview, /task-reviewer-prompt\.md/);
	assert.doesNotMatch(finalReview, /requesting-code-review/);
	assert.match(finalReview, /judgment and prose/);
	assert.match(finalReview, /arena cross-judge pool/);
});

test("writing-skills delegates drafting and binds its pressure testing to the cross-judge pool", () => {
	const text = read("skills/writing-skills/SKILL.md");
	assert.doesNotMatch(text, /superpowers:test-driven-development/);
	assert.doesNotMatch(text, /using-superpowers/);
	assert.match(text, /\[tdd\]\(\.\.\/tdd\/SKILL\.md\)/);
	assert.match(text, /harness-adapter\.md/);
	assert.match(text, /arena cross-judge pool/);
	assert.match(text, /judgment and prose/);

	const bulletproofing = read("skills/writing-skills/references/bulletproofing.md");
	assert.doesNotMatch(bulletproofing, /superpowers:test-driven-development/);

	const discovery = read("skills/writing-skills/references/discovery.md");
	assert.match(discovery, /`\*\*REQUIRED SUB-SKILL:\*\* Use \/tdd`/);
	assert.doesNotMatch(discovery, /Use`\/tdd/);
});
test("every relative link in the adapted skills resolves to an existing file", () => {
	const broken = [];
	for (const dir of [
		...UPSTREAM_DIRS,
		"skills/make-pr-easy-to-review",
		"skills/thermo-nuclear-code-quality-review",
	]) {
		for (const rel of markdownFilesUnder(dir)) {
			const mdPath = path.join(repoDir, rel);
			const mdDir = path.dirname(mdPath);
			for (const target of markdownLinks(rel)) {
				if (target.startsWith("http://") || target.startsWith("https://") || target.startsWith("#") || target.startsWith("mailto:")) {
					continue;
				}
				const clean = target.split("#")[0].split("?")[0].trim();
				if (!clean) continue;
				const resolved = path.resolve(mdDir, clean);
				if (!fs.existsSync(resolved)) broken.push(`${rel} -> ${target} (resolved to ${resolved})`);
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
	assert.match(text, /docs\/plans\/YYYY-MM-DD-<feature-name>\.md/);
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
	assert.doesNotMatch(text, /superpowers:test-driven-development/);
	assert.doesNotMatch(text, /using-superpowers/);
	assert.match(text, /\[tdd\]\(\.\.\/tdd\/SKILL\.md\)/);
	assert.match(text, /harness-adapter\.md/);
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

const TASK5_PROSE_SKILLS = TASK5_SKILLS.filter(
	(rel) => !/writing-rules|proof-driven-development|proving-with|model-checking-protocols|analyzing-with-abstract|auditing-proof/.test(rel),
);

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
