#!/usr/bin/env node
import fs from "node:fs";
import process from "node:process";

const MAX_NODES = 15;
const BANNED_DIAGRAM_TYPES = /^(architecture-beta|C4Context|C4Container|C4Component|C4Dynamic|C4Deployment)\b/;
const EDGE_SPLIT = /<-->|-->|-.->|==>|---|~~~/;
const BLOCK_OPEN_FLOWCHART = /^\s*subgraph\b/i;
const BLOCK_OPEN_SEQ = /^\s*(?:alt|opt|loop|par|critical|break|rect)\b/i;
const BLOCK_END = /^\s*end\s*$/;
const SKIP_STMT = /^\s*(?:flowchart|graph|sequenceDiagram|stateDiagram-v2|erDiagram|subgraph|end|else|and|option|classDef|class|style|linkStyle|click|direction|autonumber|participant|actor|note|activate|deactivate|title|%%)\b/i;

const file = process.argv[2];
if (!file) {
	console.error("Usage: node check-mermaid.mjs <markdown-file>");
	process.exit(2);
}
if (!fs.existsSync(file)) {
	console.error(`${file}: file not found`);
	process.exit(2);
}

const rawLines = fs.readFileSync(file, "utf8").split(/\r?\n/);
const errors = [];
const fail = (line, msg) => errors.push(`${file}:${line}: ${msg}`);

const mermaidBlocks = [];
const nonMermaidLines = [];
let inMermaid = false;
let inOtherFence = false;
let currentBlock = null;

for (let i = 0; i < rawLines.length; i++) {
	const line = rawLines[i];
	const lineNum = i + 1;
	const trimmed = line.trim();

	if (!inMermaid && !inOtherFence) {
		if (/^(`{3,}|~{3,})mermaid\b/i.test(trimmed)) {
			inMermaid = true;
			currentBlock = { startLine: lineNum, lines: [] };
			continue;
		}
		if (/^(`{3,}|~{3,})/.test(trimmed)) {
			inOtherFence = true;
			continue;
		}
		nonMermaidLines.push(line);
	} else if (inMermaid) {
		if (/^(`{3,}|~{3,})\s*$/.test(trimmed)) {
			mermaidBlocks.push(currentBlock);
			currentBlock = null;
			inMermaid = false;
		} else {
			currentBlock.lines.push({ n: lineNum, text: line });
		}
	} else if (inOtherFence) {
		if (/^(`{3,}|~{3,})\s*$/.test(trimmed)) {
			inOtherFence = false;
		}
	}
}

if (inMermaid && currentBlock) {
	fail(currentBlock.startLine, "unclosed mermaid code fence");
}

function stripQuotedAndLabels(text) {
	return text
		.replace(/"(?:[^"\\]|\\.)*"/g, '""')
		.replace(/\|[^|]*\|/g, " ");
}

function stripShapeContents(text) {
	return stripQuotedAndLabels(text)
		.replace(/\[[^\]]*\]/g, "")
		.replace(/\([^)]*\)/g, "")
		.replace(/\{[^}]*\}/g, "");
}

function extractNodeId(fragment) {
	const cleaned = stripQuotedAndLabels(fragment).trim();
	if (!cleaned) return null;
	const match = cleaned.match(/^([A-Za-z_][A-Za-z0-9_.-]*)/);
	return match ? match[1] : null;
}

const referencedEdges = new Map();

for (const block of mermaidBlocks) {
	const activeLines = block.lines.filter((l) => {
		const t = l.text.trim();
		return t.length > 0 && !t.startsWith("%%");
	});
	if (activeLines.length === 0) {
		fail(block.startLine, "empty mermaid block");
		continue;
	}

	const header = activeLines[0].text.trim();
	if (BANNED_DIAGRAM_TYPES.test(header)) {
		fail(activeLines[0].n, `banned diagram type "${header.split(/\s+/)[0]}"; use flowchart LR, sequenceDiagram, or stateDiagram-v2`);
		continue;
	}

	const isFlowchart = /^(?:flowchart|graph)\b/i.test(header);
	const isSequence = /^sequenceDiagram\b/i.test(header);

	const blockStack = [];
	const nodes = new Set();

	for (const { n, text } of activeLines) {
		const trimmed = text.trim();
		if (BANNED_DIAGRAM_TYPES.test(trimmed)) {
			fail(n, `banned diagram syntax "${trimmed.split(/\s+/)[0]}"`);
		}

		if (isFlowchart) {
			if (BLOCK_OPEN_FLOWCHART.test(trimmed)) {
				const isLegend = /^\s*subgraph\s+(?:"?Legend"?\b|Legend\s*\[)/i.test(trimmed);
				blockStack.push(isLegend ? "legend" : "subgraph");
				continue;
			}
			if (BLOCK_END.test(trimmed)) {
				if (blockStack.length === 0) fail(n, "unexpected 'end' with no open subgraph");
				else blockStack.pop();
				continue;
			}

			const unquoted = stripShapeContents(trimmed);
			if (/\bend\b/.test(unquoted)) {
				fail(n, "lowercase 'end' cannot be used as a flowchart node ID");
			}

			let m;
			const edgeIdPipeRegex = /\|\s*"?(E\d+)\s*(?:[:|"]|$)/g;
			while ((m = edgeIdPipeRegex.exec(trimmed)) !== null) {
				if (!referencedEdges.has(m[1])) referencedEdges.set(m[1], n);
			}
			const edgeIdMidRegex = /--\s*"?(E\d+)\s*(?:[:"]|$)/g;
			while ((m = edgeIdMidRegex.exec(trimmed)) !== null) {
				if (!referencedEdges.has(m[1])) referencedEdges.set(m[1], n);
			}

			const inLegend = blockStack.includes("legend");
			if (!inLegend && !SKIP_STMT.test(trimmed)) {
				const parts = trimmed.split(EDGE_SPLIT);
				for (const part of parts) {
					const id = extractNodeId(part);
					if (id && id !== "end") nodes.add(id);
				}
			}
		} else if (isSequence) {
			if (BLOCK_OPEN_SEQ.test(trimmed)) {
				blockStack.push("seq");
			} else if (BLOCK_END.test(trimmed)) {
				if (blockStack.length === 0) fail(n, "unexpected 'end' with no open sequence block");
				else blockStack.pop();
			}
		}
	}

	if (blockStack.length > 0) {
		fail(block.startLine, `unbalanced diagram blocks: ${blockStack.length} unclosed block(s)`);
	}

	if (isFlowchart && nodes.size > MAX_NODES) {
		fail(block.startLine, `flowchart defines ${nodes.size} non-legend nodes (max ${MAX_NODES}); split across complementary views`);
	}
}

if (referencedEdges.size > 0) {
	const tableEdges = new Set();
	for (const line of nonMermaidLines) {
		const m = line.match(/^\s*\|\s*`?(E\d+)`?\s*\|/);
		if (m) tableEdges.add(m[1]);
	}
	for (const [edgeId, lineNum] of referencedEdges.entries()) {
		if (!tableEdges.has(edgeId)) {
			fail(lineNum, `flowchart edge ${edgeId} is missing from the Boundary Contract / DFMEA Markdown table`);
		}
	}
}

if (errors.length > 0) {
	for (const err of errors) console.error(err);
	process.exit(1);
}

console.log(`OK: checked ${mermaidBlocks.length} mermaid block(s) in ${file}`);
