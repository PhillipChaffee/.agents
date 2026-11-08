# Baseline (RED): Unmodified `/poteto-mode` + `/how`

**Consumer and maintainer impact.** An engineer or product manager running `/statechart` gets Mermaid statecharts, PNG diagrams, and plain-language bug stories generated from TLA+ models or hand-drawn Mermaid charts, while untrusted rule tokens in `.cfg` files cannot write files outside the temporary work folder, as verified in `skills/statechart/scripts/statechart.mjs` and `tests/pr26-regressions.test.mjs`. The next engineer maintaining `skills/statechart/scripts/statechart.mjs` inherits a single CLI entrypoint that snapshots inputs before running TLC, confines per-rule output filenames with `encodeURIComponent`, and publishes output folders atomically only after verifying that no input file changed during the run, as read in `skills/statechart/scripts/statechart.mjs` and `skills/statechart/scripts/snapshot.mjs`.

## Overview

`skills/statechart/scripts/statechart.mjs` is the CLI driver for the `/statechart` skill, as defined in `skills/statechart/SKILL.md`. It translates between TLA+ formal specifications and Mermaid statecharts so a human reader can review system transitions and invariant violations without reading raw TLC state dumps, as described in `skills/statechart/SKILL.md`.

The script exposes three subcommands in `COMMANDS` at lines 32 through 58 of `skills/statechart/scripts/statechart.mjs`. The `from-spec` subcommand runs the TLC model checker on a `.tla` model and its `.cfg` file, maps model states to reader labels through a `.map.mjs` module, and emits Mermaid charts and bug stories, as implemented in `fromSpec` at lines 812 through 844 of `skills/statechart/scripts/statechart.mjs`. The `from-chart` subcommand compiles a Mermaid chart into a TLA+ skeleton via `chart-to-tla.mjs`, runs TLC to check its rules, and compares the resulting chart back against the original input via `compare-charts.mjs`, as implemented in `fromChart` at lines 846 through 890 of `skills/statechart/scripts/statechart.mjs`. The `render` subcommand converts a `.mmd` file directly to a `.png` file, as implemented in `renderFile` at lines 560 through 577 of `skills/statechart/scripts/statechart.mjs`.

## Key Concepts

- **`Inputs` snapshot.** The `Inputs` class in `skills/statechart/scripts/snapshot.mjs` copies the input `.tla`, `.cfg`, and `.map.mjs` files along with their transitive `EXTENDS`, `INSTANCE`, and relative ES module dependencies into a temporary directory under `os.tmpdir()` before TLC runs, as read at lines 37 through 74 of `skills/statechart/scripts/snapshot.mjs`.
- **Reader mapping.** The `.map.mjs` module exports functions such as `state`, `step`, `cause`, `group`, and `detail` plus `readerActions` to translate raw TLA+ variable assignments into reader-facing state and transition labels, as read in `skills/statechart/SKILL.md` and `draw` at lines 377 through 469 of `skills/statechart/scripts/statechart.mjs`.
- **Work folder and atomic publish.** `inWorkFolder` at lines 610 through 624 of `skills/statechart/scripts/statechart.mjs` creates an isolated `statechart-*` directory in `os.tmpdir()` for all intermediate TLC runs and chart files. `publish` at lines 696 through 728 of `skills/statechart/scripts/statechart.mjs` copies that work folder to a sibling staging directory and swaps it into the destination `--out` path only after checking for foreign files and concurrent input edits.
- **Error hierarchy.** `CannotFinish` at line 28 of `skills/statechart/scripts/statechart.mjs` represents expected CLI, configuration, or tool errors that exit with status `2` at lines 899 through 903. `TlcStopped` and `NotPublished` extend `CannotFinish` to distinguish TLC output overflows and aborted directory swaps from unexpected runtime exceptions, as defined at lines 29 and 30 of `skills/statechart/scripts/statechart.mjs`.

## How It Works

When a user invokes `statechart.mjs`, `parseArgs` at lines 60 through 88 of `skills/statechart/scripts/statechart.mjs` validates the command name, flags, and theme options. If the command renders PNG files, `rendererFor` at lines 90 through 97 loads the Mermaid renderer and theme configuration before the command body runs.

In `fromSpec` at lines 812 through 844 of `skills/statechart/scripts/statechart.mjs`, the script first resolves the `.tla` file, the `.cfg` file, the `.map.mjs` file, and any optional `--fixed` or `--against` comparison model. It registers all of those files in an `Inputs` instance so that `readModel` at lines 249 through 266 reads from the frozen temporary copies rather than the live working tree. `splitRules` at lines 125 through 153 strips TLA+ block and line comments from the `.cfg` text and separates `INVARIANT` and `PROPERTY` tokens from the rest of the configuration, returning `cfgWithoutRules`, `rules`, and `properties`. Before starting TLC, `outDir` at lines 604 through 608 calls `refuseForeign` to verify that the destination output directory contains only files matching the `OWN` allowlist regex at line 581, refusing to run if unknown files exist. If the `.map.mjs` file does not exist yet, `fromSpec` writes a starter mapping via `SCAFFOLD` and exits with `CannotFinish` at lines 822 through 825.

Next, `fromSpec` enters `inWorkFolder` and calls `check` at lines 279 through 352 of `skills/statechart/scripts/statechart.mjs`. `check` creates a `tlc` subdirectory inside the temporary work folder. For each invariant in `rules`, `check` writes a dedicated `.cfg` file containing `cfgWithoutRules`, `INVARIANT <rule>`, and `CONSTRAINT <rule>`, and runs `tlc` with `-workers auto` at lines 299 through 302. If TLC reports an invariant violation on the multi-worker run, `check` runs TLC a second time with a single worker at line 305 so breadth-first search finds the shortest deterministic counterexample path. For each temporal rule in `properties`, `check` writes a `.cfg` file with `PROPERTY <property>` and runs TLC at lines 312 through 316. After checking individual rules, `check` writes a combined rules module via `writeRulesModule` and runs TLC one more time with `-dump dot,actionlabels` to export the full state graph as a `.dot` file at lines 327 through 334. `runJava` at lines 155 through 180 bounds both standard output and the `.dot` file size to `buffer.constants.MAX_STRING_LENGTH` and sends `SIGKILL` to the Java child process if either limit is exceeded.

Look at how `check` constructs the per-rule file path at line 300 and line 313 of `skills/statechart/scripts/statechart.mjs` to see how it prevents the path-traversal bug tested in `tests/pr26-regressions.test.mjs`. `splitRules` at line 130 tokenizes the `.cfg` file on whitespace (`/\s+/`), so a crafted or malformed rule name after `INVARIANT` or `PROPERTY` can contain slashes and `..` segments such as `../../../../escape`, as exercised at line 95 of `tests/pr26-regressions.test.mjs`. If `check` interpolated the raw `rule` or `property` string directly into ``path.join(tlcDir, `${name}-${rule}`)``, `path.join` would normalize the `..` segments and resolve the target path outside `tlcDir` and `work`, causing `tlc` at line 183 (``fs.writeFileSync(`${base}.cfg`, cfg)``) and line 225 (``fs.writeFileSync(`${base}.out`, r.stdout)``) to overwrite arbitrary `.cfg` and `.out` files in parent directories such as `TMPDIR`, as inferred from lines 116 through 128 of `tests/pr26-regressions.test.mjs`. Instead, line 300 and line 313 wrap the token in `encodeURIComponent(rule)` and `encodeURIComponent(property)` when building `file`:

```javascript
    const file = path.join(tlcDir, `${name}-${encodeURIComponent(rule)}`);
    const cfg = `${cfgWithoutRules}INVARIANT ${rule}\nCONSTRAINT ${rule}\n`;
    let result = await run(cfg, file, { workers: "auto" });
    // Several workers can reach a bad state by a longer path first. One worker searches breadth
    // first in a fixed order, so the chart's bug paths are the shortest, and the same every run.
    if (/^Error: Invariant /m.test(result.stdout)) result = await run(cfg, file);
    const broken = /^Error: Invariant /m.test(result.stdout);
    console.log(said(rule, broken));
    if (result.warning) console.error(`${shown(`${file}.out`)}: ${result.warning}`);
    traces.push({ file: `${file}.out`, rule, broken });
  }
  const temporal = [];
  for (const property of properties) {
    const file = path.join(tlcDir, `${name}-${encodeURIComponent(property)}`);
```

Because `encodeURIComponent` percent-encodes `/` as `%2F`, `../../../../escape` becomes the single filename component `M-..%2F..%2F..%2F..%2Fescape` inside `<tmp>/statechart-<id>/tlc/`, while the raw token remains untouched inside the `.cfg` file body passed to TLC, as asserted at lines 124 through 129 of `tests/pr26-regressions.test.mjs`.

Once `check` finishes for the primary model and any `--fixed` or `--against` model, `draw` at lines 369 through 531 of `skills/statechart/scripts/statechart.mjs` spawns `tlc-to-chart.mjs` to turn the `.dot` state graph and trace files into `chart.mmd`, per-bug `bug-<n>.mmd` charts, `stories.md`, and `summary.json`. Finally, `finish` at lines 548 through 558 calls `unchanged` to confirm no input file changed since `Inputs` snapshotted it, renders `.png` files if `--png` was passed, and calls `publish` to swap the completed directory into the output path.

## Where Things Live

- `skills/statechart/SKILL.md` defines the workflow for choosing between `from-spec` and `from-chart`, authoring reader labels and invariants, replaying bug stories against real code, and handing off artifacts, as read in `skills/statechart/SKILL.md`.
- `skills/statechart/scripts/statechart.mjs` owns CLI argument parsing, TLC execution orchestration, per-rule `.cfg` and `.out` path confinement, chart generation calls, and atomic output directory publishing, as read in `skills/statechart/scripts/statechart.mjs`.
- `skills/statechart/scripts/snapshot.mjs` owns the `Inputs` class that snapshots `.tla`, `.cfg`, and `.map.mjs` files along with their transitive imports into temporary storage and detects concurrent modifications during a run, as read in `skills/statechart/scripts/snapshot.mjs`.
- `tests/pr26-regressions.test.mjs` owns the regression tests for worktree audit safety and for `statechart.mjs` confining `INVARIANT` and `PROPERTY` output files when rule tokens contain `../../../../escape`, as read in `tests/pr26-regressions.test.mjs`.

## Gotchas

- **TLC shares `java.io.tmpdir` across runs by default.** TLC writes standard modules such as `Naturals.tla` into `java.io.tmpdir` under fixed filenames, so `tlc` in `skills/statechart/scripts/statechart.mjs` creates a per-run `tmp` directory inside `metadir` and passes `-Djava.io.tmpdir=${javaTmp}` at lines 185 through 195 to prevent concurrent runs from corrupting each other's standard modules.
- **State predicates listed under `PROPERTY` are only checked in initial states.** TLC checks a non-temporal formula under `PROPERTY` only in initial states, so `splitRules` filters out any `PROPERTY` that is already listed as an `INVARIANT` at line 151, and `check` warns via `checkedOnlyInInitialStates` at lines 321 through 322 of `skills/statechart/scripts/statechart.mjs`.
- **FUSE and cross-device mounts reject non-empty directory renames.** Some filesystems fail `fs.renameSync` on populated directories with `ENOSYS`, `EXDEV`, or `EISDIR`, so `moved` at lines 626 through 669 of `skills/statechart/scripts/statechart.mjs` falls back to renaming an empty directory while holding an open file descriptor to lock its inode number (`sameFolder`) and copying files with `COPYFILE_EXCL`.
- **Uncited action conditions in code models trigger warnings.** When comparing a model with `--fixed` or `--against`, `warnUncited` at lines 797 through 810 of `skills/statechart/scripts/statechart.mjs` flags any action condition that lacks a `\* file:line` comment so a rule cannot silently hold due to a guard that the real code never checks.

**Verification.** Ran `node --test tests/pr26-regressions.test.mjs` in `/agent/repos/.agents`, and all 11 tests passed in 734.6 ms with exit code 0, including the 4 subtests for `statechart confines INVARIANT output` and `statechart confines PROPERTY output` with `Safe_Name1` and `../../../../escape`, as measured from the test runner output.
