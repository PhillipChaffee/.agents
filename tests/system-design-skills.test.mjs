import { spawnSync } from "node:child_process";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";

const repoRoot = path.resolve(import.meta.dirname, "..");

test("Task 1: workflow-routing, using-magic, and magic-mode route designing and architecting tasks cleanly", () => {
	const routing = fs.readFileSync(path.join(repoRoot, "rules/workflow-routing.md"), "utf8");
	const usingMagic = fs.readFileSync(path.join(repoRoot, "skills/using-magic/SKILL.md"), "utf8");
	const magicMode = fs.readFileSync(path.join(repoRoot, "skills/magic-mode/SKILL.md"), "utf8");
	assert.match(routing, /designing, architecting/i);
	assert.match(usingMagic, /designing, architecting/i);
	assert.match(magicMode, /system or subsystem design/i);
	assert.match(magicMode, /\*\*System design\.\*\*/);
	const fmEnd = routing.indexOf("\n---", 4);
	const bodyWords = routing.slice(fmEnd + 4).trim().split(/\s+/).filter(Boolean).length;
	assert.ok(bodyWords < 250, `workflow-routing.md body has ${bodyWords} words (max 249)`);
});

test("Task 2: architect 2-axis triage, runnable quantitative-envelope calculator, 14 red flags, and rationale pointer work", () => {
	const arch = fs.readFileSync(path.join(repoRoot, "skills/architect/SKILL.md"), "utf8");
	const envRefPath = path.join(repoRoot, "skills/architect/references/quantitative-envelope.md");
	assert.ok(fs.existsSync(envRefPath), "missing skills/architect/references/quantitative-envelope.md");
	const envRef = fs.readFileSync(envRefPath, "utf8");
	const runner = fs.readFileSync(path.join(repoRoot, "skills/architect/references/runner-prompt.md"), "utf8");
	const redFlags = fs.readFileSync(path.join(repoRoot, "skills/architect/references/design-red-flags.md"), "utf8");
	const rationale = fs.readFileSync(path.join(repoRoot, "skills/architect/references/rationale-template.md"), "utf8");

	for (const token of [
		"## Phase 0: Triage",
		"Greenfield",
		"Brownfield Extension",
		"Brownfield Reshape",
		"Track S",
		"Track M",
		"Track L",
		"references/quantitative-envelope.md",
		"model-checking-protocols-and-code",
		"docs/adr/",
		"design-only",
	]) {
		assert.ok(arch.includes(token), `architect/SKILL.md missing ${token}`);
	}

	const jsMatch = envRef.match(/```javascript\n([\s\S]*?)```/);
	assert.ok(jsMatch, "quantitative-envelope.md must contain a runnable ```javascript block");
	const run = spawnSync(process.execPath, ["-e", jsMatch[1]], { encoding: "utf8" });
	assert.equal(run.status, 0, `calculator failed: ${run.stderr}`);
	const parsed = JSON.parse(run.stdout);
	assert.equal(parsed.qpsPeak, 5400);
	assert.equal(parsed.peakBandwidthMBps, 11.06);
	assert.equal(parsed.threeYearStorageTB, 122.067);
	assert.equal(parsed.littlesLawDegradedConcurrency, 1350);
	assert.equal(parsed.kingmanMultiplier, 1.86);
	assert.equal(parsed.uslMaxNodes, 31);
	assert.equal(parsed.fanoutTailProbPct, 22.22);

	for (const rule of ["Coupling balance", "decide", "perform", "WiscKey", "fencing token", "Transactional Outbox", "retry token bucket", "singleflight", "Static Stability", "TigerStyle"]) {
		assert.match(runner, new RegExp(rule, "i"), `runner-prompt.md missing ${rule}`);
	}

	const h2Headings = redFlags.match(/^## .+$/gm) ?? [];
	assert.equal(h2Headings.length, 14, `expected 14 red-flag H2 sections, got ${h2Headings.length}`);
	assert.match(rationale, /design-doc-template\.md/);
});

test("Task 3: arena supports orthogonal constraint axes and interrogate supports pre-code probes plus 10-class postmortem corpus", () => {
	const arena = fs.readFileSync(path.join(repoRoot, "skills/arena/SKILL.md"), "utf8");
	assert.match(arena, /orthogonal constraint axes/i);
	assert.match(arena, /shared rubric in Phases C and D/i);
	assert.match(arena, /assigned constraint axis/i);

	const corpusPath = path.join(repoRoot, "skills/interrogate/references/postmortem-corpus.md");
	assert.ok(fs.existsSync(corpusPath), "missing skills/interrogate/references/postmortem-corpus.md");
	const corpus = fs.readFileSync(corpusPath, "utf8");
	const interrogate = fs.readFileSync(path.join(repoRoot, "skills/interrogate/SKILL.md"), "utf8");

	assert.match(interrogate, /references\/postmortem-corpus\.md/);
	assert.match(interrogate, /Pre-Code Design Mode/i);
	assert.match(interrogate, /DFMEA/i);

	for (const outageClass of [
		"Bad Global Config",
		"Downstream Gray Failure",
		"Retry and Reconnect Amplification Storm",
		"Cache Cold-Start",
		"Poison-Pill Input",
		"Clock Drift",
		"Asymmetric Network Partition",
		"Storage Compaction",
		"Hidden Resource Exhaustion",
		"Rolling Deploy Wire Incompatibility",
	]) {
		assert.ok(corpus.includes(outageClass), `postmortem-corpus.md missing ${outageClass}`);
	}
});

test("Task 4: migration carve-out, principles, prototype, benchmark knee, blast-radius skew, and language-agnostic correct rules align", () => {
	const migrate = fs.readFileSync(path.join(repoRoot, "skills/principle-migrate-callers-then-delete-legacy-apis/SKILL.md"), "utf8");
	const refactoring = fs.readFileSync(path.join(repoRoot, "skills/magic-mode/playbooks/refactoring.md"), "utf8");
	const prototype = fs.readFileSync(path.join(repoRoot, "skills/magic-mode/playbooks/prototype.md"), "utf8");
	const idemp = fs.readFileSync(path.join(repoRoot, "skills/principle-make-operations-idempotent/SKILL.md"), "utf8");
	const sepState = fs.readFileSync(path.join(repoRoot, "skills/principle-separate-before-serializing-shared-state/SKILL.md"), "utf8");
	const bench = fs.readFileSync(path.join(repoRoot, "skills/benchmark-checklist/SKILL.md"), "utf8");
	const blast = fs.readFileSync(path.join(repoRoot, "skills/blast-radius/SKILL.md"), "utf8");
	const correct = fs.readFileSync(path.join(repoRoot, "skills/correct/SKILL.md"), "utf8");

	assert.match(migrate, /Expand-Contract/i);
	assert.match(migrate, /reverse sync/i);
	assert.match(refactoring, /Expand-Contract/i);
	assert.match(prototype, /pure reducer|state machine/i);
	assert.match(idemp, /fencing token/i);
	assert.match(idemp, /Transactional Outbox/i);
	assert.match(sepState, /Universal Scalability Law|N_max/i);
	assert.match(sepState, /hot-key|write-sharding/i);
	assert.match(bench, /quantitative-envelope\.md/);
	assert.match(bench, /coordinated omission/i);
	assert.match(blast, /rolling deploy|mixed-version/i);
	assert.match(blast, /shuffle sharding/i);
	assert.match(correct, /decreasing usage budget/i);
	assert.doesNotMatch(correct, /\bratchet\b/i);
});

test("Task 5: 3-artifact system-design playbook, design-doc template, check-mermaid linter, and synchronized counts/guides pass", () => {
	const playbook = path.join(repoRoot, "skills/magic-mode/playbooks/system-design.md");
	const sddTmpl = path.join(repoRoot, "skills/architect/references/design-doc-template.md");
	const checker = path.join(repoRoot, "skills/architect/scripts/check-mermaid.mjs");
	for (const p of [playbook, sddTmpl, checker]) {
		assert.ok(fs.existsSync(p), `missing ${path.relative(repoRoot, p)}`);
	}

	const pbText = fs.readFileSync(playbook, "utf8");
	assert.match(pbText, /docs\/designs\//);
	assert.match(pbText, /check-mermaid\.mjs/);
	assert.match(pbText, /writing-plans/);
	assert.match(pbText, /Do not create or edit application source or production test files/i);

	for (const [rel, pattern] of [
		["docs/CATALOG.md", /24 execution playbooks/],
		["README.md", /24 step-by-step playbooks/],
		["docs/magic-guide/02-magic-mode.md", /twenty-four playbooks/],
		["docs/magic-guide/04-design.md", /Track S/],
		["docs/magic-guide/04-design.md", /system-design\.md/],
	]) {
		const text = fs.readFileSync(path.join(repoRoot, rel), "utf8");
		assert.match(text, pattern, `${rel} missing ${pattern}`);
	}

	const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "mermaid-check-"));
	try {
		const runCheck = (name, lines) => {
			const file = path.join(tmpDir, name);
			fs.writeFileSync(file, lines.join("\n"));
			return spawnSync(process.execPath, [checker, file], { encoding: "utf8" });
		};

		assert.equal(
			runCheck("missing-edge.md", [
				"```mermaid",
				"flowchart LR",
				'  A -->|"E1: gRPC sync"| B',
				'  A -->|"E2: Kafka async"| C',
				"```",
				"| Edge ID | Protocol |",
				"| --- | --- |",
				"| E1 | gRPC |",
			]).status,
			1,
		);
		assert.equal(
			runCheck("missing-bare-edge.md", [
				"```mermaid",
				"flowchart LR",
				'  A -->|"E1"| B',
				"```",
			]).status,
			1,
		);

		assert.equal(runCheck("arch-beta.md", ["```mermaid", "architecture-beta", "  service api", "```"]).status, 1);
		assert.equal(runCheck("c4.md", ["```mermaid", "C4Container", '  Container(a, "API")', "```"]).status, 1);
		assert.equal(runCheck("bad-end.md", ["```mermaid", "flowchart LR", "  start --> end", "```"]).status, 1);
		assert.equal(runCheck("bad-end-decl.md", ["```mermaid", "flowchart LR", '  end["Done"] --> B', "```"]).status, 1);
		assert.equal(
			runCheck("unbalanced.md", ["```mermaid", "flowchart LR", '  subgraph Plane["Data"]', "    A --> B", "```"]).status,
			1,
		);

		const tooMany = ["```mermaid", "flowchart LR", ...Array.from({ length: 16 }, (_, i) => `  N${i}["Node ${i}"]`), "```"];
		assert.equal(runCheck("too-many.md", tooMany).status, 1);

		const good = runCheck("good.md", [
			"```mermaid",
			"flowchart LR",
			'  subgraph DataPlane["Data Plane"]',
			'    API["API Gateway"] -->|"E1: gRPC sync"| DB[("Orders DB")]',
			'    API -.->|"E2: Kafka async"| W["Worker"]',
			'    W -->|"runs E2E check"| Sink[end state]',
			"  end",
			'  subgraph Legend["Legend"]',
			'    L1["Sync"] --> L2["Async"]',
			"  end",
			"```",
			"```mermaid",
			"sequenceDiagram",
			"  autonumber",
			"  API->>DB: write order",
			"```",
			"| Edge ID | Protocol |",
			"| --- | --- |",
			"| E1 | gRPC |",
			"| E2 | Kafka |",
		]);
		assert.equal(good.status, 0, `expected good.md to pass: ${good.stderr}`);
		const tmplRes = spawnSync(process.execPath, [checker, sddTmpl], { encoding: "utf8" });
		assert.equal(tmplRes.status, 0, `design-doc-template.md check failed: ${tmplRes.stderr}`);
	} finally {
		fs.rmSync(tmpDir, { recursive: true, force: true });
	}
});
