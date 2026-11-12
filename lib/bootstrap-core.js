import fs from "node:fs";
import path from "node:path";

export const BOOTSTRAP_MARKER = "<EXTREMELY_IMPORTANT>\nYou have magic.";

const DEFAULT_PREAMBLE =
	'**IMPORTANT: The using-magic skill content is included below. It is ALREADY LOADED - you are currently following it. Do NOT use the skill tool to load "using-magic" again - that would be redundant.**';

const _bootstrapCache = new Map();

export function extractAndStripFrontmatter(content) {
	const match = content.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n?([\s\S]*)$/);
	if (!match) return { frontmatter: {}, content };

	const frontmatterStr = match[1];
	const body = match[2];
	const frontmatter = {};
	let lastKey = null;

	for (const rawLine of frontmatterStr.split("\n")) {
		const line = rawLine.replace(/\r$/, "");
		const colonIdx = line.indexOf(":");
		if (colonIdx > 0 && !/^\s/.test(line)) {
			const key = line.slice(0, colonIdx).trim();
			const value = line.slice(colonIdx + 1).trim();
			frontmatter[key] = /^(>[+-]?|\|[+-]?)$/.test(value) ? "" : value;
			lastKey = key;
		} else if (lastKey !== null && line.trim() !== "") {
			frontmatter[lastKey] = `${frontmatter[lastKey]} ${line.trim()}`.trim();
		}
	}

	for (const key of Object.keys(frontmatter)) {
		frontmatter[key] = frontmatter[key].replace(/^(["'])([\s\S]*)\1$/, "$2");
	}

	return { frontmatter, content: body };
}

export function loadKitRules(rulesDir) {
	if (!fs.existsSync(rulesDir)) return "";

	const bodies = fs
		.readdirSync(rulesDir, { withFileTypes: true })
		.filter((entry) => entry.isFile() && entry.name.endsWith(".md"))
		.map((entry) => entry.name)
		.sort()
		.map((name) => extractAndStripFrontmatter(fs.readFileSync(path.join(rulesDir, name), "utf8")).content.trim())
		.filter((body) => body !== "");

	return bodies.join("\n\n");
}

export function loadKitAgents(agentsDir) {
	if (!fs.existsSync(agentsDir)) return [];

	return fs
		.readdirSync(agentsDir, { withFileTypes: true })
		.filter((entry) => entry.isDirectory() && !entry.name.startsWith("."))
		.map((entry) => entry.name)
		.sort()
		.flatMap((id) => {
			const agentPath = path.join(agentsDir, id, "agent.md");
			if (!fs.existsSync(agentPath)) return [];

			const { frontmatter, content } = extractAndStripFrontmatter(fs.readFileSync(agentPath, "utf8"));
			return [
				{
					id,
					name: frontmatter.name ?? id,
					description: frontmatter.description ?? "",
					readonly: String(frontmatter.readonly).trim() === "true",
					prompt: content.trim(),
					path: agentPath,
				},
			];
		});
}

export function parseMagicModels(raw) {
	const { content } = extractAndStripFrontmatter(raw);
	const parsed = { orchestratorMode: "thin", budget: null, roles: {}, hasDirectives: false };

	for (const rawLine of content.split("\n")) {
		const line = rawLine.trim();
		if (line === "") continue;

		if (line.startsWith("#")) {
			const directive = line.slice(1).trim();
			const colonIdx = directive.indexOf(":");
			if (colonIdx <= 0) continue;

			const directiveKey = directive.slice(0, colonIdx).trim().toLowerCase();
			const directiveValue = directive.slice(colonIdx + 1).trim();
			if (directiveKey === "orchestrator") {
				const mode = directiveValue.toLowerCase();
				if (mode === "thin" || mode === "standard") {
					parsed.orchestratorMode = mode;
					// An unrelated `# orchestrator:` note must not make a stub
					// file look usable and shadow a real one further down.
					parsed.hasDirectives = true;
				}
			} else if (directiveKey === "budget") {
				// `# budget:` with no value carries no configuration, so it
				// normalizes to null and does not make the file usable.
				parsed.budget = directiveValue || null;
				if (directiveValue !== "") parsed.hasDirectives = true;
			}
			continue;
		}

		const colonIdx = line.indexOf(":");
		if (colonIdx <= 0) continue;

		const key = line.slice(0, colonIdx).trim();
		const value = line.slice(colonIdx + 1).trim();
		if (key !== "" && value !== "") parsed.roles[key] = value;
	}

	return parsed;
}

export function loadMagicModelsRule(candidatePaths) {
	for (const candidate of candidatePaths) {
		if (!fs.existsSync(candidate)) continue;

		try {
			const raw = fs.readFileSync(candidate, "utf8");
			const parsed = parseMagicModels(raw);
			// A stub or prose-only file at a higher-priority path must not
			// shadow a real one further down the candidate list.
			if (!isUsableMagicModels(parsed)) continue;
			return { path: candidate, raw, parsed };
		} catch {
			// Unreadable candidate: fall through to the next configured path.
		}
	}

	return null;
}

export function isUsableMagicModels(parsed) {
	return Boolean(parsed && (parsed.hasDirectives || Object.keys(parsed.roles).length > 0));
}

export function loadBootstrapContent(skillsDir, toolMapping, preamble = DEFAULT_PREAMBLE, extraSections = []) {
	const sections = extraSections
		.filter((section) => typeof section === "string" && section.trim() !== "")
		.map((section) => section.trim());
	const cacheKey = `${skillsDir}\0${toolMapping}\0${preamble}\0${sections.join("\0")}`;
	if (_bootstrapCache.has(cacheKey)) return _bootstrapCache.get(cacheKey);

	const skillPath = path.join(skillsDir, "using-magic", "SKILL.md");
	if (!fs.existsSync(skillPath)) {
		_bootstrapCache.set(cacheKey, null);
		return null;
	}

	const fullContent = fs.readFileSync(skillPath, "utf8");
	const { content } = extractAndStripFrontmatter(fullContent);
	const blocks = [preamble, content.trim(), ...sections, toolMapping];
	const formatted = `${BOOTSTRAP_MARKER}\n\n${blocks.join("\n\n")}\n</EXTREMELY_IMPORTANT>`;
	_bootstrapCache.set(cacheKey, formatted);
	return formatted;
}
