import fs from "node:fs";
import os from "node:os";
import path from "node:path";

export const BOOTSTRAP_MARKER = "<EXTREMELY_IMPORTANT>\nYou have magic.";

const DEFAULT_PREAMBLE =
	'**IMPORTANT: The using-magic skill content is included below. It is ALREADY LOADED - you are currently following it. Do NOT use the skill tool to load "using-magic" again - that would be redundant.**';

const _bootstrapCache = new Map();
const _rulesCache = new Map();
const _magicModelsCache = new Map();

export function extractAndStripFrontmatter(content) {
	if (typeof content !== "string") return { frontmatter: {}, content: "" };
	if (!content.startsWith("---\r\n") && !content.startsWith("---\n")) {
		return { frontmatter: {}, content };
	}

	const start = content.startsWith("---\r\n") ? 5 : 4;
	const rest = content.slice(start);

	let frontmatterStr = "";
	let body = content;

	if (rest.startsWith("---\r\n") || rest.startsWith("---\n") || rest === "---") {
		const fenceLen = rest.startsWith("---\r\n") ? 5 : (rest.startsWith("---\n") ? 4 : 3);
		frontmatterStr = "";
		body = rest.slice(fenceLen);
	} else {
		let matchIdx = -1;
		let delimLen = 0;
		for (const delim of ["\n---\r\n", "\n---\n"]) {
			const idx = content.indexOf(delim, start);
			if (idx !== -1 && (matchIdx === -1 || idx < matchIdx)) {
				matchIdx = idx;
				delimLen = delim.length;
			}
		}
		if (matchIdx !== -1) {
			frontmatterStr = content.slice(start, matchIdx);
			body = content.slice(matchIdx + delimLen);
		} else if (content.endsWith("\n---")) {
			frontmatterStr = content.slice(start, content.length - 4);
			body = "";
		} else {
			return { frontmatter: {}, content };
		}
	}

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
	if (!rulesDir || !fs.existsSync(rulesDir)) return "";
	if (_rulesCache.has(rulesDir)) return _rulesCache.get(rulesDir);

	const bodies = fs
		.readdirSync(rulesDir, { withFileTypes: true })
		.filter((entry) => entry.isFile() && entry.name.endsWith(".md"))
		.map((entry) => entry.name)
		.sort()
		.map((name) => extractAndStripFrontmatter(fs.readFileSync(path.join(rulesDir, name), "utf8")).content.trim())
		.filter((body) => body !== "");

	const joined = bodies.join("\n\n");
	_rulesCache.set(rulesDir, joined);
	return joined;
}

function parseStringArray(val) {
	if (!val || typeof val !== "string") return [];
	const trimmed = val.trim();
	if (trimmed.startsWith("[") && trimmed.endsWith("]")) {
		return trimmed
			.slice(1, -1)
			.split(",")
			.map((s) => s.trim().replace(/^["']|["']$/g, ""))
			.filter(Boolean);
	}
	return [];
}

export function loadKitAgents(agentsDir) {
	if (!agentsDir || !fs.existsSync(agentsDir)) return [];

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
					disallowedTools: parseStringArray(frontmatter.disallowedTools),
					readonly: String(frontmatter.readonly).trim() === "true",
					prompt: content.trim(),
					path: agentPath,
				},
			];
		});
}

export function loadKitSkills(skillsDir) {
	if (!skillsDir || !fs.existsSync(skillsDir)) return [];

	const skills = [];
	for (const entry of fs.readdirSync(skillsDir, { withFileTypes: true })) {
		if (!entry.isDirectory() || entry.name.startsWith(".")) continue;
		const skillPath = path.join(skillsDir, entry.name, "SKILL.md");
		if (!fs.existsSync(skillPath)) continue;

		const { frontmatter, content } = extractAndStripFrontmatter(fs.readFileSync(skillPath, "utf8"));
		skills.push({
			id: entry.name,
			name: frontmatter.name || entry.name,
			...(frontmatter.description ? { description: frontmatter.description } : {}),
			path: skillPath,
			content,
		});
	}
	return skills;
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
					parsed.hasDirectives = true;
				}
			} else if (directiveKey === "budget") {
				parsed.budget = directiveValue || null;
				if (directiveValue !== "") parsed.hasDirectives = true;
			}
			continue;
		}

		const colonIdx = line.indexOf(":");
		if (colonIdx <= 0) continue;

		const key = line.slice(0, colonIdx).trim();
		const rawVal = line.slice(colonIdx + 1).trim();
		// Strip any trailing `# comment` preceded by whitespace, preserving `#variant` in `provider/model#variant`
		const value = rawVal.replace(/\s+#.*$/, "").trim();
		if (key !== "" && value !== "") parsed.roles[key] = value;
	}

	return parsed;
}

export function loadMagicModelsRule(candidatePaths) {
	for (const candidate of candidatePaths) {
		if (!candidate) continue;
		let stat;
		try {
			stat = fs.statSync(candidate, { throwIfNoEntry: false });
		} catch {
			stat = null;
		}
		if (!stat || !stat.isFile()) continue;

		const cacheKey = `${candidate}\0${stat.mtimeMs}\0${stat.size}`;
		if (_magicModelsCache.has(cacheKey)) {
			const cached = _magicModelsCache.get(cacheKey);
			if (isUsableMagicModels(cached.parsed)) return cached;
			continue;
		}

		try {
			const raw = fs.readFileSync(candidate, "utf8");
			const parsed = parseMagicModels(raw);
			const entry = { path: candidate, raw, parsed };
			_magicModelsCache.set(cacheKey, entry);
			if (!isUsableMagicModels(parsed)) continue;
			return entry;
		} catch {
			// Unreadable candidate: fall through to the next configured path.
		}
	}

	return null;
}

export function isUsableMagicModels(parsed) {
	return Boolean(parsed && (parsed.hasDirectives || Object.keys(parsed.roles).length > 0));
}

export function loadModelsJsonPresets(modelsJsonPath) {
	const resolvedPath =
		modelsJsonPath ??
		(process.env.MAGIC_MODELS_JSON_PATH || path.join(os.homedir(), ".agents", "models.json"));
	if (!resolvedPath || !fs.existsSync(resolvedPath)) return null;

	try {
		const raw = fs.readFileSync(resolvedPath, "utf8");
		const data = JSON.parse(raw);
		if (data && typeof data.presets === "object" && data.presets !== null) {
			return data.presets;
		}
	} catch {
		// Ignore read/parse failure
	}
	return null;
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
