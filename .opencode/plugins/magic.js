import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
	BOOTSTRAP_MARKER,
	extractAndStripFrontmatter,
	loadBootstrapContent,
} from "../../lib/bootstrap-core.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const magicSkillsDir = path.resolve(__dirname, "../../skills");

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
- Create or update todos → OpenCode v2 has no todo tool; track the plan in a markdown file (or the harness's plan facility) instead
- \`Subagent (general-purpose):\` → \`subagent\` with \`agent: "general"\` (give it \`description\` and \`prompt\`, optionally \`background\`; pass \`sessionID\` to continue a previous subagent)
- Invoke a skill → OpenCode's native \`skill\` tool. Skill ids are bare names, so drop the \`magic:\` prefix skills use when they name each other (\`magic:magic-mode\` → \`skill\` with \`id: "magic-mode"\`)
- Read files → \`read\`
- Create, edit, or delete files → use \`patch\` with \`patchText\` when available; otherwise use \`write\` to create or overwrite files, \`edit\` for targeted changes, and \`shell\` for deletion
- Run shell commands → \`shell\` (\`command\`, \`workdir\`, \`timeout\`, \`background\`)
- Search files → \`grep\`, \`glob\`
- Fetch a URL → \`webfetch\`
- Search the web → \`websearch\`

Use OpenCode's native \`skill\` tool to list and load skills.`;

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
			if (Array.isArray(config.skills)) return;
			config.skills = config.skills || {};
			config.skills.paths = config.skills.paths || [];
			if (!config.skills.paths.includes(magicSkillsDir)) {
				config.skills.paths.push(magicSkillsDir);
			}
		},

		"experimental.chat.messages.transform": async (_input, output) => {
			const bootstrap = loadBootstrapContent(magicSkillsDir, V1_MAPPING);
			if (!bootstrap || !output.messages.length) return;
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
		const skills = [];
		if (fs.existsSync(magicSkillsDir)) {
			for (const entry of fs.readdirSync(magicSkillsDir, { withFileTypes: true })) {
				if (!entry.isDirectory() || entry.name.startsWith(".")) continue;
				const skillPath = path.join(magicSkillsDir, entry.name, "SKILL.md");
				if (!fs.existsSync(skillPath)) continue;
				const { frontmatter, content } = extractAndStripFrontmatter(
					fs.readFileSync(skillPath, "utf8"),
				);
				skills.push({
					id: entry.name,
					name: frontmatter.name || entry.name,
					...(frontmatter.description ? { description: frontmatter.description } : {}),
					path: skillPath,
					content,
				});
			}
		}
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

	const injectBootstrap = async (event) => {
		try {
			const bootstrap = loadBootstrapContent(magicSkillsDir, V2_MAPPING);
			if (!bootstrap || !event.messages || !event.messages.length) return;
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
