import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";

const repoDir = path.resolve(import.meta.dirname, "..");
const hooksDir = path.join(repoDir, "hooks");
const sessionStartHook = path.join(hooksDir, "session-start");
const runHookCmd = path.join(hooksDir, "run-hook.cmd");
const bashBin = spawnSync("bash", ["-c", 'printf "%s" "$BASH"'], { encoding: "utf8" }).stdout.trim() || "/bin/bash";

function parseHookOutput(stdout, shape) {
	const payload = JSON.parse(stdout);
	const keys = Object.keys(payload);
	let context;
	if (shape === "nested") {
		assert.deepEqual(keys, ["hookSpecificOutput"]);
		assert.equal(payload.hookSpecificOutput.hookEventName, "SessionStart");
		assert.deepEqual(Object.keys(payload.hookSpecificOutput).sort(), ["additionalContext", "hookEventName"]);
		context = payload.hookSpecificOutput.additionalContext;
	} else if (shape === "cursor") {
		assert.deepEqual(keys, ["additional_context"]);
		context = payload.additional_context;
	} else if (shape === "sdk") {
		assert.deepEqual(keys, ["additionalContext"]);
		context = payload.additionalContext;
	} else {
		assert.fail(`unknown shape: ${shape}`);
	}
	assert.match(context, /^<EXTREMELY_IMPORTANT>\nYou have magic\./);
	assert.match(context, /magic:using-magic/);
	assert.match(context, /# Using Magic/);
	assert.doesNotMatch(context, /Error reading using-magic skill/);
	return context;
}

test("hooks/hooks.json and hooks/hooks-cursor.json register cross-platform SessionStart commands", () => {
	const claudeHooks = JSON.parse(fs.readFileSync(path.join(hooksDir, "hooks.json"), "utf8"));
	const hookEntry = claudeHooks?.hooks?.SessionStart?.[0]?.hooks?.[0];
	assert.ok(hookEntry, "missing SessionStart[0].hooks[0] in hooks/hooks.json");
	assert.equal(hookEntry.type, "command");
	assert.equal(hookEntry.shell, "bash");
	assert.equal(hookEntry.async, false);
	assert.equal(hookEntry.command, '"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd" session-start');
	assert.equal(hookEntry.powershell, '& "${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd" session-start');

	const cursorHooks = JSON.parse(fs.readFileSync(path.join(hooksDir, "hooks-cursor.json"), "utf8"));
	assert.equal(cursorHooks.version, 1);
	assert.equal(cursorHooks?.hooks?.sessionStart?.[0]?.command, "./hooks/run-hook.cmd session-start");

	for (const script of [runHookCmd, sessionStartHook]) {
		fs.accessSync(script, fs.constants.X_OK);
	}
});

test("session-start and run-hook.cmd emit mutually exclusive harness JSON shapes and survive empty PATH, bare filenames, backslash paths, and early-closed stdout", (t) => {
	const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "dot-agents-hooks-"));
	t.after(() => fs.rmSync(tmpDir, { recursive: true, force: true }));

	const envCases = [
		{
			name: "Claude Code nested hookSpecificOutput",
			shape: "nested",
			env: { HOME: tmpDir, PATH: process.env.PATH ?? "", CLAUDE_PLUGIN_ROOT: repoDir },
		},
		{
			name: "Cursor additional_context precedence over CLAUDE_PLUGIN_ROOT",
			shape: "cursor",
			env: {
				HOME: tmpDir,
				PATH: process.env.PATH ?? "",
				CURSOR_PLUGIN_ROOT: repoDir,
				CLAUDE_PLUGIN_ROOT: repoDir,
			},
		},
		{
			name: "Copilot CLI top-level additionalContext",
			shape: "sdk",
			env: {
				HOME: tmpDir,
				PATH: process.env.PATH ?? "",
				COPILOT_CLI: "1",
				CLAUDE_PLUGIN_ROOT: repoDir,
			},
		},
		{
			name: "Empty PATH survival",
			shape: "nested",
			env: { HOME: tmpDir, PATH: "", CLAUDE_PLUGIN_ROOT: repoDir },
		},
	];

	for (const { name, shape, env } of envCases) {
		for (const args of [[sessionStartHook], [runHookCmd, "session-start"]]) {
			const res = spawnSync(bashBin, args, { env, encoding: "utf8" });
			assert.equal(res.status, 0, `${name} (${args.join(" ")}) failed: ${res.stderr}`);
			assert.equal(res.stderr, "");
			parseHookOutput(res.stdout, shape);
		}
	}

	for (const cmd of ["exec \"$1\" session-start", "exec \"$1\" run-hook.cmd session-start"]) {
		const res = spawnSync(bashBin, ["-c", cmd, "_", bashBin], {
			cwd: hooksDir,
			env: { HOME: tmpDir, PATH: "", CLAUDE_PLUGIN_ROOT: repoDir },
			encoding: "utf8",
		});
		assert.equal(res.status, 0, res.stderr);
		parseHookOutput(res.stdout, "nested");
	}

	const backslashRoot = path.join(tmpDir, "backslash-root");
	fs.mkdirSync(backslashRoot, { recursive: true });
	fs.symlinkSync(hooksDir, path.join(backslashRoot, "hooks"));
	fs.symlinkSync(path.join(repoDir, "skills"), path.join(backslashRoot, "skills"));
	fs.symlinkSync(sessionStartHook, path.join(backslashRoot, "hooks\\session-start"));
	const backslashRes = spawnSync(bashBin, ["hooks\\session-start"], {
		cwd: backslashRoot,
		env: { HOME: tmpDir, PATH: "", CLAUDE_PLUGIN_ROOT: repoDir },
		encoding: "utf8",
	});
	assert.equal(backslashRes.status, 0, backslashRes.stderr);
	parseHookOutput(backslashRes.stdout, "nested");

	for (const target of [
		`"${bashBin}" "${sessionStartHook}" | :`,
		`"${bashBin}" "${runHookCmd}" session-start | :`,
	]) {
		const closedRes = spawnSync(bashBin, ["-o", "pipefail", "-c", target], {
			env: { HOME: tmpDir, PATH: process.env.PATH ?? "", CLAUDE_PLUGIN_ROOT: repoDir },
			encoding: "utf8",
		});
		assert.equal(closedRes.status, 0, closedRes.stderr);
		assert.equal(closedRes.stderr, "");
	}

	const straceCheck = spawnSync("which", ["strace"], { encoding: "utf8" });
	if (process.platform === "linux" && straceCheck.status === 0) {
		for (const args of [[sessionStartHook], [runHookCmd, "session-start"]]) {
			const forkLog = path.join(tmpDir, "forks.log");
			const traceRes = spawnSync(
				straceCheck.stdout.trim(),
				["-f", "-qq", "-e", "trace=fork,vfork,clone,clone3", "-o", forkLog, bashBin, ...args],
				{
					env: { HOME: tmpDir, PATH: process.env.PATH ?? "", CLAUDE_PLUGIN_ROOT: repoDir },
					encoding: "utf8",
				},
			);
			assert.equal(traceRes.status, 0, traceRes.stderr);
			const logText = fs.readFileSync(forkLog, "utf8");
			assert.doesNotMatch(logText, /(?:fork|clone3?)\(/, `expected zero child forks for ${args.join(" ")}`);
		}
	}
});

test("Claude Code, Cursor, and Codex plugin and marketplace manifests satisfy schema contracts", () => {
	const claudePlugin = JSON.parse(
		fs.readFileSync(path.join(repoDir, ".claude-plugin/plugin.json"), "utf8"),
	);
	assert.equal(claudePlugin.name, "magic");
	assert.equal(claudePlugin.version, "0.2.0");
	assert.equal(claudePlugin.repository, "https://github.com/PhillipChaffee/magic");

	const claudeMarketplace = JSON.parse(
		fs.readFileSync(path.join(repoDir, ".claude-plugin/marketplace.json"), "utf8"),
	);
	assert.equal(claudeMarketplace.name, "magic-dev");
	assert.equal(claudeMarketplace.plugins?.[0]?.name, "magic");
	assert.equal(claudeMarketplace.plugins?.[0]?.version, "0.2.0");
	assert.equal(claudeMarketplace.plugins?.[0]?.source, "./");

	const cursorPlugin = JSON.parse(
		fs.readFileSync(path.join(repoDir, ".cursor-plugin/plugin.json"), "utf8"),
	);
	assert.equal(cursorPlugin.name, "magic");
	assert.equal(cursorPlugin.displayName, "magic");
	assert.equal(cursorPlugin.version, "0.2.0");
	assert.equal(cursorPlugin.skills, "./skills/");
	assert.equal(cursorPlugin.agents, "./agents/");
	assert.equal(cursorPlugin.rules, "./rules/");
	assert.equal(cursorPlugin.hooks, "./hooks/hooks-cursor.json");

	const cursorMarketplace = JSON.parse(
		fs.readFileSync(path.join(repoDir, ".cursor-plugin/marketplace.json"), "utf8"),
	);
	assert.equal(cursorMarketplace.name, "magic-dev");
	assert.equal(cursorMarketplace.plugins?.[0]?.name, "magic");
	assert.equal(cursorMarketplace.plugins?.[0]?.version, "0.2.0");
	assert.equal(cursorMarketplace.plugins?.[0]?.source, "./");

	const codexPlugin = JSON.parse(
		fs.readFileSync(path.join(repoDir, ".codex-plugin/plugin.json"), "utf8"),
	);
	assert.equal(codexPlugin.name, "magic");
	assert.equal(codexPlugin.version, "0.2.0");
	assert.equal(codexPlugin.skills, "./skills/");
	assert.deepEqual(codexPlugin.hooks, {});
	assert.ok(codexPlugin.interface && typeof codexPlugin.interface === "object");

	const codexMarketplace = JSON.parse(
		fs.readFileSync(path.join(repoDir, ".agents/plugins/marketplace.json"), "utf8"),
	);
	assert.equal(codexMarketplace.name, "magic-dev");
	assert.deepEqual(codexMarketplace.plugins, [
		{
			name: "magic",
			source: { source: "url", url: "./" },
			policy: { installation: "AVAILABLE", authentication: "ON_INSTALL" },
			category: "Developer Tools",
		},
	]);
});
