import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
	BOOTSTRAP_MARKER,
	extractAndStripFrontmatter,
	isUsableMagicModels,
	loadBootstrapContent,
	loadKitAgents,
	loadKitRules,
	loadKitSkills,
	loadMagicModelsRule,
	loadModelsJsonPresets,
} from "../../lib/bootstrap-core.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const magicSkillsDir = path.resolve(__dirname, "../../skills");
const magicAgentsDir = path.resolve(__dirname, "../../agents");
const magicRulesDir = path.resolve(__dirname, "../../rules");

export const V1_MAPPING = `**Tool Mapping for OpenCode:**
When skills request actions, substitute OpenCode equivalents:
- Create or update todos → \`todowrite\`
- \`Subagent (general-purpose):\` → \`task\` with \`subagent_type: "general"\`
- Invoke a skill → OpenCode's native \`skill\` tool. Skill ids are bare names, so drop the \`magic:\` prefix skills use when they name each other (\`magic:magic-mode\` → \`skill\` with \`name: "magic-mode"\`)
- Read files → \`read\`
- Create, edit, or delete files → \`apply_patch\`
- Run shell commands → \`bash\`
- Search files → \`grep\`, \`glob\`
- Fetch a URL → \`webfetch\`

Use OpenCode's native \`skill\` tool to list and load skills.`;

export const V2_MAPPING = `**Tool Mapping for OpenCode:**
When skills request actions, substitute OpenCode equivalents:
- Create or update todos → \`todowrite\` when offered; otherwise track the plan in a markdown file (or the harness's plan facility)
- \`Subagent (general-purpose):\` → \`subagent\` with \`agent: "general"\`, or \`agent: "<id>"\` for registered kit subagents (\`magic-agent\`, \`comment-sicko\`, \`researcher-lite\`, \`researcher-mid\`, \`researcher-deep\`, \`research-planner\`, \`research-synthesizer\`). Give it \`description\` and \`prompt\`, optionally \`background\`, and pass \`sessionID\` to continue a previous subagent. When \`magic-models\` specifies a resolved \`providerID/modelID\` or \`providerID/modelID#variant\` for the role, pass it in \`model\` (entries in \`magic-models\` are explicit user model selections).
- Invoke a skill → OpenCode's native \`skill\` tool. Skill ids are bare names, so drop the \`magic:\` prefix skills use when they name each other (\`magic:magic-mode\` → \`skill\` with \`id: "magic-mode"\`)
- Read files → \`read\`
- Create, edit, or delete files → use \`patch\` with \`patchText\` when available; otherwise use \`write\` to create or overwrite files, \`edit\` for targeted changes, and \`shell\` for deletion
- Run shell commands → \`shell\` (\`command\`, \`workdir\`, \`timeout\`, \`background\`)
- Search files → \`grep\`, \`glob\`
- Fetch a URL → \`webfetch\`
- Search the web → \`websearch\`

Use OpenCode's native \`skill\` tool to list and load skills.`;

const DEEP_ROLES = "researcher-deep, planner, synthesizer";

const AGENT_ROLE_KEYS = {
	"researcher-lite": ["researcher-lite, collectors", "fast, mechanical, miners", "fast"],
	"researcher-mid": ["researcher-mid", "main"],
	"researcher-deep": [DEEP_ROLES, "deep"],
	"research-planner": [DEEP_ROLES, "deep"],
	"research-synthesizer": [DEEP_ROLES, "deep"],
	"comment-sicko": ["comment-sicko", "main"],
	"magic-agent": ["feature, refactoring", "main"],
};

const AGENT_DEFAULT_TIERS = {
	"researcher-lite": "fast",
	"researcher-mid": "main",
	"researcher-deep": "deep",
	"research-planner": "deep",
	"research-synthesizer": "deep",
	"comment-sicko": "main",
	"magic-agent": "main",
};

const TIER_NAMES = new Set(["fast", "main", "deep"]);
const UNRESOLVED_MODELS = new Set(["", "inherit-parent", "auto", "fast", "main", "deep"]);

const firstEntry = (value) => (typeof value === "string" ? value.split(",")[0].trim() : "");

// Role files may carry an inline `# comment` after the entry. Strip only a
// whitespace-preceded `#`, because `provider/model#variant` attaches its own.
const stripModelComment = (entry) => (typeof entry === "string" ? entry.replace(/\s+#.*$/, "").trim() : "");

export function resolveAgentModel(agentId, parsed, presets) {
	const effectivePresets = presets ?? loadModelsJsonPresets();
	if (parsed?.roles) {
		for (const key of AGENT_ROLE_KEYS[agentId] ?? []) {
			if (!(key in parsed.roles)) continue;

			const rawVal = firstEntry(parsed.roles[key]);
			const stripped = stripModelComment(rawVal);
			if (stripped === "inherit-parent" || stripped === "auto") {
				return undefined;
			}

			let value = stripped;
			if (TIER_NAMES.has(value)) {
				value = stripModelComment(firstEntry(parsed.roles[value] ?? effectivePresets?.[value]));
			}

			if (value && value.includes("/") && !UNRESOLVED_MODELS.has(value)) {
				return value;
			}
		}
	}

	const defaultTier = AGENT_DEFAULT_TIERS[agentId];
	const fallbackFromPresets = stripModelComment(firstEntry(effectivePresets?.[defaultTier]));
	if (fallbackFromPresets && fallbackFromPresets.includes("/") && !UNRESOLVED_MODELS.has(fallbackFromPresets)) {
		return fallbackFromPresets;
	}

	return undefined;
}

// Mirrors `Model.Ref.parse` from @opencode/schema: V2 Agent.Info.model is a
// Ref object, so a resolved role string must become `{ providerID, id, variant }`.
export const parseModelRef = (input) => {
	if (typeof input !== "string") return undefined;
	const providerEnd = input.indexOf("/");
	if (providerEnd <= 0) return undefined;
	const providerID = input.slice(0, providerEnd);
	const variantStart = input.indexOf("#", providerEnd + 1);
	const id = input.slice(providerEnd + 1, variantStart === -1 ? undefined : variantStart);
	const variant = variantStart === -1 ? undefined : input.slice(variantStart + 1);
	if (!id || providerID.includes("#") || (variant !== undefined && (!variant || variant.includes("#")))) {
		return undefined;
	}
	return { providerID, id, ...(variant ? { variant } : {}) };
};

const V2_DEFAULT_PERMISSIONS = [{ action: "*", resource: "*", effect: "allow" }];
const v2DefaultRequest = () => ({ settings: {}, headers: {}, body: {} });

const v2Permissions = (draft, agent) => {
	const rules = Array.isArray(draft?.permissions)
		? draft.permissions.map((rule) => ({ ...rule }))
		: V2_DEFAULT_PERMISSIONS.map((rule) => ({ ...rule }));

	// All kit subagents are depth-1 leaves: deny nested subagents and questions
	rules.push({ action: "subagent", resource: "*", effect: "deny" });
	rules.push({ action: "question", resource: "*", effect: "deny" });

	const disallowed = new Set(agent?.disallowedTools ?? []);
	if (agent?.id === "research-planner" || (disallowed.has("Read") && disallowed.has("Bash"))) {
		return [{ action: "*", resource: "*", effect: "deny" }];
	}

	if (disallowed.has("Bash")) {
		rules.push({ action: "shell", resource: "*", effect: "deny" });
	}

	if (agent?.readonly || disallowed.has("Edit") || disallowed.has("Write")) {
		rules.push({ action: "edit", resource: "*", effect: "deny" });
	}

	if (agent?.id === "research-synthesizer") {
		// Allow writing designated research artifacts
		rules.push({ action: "edit", resource: "docs/research/*", effect: "allow" });
	}

	return rules;
};

const v1Permission = (agent) => {
	const perm = { subagent: "deny", question: "deny", task: "deny" };
	const disallowed = new Set(agent?.disallowedTools ?? []);
	if (agent?.id === "research-planner") {
		return { "*": "deny", ...perm };
	}
	if (disallowed.has("Bash")) {
		perm.bash = "deny";
		perm.shell = "deny";
	}
	if (agent?.readonly || disallowed.has("Edit") || disallowed.has("Write")) {
		perm.edit = "deny";
		perm.write = "deny";
	}
	return perm;
};

const toModelRef = (value) => {
	if (typeof value === "string") return parseModelRef(value);
	if (value && typeof value === "object" && typeof value.providerID === "string" && typeof value.id === "string") {
		return value;
	}
	return undefined;
};

const PROFILE_MODELS_FILE = /^magic-models.*\.md$/i;

function expandCandidatePath(value, baseDir) {
	if (typeof value !== "string") return null;
	const trimmed = value.trim();
	if (trimmed === "") return null;
	if (trimmed === "~") return os.homedir();
	if (trimmed.startsWith("~/")) return path.join(os.homedir(), trimmed.slice(2));
	return path.isAbsolute(trimmed) ? trimmed : path.resolve(baseDir, trimmed);
}

// A profile overlay carries its own role file, because profiles exist to run
// different provider entitlements. The profile file wins over the shared one.
function profileMagicModelsCandidates() {
	const configPath = process.env.OPENCODE_CONFIG;
	if (!configPath) return [];

	const configDir = path.dirname(configPath);
	const fromInstructions = [];
	try {
		const config = JSON.parse(fs.readFileSync(configPath, "utf8"));
		for (const entry of Array.isArray(config?.instructions) ? config.instructions : []) {
			const resolved = expandCandidatePath(entry, configDir);
			if (resolved && PROFILE_MODELS_FILE.test(path.basename(resolved))) fromInstructions.push(resolved);
		}
	} catch (err) {
		console.error("[magic] could not read OPENCODE_CONFIG, ignoring its instruction entries:", err);
	}

	const profileName = path.basename(configPath, ".json");
	const byProfileName = [
		path.join(os.homedir(), ".config/opencode/rules", `magic-models-${profileName}.md`),
		process.env.OPENCODE_CONFIG_DIR
			? path.join(process.env.OPENCODE_CONFIG_DIR, "rules", `magic-models-${profileName}.md`)
			: null,
	].filter(Boolean);

	return [...fromInstructions, ...byProfileName];
}

function magicModelsCandidates() {
	return [
		process.env.MAGIC_MODELS_PATH,
		...profileMagicModelsCandidates(),
		process.env.OPENCODE_CONFIG_DIR
			? path.join(process.env.OPENCODE_CONFIG_DIR, "rules/magic-models.md")
			: null,
		path.join(os.homedir(), ".config/opencode/rules/magic-models.md"),
		path.join(os.homedir(), ".agents/rules/magic-models.md"),
	].filter(Boolean);
}

const loadMagicModels = () => loadMagicModelsRule(magicModelsCandidates());

// `loadMagicModelsRule` already skips unusable files; re-check the parsed
// contract so a caller that supplies its own record cannot inject prose.
const bootstrapSections = (magicModels) => [
	loadKitRules(magicRulesDir),
	isUsableMagicModels(magicModels?.parsed) ? extractAndStripFrontmatter(magicModels.raw).content.trim() : "",
];

const CHILD_SESSION_CACHE_MAX = 512;
const _childSessionCache = new Map();

const _cacheChildSession = (sessionID, isChild) => {
	if (_childSessionCache.size >= CHILD_SESSION_CACHE_MAX) {
		let toDrop = Math.ceil(CHILD_SESSION_CACHE_MAX / 4);
		for (const key of _childSessionCache.keys()) {
			if (toDrop-- <= 0) break;
			_childSessionCache.delete(key);
		}
	}
	_childSessionCache.set(sessionID, isChild);
};

const isChildSession = async (fetchSession, sessionID) => {
	if (!sessionID) return false;
	if (_childSessionCache.has(sessionID)) return _childSessionCache.get(sessionID);

	let isChild = false;
	try {
		const result = await fetchSession(sessionID);
		if (!result || typeof result !== "object" || Array.isArray(result)) {
			throw new Error("Session lookup returned no usable record");
		}
		if (result.error != null || result.response?.ok === false) {
			throw new Error("Session lookup was unsuccessful");
		}
		const session = "data" in result ? result.data : result;
		if (!session || typeof session !== "object" || Array.isArray(session) || session.id !== sessionID) {
			throw new Error("Session lookup returned an invalid session identity");
		}
		if (
			session.parentID !== undefined &&
			(typeof session.parentID !== "string" || session.parentID.length === 0)
		) {
			throw new Error("Session lookup returned an invalid parent identity");
		}
		isChild = session.parentID !== undefined;
	} catch (err) {
		console.error("[magic] session lookup failed, treating session as top-level:", err);
		return false;
	}
	_cacheChildSession(sessionID, isChild);
	return isChild;
};

export const MagicPlugin = async ({ client }) => {
	return {
		config: async (config) => {
			try {
				const magicModels = loadMagicModels();
				const modelsPresets = loadModelsJsonPresets();
				config.agent = config.agent || {};
				for (const agent of loadKitAgents(magicAgentsDir)) {
					const resolvedModel = resolveAgentModel(agent.id, magicModels?.parsed, modelsPresets);
					const existing = config.agent[agent.id] || {};
					config.agent[agent.id] = {
						mode: "subagent",
						description: agent.description,
						prompt: agent.prompt,
						...(resolvedModel ? { model: resolvedModel } : {}),
						...existing,
						permission: { ...(existing.permission || {}), ...v1Permission(agent) },
					};
				}
			} catch (err) {
				console.error("[magic] agent config registration failed:", err);
			}

			if (Array.isArray(config.skills)) return;
			config.skills = config.skills || {};
			config.skills.paths = config.skills.paths || [];
			if (!config.skills.paths.includes(magicSkillsDir)) {
				config.skills.paths.push(magicSkillsDir);
			}
		},

		"experimental.chat.messages.transform": async (_input, output) => {
			if (!output.messages || !output.messages.length) return;
			const firstUser = output.messages.find((m) => m.info.role === "user");
			if (!firstUser || !firstUser.parts.length) return;
			if (firstUser.parts.some((p) => p.type === "text" && p.text.startsWith(BOOTSTRAP_MARKER))) return;

			if (
				client &&
				(await isChildSession(
					(id) => client.session.get({ path: { id } }),
					firstUser.info.sessionID,
				))
			) {
				return;
			}

			const bootstrap = loadBootstrapContent(
				magicSkillsDir,
				V1_MAPPING,
				undefined,
				bootstrapSections(loadMagicModels()),
			);
			if (!bootstrap) return;

			const ref = firstUser.parts[0];
			firstUser.parts.unshift({ ...ref, type: "text", text: bootstrap });
		},
	};
};

export const DotAgentsPlugin = MagicPlugin;

async function setup(ctx) {
	if (
		!ctx ||
		!ctx.skill ||
		typeof ctx.skill.transform !== "function" ||
		!ctx.session ||
		typeof ctx.session.hook !== "function"
	) {
		return;
	}

	try {
		const skills = loadKitSkills(magicSkillsDir);
		await ctx.skill.transform((draft) => {
			for (const skill of skills) {
				try {
					draft.add(skill);
				} catch (err) {
					console.error(`[magic] skill "${skill.id}" rejected by host, skipping:`, err);
				}
			}
		});
	} catch (err) {
		console.error("[magic] skill registration failed:", err);
	}

	if (ctx.agent && typeof ctx.agent.transform === "function") {
		try {
			const magicModels = loadMagicModels();
			const modelsPresets = loadModelsJsonPresets();
			const agents = loadKitAgents(magicAgentsDir);
			ctx.agent.transform((editor) => {
				if (!editor || typeof editor.update !== "function") return;
				for (const agent of agents) {
					const resolvedModel = resolveAgentModel(agent.id, magicModels?.parsed, modelsPresets);
					const resolvedRef = parseModelRef(resolvedModel);
					try {
						editor.update(agent.id, (draft = {}) => {
							const rawDraft = draft && typeof draft === "object" ? draft : {};
							const { model: draftModel, ...current } = rawDraft;
							const model = toModelRef(draftModel) ?? resolvedRef;
							const next = {
								...current,
								id: agent.id,
								name: agent.name,
								mode: "subagent",
								description: agent.description,
								system: agent.prompt,
								hidden: current.hidden ?? false,
								request: current.request ?? v2DefaultRequest(),
								permissions: v2Permissions(current, agent),
								...(model ? { model } : {}),
							};
							if (draft && typeof draft === "object" && !Object.isFrozen(draft)) {
								if (!("model" in next)) delete draft.model;
								Object.assign(draft, next);
							}
							return next;
						});
					} catch (err) {
						console.error(`[magic] agent "${agent.id}" registration failed:`, err);
					}
				}
			});
		} catch (err) {
			console.error("[magic] agent registration failed:", err);
		}
	}

	const injectBootstrap = async (event) => {
		try {
			if (!event.messages || !event.messages.length) return;
			const firstUser = event.messages.find((m) => m.role === "user");
			if (firstUser && (!firstUser.content || !firstUser.content.length)) return;
			if (
				firstUser?.content.some(
					(p) => p.type === "text" && p.text && p.text.startsWith(BOOTSTRAP_MARKER),
				)
			) {
				return;
			}

			if (
				typeof ctx.session.get === "function" &&
				(await isChildSession((id) => ctx.session.get({ sessionID: id }), event.sessionID))
			) {
				return;
			}

			const bootstrap = loadBootstrapContent(
				magicSkillsDir,
				V2_MAPPING,
				undefined,
				bootstrapSections(loadMagicModels()),
			);
			if (!bootstrap) return;

			if (firstUser) {
				firstUser.content.unshift({ type: "text", text: bootstrap });
			} else {
				event.messages.push({ role: "user", content: [{ type: "text", text: bootstrap }] });
			}
		} catch (err) {
			console.error("[magic] session hook failed:", err);
		}
	};

	for (const hookName of ["context", "compaction", "generate"]) {
		try {
			await ctx.session.hook(hookName, injectBootstrap);
		} catch (err) {
			console.error(`[magic] session hook registration failed (${hookName}):`, err);
		}
	}
}

export default {
	id: "magic",
	server: MagicPlugin,
	setup,
};
