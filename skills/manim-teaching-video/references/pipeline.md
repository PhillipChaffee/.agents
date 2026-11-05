# Pipeline: twelve steps from a topic to a verified video

Attribution: the principles, patterns and rubric in this file are derived from a study
of 3Blue1Brown's videos and the public source in the 3b1b/videos repository
(CC BY-NC-SA 4.0). The analysis records live in the manim-3b1b-corpus repository. No
frames, transcript text or source code from those videos appear here; every example is
an original ManimCE rendering.

This file is the parent's procedure. The parent is the agent that runs the skill: it reads
`SKILL.md` and this file, keeps `lesson.json` as the one state file of the run, runs the
scripts and dispatches the five roles of `roles.md` as subagents. Below are the twelve steps
with the gate after each, the bound on every loop, who reads what, the commands the parent
runs between dispatches, and what stop and resume mean. Rule ids refer to `framework.md`,
rubric items to `rubric.md`.

## Conventions

- `scripts/` and `references/` are the skill's own directories. The run directory is
  `mtv-runs/<slug>/` in the user's project, written `<run>/` below, and every file of a run
  lives under it.
- `python` is the interpreter `preflight.py` passed: Python 3.11 or 3.12 with ManimCE 0.22,
  with `manim` on `PATH` from the same environment.
- Every script takes `<run>/lesson.json` as its positional argument unless its command shows
  otherwise, prints a one-line verdict last, and exits 0 on a pass, 1 on a gate failure, which
  leaves `lesson.json` valid with what the script measured recorded in it, and 2 on a usage or
  environment error.
- Each step records itself in the `stages` block of `lesson.json`. `narrate.py`,
  `render.py`, `frames.py`, `assemble.py` and `verify.py` do it themselves; the parent does
  it for `brief`, `script`, `storyboard` and `scenes` with the mark helper below, once the
  step's gate passes.
- Before every subagent dispatch, re-dispatches included, the parent bumps
  `attempts.dispatches`. At 48 it stops with a resumable `lesson.json` instead of
  dispatching.
- The parent never installs TeX Live or any other tool, never reads an API key from a file
  (only `ELEVENLABS_API_KEY` from the environment) and never commits.

## Steps

| Step | Action | Gate | Bounded loop |
| --- | --- | --- | --- |
| 0 triage | say the triage line out loud; `exemplars.py check` when `MTV_EXEMPLARS` is set | none | none |
| 1 preflight | `python scripts/preflight.py --json` | exit 0 | none; a failure is a stop with install lines |
| 2 brief | at most three questions; the parent writes the `lesson.json` header | `lesson.validate` empty | none |
| 3 script | one scriptwriter dispatch; `storyboard_check.py --script` | word budget of 150 words per target minute within 15 percent; voice predicates R08 to R11 | 1 retry (`attempts.script_retries`), then ask |
| 4 storyboard | `exemplars.py pick --role storyboarder` when a pack is present; one storyboarder dispatch; `storyboard_check.py`; one storyboard-critic dispatch, always | check exit 0 and critic verdict `pass` | 2 rounds (`attempts.storyboard_rounds`), then ask |
| 5 narrate | `python scripts/narrate.py <run>/lesson.json` | every beat has `duration_s` and `marks_s` | 3 provider retries (`attempts.provider_retries`), then the Kokoro fallback named in the report |
| 6 scenes | one scene-coder dispatch per scene, in waves of four; the parent writes `<run>/lesson.py`; `check_scenes.py` | exit 0, the dry run of every class included | 1 re-dispatch per malformed return (`attempts.redispatches`), then stop |
| 7 draft render and frame review | `render.py --tier draft`; `frames.py --tier draft`; `exemplars.py pick --role frame-critic --scene <id>` when a pack is present; one frame-critic dispatch per scene | every scene rendered; every critic returns 16 scores and its failed beats | render retries per scene (`attempts.render_retries`) |
| 8 fix loop | failed beats return to their coders with the critic's text and the error-table row; only failed scenes re-render and are re-reviewed | the final vector passes the rubric (25 of 32, no item at 0) and no hard gate fails | 2 passes (`attempts.fix_passes`), then deliver with the failing items listed, or stop if a hard gate fails |
| 9 standard render | skipped at tier `draft`; print the estimate; ask before spending more than 45 minutes; `render.py --tier standard` | every scene rendered | render retries per scene |
| 10 assemble | `python scripts/assemble.py <run>/lesson.json --tier <tier>` | the MP4 exists with one video and one audio stream | none |
| 11 verify and report | `python scripts/verify.py <run>/lesson.json --tier <tier>`, which writes `report.md` | exit 0; a failing file is never delivered | none |

## Step by step

### 0 Triage

Say one line out loud before anything runs. It names the tier (`standard`, 1920x1080 at 30
fps, unless the user asks for `draft`, 854x480 at 15 fps), the target length in minutes
(the user's, or 5), the provider (`kokoro`, or `elevenlabs` when the user asks for it and
`ELEVENLABS_API_KEY` is set), the output directory `mtv-runs/<slug>/` (the topic in lower
case with hyphens) and the exemplar directory. When `MTV_EXEMPLARS` is set, run
`python scripts/exemplars.py check` first: on exit 0 the exemplar directory is that path and
the line `index.json sha256 <hex>` it prints is kept for step 2; on exit 1 the exemplar
directory is none and its findings are kept for step 2. When the variable is unset the
exemplar directory is none. An example: "Triage: tier standard, 5 minutes, provider kokoro,
output mtv-runs/what-a-neuron-computes/, exemplars none."

### 1 Preflight

Run `python scripts/preflight.py --json`, adding `--provider elevenlabs` when the triage
chose ElevenLabs. It checks Python 3.11 or 3.12, ManimCE 0.22, `latex`, `dvisvgm`,
`ffmpeg`, `ffprobe`, the provider with a short timed synthesis, the fonts, at least 5 GB of
free disk and the CPU count, and it reruns the exemplar check. A missing font candidate or a
failed pack only reports. Any other failure is a stop: give the user the install line the
JSON names for each failing tool. A Python other than 3.11 or 3.12 is fixed with
`uv venv --python 3.12`. Missing LaTeX is a stop, never a `Text` stand-in for math; the
skill has one math engine.

### 2 Brief

Ask at most three questions, together: who the audience is, how long the video should be,
and, only when `ELEVENLABS_API_KEY` is present in the environment, whether to narrate with
ElevenLabs instead of Kokoro. Then write `<run>/lesson.json` with the header alone:

- `schema` `mtv-lesson/1`, and `slug`, `title`, `audience`, `target_minutes`, `tier` and
  `provider` from the triage and the answers;
- `voice`: the provider's default unless the user named one, `af_heart` for Kokoro and the
  ElevenLabs voice id of `DEFAULT_VOICES` in `scripts/mtv/common.py`;
- `seed`: an integer, the user's when given; every noun helper and every random value of
  the lesson derives from it (R30);
- `colors`: for a lesson about networks or their training, the contract palette of R19,
  `{"weight_pos": "BLUE", "weight_neg": "RED", "bias": "MAROON_B", "cost": "RED", "emphasis": "PURE_YELLOW"}`,
  the `ROLE_COLORS` of `scripts/mtv/common.py`, and one key per further role the topic needs,
  each with a color the palette leaves free, such as `GREEN`, `TEAL`, `GOLD` or `PURPLE`; for
  any other topic, `emphasis` `PURE_YELLOW` and one key per role of its own in any color,
  `BLUE`, `RED` and `MAROON_B` included. Either way each color holds one role (R18).
  `check_scenes.py` rejects a color constant written by name in the scenes, such as `GREEN`,
  that is neither a value of this map nor a neutral white, grey or black, and leaves any other
  color value, a hex string or a `ManimColor`, to the critics, so every role the lesson draws
  is named here;
- `exemplars`: `{"dir": null, "index_sha256": null, "used": {"storyboarder": [],
  "frame-critic": {}}}` when the triage found no pack; the directory and the sha256 the
  check printed when it passed; the directory, a null `index_sha256` and `check_findings`,
  the list of the check's findings, when it failed, which `report.md` then lists as a
  warning;
- `scenes` as `[]`, `attempts` with every counter at 0 and `render_retries` as `{}`,
  `checks` with its four values null, and `stages` as `{}`.

Gate: the validate helper prints `valid`. Then mark `brief`.

### 3 Script

Bump `attempts.dispatches` and dispatch the scriptwriter of `roles.md`. Its return holds the
scenes array with ids, titles, beat ids and narration only; put that array in `scenes`,
discard its notes, and run the validate helper (an invalid return is a malformed return:
one re-dispatch with the errors, `attempts.redispatches`, then stop). Then run:

```bash
python scripts/storyboard_check.py <run>/lesson.json --script
```

Gate: exit 0, which means the script's word count, as `normalize_words` counts it, lies within
15 percent of `target_minutes` times 150, and the voice predicates R08 to R11 hold. On exit 1,
bump `attempts.script_retries` and dispatch the scriptwriter once more with the findings. When
the retry fails too, show the user the findings and ask whether to accept a different length,
change the brief or stop. An accepted length or a changed brief is written into the header
(`target_minutes` for a length), checked with the validate helper and marked `brief` again;
then the check runs again, or, for a changed brief, the scriptwriter is dispatched again. Then
mark `script`.

### 4 Storyboard

A round is one storyboarder dispatch, its check and its critic. Before every round, the first
and each one sent back, when `exemplars.index_sha256` is set, pick the storyboarder's
exemplars:

```bash
python scripts/exemplars.py pick <run>/lesson.json --role storyboarder --max-images 8 --max-words 1000
```

It prints a JSON list of picks, each with `id`, `tag`, `sheet`, `excerpt` and `words`, and
records the ids in `exemplars.used`, replacing the previous round's. Paths are relative to the
pack directory, `exemplars.dir`: the parent passes each sheet path and excerpt path resolved
against it, with the pick's `words`, and opens neither; the role opens the sheet and reads the
first `words` words of the excerpt. The pick is deterministic, so it changes between rounds
only through the storyboard: the first round's scenes have no `scene_kind`, and
`camera-as-narrator` joins once a storyboard has set a scene to camera or 3d. Print the indexed
words with the words helper, then dispatch the storyboarder with the indexed words and the
picks. Its return holds the scenes array with every storyboard field filled. Check that its
scene ids, titles, beat ids and narration equal the script's, put the array in `scenes`,
discard its notes, run the validate helper (a change or an invalid return is malformed: one
re-dispatch, then stop) and run:

```bash
python scripts/storyboard_check.py <run>/lesson.json
```

Exit 0 means every mark resolves to a word, no exemplar id appears in any field and the
predicates of R01, R03, R06, R07, R08, R09, R10, R11, R16 and R28 hold. Then dispatch the
storyboard critic, always, even when the check passed; save its return as
`<run>/reviews/storyboard.json` and, once the check has passed, file its scores with the
storyboard-critic helper so that `report.md` shows the storyboard's total.

Gate: the check exits 0 and the critic's verdict is `pass`. A pass ends the step: the critic's
failed beats go with their scenes to step 6's coders and its wording requests into the final
message. Otherwise bump
`attempts.storyboard_rounds` and send the storyboard back: the check's findings and the
critic's failed beats go to the storyboarder; the critic's wording requests go first to the
scriptwriter. Its return holds only ids, titles, beat ids and narration, so in this round the
parent does not put the array in `scenes` as step 3 does. It first checks that the return
keeps the lesson's scene ids, titles and beat ids, in order: a return that adds, drops or
renumbers a beat, or changes an id or a title, is malformed (one re-dispatch,
`attempts.redispatches`, then stop), since its narration would land on beats staged for other
words. Then it copies each returned narration into its beat and keeps every storyboard field,
runs the validate helper and runs `storyboard_check.py --script`; on exit 1 the findings go
back to the scriptwriter as in step 3, under the same `script_retries` bound, and its return
is checked the same way. Once it exits 0, mark `script` again with the mark
helper, before the storyboarder restages: the `script` stage hashes every beat's narration, so
without the new mark the first-stage helper would send a later resume back to step 3, whose
fresh `scenes` array wipes the storyboard. The storyboarder then restages the changed beats,
their marks included, since new words move the word indices, with the words helper's new
indexed words. A mark that does not resolve to a word is the storyboarder's to fix. When the
storyboard is still failing after two rounds sent back, show the user the findings and the
critic's reasons and ask how to go on. Then mark `storyboard`.

### 5 Narrate

```bash
python scripts/narrate.py <run>/lesson.json
```

It synthesizes each beat's WAV, times every mark and writes `audio`, `words`,
`duration_s`, `marks_s` and `interpolated` for each beat. A network failure is retried three
times with backoff of 2, 4 and 8 s, each retry counted in `attempts.provider_retries`, and
then Kokoro speaks instead; the fallback is named in the report. A beat whose marks cannot
be aligned to the provider's words gets proportional times and `interpolated: true`, which
the report lists; it is never a stop. Gate: exit 0, so every beat has `duration_s` and
`marks_s`. Exit 2 (a provider failure that retrying and the fallback cannot fix) is a stop.

### 6 Scenes

Dispatch one scene coder per scene, at most four at a time, bumping `attempts.dispatches`
for each. Each coder receives its own scene of `lesson.json`, the lesson's `seed` and
`colors`, the previous scene's `closing_state` when its `opening_state` is `continue`, the
storyboard critic's failed beats for its scene when step 4 passed with some, and the
signatures and docstrings of the helpers its beats name, printed by the helper-docs helper. Each returns one class. Once every class is back, a second round runs down each
chain of `continue` scenes: a `continue` scene's coder goes out once the previous scene's
last class is back (its round-2 class when that scene continues, else its round-1 class),
with its class and that one, to open on that class's end state and adapt every beat to it,
each recurring object staying where that state has it until a beat's `visual` moves it. The
parent keeps each class in a file and copies each round-1 file aside; a round-2 coder reads
both classes from their files, overwrites its own, dry-runs only its class (once unless it
fixes something) and returns the path, that run's result and, for a camera scene, its closing
camera frame (the center and width its last `zoom_to` or camera move leaves, read from its
code), not the class; the parent passes that frame on to the next scene's coder. Before the
next coder or the check, a file that `cmp` finds equal to its round-1 copy, or a return whose
dry run failed, is malformed (one re-dispatch, `attempts.redispatches`). Each
round goes out at most four Agent calls per message, every one with
`run_in_background: false`. The parent writes `<run>/lesson.py` as this header followed by
the classes in scene order, two blank lines between them:

```python
import random

from manim import *
from mtv.narrated import Narrated3DScene, NarratedCameraScene, NarratedScene
from mtv.patterns import *

SEED = 20261025  # the lesson's seed
```

Then run:

```bash
python scripts/check_scenes.py <run>/lesson.py <run>/lesson.json
```

It lints the file for banned names, `play(mob.method)`, named colors outside `colors`, a base
class that does not match `scene_kind` (`flat` needs `NarratedScene`, `camera`
`NarratedCameraScene`, `3d` `Narrated3DScene`) and `zoom_to` together with
`orbit_with_hud` in one class, and then runs `manim --dry_run` on every class with the draft
render's `manim.cfg.draft`, killing a class whose output stops growing for ten minutes. Gate:
exit 0.
The lint also rejects a `Text`, `MarkupText`, `Paragraph` or `question_caption` string that
holds a digit, a math sign or a Greek letter, or has a value formatted into it (an f-string
field, `str()`, `%` or `.format`): numbers, signs and formulas go in `MathTex` (`DecimalNumber`
or `Integer` when the value changes) beside the words' `Text` in one `VGroup`.
So does a single letter, other than a, A or I, standing alone in such a string when the same
file sets that letter as math (`MathTex("n")`, or between `$` signs in `Tex`), as the n of
`Text("list size n")`: the symbol goes in `MathTex` too, or the caption is reworded.
The percent sign is one of those signs (`MathTex` sets it as `\%`); a function name the same
file sets as a math operator (one of LaTeX's 32, such as `\cos`, `\log` or `\limsup`, read
as lim sup, or any `\operatorname{name}` other than a, A or I) is rejected when it stands
alone in such a string, as the cos of `Text("cos")`, and goes in `MathTex` beside the words
or is reworded; and all of these readings follow a string through a function the file
defines outside a class body (such as one nested in `construct`) whose parameter reaches
`Text`, `MarkupText`, `Paragraph` or `question_caption` unchanged, as `lbl("slope 6")` for
`def lbl(s): return Text(s)`, unless that function also passes the parameter to `MathTex`,
`SingleStringMathTex` or `Tex`.
Each finding names a line and its fix (from `manimce.md`, or the `MathTex` form above), and
each failed dry run names its class; the owning coder gets them in one re-dispatch (`attempts.redispatches`), and a second
failure of the same scene is a stop. Then mark `scenes`.

### 7 Draft render and frame review

```bash
python scripts/render.py <run>/lesson.json --tier draft
python scripts/frames.py <run>/lesson.json --tier draft
```

Before it selects a scene or looks for `manim`, `render.py` checks steps 4 and 5: until
`storyboard` and `narrate` are marked for the current `lesson.json`, it renders nothing, at any
tier or with `--scenes`, exits 2 and prints each gate that has not passed with the command that
clears it.

`render.py` renders one `manim` process per scene, `--jobs N` at once (default the CPU count
minus one), into `<run>/render/draft/<scene>/`, and fills each beat's `render` block. A
scene with no new line in `render.log` or `run.log` for ten minutes is killed and retried
once with `--disable_caching`; `render.py` does that itself and counts it in
`attempts.render_retries[scene]`. A scene that fails is named in the verdict with its
error-table row, as `<scene>: <idiom> | fix: <fix text>`, or with the last line of its
`render.log`. Bump `attempts.render_retries[scene]`, re-dispatch the owning coder with that
row's fix text and the tail of the scene's `render.log`, replace its class in `lesson.py`
with the returned one and run `check_scenes.py` (a finding gets one re-dispatch,
`attempts.redispatches`), then re-render that scene alone with `--scenes <id>`. A
`latex error` shows the offending TeX lines from `render.log`; the coder fixes the TeX it
wrote and never adds a package in `lesson.py`. A scene gets three render attempts in all.
After the third failure the parent swaps the failing beats' `patterns` for simpler helpers
once (or none, plain ManimCE), reruns `storyboard_check.py` and marks `storyboard` again,
files `<run>/reviews/storyboard.json` again with the storyboard-critic helper, since the
check rewrote `checks.storyboard`, re-dispatches the coder, reruns `check_scenes.py` and
marks `scenes` again, and renders a last time; a failure after that is a stop.

`frames.py` writes, for every beat, a still at each mark (`frames/<scene>/<beat>-<mark>.png`),
its last frame (`<beat>-last.png`), the first frame of a scene's first beat
(`<beat>-first.png`) and the six-frame sheet (`<beat>-sheet.jpg`), and it measures every scene
boundary into `frames/continuity.json`. Then, for each scene, when `exemplars.index_sha256` is
set, pick the frame critic's exemplars:

```bash
python scripts/exemplars.py pick <run>/lesson.json --role frame-critic --scene <id> --max-images 4 --max-words 500
```

and dispatch one frame critic for the scene with the inputs its section of `roles.md` names,
the previous scene's `closing_state` among them when the scene opens with `continue`, the
earlier beats' values that the earlier-values helper prints for the scene, and its picks. Save
each return as `<run>/reviews/<scene>.json` and file them with the frame-critic helper, which
stores each return unchanged under `checks.frames.scenes[scene]`. Gate: every scene rendered
and every critic returned 16 scores and its failed beats (a malformed return gets one
re-dispatch).

### 8 Fix loop

The frame-critic helper also computes `checks.frames.final` with `lesson.frames_final`: the
final score of an item is its minimum across the scenes, except that an item whose 1 anchor
names a single lapse (the nine of `rubric.md`'s How to score step 2) scores 0 when two or more
scenes score it 1, since each such 1 is one lapse in the lesson and a second lapse scores 0;
`zeros` lists the items at 0, and `pass` is true when the total is at least 25 of 32 and no
item is 0. The hard gates are the gates of `verify.py`; at
this step the parent runs them on the draft:

```bash
python scripts/assemble.py <run>/lesson.json --tier draft
python scripts/verify.py <run>/lesson.json --tier draft
```

Gate: `checks.frames.final.pass` is true and `verify.py` exits 0. Otherwise bump
`attempts.fix_passes` and send each failed beat back to its scene's coder with the critic's
reason and rule ids, the error-table row when a render failed, or the failing `verify.py`
gate (an overrun past 1.0 s is fixed by shorter plays and waits in the beat; a jump cut at
a `continue` boundary by rebuilding the previous `closing_state` before the first beat; a
clipped or illegible object by a new layout). Replace each returned class in `lesson.py`,
run `check_scenes.py`, re-render only the failed scenes with `--scenes`, run `frames.py`,
pick again and dispatch a frame critic for those scenes only, file the new returns and
assemble and verify the draft again. After two passes a lesson whose hard gates pass goes
on with its failing rubric items listed in the report; a hard gate still failing is a stop.

### 9 Standard render

Skipped when the tier is `draft`. Otherwise print the estimate first: the wall clock of the
full draft render of step 7, which `render.py` printed in its verdict, times
`STANDARD_TO_DRAFT_RATIO` in `scripts/mtv/common.py` (2.00 in this kit). When the
estimate is above 45 minutes, ask before spending it, and offer the draft tier instead.
Then:

```bash
python scripts/render.py <run>/lesson.json --tier standard
```

Gate: every scene rendered. Failures follow the render retries of step 7.

### 10 Assemble

```bash
python scripts/assemble.py <run>/lesson.json --tier <tier>
```

It joins the beat videos in order, places each beat's WAV at its beat's start, normalizes
the narration to -16 LUFS, applies a saturation of 1.5 (`--saturation 1.0` turns it off)
and writes `<run>/out/<slug>.<tier>.mp4` with `<run>/out/<slug>.<tier>.srt`. Gate: the MP4
exists with one video and one audio stream.

### 11 Verify and report

```bash
python scripts/verify.py <run>/lesson.json --tier <tier>
```

It runs every hard gate (the streams, the container duration, each beat's run log against
the section index, each WAV within its beat, every mark inside its beat, overruns at most
1.0 s, no banned name, a section index entry for every beat, no `latex error`, continuity at
every `continue` boundary), writes `checks.verify` and writes `<run>/report.md`. Gate: exit
0. A file that fails is never delivered. A valid run leaves an MP4 that passed `verify.py`,
a `report.md` and a `lesson.json` with every stage its tier runs recorded; the parent hands
the user the MP4, its subtitles and the report.

## Bounded loops

Every counter counts repeats, never the first attempt, and lives in `attempts`; the parent
bumps it with the bump helper unless the table names a script.

| Loop | Bound | Counter | After the bound |
| --- | --- | --- | --- |
| script word budget or voice rule | 1 retry | `script_retries` | ask the user |
| storyboard check plus critic | 2 rounds sent back | `storyboard_rounds` | ask the user |
| malformed subagent return | 1 re-dispatch per call | `redispatches` | stop |
| render exception per scene | 3 attempts, then 1 pattern simplification | `render_retries[scene]` | stop |
| hung render per scene | 1 retry with `--disable_caching`, by `render.py` | `render_retries[scene]` | stop |
| frame-review fix loop | 2 passes | `fix_passes` | deliver with the failing rubric items listed, or stop if a hard gate fails |
| provider network failure | 3 retries, backoff 2, 4 and 8 s, by `narrate.py` | `provider_retries` | fall back to Kokoro |
| parent hand-off | 48 dispatches | `dispatches` | stop with a resumable `lesson.json` |
| sync gate | `SYNC_BEAT_TOLERANCE_S` per beat (2/15 s, two draft frames) and `SYNC_CONTAINER_TOLERANCE_S` per container (0.5 s), in `scripts/mtv/common.py` | not a loop | a failing gate is fixed in the fix loop or stops the run |

## Load order

The parent never loads `patterns.md`, the analyses or an exemplar pack; it copies a role's
section of `roles.md` into that role's dispatch and works from nothing else in that file.

| Role | Reads |
| --- | --- |
| parent | `SKILL.md`, `pipeline.md`, the `lesson.json` header and the `checks` block; a role's section of `roles.md` to dispatch it |
| scriptwriter | `framework.md`; the brief, which is the `lesson.json` header |
| storyboarder | `framework.md`, `patterns.md`, the script and its indexed words; the picked exemplars when a pack is present |
| storyboard critic | `rubric.md`, the storyboard |
| scene coder | its scene of `lesson.json` with the seed, the colors and the previous scene's `closing_state`; the storyboard critic's failed beats for its scene when step 4 passed with some; in round 2, its own class file and the previous scene's, and that scene's closing camera frame when it is a camera scene; the signatures and docstrings of the helpers it names; `manimce.md` |
| frame critic | `rubric.md`, its whole scene of `lesson.json` with the colors and, when it opens with `continue`, the previous scene's `closing_state`; the `shows_value_of` and `symbol_introduced` of every earlier beat; its scene's sheets and mark frames, its boundary in `continuity.json`, the bounding boxes of its `run.log`; its scene's picked exemplars when a pack is present |

## Parent helpers

`lesson.json` has no command of its own, so the parent reaches `scripts/mtv/lesson.py`
through these lines, run from the directory that holds `scripts/` and `mtv-runs/` or with
the paths written out.

Validate, which prints `valid` or the schema errors:

```bash
PYTHONPATH=scripts python -c 'import sys; from pathlib import Path; from mtv import lesson; errors = lesson.validate(lesson.load(Path(sys.argv[1]))); print("\n".join(errors) or "valid"); sys.exit(1 if errors else 0)' <run>/lesson.json
```

Mark a stage (`brief`, `script`, `storyboard` or `scenes`) done:

```bash
PYTHONPATH=scripts python -c 'import sys; from pathlib import Path; from mtv import lesson; p = Path(sys.argv[1]); d = lesson.load(p); lesson.mark_done(d, sys.argv[2], {}); lesson.save(d, p)' <run>/lesson.json <stage>
```

Bump a counter, with a scene id for `render_retries`; it prints the new count:

```bash
PYTHONPATH=scripts python -c 'import sys; from pathlib import Path; from mtv import lesson; p = Path(sys.argv[1]); d = lesson.load(p); print(lesson.bump(d, *sys.argv[2:4])); lesson.save(d, p)' <run>/lesson.json <counter> [<scene>]
```

Words: each beat's words as `normalize_words` counts them, numbered from 0, which are the
indices a mark names. Run it with the same `python` as `narrate.py`, since a numeral counts
as its spoken words only where `num2words` is installed:

```bash
PYTHONPATH=scripts python -c 'import sys; from pathlib import Path; from mtv import common, lesson; [print(beat["id"], " ".join(f"{i}:{w}" for i, w in enumerate(common.normalize_words(beat["narration"])))) for _, beat in lesson.beats(lesson.load(Path(sys.argv[1])))]' <run>/lesson.json
```

Helper docs: the signature and docstring of each named helper, for a scene coder:

```bash
PYTHONPATH=scripts python -c 'import inspect, sys; from mtv import patterns; [print(f"{name}{inspect.signature(getattr(patterns, name))}\n{inspect.getdoc(getattr(patterns, name))}\n") for name in sys.argv[1:]]' <helper> [<helper> ...]
```

Earlier values: for a frame critic, each beat before scene `<id>` with its `shows_value_of`
and `symbol_introduced`, which value before symbol reads across the lesson as
`storyboard_check.py`'s R07 does; it prints `[]` for the first scene:

```bash
PYTHONPATH=scripts python -c 'import json, sys; from pathlib import Path; from mtv import lesson; d = lesson.load(Path(sys.argv[1])); ids = [s["id"] for s in d["scenes"]]; before = set(ids[:ids.index(sys.argv[2])]); print(json.dumps([{"beat": b["id"], "shows_value_of": b.get("shows_value_of", []), "symbol_introduced": b.get("symbol_introduced", [])} for s, b in lesson.beats(d) if s["id"] in before]))' <run>/lesson.json <id>
```

Storyboard critic: file the critic's scores in `checks.storyboard` after a passing
`storyboard_check.py` run, which rewrites that block, so every later run of the check, as in
step 7's pattern swap, is followed by filing them again:

```bash
PYTHONPATH=scripts python -c 'import json, sys; from pathlib import Path; from mtv import lesson; p = Path(sys.argv[1]); d = lesson.load(p); d["checks"]["storyboard"]["scores"] = json.loads(Path(sys.argv[2]).read_text())["scores"]; lesson.save(d, p)' <run>/lesson.json <run>/reviews/storyboard.json
```

Frame critic: file the returns and compute the final vector:

```bash
PYTHONPATH=scripts python - <run>/lesson.json <run>/reviews/s01.json <run>/reviews/s02.json <<'EOF'
import json, sys
from pathlib import Path
from mtv import lesson
path = Path(sys.argv[1])
data = lesson.load(path)
frames = data["checks"].get("frames") or {"scenes": {}}
for name in sys.argv[2:]:
    review = json.loads(Path(name).read_text())
    frames["scenes"][review["scene"]] = review
reviews = frames["scenes"].values()
frames["final"] = lesson.frames_final(reviews)
scores, zeros = frames["final"]["scores"], frames["final"]["zeros"]
data["checks"]["frames"] = frames
lesson.save(data, path)
print(f"final {sum(scores.values())}/32, zeros {zeros or 'none'}, pass {frames['final']['pass']}")
EOF
```

First stage to run, for a resume. At tier `draft` it skips `render.standard`, which step 9
never runs there, so a finished draft run prints `none`. The frame review and the fix loop
have no stage of their own; a printed stage after `frames` means steps 7 and 8 are finished
first, as Stop and resume says:

```bash
PYTHONPATH=scripts python -c 'import sys; from pathlib import Path; from mtv import lesson; d = lesson.load(Path(sys.argv[1])); print(next((s for s in lesson.STAGES if (s != "render.standard" or d["tier"] != "draft") and lesson.needs_rerun(d, s)), "none"))' <run>/lesson.json
```

Frame reviews owed, for a resume: each scene whose frame critic's return is not filed in
`checks.frames.scenes`, or was saved in `<run>/reviews/` before the scene's latest draft
render, as when a fix pass stopped between a re-render and the new review; it prints `none`
when every scene's return is current:

```bash
PYTHONPATH=scripts python -c 'import sys; from pathlib import Path; from mtv import lesson; p = Path(sys.argv[1]); d = lesson.load(p); filed = (d["checks"].get("frames") or {}).get("scenes") or {}; saved = lambda s: p.parent / "reviews" / (s["id"] + ".json"); drawn = lambda s: max((f.stat().st_mtime for f in (p.parent / "render" / "draft" / s["id"]).glob("*.mp4")), default=0); print(" ".join(s["id"] for s in d["scenes"] if s["id"] not in filed or not saved(s).exists() or saved(s).stat().st_mtime < drawn(s)) or "none")' <run>/lesson.json
```

## Stop and resume

Stop always means: write `<run>/report.md` naming the failing step and gate with its
findings, keep every artifact, and tell the user how to resume. After step 11 `verify.py`
has written the report; before it, the parent writes one in the same form, with the title,
the failing gate, the warnings so far, the `attempts` block and the resume line. Ask is not
a stop: the run waits for the user's answer.

To resume, rerun the skill in the same directory. The parent sets every `attempts` counter
back to 0, keeps the `stages` block, and starts at the first stage whose inputs have
changed since it was recorded, as the first-stage helper prints: each stage hashes the
`lesson.json` fields it reads, and from `render.draft` on the hash includes `lesson.py`, so
an edited scene renders again. The stages run in the order `brief`, `script`, `storyboard`,
`narrate`, `scenes`, `render.draft`, `frames`, `render.standard`, `assemble` and `verify`,
and every step after the first stale one runs again; a stale `render.draft` or `frames`
reruns step 7 in full, its frame critics included.

The frame review and the fix loop have no stage: `frames.py` marks `frames` before any
frame critic is dispatched, and nothing records step 8's gate. So when the first stage to
run comes after `frames` (`render.standard`, `assemble`, `verify` or `none`), finish steps 7
and 8 before it. Dispatch step 7's frame critic for each scene the frame-reviews-owed helper
prints, with its picks, and file the returns with the frame-critic helper. Then apply step
8, from its draft assemble and verify on, unless `checks.frames.final.pass` and
`checks.verify.pass` are both true, since `checks.verify` holds the last verify, of the
draft or of the delivery. Only then run the printed stage and the stages after it, so a
resume never skips the frame review or step 8's gate.
