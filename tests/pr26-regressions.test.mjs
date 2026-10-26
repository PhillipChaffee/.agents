import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import test from "node:test";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const audit = path.join(root, "skills/poteto-mode/scripts/worktree-audit.sh");
const statechart = path.join(root, "skills/statechart/scripts/statechart.mjs");
const realGit = spawnSync("which", ["git"], { encoding: "utf8" }).stdout.trim();

test("cleanup guide requires fresh inspection and non-forced removal", () => {
  const guide = fs.readFileSync(path.join(root, "skills/poteto-mode/playbooks/worktree-cleanup.md"), "utf8");
  assert.match(guide, /--untracked-files=all --ignored --ignore-submodules=none/);
  assert.match(guide, /successful exit and empty output/);
  assert.doesNotMatch(guide, /worktree remove --force|rm -rf|untracked throwaway/);
});

function fixture(t) {
  const directory = fs.realpathSync(fs.mkdtempSync(path.join(os.tmpdir(), "agents-regression-")));
  t.after(() => fs.rmSync(directory, { recursive: true, force: true }));
  const tmp = path.join(directory, "tmp");
  fs.mkdirSync(tmp);
  const env = Object.fromEntries(
    Object.entries(process.env).filter(([key]) => !key.startsWith("GIT_") && !key.startsWith("WORKTREE_AUDIT_")),
  );
  Object.assign(env, {
    HOME: directory,
    XDG_CONFIG_HOME: directory,
    GIT_CONFIG_GLOBAL: path.join(directory, "no-global-config"),
    GIT_CONFIG_NOSYSTEM: "1",
    GIT_TERMINAL_PROMPT: "0",
    TMPDIR: tmp,
  });
  return { directory, tmp, env };
}

function run(command, args, options) {
  const result = spawnSync(command, args, { encoding: "utf8", timeout: 10000, ...options });
  assert.equal(result.error, undefined, result.error?.message);
  return result;
}

for (const kind of ["clean", "tracked", "untracked", "ignored", "hidden-untracked", "status-failure"]) {
  test(`worktree audit preserves ${kind} work`, (t) => {
    const { directory, env } = fixture(t);
    const repo = path.join(directory, "repo");
    const linked = path.join(directory, "linked");
    const git = (...args) => {
      const result = run(realGit, args, { env });
      assert.equal(result.status, 0, result.stderr);
    };
    git("init", "-q", "-b", "main", repo);
    git("-C", repo, "config", "user.name", "Regression Test");
    git("-C", repo, "config", "user.email", "test@example.invalid");
    fs.writeFileSync(path.join(repo, "tracked.txt"), "original\n");
    fs.writeFileSync(path.join(repo, ".gitignore"), "private.dat\n");
    git("-C", repo, "add", ".");
    git("-C", repo, "commit", "-qm", "fixture");
    git("-C", repo, "worktree", "add", "-q", "--detach", linked, "HEAD");
    if (kind === "tracked") fs.appendFileSync(path.join(linked, "tracked.txt"), "keep\n");
    if (["untracked", "hidden-untracked"].includes(kind))
      fs.writeFileSync(path.join(linked, "notes.txt"), "keep\n");
    if (kind === "hidden-untracked") git("-C", repo, "config", "status.showUntrackedFiles", "no");
    if (kind === "ignored") fs.writeFileSync(path.join(linked, "private.dat"), "keep\n");
    if (kind === "status-failure") {
      const bin = path.join(directory, "bin");
      fs.mkdirSync(bin);
      fs.writeFileSync(
        path.join(bin, "git"),
        '#!/bin/sh\nif [ "$3" = status ]; then exit 1; fi\nexec "$TEST_REAL_GIT" "$@"\n',
        { mode: 0o755 },
      );
      env.PATH = `${bin}${path.delimiter}${env.PATH}`;
      env.TEST_REAL_GIT = realGit;
    }
    const result = run("bash", [audit, "-b", "main", repo], { env, cwd: repo });
    assert.equal(result.status, 0, result.stderr);
    const row = result.stdout.split("\n").map((line) => line.split("\t")).find((fields) => fields[8] === linked);
    assert.ok(row, result.stdout);
    assert.equal(row[2], "YES");
    if (kind === "clean") {
      assert.equal(row[3], "clean");
      assert.equal(row[7], "safe");
    } else {
      assert.notEqual(row[3], "clean");
      assert.match(row[7], /^hold-/);
    }
  });
}

for (const kind of ["INVARIANT", "PROPERTY"]) {
  for (const token of ["Safe_Name1", "../../../../escape"]) {
    test(`statechart confines ${kind} output for ${token}`, (t) => {
      const { directory, tmp, env } = fixture(t);
      const spec = path.join(directory, "M.tla");
      fs.writeFileSync(spec, "---- MODULE M ----\nSpec == TRUE\nSafe_Name1 == TRUE\n====\n");
      fs.writeFileSync(path.join(directory, "M.cfg"), `SPECIFICATION Spec\n${kind} ${token}\n`);
      fs.writeFileSync(path.join(directory, "M.map.mjs"), "export {};\n");
      const jar = path.join(directory, "tla2tools.jar");
      fs.writeFileSync(jar, "");
      const java = path.join(directory, "java");
      fs.writeFileSync(java, '#!/bin/sh\nexec "$TEST_NODE" "$TEST_JAVA_STUB" "$@"\n', { mode: 0o755 });
      const stub = path.join(directory, "java-stub.mjs");
      fs.writeFileSync(stub, [
        'import fs from "node:fs";',
        'const args = process.argv.slice(2);',
        'const cfg = args[args.indexOf("-config") + 1];',
        'fs.appendFileSync(process.env.TEST_CALLS, JSON.stringify({cfg, text: fs.readFileSync(cfg, "utf8")}) + "\\n");',
        'console.log("TLC2 Version regression-stub\\nError: regression-stop");',
      ].join("\n"));
      const capture = path.join(directory, "calls.jsonl");
      Object.assign(env, { JAVA: java, TLA2TOOLS: jar, TEST_NODE: process.execPath, TEST_JAVA_STUB: stub, TEST_CALLS: capture });
      for (const ext of ["cfg", "out"]) fs.writeFileSync(path.join(tmp, `escape.${ext}`), "KEEP\n");
      const result = run(process.execPath, [statechart, "from-spec", spec, "--out", path.join(directory, "output")], { env, cwd: directory });
      assert.equal(result.status, 2, result.stderr);
      assert.match(result.stderr, /regression-stop/);
      const calls = fs.readFileSync(capture, "utf8").trim().split("\n").map(JSON.parse);
      assert.equal(calls.length, 1);
      for (const ext of ["cfg", "out"])
        assert.equal(fs.readFileSync(path.join(tmp, `escape.${ext}`), "utf8"), "KEEP\n");
      const relative = path.relative(tmp, calls[0].cfg).split(path.sep);
      assert.equal(relative.length, 3);
      assert.match(relative[0], /^statechart-/);
      assert.equal(relative[1], "tlc");
      assert.equal(relative[2], `M-${encodeURIComponent(token)}.cfg`);
      assert.ok(calls[0].text.includes(`${kind} ${token}\n`));
    });
  }
}
