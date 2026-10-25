# Architecture: repeatable process first

This is one of the candidate architectures for the `manim-teaching-video`
skill. Its angle is that the run-time process is the product: a topic goes in,
one finished MP4 comes out, and every step in between is deterministic,
inspectable, resumable and gated. The framework, pattern library and rubric
exist to make those gates checkable; they are not the deliverable on their
own. Evidence is cited as `map NN` (the seven design maps in
`scratchpad/design/maps/`) with the file and line references those maps
carry, or marked unverified.

## 1. Thesis

The design optimizes for **never shipping a bad video**, with "bad" defined
operationally and checked by code or by a subagent reading a fixed rubric,
before any expensive step runs. Three facts from the maps drive this choice.

1. 3Blue1Brown's own process is a human loop: write a beat, render a beat, look
   at it, fix it, then resolve narration timing in a video editor
   (map 03, sections 3 and 6: `checkpoint_paste()` keyed by a leading comment;
   `add_sound` never used for speech; `wait()` values hand-tuned). The agent
   has no window, no clipboard and no editor, so every one of those human
   checks must become a batch check with a pass or fail result.
2. Rendering is the slowest and most fragile step (map 04, performance traps:
   60 fps presets, LaTeX compile per formula, Cairo 3D cost), so the pipeline
   must catch script, storyboard, code and narration defects before the first
   frame renders, and must render cheaply (`-ql`, one section at a time) until
   the last gate.
3. Context is finite. The corpus analyses, framework, pattern library and
   rubric together will run to thousands of lines; no single agent may hold all
   of them. Each subagent gets exactly the slice it needs, and the parent
   orchestrator holds only the storyboard and the gate results.

Consequences: narration is synthesized before scene code is written, so timing
is a known input rather than a post-hoc edit; one `Scene` per storyboard
section and one `next_section` per beat, so failures are local and re-renders
are partial; every stage writes a file and a state record, so a run resumes
after a usage-limit cutoff without redoing work; quality is scored at three
points (storyboard, low-quality render, final render) and the run stops at the
first failed gate with a report the user can act on.

## 2. System overview

### 2.1 Components and data flow

```text
  DEVELOPMENT TIME (once, in the implementation session)

  3b1b/videos source ─┐
  site repo + bucket ─┼─► [A] corpus tools ─► corpus/ cache (gitignored)
  YouTube captions   ─┘            │
                                   ▼
                      [B] per-video analysis (subagents) ─► references/analyses/*.md
                                   │
                                   ▼
                      [C] framework synthesis ─► references/framework.md
                                                 references/patterns/**
                                                 references/rubric.md
                                                 references/manimce.md
                                   │
                                   ▼
                      [D] skill authoring (RED/GREEN) ─► SKILL.md, agents/mv-*, scripts/, evals/

  RUN TIME (every invocation)

  topic ─► G0 preflight ─► G1 script ─► G2 storyboard ─► G3 narration
        ─► G4 scene code (static checks) ─► G5 draft render + frame review
        ─► G6 final render ─► G7 assemble + verify ─► final.mp4 + report
```

### 2.2 Unit boundaries

Each unit has one input file set, one output file set and one way to test it
alone.

| Unit | Inputs | Outputs | Depends on | Tested alone by |
| --- | --- | --- | --- | --- |
| A. Corpus tools (`corpus_tools/` in a separate repo, section 3) | video id list, cloned source, site repo, bucket | `corpus/<id>/` with captions, word-timed transcript, keyframes, figures, `manifest.json` | yt-dlp, faster-whisper, ffmpeg, curl | `make smoke` on one short video; manifest hashes |
| B. Analysis (section 4) | `corpus/<id>/`, source files for that video | `references/analyses/<slug>.md` + `analyses/<slug>.json` | A | schema check script; spot-check of 10 percent of citations |
| C. Framework (section 5) | all analyses | `framework.md`, `rubric.md`, `patterns/`, `manimce.md` | B | every rule has a check; every pattern renders under ManimCE 0.22 |
| D. Skill (section 6) | C, kit contract (map 06) | `SKILL.md`, `agents/mv-*/agent.md`, `scripts/*.py`, `evals/` | C | `scripts/validate.sh`, sandbox install, eval suite |
| R1. Preflight (`scripts/preflight.py`) | environment | `run/preflight.json` | none | run in a container missing LaTeX; expect the exact fallback message |
| R2. Script stage | topic, `framework.md` | `run/script.md` | R1 | rubric section S scored by `mv-critic` |
| R3. Storyboard stage (`scripts/storyboard.py`) | `script.md`, `assets/storyboard.schema.json` | `run/storyboard.json` | R2 | JSON schema validation; budget arithmetic |
| R4. Narration (`scripts/narrate.py`) | `storyboard.json` | `run/narration/<beat>.wav`, `<beat>.words.json`, `narration.json` | R3, TTS provider | durations sum; words cover text; provider swap test |
| R5. Scene code (`scripts/scaffold.py`, `scripts/check.py`) | `storyboard.json`, `narration.json`, `patterns/` | `run/scenes/lesson.py`, `mtv_runtime.py`, `manim.cfg` | R4 | `check.py` static rules; `manim --dry_run` |
| R6. Render (`scripts/render.py`) | `lesson.py`, tier | `run/media/**`, `sections/*.json`, `run/render.json` | R5, ManimCE | one-beat fixture renders at `-ql` in under a minute |
| R7. Frame review (`scripts/frames.py` + `mv-frame-reviewer`) | section videos, `storyboard.json` | `run/review/frames/*.png`, `review.json` | R6 | fixture with a known off-screen label is caught |
| R8. Assemble and verify (`scripts/assemble.py`, `scripts/verify.py`) | sections, narration, SRT | `final.mp4`, `final.srt`, `run/report.json` | R6, ffmpeg | ffprobe stream and duration assertions |

The parent orchestrator (the agent running `SKILL.md`) owns `run/state.json`
and calls units in order; it never edits scene code itself and never pastes
subagent output (rules/subagents.md via map 06, section 4.1).

## 3. Corpus pipeline

### 3.1 Where it lives

Corpus tooling is development-time only and is not bundled in the skill. It
lives in its own small repository, `manim-corpus-tools` (MIT), with a
gitignored `corpus/` cache, because: the kit's hygiene gates run jscpd and
typos over every Python and text file (map 06, sections 3.3 and 3.4), machine
transcripts and figure sets are third-party material that must not enter the
kit (map 07, section 6), and the installer copies everything under
`skills/<id>/` into every consumer home (map 06, section 2.3). The kit
receives only the derived analyses (unit B) and a research note at
`docs/research/manim-teaching-video.md` that records how the corpus was built
and the manifest hashes, so it can be rebuilt.

### 3.2 Steps

All steps are idempotent: each writes into `corpus/<video_id>/` and skips
work whose output exists and matches `manifest.json`. `make all` runs them in
order; `make <step> VIDEO=<id>` runs one.

| Step | Tool | Input | Output | Idempotency key |
| --- | --- | --- | --- | --- |
| 1. `inventory` | Python, reads `app/data/topics.json` and lesson frontmatter from the sparse site clone (map 07, section 1) | site repo | `corpus/videos.json` (slug, title, YouTube id, date, source path, site chapter, YouTube chapter) | site HEAD hash |
| 2. `metadata` | `yt-dlp --skip-download --write-info-json --write-description --write-thumbnail --write-subs --write-auto-subs --sub-langs "en.*" --sub-format "json3/vtt" --js-runtimes node` (map 05, section 4; map 07, appendix B) | video id | `<id>.info.json`, captions | file exists and `yt-dlp --list-subs` unchanged |
| 3. `audio` | `yt-dlp -f bestaudio -x` | video id | `<id>.m4a` | sha256 in manifest |
| 4. `transcript` | faster-whisper `large-v3-turbo` int8, `word_timestamps=True`, `vad_filter=True`, `initial_prompt` with domain terms; fall back to `small.en` when the run exceeds its budget (map 05, section 4) | audio | `transcript.words.json`, `transcript.segments.json` | model name + audio hash |
| 5. `align_captions` | stable-ts `align()` of manual captions to audio when manual captions exist (map 05, section 4, "Best transcript") | captions + audio | `transcript.aligned.json` | both input hashes |
| 6. `figures` | curl against the public bucket XML listing, jpg only (map 07, section 2) | lesson prefix | `figures/*.jpg`, `figures.json` with the `<Figure>` caption each one sits next to in the MDX | listing ETag per object |
| 7. `video` | `yt-dlp -f "bv*[height<=1080]+ba/b[height<=1080]"` | video id | `<id>.mp4` | sha256 |
| 8. `keyframes` | PySceneDetect `AdaptiveDetector` plus one frame at each transcript segment midpoint, deduplicated within 1 s by perceptual hash, capped at 300, downscaled to 480p (map 05, section 5) | video + transcript | `frames/<t>.jpg`, `frames.json` | detector params + video hash |
| 9. `scenes` | Python `ast` walk over the source files named in frontmatter: class name, line span, base class, beat comments, string literals, `play`/`wait` counts (the method of map 01, appendix A) | source clone at commit `306a1346` | `scenes.json` | source commit |
| 10. `align_scenes` | monotonic DP alignment of `scenes.json` to transcript sections scored by string-literal hits, class-name similarity and figure bridge (map 07, section 4) | 4, 6, 8, 9 | `alignment.json` with per-link confidence | input hashes |
| 11. `anchors` | a reader (agent with frames and transcript open) fixes 3 to 6 low-confidence links per video; stored as `anchors.json`, then step 10 re-runs | 10 | `anchors.json` | manual, versioned |
| 12. `manifest` | sha256 of every artifact, tool versions, dates | all | `manifest.json` | always rewritten |

Steps 3, 7 and 8 are the ToS-sensitive ones (map 07, section 6). They are
behind an explicit `DOWNLOAD_MEDIA=1` flag; without it the corpus is captions,
figures, source and metadata only, which already supports steps 9 to 11
because the bucket figures are curated keyframes (245 `<Figure>` tags, map
07, section 2). Media files are deleted by `make clean-media` once keyframes
exist.

### 3.3 Running in a fresh session with network

```bash
GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 https://github.com/3b1b/videos $HOME/3b1b/videos
git clone --depth 1 --filter=blob:none --no-checkout https://github.com/3b1b/3Blue1Brown.com $HOME/3b1b/3Blue1Brown.com
python -m venv $HOME/.venvs/corpus && . $HOME/.venvs/corpus/bin/activate
pip install yt-dlp faster-whisper stable-ts scenedetect[opencv] imagehash
make inventory metadata figures scenes          # no media, no ToS exposure
DOWNLOAD_MEDIA=1 make audio transcript align_captions video keyframes
make align_scenes && make anchors VIDEO=aircAruvnKk && make manifest
```

Hosts to allow: `github.com`, `raw.githubusercontent.com`, `pypi.org`,
`files.pythonhosted.org`, `huggingface.co` (whisper and alignment models),
`storage.googleapis.com` (figures), and the YouTube hosts for steps 2, 3 and
7 (map 05, section 7). Expected volume: 150 to 250 MB audio, 1.7 to 4.5 GB
video if downloaded, 50 to 90 MB of 480p keyframes, 100 to 130 MB figures
(map 07, section 5). Budget: whisper `large-v3-turbo` on 4 CPUs is the slow
step; plan one to two hours for the 149 primary minutes and run it in the
background (map 05, section 4 extrapolation, low confidence).

### 3.4 Committed versus local

Committed to `manim-corpus-tools`: the scripts, `videos.json`, `anchors.json`,
`alignment.json`, `scenes.json`, `manifest.json` (hashes only), and
`figures.json` (object keys and caption paraphrases, no images). Committed to
the kit: `references/analyses/*` and the research note. Never committed
anywhere: media, frames, figures, verbatim captions or transcripts, article
text (map 07, section 5 "What to commit"; map 06, section 6).

## 4. Per-video analysis method

### 4.1 Who analyzes

One subagent per video section, not per video. A 20-minute video has 8 to 14
transcript sections after step 10; a spine scene such as
`SimplestNetworkExample` is 1,528 lines on its own (map 01, section 1.4), so
a per-video subagent would overflow its context. The parent fans out in waves
of 4 to 6 (rules/subagents.md batching, map 06, section 4.1). Each section
analyst receives only: the transcript paraphrase and time range for its
section, the aligned scene classes with their source line spans (it reads
those lines from the clone itself), the figure captions and keyframe paths in
its time range, the shared record schema, and the vocabulary of teaching
moves fixed in advance (hook, concrete, abstraction, formula, recap, aside,
meta, from map 01, section 1). A second, cheaper pass per video merges the
section records into `references/analyses/<slug>.md` and writes the
video-level fields.

### 4.2 Record schema

Stored as `references/analyses/<slug>.json` (machine) and rendered into
`<slug>.md` (human) by one script, so the two never disagree.

```json
{
  "lesson": "neural-networks",
  "video_id": "aircAruvnKk",
  "source_files": ["_2017/nn/part1.py"],
  "sections": [
    {
      "id": "s04",
      "t_start": 221.0,
      "t_end": 318.5,
      "narration_summary": "paraphrase, never verbatim",
      "teaching_move": "concrete_to_abstraction",
      "scenes": [{"class": "IntroduceEachLayer", "file": "_2017/nn/part1.py", "lines": [1036, 1335]}],
      "visual_nouns": ["network_diagram", "decimal_in_neuron", "pixel_grid"],
      "animation_idioms": [{"name": "staggered_reveal", "evidence": "part1.py:1047-1053"}],
      "color_roles": {"activation": "WHITE", "emphasis": "YELLOW"},
      "layout": "diagram bottom scaled 0.8, question text top",
      "pacing": {"plays": 25, "waits": 15, "wait_seconds": 15, "narration_wpm": 158},
      "why_it_works": ["number shown inside the neuron before the word activation is written"],
      "keyframes": ["frames/00231.4.jpg"],
      "figures": ["lessons/2017/neural-networks/layers.jpg"],
      "confidence": 0.8,
      "open_questions": []
    }
  ],
  "video_level": {
    "arc": ["hook", "working_demo", "name_taken_apart", "mechanics", "formula", "reframe", "handoff"],
    "color_contract": {"cost": "RED", "sigma": "YELLOW", "weights": "BLUE", "bias": "MAROON_B"},
    "object_budget_max": "about 200 edges after thinning, one image, one caption, one formula",
    "recap_devices": ["plan list dims done items"]
  }
}
```

### 4.3 Evidence grounding

Every `evidence` and `scenes` entry is a `file:line` or `file:lines` into the
clone at a named commit; every `keyframes` entry is a timestamp-named frame;
every `narration_summary` is a paraphrase. A validator
(`corpus_tools/check_analysis.py`) rejects records whose cited lines do not
contain the named class or idiom token, whose keyframe files do not exist in
the cache, or whose `narration_summary` shares a run of 12 or more words with
the transcript (verbatim leak). Alignment of transcript to code is the step 10
and 11 output; the analyst never guesses it, it only reads the aligned span.

### 4.4 Quality of the analyses

1. Schema and citation validation by script (above).
2. Adversarial refutation: for each video a second subagent receives the
   record and the same inputs and is told to find three claims that the cited
   lines do not support; a claim with a sustained refutation is deleted or
   re-cited.
3. Cross-video consistency: a script tabulates `color_roles`,
   `animation_idioms` names and `teaching_move` values across all records
   and flags singletons for review, so the vocabulary converges before
   synthesis.
4. Coverage: every aligned scene class with a `construct` and more than 20
   lines appears in exactly one section record; stubs, thumbnails, end screens
   and Pi-creature reaction scenes are tagged `interstitial` and summarized in
   one line each (map 03, section 4.3 `kind` field).

## 5. Framework representation

### 5.1 Files

All under `skills/manim-teaching-video/references/`, each linked one level
deep from `SKILL.md` (map 06, section 5.1):

| File | Lines (target) | Read by |
| --- | --- | --- |
| `framework.md` | 250 to 400 | `mv-scriptwriter`, `mv-storyboarder`, `mv-critic` |
| `rubric.md` | 150 to 250 | `mv-critic`, `mv-frame-reviewer`, parent at gates |
| `manimce.md` | 300 to 450 | `mv-scene-coder` only |
| `patterns/README.md` (index) | 80 to 120 | `mv-scene-coder` |
| `patterns/<name>.md` + `patterns/<name>.py` | 40 to 120 each | `mv-scene-coder`, fetched by name |
| `narration.md` | 80 to 150 | `mv-scriptwriter`, parent |
| `analyses/<slug>.md` | 200 to 400 each | nobody at run time by default; `mv-scriptwriter` may fetch one section on request |
| `attribution.md` | 20 | linked from `framework.md` header |

### 5.2 How rules are phrased

Every rule has four parts so an agent can both apply and check it:

```text
R-07 Numbers before symbols
  Apply: the first appearance of any quantity is a concrete value on screen
         (DecimalNumber in or beside the object); the symbol is introduced by
         a transform from that value, never before it.
  Check: storyboard.json: for each `symbol_introduced`, an earlier or same
         beat in the same section has `shows_value_of` the same concept.
         Scored by scripts/storyboard.py (static) and rubric item Q3.
  Why:   activations are decimals inside circles before "activation" is
         written; the cost is (0.00 - 0.00)^2 of on-screen decimals before
         C(w) (map 01, section 8, move 4).
  Fails: a storyboard whose first beat writes `a = sigma(Wx + b)`.
```

Rule ids are stable (`R-NN`), each cites the analyses it derives from, and
`rubric.md` items reference rules by id, so a failed rubric item points at
the rule text. Roughly 25 to 35 rules are expected from the maps: structure
(working thing first, preview then hide, plan list dims done items), objects
(one helper per visual noun, object budget, role colors introduced once),
motion (motion with a reason, dim do not delete, provenance by transform,
light the path then release), pacing (2 s default run time, 1 s wait after
most plays, 2 s wait closing a step, holds for contemplation), honesty (say
what you do not know, admit what is skipped, count the parameters), and
narration (one beat per sentence group, visual lands on the noun it names).
Sources: map 01 section 8 (16 moves), map 02 sections 6.3 and 8 (8 patterns,
14 moves), map 03 section 8.

### 5.3 Pattern library

Original ManimCE 0.22.0 idioms, one directory per pattern, each with a
`.md` (when to use, the 3b1b move it serves with citation, parameters,
gotchas) and a `.py` that renders standalone under `manim -ql`. Target 24
patterns in four groups, derived from the counts in map 04 and the visual
nouns in maps 01 and 02:

1. Nouns (8): `network_diagram` (layer sizes, thinning, activation fill,
   decimal readouts), `vector_column` (bracketed decimals colored by sign),
   `weight_matrix` (sign-colored entries with ellipsis row and column),
   `token_tape`, `attention_grid`, `bar_distribution`, `graph_with_dot`
   (axes, plot, tracked dot, tangent), `plan_list` (dims done items).
2. Moves (9): `focus_and_dim`, `provenance_transform`
   (`TransformFromCopy` and `ReplacementTransform` from object to symbol),
   `formula_build` (`MathTex` with `substrings_to_isolate`, parts flying in
   from referents), `signal_flash` (`ShowPassingFlash` on a thickened copy),
   `staggered_reveal` (`LaggedStartMap` with `lag_ratio` 0.05 to 0.5),
   `nudge_and_return` (`there_and_back`, `wiggle`), `count_in`
   (`ChangeDecimalToValue` with brace), `camera_zoom`
   (`MovingCameraScene` save and `Restore`), `montage` (sub-second waits).
3. Layout (4): `diagram_low_text_high`, `caption_with_arrow`,
   `split_screen`, `region_box` (`SurroundingRectangle` in `PURE_YELLOW`,
   removed before the next idea).
4. Infrastructure (3): `narrated_scene` (the `NarratedScene` base and
   `beat()` context manager, section 7), `tex_template` (the preamble
   additions `dsfont`, `mathrsfs`, `physics`, `xcolor`; map 03, section 1.3),
   `palette` (`PURE_YELLOW` for 3b1b yellow, `BLUE_E` override, role color
   map; map 04 constants table).

Each `.py` is exercised by `scripts/selftest.py --patterns` when ManimCE is
installed; a pattern that fails to render blocks the PR. No 3D pattern in the
first version (section 12).

### 5.4 Rubric

`rubric.md` has 18 items in three groups, each with a 0 to 2 score, the rule
it checks, who scores it and when:

| Group | Items (examples) | Scorer | Gate |
| --- | --- | --- | --- |
| S. Script and storyboard (7) | hook before definition; working example before formula; one new idea per section; every symbol has a value first; parameter count or scale shown; honesty beat present; recap carries the picture forward | `mv-critic` on `storyboard.json` | G2 |
| V. Visual (7) | role colors consistent; object budget respected; focus dimmed not deleted; captions adjacent to referents; nothing clipped at frame edge; text legible at 480p; motion direction matches data flow | `mv-frame-reviewer` on frames, plus `check.py` for colors and `frames.py` bounding boxes | G5 |
| N. Narration and sync (4) | each beat's named visual is on screen within 0.5 s of the word; no beat where the screen is static for more than 6 s of speech; total drift under 1 frame per section; speech rate 140 to 170 words per minute | `verify.py` plus `mv-frame-reviewer` at bookmark frames | G7 |

Pass bar: no item scores 0; group means at least 1.5; the three objective
checks (clipping, drift, stream presence) are hard failures regardless of
score. The bar is a decision for the user (section 13).

### 5.5 Context budgets and progressive disclosure

`SKILL.md` stays an orchestrator of about 1,500 words (map 06, section 4.1).
It links `framework.md`, `rubric.md`, `narration.md`, `manimce.md` and
`patterns/README.md`; the analyses are linked but marked "fetch one section
only when a storyboard needs a precedent". Subagent prompts name the exact
files to read and forbid the rest. The scene coder gets the pattern index and
is told to open at most the five patterns the storyboard section lists under
`patterns_used`. `manimce.md` carries the translation rows that matter for
generated code (the GL names that do not exist in CE, the `Tex`/`MathTex`
swap, `PURE_YELLOW`, the runtime error table from map 04) and nothing about
corpus history.

## 6. Skill design

### 6.1 SKILL.md outline

```text
---
compatibility: Requires Python 3.11+, ManimCE 0.22, ffmpeg, a LaTeX
  distribution or the typst extra, and a narration provider (Kokoro default)
description: >-
  Produces a narrated 3Blue1Brown-style teaching video with Manim Community
  Edition from a topic: script, storyboard, synthesized narration, synced
  animation, verified MP4. Use when asked to make, render or animate an
  explainer, lesson, math video, teaching video or Manim video.
enabled: true
id: manim-teaching-video
name: manim-teaching-video
---
# Manim Teaching Video (gated pipeline)
## 0. Triage and the run directory (say the tier and output dir out loud)
## 1. Preflight (python scripts/preflight.py; stop on hard failures)
## 2. Script (dispatch mv-scriptwriter; gate G1)
## 3. Storyboard (dispatch mv-storyboarder; scripts/storyboard.py; mv-critic; gate G2)
## 4. Narration (python scripts/narrate.py; gate G3)
## 5. Scene code (dispatch mv-scene-coder per section; scripts/check.py; gate G4)
## 6. Draft render and frame review (scripts/render.py --tier draft; mv-frame-reviewer; gate G5)
## 7. Final render (scripts/render.py --tier <final>; gate G6)
## 8. Assemble and verify (scripts/assemble.py; scripts/verify.py; gate G7)
## 9. Report (text template)
## Roster (table of mv-* agents, what each reads, what it returns)
## Resuming a run (state.json)
## Guardrails / Scope boundaries / Communication style
```

### 6.2 Run directory and state

Every run writes to `<cwd>/mtv/<slug>/` (the user may override). The
directory is the only state; `state.json` records the last passed gate, the
tier, hashes of every stage input, and tool versions. A re-invocation with
the same topic resumes at the first stage whose inputs changed. Nothing is
committed by the skill; git is left to the user (rules/git-worktrees.md via
map 06, section 8).

```text
mtv/<slug>/
  state.json  preflight.json  brief.md  script.md  storyboard.json
  narration/<beat>.wav  narration/<beat>.words.json  narration.json
  scenes/lesson.py  scenes/mtv_runtime.py  scenes/manim.cfg  scenes/media/
  review/frames/*.png  review/review.json  review/critic-G2.json
  final.mp4  final.srt  report.json  render.log
```

### 6.3 The process, stage by stage

1. **Triage.** The parent states the tier (`draft`, `standard`, `uhd`), the
   target length (default 4 to 8 minutes; ask if the topic implies more than
   12), the audience line, and the run directory. It asks the user exactly
   two questions when the topic alone does not answer them: audience level
   and target length. Everything else has a default.
2. **G0 Preflight.** `python scripts/preflight.py --json` checks: Python
   version; `manim --version` is 0.22.x (warn on other 0.2x, stop below
   0.19); `latex` and `dvisvgm` present, else whether `typst` is importable;
   ffmpeg present (ManimCE 0.19+ encodes with PyAV, but assembly uses ffmpeg;
   map 04 features); the narration provider imports and can synthesize one
   word; fonts list contains the configured font or falls back to Pango
   default with a note; free disk; CPU count. Output decides the math engine
   (`mathtex`, `typst`, `text_only`) and the render-time estimate constants.
3. **G1 Script.** `mv-scriptwriter` receives the brief, `framework.md`,
   `narration.md` and the length budget; returns `script.md`: sections with
   titles, each a list of beats, each beat a narration paragraph of 1 to 3
   sentences (15 to 45 words) and a one-line "what is on screen". The parent
   checks word count against the length budget at 150 words per minute and
   loops once if off by more than 20 percent.
4. **G2 Storyboard.** `mv-storyboarder` turns `script.md` into
   `storyboard.json` (schema below). `python scripts/storyboard.py --check`
   validates the schema, the static rule checks (section 5.2), that each
   section lists at most two visual nouns new to the video, that
   `patterns_used` names exist, and that the math engine is compatible with
   the formulas used. `mv-critic` scores group S. Fail: the storyboard goes
   back with the critic's findings, at most two rounds, then the parent asks
   the user.
5. **G3 Narration.** `python scripts/narrate.py storyboard.json` synthesizes
   one WAV per beat and a `words.json` with word start and end times
   (section 7), writes `narration.json` with per-beat durations, and checks:
   no beat shorter than 1.5 s or longer than 45 s, every bookmark word found,
   total duration within the length budget. Narration is cached by
   `sha256(provider, voice, text)` so an edited beat re-synthesizes alone.
6. **G4 Scene code.** `python scripts/scaffold.py` emits `lesson.py` with one
   `NarratedScene` subclass per section, a `beat()` block per beat already
   carrying the beat id, audio path and duration, `SCENES_IN_ORDER`, and the
   `manim.cfg` for the tier; it copies `mtv_runtime.py` beside it. Then one
   `mv-scene-coder` per section (waves of 4) fills the beat bodies using only
   the listed patterns and `manimce.md`. `python scripts/check.py lesson.py`
   runs the static gate: AST parse; no `manimlib` import and no GL-only names
   (`ShowCreation`, `set_backstroke`, `fix_in_frame`, `reorient`, `get_grid`,
   `replicate`, `time_span`, from map 04); every beat id present once and in
   storyboard order; no hard-coded `wait()` inside a beat (the runtime pads);
   role colors from the storyboard's `color_contract` used, `YELLOW` replaced
   by `PURE_YELLOW`; no `MathTex` when the engine is `text_only`; then
   `manim --dry_run` per scene to catch LaTeX and construction errors without
   frames. Failures go back to the owning coder with the error table row
   (map 04, runtime errors), at most three attempts per section.
7. **G5 Draft render and frame review.** `python scripts/render.py --tier
   draft` renders every scene at 854x480, 15 fps, `--save_sections`,
   `--disable_caching` off (caching helps re-renders), and parses each
   `<Scene>.json` section index. `python scripts/frames.py` extracts the last
   frame of each beat plus one frame at each bookmark time, and reads a
   bounding-box log the runtime writes at the end of each beat (every mobject
   in `self.mobjects` must lie inside the frame with a 0.2 unit margin).
   `mv-frame-reviewer` receives the frames for one section at a time with
   the beat's narration text and scores group V; it is told to read images
   and to answer per frame "is the thing the narration names on screen and
   legible". Fail: section-local fixes by the coder, re-render that scene
   only (one scene per section makes this cheap).
8. **G6 Final render.** Same command at the chosen tier. `standard` is
   1920x1080 at 30 fps (3b1b uses 30 fps; map 03, section 1.1); `uhd` is
   3840x2160 at 30 fps and is opt-in. The render runs in the background
   with progress parsed from the log; the parent checks in rather than
   waiting.
9. **G7 Assemble and verify.** `python scripts/assemble.py` concatenates the
   section videos in `SCENES_IN_ORDER` with the ffmpeg concat demuxer, builds
   the narration track by placing each beat WAV at its section start,
   normalizes to -16 LUFS with two-pass `loudnorm`, muxes AAC 192k, writes
   `final.srt` from the storyboard text and narration timings (map 05,
   section 6). `python scripts/verify.py` asserts: one video and one audio
   stream; container duration equals the sum of section durations within one
   frame; per-section drift between narration and video under one frame;
   resolution and fps match the tier; `final.srt` cue count equals the beat
   count; file size plausible. It writes `report.json` with every gate result
   and rubric score.
10. **Report.** The parent returns the text template: output path, duration,
    tier, rubric scores per group, the two lowest-scoring items with the
    rule ids, and anything the user was asked or should know (for example
    "math engine fell back to Typst because LaTeX was missing").

### 6.4 Storyboard schema (the contract every stage reads)

```json
{
  "slug": "what-is-a-derivative",
  "title": "What is a derivative?",
  "audience": "first-year calculus",
  "length_budget_s": 360,
  "math_engine": "mathtex",
  "color_contract": {"slope": "PURE_YELLOW", "function": "BLUE", "dx": "GREEN"},
  "sections": [
    {
      "id": "s01",
      "title": "A car and its speedometer",
      "scene_class": "S01Speedometer",
      "patterns_used": ["graph_with_dot", "caption_with_arrow", "count_in"],
      "beats": [
        {
          "id": "s01b01",
          "narration": "Before any formula, look at a car moving along a road.",
          "on_screen": "road line, car dot moving right, distance readout counting",
          "introduces": ["distance"],
          "shows_value_of": ["distance"],
          "symbol_introduced": [],
          "bookmarks": {"formula": 3, "readout": 9},
          "sync": {"readout": "distance readout visible"}
        }
      ]
    }
  ]
}
```

`bookmarks` map a name to a word index in `narration`; `sync` names the
visual that must be on screen at that word, which is what the frame reviewer
checks. `scripts/storyboard.py` is the single reader of this schema for
validation; `scaffold.py`, `narrate.py` and `verify.py` import it from
`scripts/common.py` so there is one parser.

### 6.5 Verification loops

| Loop | Trigger | Who fixes | Bound | Escalation |
| --- | --- | --- | --- | --- |
| Script length | words outside 20 percent of budget | `mv-scriptwriter` | 1 retry | ask user for a length |
| Storyboard rules and group S | `storyboard.py --check` or critic item at 0 | `mv-storyboarder` | 2 rounds | show the user the failing items and ask |
| Narration | missing bookmark word, beat too long or short | `mv-scriptwriter` rewrites that beat | 2 rounds | switch provider or ask |
| Static code | `check.py` or `--dry_run` failure | owning `mv-scene-coder` with the error row | 3 attempts per section | parent replaces the section's patterns with simpler ones and retries once, else stops |
| Draft frames and group V | clipped mobject, illegible text, item at 0 | owning coder | 2 rounds per section | drop the beat's optional visual noun, re-run; else stop |
| Final verify | any assertion | `assemble.py` rerun once; else coder for the section with drift | 1 | stop; never deliver a file that failed `verify.py` |

"Stop" always means: write `report.json` with the failing gate, keep every
artifact, and tell the user how to resume (`state.json` makes the next
invocation start at that gate).

### 6.6 Error handling

- **Render failures.** Exceptions are matched against the error table in
  `manimce.md` (map 04) by regex; the matching row's fix text is included in
  the coder's retry prompt. Unknown errors are quoted verbatim. Each scene is
  rendered in its own `manim` process so one failure never loses other
  sections' cached partial movies.
- **LaTeX missing.** Decided at G0, before any content exists. Order of
  preference: `mathtex`; `typst` when `manim[typst]` imports (map 04, text
  section); `text_only`, which forbids `MathTex`, `DecimalNumber`,
  `Matrix`, `NumberLine(include_numbers=True)` and `Brace.get_text` (the list
  of LaTeX-dependent classes in map 04) and makes the storyboarder use
  `Text` and the `vector_column` pattern's `Text` variant. The report names
  the engine used. The skill never installs TeX Live on its own; it prints
  the install line.
- **TTS or network failures.** `narrate.py` retries a provider three times
  with backoff; on persistent failure it tries the next provider in the
  configured chain (default `kokoro` then `piper`), and if the chain is
  exhausted it stops at G3. A silent video is never produced. Cloud
  providers read keys from the environment only (README line 128 via map 06).
- **Long renders.** `render.py` estimates frames as `fps * total_seconds`
  and warns when the estimate exceeds the tier's budget (draft 5 minutes,
  standard 40 minutes, uhd 3 hours on 4 CPUs; these constants are
  calibration targets, unverified until measured). Renders run in the
  background; the log is tailed for progress; a hung process (no log line for
  10 minutes) is killed and the scene retried once with `--disable_caching`.
- **Usage limit or interruption.** Every stage writes before it returns; the
  next invocation reads `state.json` and resumes. Narration and partial-movie
  caches survive.

### 6.7 Render-time budget and quality tiers

| Tier | Resolution and fps | When | Frame estimate for 6 minutes |
| --- | --- | --- | --- |
| `draft` | 854x480 at 15 | G5 frame review, evals | 5,400 frames |
| `standard` (default final) | 1920x1080 at 30 | G6 | 10,800 frames |
| `uhd` | 3840x2160 at 30 | user opt-in | 10,800 frames at 4 times the pixels |

The 60 fps presets are never used (map 04, quality flags). `manim.cfg`
written by `scaffold.py` sets `pixel_width`, `pixel_height`, `frame_rate`,
`background_color = BLACK`, `save_sections = True`, `max_inflight_encoders =
4` and `format = mp4`, so the CLI only varies the output directory.

### 6.8 What the skill asks the user and when

Before G1: audience and length if not inferable; the tier if the user has not
said. At a stopped gate: the failing items and a choice (retry with a simpler
storyboard, change engine or provider, accept and continue). Never during
rendering. Never for API keys (it reads the environment and reports which
provider it selected).

## 7. Narration and sync

### 7.1 Provider

Default **Kokoro-82M** (`kokoro` package, Apache-2.0 weights, offline,
24 kHz, per-token `start_ts` and `end_ts` from `KPipeline.join_timestamps`;
map 05, section 2). Stated assumption: voice `af_heart`, speed 1.0, Python
3.11 or 3.12 from PyPI, GitHub install on 3.13 (the PyPI wheel declares
`<3.13`; map 05). Fallback **Piper** (`piper-tts`, GPL used as a subprocess,
phoneme alignments aggregated to words). Premium **ElevenLabs** through
`convert_with_timestamps` (character-level `alignment` and
`normalized_alignment`; map 05, section 2), key from `ELEVENLABS_API_KEY`.
Alternate **OpenAI `gpt-4o-mini-tts`**, which returns no timestamps, so the
forced-alignment path below is mandatory for it. edge-tts and gTTS are not
offered as defaults (terms of use and undocumented endpoints; map 05).

Provider interface in `scripts/narrate.py`:

```python
class Provider(Protocol):
    name: str
    def synthesize(self, text: str, out_wav: Path) -> list[Word]: ...
    # Word = (text, start_s, end_s); an empty list means "no native timing"
```

### 7.2 Alignment

1. Native timestamps from the provider when present (Kokoro, ElevenLabs,
   Azure if added later).
2. Otherwise forced alignment of the known script text with
   `torchaudio.functional.forced_align` and `WAV2VEC2_ASR_BASE_960H` after
   number spelling and symbol stripping, or stable-ts `align()` when a
   whisper model is already installed (map 05, section 3). Never
   transcription of the synthesized audio as the primary source.
3. Fallback proportional interpolation only when alignment fails, with a
   warning carried into `report.json` and rubric item N1 capped at 1.

`words.json` is the only timing artifact the scene runtime reads, so the
provider is invisible to scene code.

### 7.3 Runtime helper instead of manim-voiceover

`mtv_runtime.py` (about 120 lines, bundled, copied beside `lesson.py`)
provides:

```python
class NarratedScene(Scene):
    def beat(self, beat_id):           # context manager
        # next_section(beat_id); add_sound(wav); remember start time;
        # on exit: wait(remaining) so the section lasts exactly the audio;
        # write bounding-box log line for frames.py
    def until(self, mark):             # wait until the bookmark word starts
    def remaining(self, buff=0.0):     # seconds left in the beat's audio
```

Reasons not to depend on manim-voiceover (map 05, section 1): a single
maintainer with stale service pins (`elevenlabs<0.3`, `openai<2`), bookmark
timing by whisper transcription plus interpolation, a PyTorch-plus-whisper
requirement for timing the default provider already gives, a lock file on
ManimCE 0.20.1 against our 0.22.0 target, and reliance on renderer internals
(`renderer.time`, `_original_skipping_status`) across the 0.22 `Manager`
refactor. The `voiceover()` and `<bookmark/>` ergonomics are kept in spirit
(`beat()` and `until()`), which is what the design borrows under MIT.

### 7.4 Sync rules enforced

Narration-first: the beat's audio length is the beat's duration budget;
animations inside consume their natural `run_time` and the runtime pads the
rest (map 03, section 6 implication). `check.py` rejects a beat whose declared
`run_time`s sum to more than the audio length minus 0.3 s, so a beat can never
run long and shift later beats. `verify.py` compares the section JSON
durations to `narration.json` and fails above one frame of drift.

## 8. Testing strategy

### 8.1 Scripts

- `python scripts/selftest.py` runs without ManimCE: schema validation of
  three fixture storyboards (one valid, one with a rule violation, one with a
  bad bookmark), `check.py` against a fixture `lesson.py` containing every
  banned GL name, `assemble.py` and `verify.py` against two 1-second
  synthetic section videos and a tone WAV generated with ffmpeg, and
  `narrate.py` with a `null` provider that writes silence and evenly spaced
  words. With ManimCE present it adds `--patterns` (every pattern renders at
  `-ql`) and `--one-beat` (a one-section, one-beat lesson renders, assembles
  and verifies end to end in under two minutes).
- The kit has no Python gate (map 06, section 3.10); the implementation
  session runs `selftest.py` before every commit, and the PR description
  records the output. Shared code lives in `scripts/common.py` so jscpd's
  5 percent threshold is not tripped by repeated argparse or ffprobe blocks.

### 8.2 Framework

A conformance eval, run before the skill exists: give a subagent one
storyboard section, `framework.md`, `manimce.md` and the listed patterns, ask
for the scene code, run `check.py` and a draft render, score with
`mv-critic` and `mv-frame-reviewer`. Repeat on five sections drawn from
different test topics. Pass: all five pass `check.py` within three attempts
and no rubric item scores 0. If a rule is violated in three of five runs, the
rule text or its check is rewritten before skill authoring begins.

### 8.3 Skill

Following the superpowers writing-skills method and the skill-creator eval
layout as combined in map 06, section 5.3:

1. **Fixed prompt set** in `evals/`: `derivative-intro` (calculus, formulas),
   `bayes-rule` (probability, numbers before symbols), `binary-search`
   (computer science, no LaTeX needed), `springs-and-oscillation` (physics,
   graphs), `fourier-idea` (hard, long), `how-vaccines-train-immunity`
   (non-math, tests that the framework is not formula-bound). Each
   `prompt.md` is a one-line user request plus the settings block; each
   `case.yaml` names the expected outcome; graders are objective where
   possible: `ffprobe` shows one video and one audio stream; duration within
   10 percent of the requested length; no `manimlib` import; section count
   equals storyboard section count; `report.json` present with all gates
   passed; and one LLM grader applying `rubric.md` with the floor from
   section 5.4.
2. **Pressure scenarios** for the three discipline rules: "the user is in a
   hurry, skip the storyboard review and render now"; "LaTeX is missing,
   just use plain text everywhere and do not mention it"; "the narration is
   two seconds longer than the video, ship it, nobody will notice". Pass is
   compliance with the gate, citing the skill, under three combined pressures.
3. **RED baseline**: the six prompts and three scenarios run as subagents
   without the skill; failures recorded verbatim in the gitignored
   `manim-teaching-video-workspace/iteration-0/`.
4. **GREEN**: minimal `SKILL.md`, references and scripts that address the
   recorded failures; with-skill and without-skill runs in the same turn;
   grade, aggregate, static viewer.
5. **Pass definition** for the skill: all six prompts pass every objective
   grader; the LLM rubric grader passes on at least five; the baseline fails
   at least one objective grader on at least four of six (otherwise the skill
   adds nothing measurable); all three pressure scenarios pass.
6. **Description optimization** with skill-creator's `run_loop.py` from a
   scratch project, then re-check against the kit contract (third person,
   no angle brackets, no workflow summary, sorted keys).

## 9. Repo layout inside the kit and required kit changes

### 9.1 Layout

```text
skills/manim-teaching-video/
  SKILL.md
  references/
    framework.md  rubric.md  manimce.md  narration.md  attribution.md
    patterns/README.md  patterns/<name>.md  patterns/<name>.py
    analyses/<slug>.md  analyses/<slug>.json
  scripts/
    common.py  preflight.py  storyboard.py  narrate.py  scaffold.py
    check.py  render.py  frames.py  assemble.py  verify.py  selftest.py
    mtv_runtime.py  providers/{kokoro,piper,elevenlabs,openai,null}.py
  assets/
    storyboard.schema.json  manim.cfg.template  tex_template.tex
    fixtures/ (three storyboards, one lesson.py, generated at selftest)
  evals/
    <case>/prompt.md  <case>/case.yaml  <case>/graders/NN-*.md
agents/
  mv-scriptwriter/agent.md  mv-storyboarder/agent.md
  mv-scene-coder/agent.md  mv-critic/agent.md  mv-frame-reviewer/agent.md
docs/research/manim-teaching-video.md
docs/adr/0008-skills-may-ship-scripts.md
docs/adr/0009-corpora-are-studied-not-vendored.md
```

File names stay within `[A-Za-z0-9._/-]` so the installer stamp tracks them
(map 06, section 2.3). Skill markdown never contains a bare absolute path,
a `~/` path, `${VAR}/`, a shebang in a fence, or `> /dev/null` (the
`SLASH_REF` rules in map 06, section 1.4); paths are relative to the run
directory or use `$HOME`.

### 9.2 Kit changes

1. `scripts/install.sh`: replace the `*.md`-only `find` with one that ships
   every regular file except `SKILL.md`, `evals/`, `__pycache__` and `*.pyc`
   (the one-expression change in map 06, section 2.2), tab-indented for
   `shfmt`.
2. `scripts/validate.sh`: exclude `evals` from the markdown reference scan
   and extend `AGENT_REF` to `(?:cr|mv)-[a-z][a-z-]*` so the five new agent
   ids are validated (map 06, sections 2.2 and 4.2).
3. `.github/workflows/validate.yml`: add `test -f` smoke lines for
   `skills/manim-teaching-video/skill.md`, `scripts/common.py` and
   `references/framework.md` in the sandbox install.
4. `README.md`: skills count, the agents table (five `mv-` rows), install
   note that skills may ship scripts.
5. `CHANGELOG.md`: an `Unreleased` entry in the existing style.
6. `docs/adr/0008` and `0009` in the kit's one-paragraph ADR voice (map 06,
   section 7).
7. `.gitignore`: `manim-teaching-video-workspace/`, `mtv/`, `media/`.
8. `CONTEXT.md`: add "Beat", "Section", "Tier", "Gate" to the vocabulary.

All of this lands from one worktree at `$HOME/worktrees/.agents/<branch>`
(rules/git-worktrees.md via map 06, section 8).

## 10. Phasing and milestones

Effort is in focused agent-session days with the network open; each
milestone ends with a committed artifact and a stated proof.

| M | Deliverable | Effort | Proves |
| --- | --- | --- | --- |
| M0 | Environment: ManimCE 0.22 installed, LaTeX or Typst, Kokoro synthesizes one sentence with timestamps, `preflight.py` passes; measured render time for a 30 s two-formula scene at each tier | 1 day | the budget constants in section 6.7 are real numbers, not guesses |
| M1 | `manim-corpus-tools` repo; corpus built without media for all eight videos; with media for two (chapter 1 and attention) | 2 days | the pipeline is idempotent and the ToS-free path yields usable keyframes (figures) |
| M2 | Eight analysis records validated by `check_analysis.py`, refuted once each | 3 to 4 days | records are evidence-grounded (zero unsupported citations after refutation) |
| M3 | `framework.md` (rules with checks), `rubric.md`, 24 patterns rendering under `selftest.py --patterns`, `manimce.md` | 3 to 4 days | every rule is checkable; every pattern is original and renders |
| M4 | Runtime scripts and `mtv_runtime.py`; `selftest.py --one-beat` passes end to end; framework conformance eval (section 8.2) | 3 to 4 days | a beat goes from storyboard to verified MP4 with sync under one frame |
| M5 | RED baselines, `SKILL.md`, five agents, evals, GREEN run | 3 to 4 days | the skill measurably beats the baseline on the fixed prompt set |
| M6 | REFACTOR, description optimization, pressure-scenario hardening | 2 days | discipline rules hold under pressure; description triggers correctly |
| M7 | Kit integration: installer and validator changes, README, CHANGELOG, ADRs, all hygiene gates, PR | 1 day | the kit ships the skill intact to a sandbox home |

Total: roughly 19 to 24 session days. M0 and M1 can run in parallel; M3
cannot start before M2 has at least four records.

## 11. Risks and mitigations

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| ManimCE API skew between training data and 0.22 (names removed in 0.22, `MathTex` rewrite in 0.20, PyAV encoding since 0.19; map 04) | high | render failures | pin 0.22 in `compatibility`; `check.py` bans GL names; `manimce.md` error table; `--dry_run` before frames |
| LaTeX absent on the consumer machine (map 04, what breaks without LaTeX) | high | half the mobject vocabulary unusable | G0 decides the engine before content exists; `text_only` variants of number-bearing patterns; report states the engine |
| Kokoro Python constraint (`<3.13` on PyPI) and unmeasured CPU speed (map 05) | medium | no default voice | GitHub install path documented; Piper fallback; M0 measures real-time factor |
| LLM judge inconsistency on rubric scores | medium | false passes or flaky fails | objective checks are hard gates independent of the judge; two-judge agreement on G2 for `standard` and `uhd`; rubric items phrased as observable predicates |
| Frame review misses visual defects a human would catch | medium | ugly but passing video | bounding-box log is code, not vision; frames at bookmark times (where it matters most); `draft` tier always reviewed before final |
| Render time on 4 CPUs exceeds patience | medium | abandoned runs | tiers; background renders; one scene per process; caching; estimates printed before G6 |
| Context overflow in scene coders on long sections | medium | truncated or wrong code | storyboard caps a section at 8 beats and 2 new nouns; coders get one section and at most five patterns |
| License leakage (his code or transcript text in references) | low | legal and project-decision breach | analyses store paraphrases; `check_analysis.py` 12-word overlap test; patterns are written from rule text, never from his scenes; attribution file |
| YouTube terms of service for media download (map 07, section 6) | medium | reputational | `DOWNLOAD_MEDIA` opt-in; figures and captions path sufficient for analysis; media deleted after keyframes |
| manim-voiceover drift, if someone adds it later | low | breakage | not a dependency; `mtv_runtime.py` owns timing |
| Hygiene gates reject bundled Python or fixtures (jscpd 5 percent, typos on identifiers) | medium | blocked PR | one `common.py`; fixtures generated at test time, not committed; run the pinned tools locally before the PR |
| Pi-creature "learner objection" beat has no asset | certain | lost pacing device | an original text-callout pattern (`aside_card`) carries the objection as a quoted question in a box; narration carries the pause |
| Documentation sites blocked in the design container, so CE and provider claims are source-read | certain for now | unverified details | M0 re-verifies every cited CE flag against docs with the network open; `report.json` records tool versions |

## 12. Deliberately cut

1. **3D scenes and camera orbits** in the first version. 3b1b's 2024 style
   leans on `reorient` and `fix_in_frame` (map 02, section 4.2), but CE's
   Cairo 3D is slow and the angle conventions are unverified (map 04). 2D
   with `MovingCameraScene` zooms covers the 2017 series entirely.
2. **Pi creatures, logo, end screens, thumbnails, opening quotes.** Brand
   assets that are not public (map 03, section 2); the pacing role is
   carried by narration and one callout pattern.
3. **manim-voiceover dependency** (section 7.3).
4. **OpenGL renderer and live preview.** No window exists for an agent
   (map 03, section 3.5).
5. **A two-track main-plus-supplements layout and a video editor.** One
   module, one order list, ffmpeg concat (map 03, section 4.3).
6. **Real-model data at run time** (tokenizers, GloVe, GPT-2). Values are
   synthetic and seeded with a documented hook, as the 2026 code does (map
   02, section 11.5).
7. **OCR and CLIP alignment of keyframes.** String literals, class names,
   figure bridge and 3 to 6 manual anchors per video are enough (map 07,
   section 4).
8. **Music, sound effects, chapters metadata, multiple languages, burned-in
   subtitles by default.** `final.srt` is produced; burn-in is one documented
   ffmpeg line, not a stage.
9. **A GUI eval viewer or dashboard.** The static viewer from skill-creator
   suffices.
10. **Adding Python lint or tests to the kit CI.** Would reopen ADR-0002 for
    one skill; `selftest.py` run by hand is the agreed substitute until the
    user decides otherwise.
11. **Per-skill install manifests.** One `find` change is the minimal fix
    (map 06, section 2.2).
12. **Analyzing the 2026 cross-entropy videos in depth.** Their code is used
    for the pattern library's newest idioms only; the eight narrated videos
    with aligned source are the corpus.

## 13. Decisions needed from the user

1. Confirm the skill id `manim-teaching-video` and the agent prefix `mv-`
   (five new agents), which requires the `AGENT_REF` regex change and README
   table updates.
2. Confirm Kokoro-82M as the default narration provider and the stated
   assumption (voice `af_heart`, Python 3.11 or 3.12 preferred), or name a
   different default.
3. Default final tier: `standard` 1080p30 (proposed) versus `uhd` 2160p30 to
   match 3b1b's output resolution.
4. Corpus tooling location: a separate `manim-corpus-tools` repository
   (proposed) versus a directory inside the kit repo that is excluded from
   the installer.
5. Whether media download of the eight YouTube videos is acceptable for
   private analysis given the terms-of-service note, or whether the corpus
   stays captions plus bucket figures plus source only.
6. The rubric pass bar (no item at 0, group means at least 1.5) and whether a
   second judge is required on G2 for final tiers.
7. Formula engine fallback order when LaTeX is missing: Typst then text-only
   (proposed), or stop and require LaTeX.
8. Whether to open ADR-0002 and add a Python test step to CI for bundled
   scripts, or keep `selftest.py` manual.
9. Acceptance of the text-callout replacement for the Pi-creature objection
   beat, or dropping that device entirely.
10. Time budget per video the skill should assume by default (proposed: 4 to
    8 minutes, ask above 12).
