# Architecture: corpus fidelity first

Design proposal for the `manim-teaching-video` skill in the `.agents` kit. The
skill turns a topic into a narrated, 3Blue1Brown-grade teaching video rendered
with Manim Community Edition (ManimCE) 0.22.0. This proposal takes the angle
that the skill can only be as good as the framework it carries, and the
framework can only be as good as the evidence it was distilled from, so most of
the design effort goes into an evidence-grounded, systematic reading of every
scene in the corpus and a faithful ManimCE translation of what the reading
finds. Every claim below cites one of the seven design maps under
`scratchpad/design/maps/` (referenced as M01 to M07) or a file in the local
clones; claims that could not be checked from this container are marked
unverified.

## 1. Thesis

The design optimizes for fidelity of the framework to the corpus, in this
order: completeness (every content scene of the eight primary videos gets an
analysis record), traceability (every rule, pattern and rubric item carries
citations to `file:line` in `3b1b/videos`, a transcript time range and a
keyframe), and translation accuracy (every ManimGL move the corpus uses has a
verified ManimCE idiom with an original example that renders).

Why this angle. The maps show the corpus is small enough to read in full and
rich enough to be worth it: 120 scenes with `construct` in the 2017 series and
255 scene classes in the 2024 series (M01 section 1.4, M02 section 1.2), with
five spine scenes carrying most of the teaching weight (M01 section 1.4) and
736 beat comments acting as the narration outline in 2024 (M02 section 6.1).
The moves that make the videos good are already visible as counts, not
impressions: 117 `ReplacementTransform` provenance moves, 105 `save_state` and
`restore` uses, 27 `there_and_back` nudges in 2017 (M01 sections 5.3 and 9);
148 `TransformFromCopy`, 85 `time_span` staggers and 139 camera `reorient`
calls in 2024 (M02 section 5.1). A framework written from memory would get the
flavor; a framework written from these records gets the numbers (2 s default
`run_time`, `lag_ratio` 0.1 for crowds and 0.5 for sequential reveals, 1 s
bare waits, 8 to 12 s orbits) and the exceptions (the chapter-1 color drift that
chapter 2 corrects, M01 section 3).

What this angle costs: the corpus phase is the longest milestone and the skill
cannot be tested end to end until the framework exists. Section 10 mitigates
that by shipping a thin vertical slice (one video analyzed, ten patterns,
rubric v0) before the full census, so the TDD loop for the skill starts early.

## 2. System overview

```text
 SOURCES (read-only, local or fetched once)
   3b1b/videos clone           3Blue1Brown.com clone      YouTube (blocked here)
   _2017/nn, _2024/transformers   app/pages/lessons/*.mdx    captions, media, info.json
          |                            |                          |
          v                            v                          v
 [A] corpus/raw/<video_id>/  (gitignored cache, content-hashed manifest)
          |
          v
 [B] corpus/derived/<video_id>/  scenes.json  transcript.words.json  keyframes/  figures.json
          |
          v
 [C] alignment.json  (monotonic DP over scene order x transcript sections, per-link confidence)
          |
          v
 [D] analyses/<video_id>/<section_id>.json  (+ rendered .md)   <- subagents, refuted, census-checked
          |
          v
 [E] framework/  principles.md  colors.md  timing.md  layout.md  arcs.md
     patterns/   INDEX.md  <id>.md  examples/<id>.py  (original ManimCE, rendered in CI)
     rubric.md   manimce/translation.md  manimce/gotchas.md
          |
          v
 [F] skills/manim-teaching-video/  SKILL.md  references/  scripts/  evals/   + agents/mv-*
          |
          v
 [G] RUN TIME  topic -> brief -> script -> storyboard -> scenes.py -> narration -> timing
                -> section renders -> frame review -> final render -> concat/mux -> final.mp4
```

Units, boundaries and how each is tested alone:

| Unit | Inputs | Outputs | Depends on | Tested alone by |
| --- | --- | --- | --- | --- |
| A `corpus.fetch` | video manifest (ids, slugs, source paths from M07 section 1) | `corpus/raw/<id>/` media, captions, `info.json`, mdx, figures; `manifest.lock.json` with sha256 per file | yt-dlp, curl, git | dry run against the manifest; hash check on a re-run (no re-download) |
| B `corpus.derive` | raw cache | `scenes.json` (AST scene cards), `transcript.words.json`, `keyframes/*.jpg` with `times.json`, `figures.json` | faster-whisper, ffmpeg, PySceneDetect | fixture video of 20 s and a fixture `.py` with three scene classes |
| C `corpus.align` | B outputs | `alignment.json` (M07 section 4 schema plus `kind`) | none beyond Python | synthetic transcript and scene list with a known mapping; recall above 0.8 |
| D `analyze` | C output, source file, keyframes | per-section analysis records (section 4 schema) | subagents | citation checker script, refuter pass, census |
| E `synthesize` | all D records | framework files, pattern library, rubric | subagents | every pattern example renders at `-ql`; every rule has at least two citations from two videos |
| F `skill` | E | SKILL.md, references, scripts, agents, evals | kit installer and validator | `scripts/validate.sh`, sandbox install, eval suite |
| G `runtime` | topic from the user, E via F | `final.mp4`, `script.md`, `storyboard.yaml`, `scenes.py`, `timing.json`, `report.md` | ManimCE, TTS provider, ffmpeg | per-stage contracts (section 6) and objective graders (section 8) |

Units A to E live in a corpus repository separate from the kit (section 9);
F and G live in the kit. The only artifacts that cross the boundary are the
paraphrased analysis records and the framework files, which are copied into
`skills/manim-teaching-video/references/` by a single sync script so the skill
bundles everything it needs (brief requirement) without the kit ever holding
third-party media or text.

## 3. Corpus pipeline

### 3.1 Scope

Primary tier: the eight narrated videos with Manim source (M07 section 1,
rows 1, 2, 4, 5, 6, 7, 8 and 9; about 149 minutes). Secondary tier: the two
2026 cross-entropy videos, code only (M07 section 1, tier 2), used for the
pattern library's newest idioms. Excluded: the guest video and the recorded
talk.

### 3.2 Layout and what is committed

```text
manim-3b1b-corpus/                    separate repository (MIT for our code)
  manifest.json                       committed: video ids, slugs, source files, expected durations
  manifest.lock.json                  committed: sha256 and byte size of every raw file fetched
  tools/corpus/                       committed: fetch.py derive.py align.py analyze.py census.py cite_check.py sync_to_kit.py common.py
  corpus/raw/<video_id>/              gitignored: media, captions, info.json, mdx, bucket figures
  corpus/derived/<video_id>/          gitignored: transcript.words.json, keyframes/, scenes.json, figures.json
  corpus/derived/<video_id>/alignment.json   committed (paraphrased summaries only, time ranges, class names)
  analyses/<video_id>/<section_id>.json      committed (our words, citations, no quotes over 12 words)
  analyses/<video_id>/index.md               committed (rendered from the json)
  framework/ patterns/ rubric.md manimce/    committed, synced into the kit skill
```

Committed material is limited to original work, time ranges, class names,
file paths and line numbers, per the license analysis in M07 section 6 and
M06 section 6: `3b1b/videos` is CC BY-NC-SA 4.0, the site repository is all
rights reserved, and YouTube downloads carry a terms-of-service risk. Raw
transcripts, keyframes, article text and media stay in the gitignored cache
and are deleted by `fetch.py --purge-media` after keyframes are extracted.

### 3.3 Steps

Each step is a subcommand of one entry point, `python -I tools/corpus/run.py
<step> --video <id> [--all]`, and each writes a sidecar
`corpus/derived/<id>/<step>.done.json` holding the sha256 of its inputs and the
tool versions used. A step runs only when its sidecar is missing or any input
hash changed, which gives idempotency and resume for free; `--force` overrides.

| Step | Tool | Input | Output | Notes |
| --- | --- | --- | --- | --- |
| `fetch-code` | `git` | `manifest.json` | `corpus/raw/<id>/source/` symlink into `/home/user/3b1b/videos` at commit `306a1346` | code is read in place, never copied |
| `fetch-site` | `git`, `curl` | lesson slug | `index.mdx`, `figures/*.jpg` from the public bucket listing (M07 section 2) | jpg only, skip png twins |
| `fetch-media` | `yt-dlp` | video id | `<id>.mp4` (1080p cap), `<id>.en.json3`, `<id>.en.vtt`, `<id>.info.json`, thumbnail | flags per M05 section 4 and M07 appendix B; `--js-runtimes node` |
| `transcribe` | `faster-whisper` `large-v3-turbo` int8, `word_timestamps=True`, `vad_filter=True`, domain `initial_prompt` | audio | `transcript.words.json` | if manual captions exist, `stable-ts align()` of caption text to audio replaces ASR text (M05 section 4) |
| `keyframes` | ffmpeg `select='gt(scene,0.3)'` plus PySceneDetect `AdaptiveDetector`, union with transcript-segment midpoints, dedupe within 1 s, cap 300 | mp4, transcript | `keyframes/<t>.jpg` at 480p plus `times.json` | counts and thresholds per M05 section 5; tune per video |
| `scenes` | Python `ast` | source files named in `manifest.json` | `scenes.json`: one card per class with `file`, `line`, `end_line`, `bases`, `kind`, `plays`, `waits`, `wait_seconds`, `run_time_seconds`, `beat_comments[]`, `string_literals[]`, `color_tokens{}`, `animation_counts{}` | extends the AST script already used for M01 section 1 (`scratchpad/tools/scene_metrics.py`) |
| `figures` | Python | `index.mdx` | `figures.json`: figure name, caption paraphrase, paragraph index, nearest heading | the curated keyframe set (245 figures, M07 section 2) |
| `align` | Python DP | `scenes.json`, `transcript.words.json`, `figures.json`, `keyframes/` | `alignment.json` | section 3.4 |
| `analyze` | subagents | `alignment.json`, source, keyframes, transcript | `analyses/<id>/<section>.json` | section 4 |
| `census` | Python | all records | `census.md`: coverage of scenes and minutes, open low-confidence links | gate for section 5 |
| `sync-kit` | Python | framework and analyses | copies into the kit worktree `skills/manim-teaching-video/references/` | runs the kit's markdownlint and typos before copying |

### 3.4 Alignment

Alignment follows M07 section 4: build the ordered content-scene list
(dropping helper mobjects, stubs, thumbnails, end screens; tagging
`TeacherStudentsScene` and `PiCreatureScene` subclasses as `kind: overlay` per
M03 section 4.3), split the transcript into candidate sections at pauses longer
than 1.2 s, article headings and figure positions, then run a monotonic dynamic
program over (scene, section) pairs scored by string-literal hits (highest
weight; the `Text`, `Tex` and `says` strings in `scenes.json`), class-name
token overlap, and figure-bridge hits (keyframe to bucket figure by perceptual
hash, figure to paragraph exact, paragraph to transcript by lexical overlap).
Skips carry a small penalty because not every scene survives the edit (M03
section 4.2 on `TODOStub` and `ExternallyAnimatedScene`).

Expected reliability before human anchors is 60 to 90 percent depending on
how many files a video spans (M07 section 4, signals table). The pipeline
therefore ends with a reviewer step: a subagent with the keyframes and the
transcript confirms or fixes every link with confidence below 0.7 and adds
three to six `(time, class)` anchors per video, after which `align` re-runs.
The records keep `verified_by` so the framework can weight anchored links
higher.

### 3.5 Running in a fresh session with network

```bash
GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 https://github.com/3b1b/videos "$HOME/3b1b/videos"
git clone <corpus-repo-url> "$HOME/manim-3b1b-corpus" && cd "$HOME/manim-3b1b-corpus"
python -m venv .venv && . .venv/bin/activate
pip install -r tools/requirements.txt      # yt-dlp, faster-whisper, stable-ts[fw], scenedetect, opencv-python-headless, imagehash
python -I tools/corpus/run.py fetch-code fetch-site fetch-media --all
python -I tools/corpus/run.py transcribe keyframes scenes figures align --all
python -I tools/corpus/run.py census
```

Expected wall time on 4 CPUs: media fetch under an hour; faster-whisper
`large-v3-turbo` int8 roughly real time or slower on 149 minutes (M05 section 4
extrapolates 5 to 8 minutes per 25 minutes for `small`; `turbo` is slower),
so `transcribe` runs in the background while `scenes` and `figures` proceed.
Hosts to allow-list are listed in M05 section 7. Every step prints the
`unverified` items it could not resolve (missing captions, no chapter markers)
into `corpus/derived/<id>/notes.md` so they are not lost.

## 4. Per-video analysis method

### 4.1 Who analyzes

Three subagent roles per video, dispatched in waves of four to six per the
kit's delegation rule (M06 section 4.1), each with a self-contained prompt:

1. **Code analyst**, one per spine scene or per group of up to eight short
   scenes. Reads the scene class source in full, the `scenes.json` card and
   the ManimGL defaults it needs (M01 and M04 give the file paths), and
   writes one scene card per class. Spine scenes (over 400 lines, M01 section
   1.4) get one analyst each because they carry most of the teaching weight.
2. **Narration analyst**, one per transcript section from `alignment.json`.
   Reads the word-timed transcript for the section, its keyframes and the
   matching article paragraphs, and writes what is said, in what order, what
   question is planted, what is admitted as uncertain, and where the visual
   changes relative to the words.
3. **Section synthesizer**, one per section, runs after the first two. Joins
   the scene cards and the narration record into the section record below,
   names the teaching moves and technique tags, and states why each works,
   citing both code and transcript.

Then two verification roles per video (section 4.5): a **citation refuter**
and a **census critic**. All roles are thinking-plus-reading work; none
mutates the repository (the parent writes the files from returned JSON).

### 4.2 Analysis record schema

One JSON record per section, `analyses/<video_id>/<section_id>.json`:

```json
{
  "video_id": "aircAruvnKk",
  "lesson": "neural-networks",
  "section_id": "s09",
  "t_start": 712.0,
  "t_end": 798.5,
  "title": "Weights as a pixel grid",
  "narration_summary": "paraphrase, 40 to 120 words, no verbatim quotes over 12 words",
  "question_planted": "what are these connections actually doing?",
  "admitted_uncertainty": null,
  "scenes": [
    {"class": "IntroduceWeights", "file": "_2017/nn/part1.py", "line": 2237, "end_line": 2617,
     "kind": "spine", "base": "IntroduceEachLayer", "plays": 20, "waits": 12}
  ],
  "beats": [
    {"beat_id": "b03", "t_start": 741.0, "t_end": 760.0,
     "narration_gist": "the 784 weights are laid out as a 28 by 28 grid",
     "visual": "parameter list morphs into a pixel grid next to the digit",
     "keyframes": ["keyframes/748.2.jpg"],
     "code_evidence": [{"file": "_2017/nn/part1.py", "lines": "2497-2541"}],
     "animations": ["ReplacementTransform", "LaggedStartMap"],
     "timing": {"run_time": [2, 3], "waits": [1, 1, 2]}}
  ],
  "moves": ["formula"],
  "technique_tags": ["numbers-before-symbols", "provenance-transform", "zoom-to-one-unit", "colors-by-sign"],
  "colors": {"positive_weight": "GREEN", "negative_weight": "RED", "emphasis": "YELLOW"},
  "layout": "network scaled 0.8 at bottom; grid upper left; formula top strip",
  "why_it_works": "two to five sentences, each tied to a beat id",
  "manimce_notes": ["ShowCreationThenDestruction -> ShowPassingFlash(copy, time_width=1.0)"],
  "evidence": [
    {"kind": "code", "file": "_2017/nn/part1.py", "lines": "2237-2617"},
    {"kind": "transcript", "t_start": 712.0, "t_end": 798.5},
    {"kind": "keyframe", "path": "keyframes/748.2.jpg", "t": 748.2},
    {"kind": "figure", "object": "lessons/2017/neural-networks/<name>.jpg"}
  ],
  "confidence": 0.85,
  "verified_by": ["refuter:2026-11-02", "anchor:human"]
}
```

Controlled vocabularies, fixed before analysis starts so records are
comparable:

- `moves` (one or two per section): `hook`, `concrete`, `abstraction`,
  `formula`, `recap`, `aside`, `meta`, `outro`, as used in M01 section 1.
- `technique_tags` (any number): the union of M01 section 8 and M02 section 8,
  normalized to 24 tags: `working-thing-first`, `preview-then-hide`,
  `zoom-to-one-unit`, `numbers-before-symbols`, `provenance-transform`,
  `admit-uncertainty`, `knobs-tremor`, `light-the-path`, `one-color-per-role`,
  `object-budget`, `montage-scale`, `viewer-voice`, `carry-picture-forward`,
  `seeded-randomness`, `save-and-restore`, `caption-next-to-referent`,
  `dim-not-delete`, `parameter-count`, `camera-as-narrator`,
  `real-data-where-cheap`, `honest-lie`, `one-then-all`, `pipeline-stays-on-screen`,
  `micro-timing-in-one-play`.
- `kind` for scenes: `spine`, `support`, `overlay`, `ambient`, `thumbnail`,
  `end_screen`, `stub`, `utility` (M03 section 4.3 plus M01 section 1).

### 4.3 Evidence grounding

Rules enforced by `tools/corpus/cite_check.py`, run on every record before
it is accepted:

- Every `code` citation resolves: the file exists in the clone at the pinned
  commit, the line range is inside the cited class's `lineno` to `end_lineno`
  from `scenes.json`, and at least one identifier named in the beat's
  `animations` list occurs in that range.
- Every `transcript` citation lies inside the section's `t_start` to `t_end`
  and overlaps at least one word in `transcript.words.json`.
- Every `keyframe` citation names a file that exists and whose timestamp is
  inside the beat.
- `narration_summary` and `narration_gist` contain no 13-word run that
  appears verbatim in the transcript (license rule from M07 section 5).
- `technique_tags` and `moves` are from the vocabularies above.

Records that fail are returned to the synthesizer with the failing check, not
patched by hand.

### 4.4 Transcript-to-code alignment inside a section

Within a section the synthesizer aligns beats to code blocks using three cues
in priority order: the beat comments in `scenes.json` (2024 code has 736 of
them, M02 section 6.1; 2017 code uses step methods instead, M01 section 2.7),
on-screen string literals matched to transcript words, and the `wait` and
`run_time` sums of each block compared with the beat's duration (M01 section
1 gives per-scene totals; narration is not in the code, M03 section 6, so the
sums are a weak cue used only to order, never to time). Where the edit
reordered or cut material the record says so in `manimce_notes` rather than
forcing a match.

### 4.5 Quality of the analyses

- **Citation refuter** (one per video): receives every record and tries to
  disprove three randomly chosen claims per record by opening the cited lines
  and frames; a record with any disproved claim goes back to its synthesizer.
  Target: zero disproved claims on the second pass.
- **Census critic** (one per video): checks `census.md` for completeness:
  every `spine` and `support` class has a scene card, every minute of the
  transcript belongs to exactly one section, every section has at least one
  keyframe and one code citation, and the `technique_tags` histogram per video
  is compared with the counts in M01 section 9 and M02 section 5.1 (for
  example a video with 117 `ReplacementTransform` uses but few
  `provenance-transform` tags is flagged).
- **Inter-analyst agreement**: two sections per video are analyzed twice by
  independent synthesizers; tag-set Jaccard below 0.6 triggers a vocabulary
  clarification before the rest of the video proceeds.
- **Human anchors**: the user confirms three to six links per video from the
  low-confidence list (about 30 minutes per video, M07 section 4); this is
  the only manual step in the corpus phase.

## 5. Framework representation

### 5.1 Files

All under `references/` in the skill, each starting with a table of contents
and capped at 400 lines so progressive disclosure works:

| File | Content | Loaded when |
| --- | --- | --- |
| `framework/principles.md` | 24 principles, one per technique tag, each with the fields in section 5.2 | script and storyboard stages |
| `framework/colors.md` | the role-color contract (M01 section 3, M02 section 3.1): cost `RED`, weights `BLUE` positive and `RED` negative, bias `MAROON_B`, emphasis `PURE_YELLOW`, query `YELLOW`, key `TEAL`, value `RED`, data `GREY_C` to `WHITE`; plus the CE hex traps (`YELLOW` versus `PURE_YELLOW`, `BLUE_E`, M04 constants table) | storyboard and scene coding |
| `framework/timing.md` | distributions turned into defaults: `run_time` 2 s default, 1 s confirmations, 3 to 5 s multi-part reveals, 8 to 12 s orbits; `wait()` 1 s, 2 s after reveals, 5 s on reaction beats; `lag_ratio` 0.1 crowds, 0.5 sequential, 0.7 one-at-a-time (M01 section 5.2, M02 section 6.2) | storyboard and sync |
| `framework/layout.md` | diagram low and left, text high, captions next to referent with arrow or brace, `SMALL_BUFF` default, `FRAME_WIDTH - 1` banners, object budget (M01 section 4) | scene coding |
| `framework/arcs.md` | chapter arc templates distilled from M01 section 6.1 and M02 section 6.3: working thing, plan, name taken apart, zoom to one unit, formula from parts, parameter count, failure and honesty, hand-off | script stage |
| `patterns/INDEX.md` | one row per pattern: id, name, what it says to the viewer, corpus evidence, CE classes used, example file | always, it is the lookup table |
| `patterns/<id>.md` | one pattern each, section 5.3 | on demand by id |
| `patterns/examples/<id>.py` | one original ManimCE scene per pattern, rendered in CI | copied into generated scenes |
| `rubric.md` | section 5.4 | review stages |
| `manimce/translation.md` | the M04 translation tables, condensed to the rows the corpus actually uses | scene coding, when a GL name is remembered |
| `manimce/gotchas.md` | the 24 runtime errors and the LaTeX dependency list from M04 | on render failure |
| `manimce/config.md` | `manim.cfg` for 1080p30 and 2160p30, `TexTemplate` with the packages the ported preamble needs (M03 section 1.3), font fallbacks | render stage |
| `analyses/INDEX.md` and `analyses/<lesson>.md` | per-video rendered records: section list with titles, moves, tags, one-line why | when an agent wants a worked example of an arc or a move |

### 5.2 How rules are phrased

Every principle has the same six fields so an agent can both apply and check
it. Example in the proposed form, derived from M01 section 8 item 4 and M02
section 8 item 1:

```text
P04 numbers-before-symbols
Statement: introduce every quantity as a concrete number on screen before its
  symbol, and re-expand the symbol to numbers whenever a computation is shown.
Why: activations are decimals in circles before "a"; the cost is a sum of
  on-screen decimals before C(w); vectors are columns before E_i.
  Evidence: _2017/nn/part1.py:1112-1172, part2.py:857-1004; _2024/transformers/attention.py:81-84,200-221.
Apply: storyboard beat that introduces a symbol must be preceded by a beat
  whose visual is a DecimalNumber, Matrix or labeled count of the same thing.
Check (storyboard): for each MathTex symbol first appearing in beat k, a
  numeric visual of the same concept exists in beats 1..k-1.
Check (code): scripts/lint_scene.py flags a MathTex whose storyboard concept
  has no DecimalNumber, DecimalMatrix or Integer earlier in the scene.
Pattern: PT-07 numeric-vector-to-symbol.
```

The two `Check` lines are the contract: one is a predicate the storyboard
critic agent evaluates by reading the storyboard; the other is implemented in
`scripts/lint_scene.py` where it is statically decidable (import of `manimlib`,
colors outside the contract, `self.play(mob.method, ...)` GL syntax, missing
`next_section` per beat, missing `random.seed`, more than one `MathTex`
introduced in one beat, a section without `wait`). Checks that need rendered
frames belong to the rubric.

### 5.3 Pattern library

About 44 patterns in six groups, each an original ManimCE example (no 3b1b
code) with the corpus evidence that motivates it:

| Group | Count | Examples of pattern ids |
| --- | --- | --- |
| Visual nouns | 12 | `PT-01 layered-network` (CE port of the `NetworkMobject` idea with `max_shown_neurons`, dots and brace, M01 section 2.2), `PT-02 pixel-grid`, `PT-03 numeric-vector`, `PT-04 weight-matrix-colored-by-sign`, `PT-05 token-tape`, `PT-06 machine-with-dials`, `PT-07 numeric-vector-to-symbol`, `PT-08 attention-grid`, `PT-09 next-token-bars`, `PT-10 slab-stack`, `PT-11 embedding-arrows`, `PT-12 context-arcs` |
| Provenance and transitions | 8 | `PT-13 term-flies-from-object` (`TransformFromCopy`), `PT-14 formula-from-parts` (`TransformMatchingTex` with `{{ }}` isolation), `PT-15 collapse-to-point`, `PT-16 save-and-restore-layout`, `PT-17 plan-then-move` (`generate_target`), `PT-18 mass-fade-clear`, `PT-19 recap-stack`, `PT-20 tag-open-close` |
| Emphasis and release | 7 | `PT-21 signal-flash` (`ShowPassingFlash` on a thickened copy), `PT-22 dim-the-rest`, `PT-23 knob-wiggle` (`rate_func=wiggle`), `PT-24 nudge-and-return`, `PT-25 boxed-term`, `PT-26 mask-then-reveal`, `PT-27 negate-with-cross` |
| Numbers and data | 6 | `PT-28 live-decimal-in-shape` (tracker plus color flip at 0.8 opacity), `PT-29 count-in-parameters`, `PT-30 cost-from-on-screen-decimals`, `PT-31 montage-of-examples` (0.1 to 0.5 s cadence), `PT-32 seeded-random-layout`, `PT-33 real-data-hook` (synthetic default, documented swap point, M02 section 11.5) |
| Camera and 3D | 5 | `PT-34 zoom-to-one-unit` (`MovingCameraScene`), `PT-35 orbit-while-contemplating` (`ThreeDScene`, 8 to 12 s), `PT-36 fixed-hud-title`, `PT-37 scroll-long-document`, `PT-38 receding-layers` |
| Narration and pacing | 6 | `PT-39 beat-as-section` (`next_section` plus `add_sound` plus `add_subcaption`), `PT-40 staggered-reveal`, `PT-41 delayed-sub-animation` (CE stand-in for `time_span`), `PT-42 question-caption-with-arrow`, `PT-43 learner-objection-callout` (original device replacing Pi creatures, M03 section 8 item 7), `PT-44 preview-then-hide` |

Each `patterns/<id>.md` has: intent (what the viewer should feel or learn),
when to use and when not, the corpus evidence (file:line, video id and time
range, keyframe reference in the corpus cache), the CE idiom with gotchas
(from M04), the example file, and the rubric items it serves. Each example
`.py` is a single `Scene` under 80 lines, renders at `-ql` in under 30 s, and
is exercised by the framework CI (section 8.2). The GL-to-CE swaps most likely
to bite are repeated in the pattern that uses them: `Tex` versus `MathTex`,
`ShowCreation` to `Create`, `PURE_YELLOW` for the highlight yellow, no
`time_span`, `MovingCameraScene` for any frame move (M04 translation tables).

### 5.4 Quality rubric

Twenty items in four groups, each scored 0, 1 or 2 with a one-line evidence
requirement, in `rubric.md`:

| Group | Items (gate items marked G) | Scored by |
| --- | --- | --- |
| Teaching | G hook is a concrete thing or question in beat 1; G every symbol preceded by numbers; one idea per beat; questions planted before answers; uncertainty or simplification admitted when the script simplifies; recap carries the picture forward | storyboard critic (`mv-critic`) on `storyboard.yaml`; re-checked on the final script |
| Visual | G role colors consistent across all beats; object budget (no frame with more than about 250 primitives unless a montage); captions adjacent to referents; provenance transforms used for every symbol-from-object; dim-not-delete when focus shifts; motion direction matches meaning | critic on storyboard; frame reviewer (`mv-frame-reviewer`) on rendered stills |
| Pacing and sync | G every beat's visual lands within 0.5 s of its narration anchor; no hold over 6 s without ambient motion or a stated reason; beat durations between 4 s and 40 s; 1 s rest after each reveal | `scripts/verify_sync.py` (objective) plus frame reviewer |
| Technical | G renders with zero errors and no `manimlib` import; G all mobjects inside the frame (bounding-box check); G audio and video durations within 0.25 s; narration at -16 LUFS integrated within 1 LU; SRT present | `scripts/lint_scene.py`, `scripts/check_frames.py`, `scripts/verify_sync.py`, ffprobe |

Pass bar: every gate item at 2, total at least 34 of 40, and no item at 0.
The storyboard must pass before any scene code is written (discipline rule);
the rendered video must pass before the final render tier is spent.

### 5.5 Context budgets

- `SKILL.md` stays under 200 lines and links every reference one level deep
  (Anthropic guidance quoted in M06 section 5.1).
- A **load order** table in `SKILL.md` names which references each stage
  reads: script stage reads `arcs.md` and `principles.md`; storyboard adds
  `patterns/INDEX.md`, `colors.md`, `timing.md`; scene coding adds the
  specific `patterns/<id>.md` files named in the storyboard plus
  `manimce/translation.md`; render adds `config.md`; review adds `rubric.md`.
  No stage loads the analyses unless it asks for a worked example.
- `patterns/INDEX.md` is the only file that lists everything; the per-pattern
  files are fetched by id. Expected budget: under 6 k tokens for the script
  stage, under 15 k for scene coding of one section.
- Subagents receive only the files their stage needs, listed by path in the
  prompt (kit rule: self-contained prompts, M06 section 4.1).

## 6. Skill design

### 6.1 SKILL.md outline

```text
---
compatibility: Requires Python 3.11+, manim 0.22, ffmpeg, a LaTeX distribution or Typst, and a narration provider (Kokoro by default)
description: >-
  Produces a narrated 3Blue1Brown-style teaching video from a topic with ManimCE: script,
  storyboard, scenes, synthesized narration, synced render and a final MP4. Use when asked
  for an explainer video, animated lesson, math or ML visualization video, Manim video, or
  narrated animation.
enabled: true
id: manim-teaching-video
name: manim-teaching-video
---
# Manim Teaching Video (orchestrator)
0. Triage out loud: topic scope, audience, target length, quality tier, provider available.
1. Environment check: python scripts/doctor.py (manim, LaTeX or Typst, ffmpeg, TTS, fonts).
2. Brief: five questions to the user (section 6.6) unless answered in the request.
3. Script: one mv-scriptwriter; read framework/arcs.md, principles.md. Output script.md.
4. Storyboard: one mv-storyboarder; output storyboard.yaml. Then one mv-critic (MANDATORY) with rubric.md.
   Loop until all gate items pass; at most three rounds, then ask the user.
5. Narration: python scripts/narrate.py storyboard.yaml -> narration/*.wav, timing.json.
6. Scenes: one mv-scene-coder per section in parallel waves of four; output scenes.py sections.
   Each coder gets its beats, the named patterns, colors.md, timing.md, translation.md.
7. Lint and dry run: python scripts/lint_scene.py; manim --dry_run.
8. Section renders at -ql; python scripts/check_frames.py; one mv-frame-reviewer per section.
9. Fix loop (re-render only changed sections), then final tier render, concat, mux, loudnorm.
10. Verify: python scripts/verify_sync.py; rubric self-review; report.md; hand the MP4 path to the user.
## Roster table (mv-scriptwriter, mv-storyboarder, mv-critic, mv-scene-coder, mv-frame-reviewer)
## Prompt contents per role
## Load order table (section 5.5)
## Output template (text fence)
## Guardrails / Scope boundaries / Communication style
```

The kit voice applies: imperative, triage first, roster table, "Prompt must
include" lists, MANDATORY markers, no model pins (ADR-0001), no code-host
references (ADR-0007), relative paths only inside skill markdown because of the
validator's `SLASH_REF` regex (M06 section 1.4).

### 6.2 references/ and scripts/

`references/` is section 5.1. `scripts/` is Python only (shell would face
shellcheck and shfmt, M06 section 3.5), grouped by domain with one shared
`common.py`, all invoked as `python scripts/<name>.py`:

| Script | Role | Contract |
| --- | --- | --- |
| `doctor.py` | environment check | prints a table: `manim --version`, `latex`, `dvisvgm`, `typst`, `ffmpeg`, fonts via `manimpango`, TTS provider reachable; exit code 1 lists what is missing and which quality tier is still possible |
| `storyboard_check.py` | storyboard contract | validates `storyboard.yaml` against the schema in section 6.3, the static principle checks, color contract, beat duration bounds |
| `narrate.py` | TTS plus timing | one WAV per beat, `timing.json` with word times and bookmark times; caches by sha256 of (provider, voice, text) |
| `lint_scene.py` | static scene checks | section 5.2 checks; also that `SECTIONS_IN_ORDER` matches the storyboard section ids |
| `render.py` | render driver | wraps `manim` with the tier's `manim.cfg`, `--save_sections`, retries, per-section timing log, caching on |
| `check_frames.py` | frame extraction and bounds | pulls last frame and two mid-beat frames per section from the section MP4s and JSON index, writes `frames/<section>/<beat>.png`, runs the bounding-box check from a dry-run hook |
| `assemble.py` | concat and mux | ffmpeg concat demuxer, `adelay` or back-to-back WAV concat, two-pass `loudnorm` to -16 LUFS, AAC mux, SRT soft-mux (M05 section 6) |
| `verify_sync.py` | objective sync check | compares each beat's anchor time in `timing.json` with the section JSON index and the SRT; reports max drift and the per-beat table |
| `selftest.py` | the scripts' own tests | runs unit tests on fixtures; the only Python gate the kit has (M06 section 3.10) |

### 6.3 Run-time artifacts and their contracts

All artifacts live in the user's chosen output directory (default
`out/<slug>/`), never in the kit:

1. `brief.md`: topic, audience, length target in minutes, quality tier,
   provider, constraints the user stated.
2. `script.md`: numbered sections, each with a title, narration paragraphs,
   the arc stage it serves (from `arcs.md`), and the question it plants. Word
   budget from the length target at 150 words per minute.
3. `storyboard.yaml`:

   ```yaml
   video: {slug: softmax-intro, length_target_s: 480, tier: standard, provider: kokoro}
   sections:
     - id: s01
       title: A working thing first
       arc_stage: working-thing-first
       scene_class: S01WorkingThing
       beats:
         - id: b01
           narration: "Here are three handwritten digits and a network that reads them."
           bookmarks: {reveal: "network that"}
           visual: "three digits fade in; layered network (PT-01) at bottom; answer box lights"
           patterns: [PT-01, PT-21]
           colors: {activation: WHITE, signal: PURE_YELLOW}
           duration_hint_s: 9
           rubric_tags: [hook]
   ```

4. `scenes.py`: one `Scene` subclass per section, `SECTIONS_IN_ORDER` list,
   `self.next_section(beat_id)` per beat, `add_sound` of the beat WAV, waits
   padded to the beat audio duration (M03 section 8 items 3 and 6), seeded
   randomness, `from manim import *` plus `from patterns_runtime import *` for
   the copied pattern helpers.
5. `narration/<beat_id>.wav` plus `timing.json`
   (`{beat_id: {duration, words: [{w, start, end}], bookmarks: {name: t}}}`).
6. `media/videos/scenes/<quality>/sections/*.mp4` and `<Scene>.json` indexes.
7. `frames/<section>/<beat>.png` for review.
8. `final.mp4`, `final.srt`, `report.md` (rubric scores, drift table, render
   time, what the user should check).

### 6.4 Verification loops

- **Storyboard loop**: `storyboard_check.py` then `mv-critic` with
  `rubric.md`; the critic returns per-item scores with beat ids as evidence;
  the storyboarder revises; at most three rounds before the user is asked.
- **Render loop**: `lint_scene.py`, `manim --dry_run` (catches LaTeX and API
  errors before frames are drawn, M03 section 3.5), section render at `-ql`,
  `check_frames.py`, then `mv-frame-reviewer` reads the PNGs (image reading)
  against the storyboard's `visual` text and the visual rubric items; fixes
  re-render only the changed sections, which ManimCE caches per `play` hash
  (M04 caching section).
- **Sync loop**: `verify_sync.py` after assembly; drift above 0.5 s on any
  beat sends that section back to the render loop with the measured offsets.
- **Final self-review**: the parent fills `report.md` from the scripts'
  outputs and the critic's last scores; it never claims a pass without the
  script output (kit's verification posture).

### 6.5 Error handling

| Failure | Detection | Response |
| --- | --- | --- |
| LaTeX missing or a package missing | `doctor.py`; `ValueError: latex error converting to dvi` (M04 gotchas) | switch the tier's config to `Text` for labels and `MathTypst` for formulas if `typst` is present; otherwise tell the user which TeX Live packages to install and stop before rendering |
| Render failure in one section | non-zero exit from `render.py` with the traceback | map the error through `manimce/gotchas.md`; the coder fixes only that section; three failures on one section escalate to the user with the traceback |
| TTS provider unreachable or key missing | `narrate.py` exception | fall back in order Kokoro, Piper, then stop; never fall back to edge-tts or gTTS without explicit opt-in (M05 section 2) |
| Network blocked for model weights | `doctor.py` download probe | state the host to allow-list from the M05 section 7 table; offer `draft` tier with Piper if its voice is cached |
| Long render | `render.py` estimates frames times measured seconds per frame from the `-ql` pass | if the estimate exceeds the tier budget, ask before the final render; suggest `standard` instead of `final` |
| Frame out of bounds or overlap | `check_frames.py` bounding boxes; frame reviewer | coder applies `scale_to_fit_width` or layout change; re-render the section |
| Sync drift | `verify_sync.py` | re-pad waits from `timing.json`; if a beat's animation is longer than its audio, split the beat or shorten `run_time` |

### 6.6 Budget, tiers and what the skill asks

| Tier | Resolution and fps | Narration | Render budget target | Use |
| --- | --- | --- | --- | --- |
| `draft` | 854x480 at 15 (`-ql`) | Kokoro | under 10 minutes for a 5-minute video | iteration and evals |
| `standard` | 1920x1080 at 30 | Kokoro or premium | under 60 minutes | default deliverable |
| `final` | 3840x2160 at 30 (`-r 3840,2160 --fps 30`, the 3b1b setting from `custom_config.yml`, M03 section 1.1) | premium if available | hours; only after `standard` passed the rubric | publication |

Questions to the user, asked once at the brief stage and only when the request
left them open: topic scope and one sentence on what the viewer should be able
to do afterwards; audience level; target length (default 5 to 8 minutes);
quality tier (default `standard`); narration provider when a premium key is
present in the environment (default Kokoro). One approval checkpoint after the
storyboard passes the critic, because that is the last cheap moment to change
the story. Everything else runs unattended and ends with the MP4 path and
`report.md`.

## 7. Narration and sync

- **Default TTS**: Kokoro-82M, voice `af_heart`, speed 1.0, offline,
  Apache-2.0, per-token `start_ts` and `end_ts` from `KPipeline.join_timestamps`
  (M05 section 2). Stated assumption: installed from GitHub on Python 3.13 or
  PyPI on 3.10 to 3.12; `kokoro-onnx` as the lighter fallback when PyTorch is
  unwanted (token timestamps there are unverified).
- **Premium**: ElevenLabs `convert_with_timestamps` (character-level
  alignment, `previous_text` and `next_text` for prosody across beats); OpenAI
  `gpt-4o-mini-tts` and Azure as alternates (M05 section 2). Keys come from
  the environment only (`ELEVENLABS_API_KEY`, `OPENAI_API_KEY`), never from
  files in the kit (gitleaks scans history, M06 section 3.6).
- **Alignment**: use the engine's own timestamps when it has them (Kokoro,
  ElevenLabs, Azure); otherwise forced-align the known script with
  `torchaudio.functional.forced_align` and `WAV2VEC2_ASR_BASE_960H` after
  spelling out numbers, or `stable-ts align()` if whisper is already installed;
  proportional interpolation only as a last resort with a warning in
  `report.md` (M05 section 3).
- **manim-voiceover**: not a dependency. Reasons from M05 section 1: single
  maintainer and a 20-month release gap; stale service pins (`elevenlabs<0.3`,
  `openai<2`); bookmark timing by whisper transcription plus character-offset
  interpolation; a PyTorch-plus-whisper requirement for timing the default
  engine already provides; and reliance on renderer internals
  (`renderer._original_skipping_status`) that the 0.22 `Manager` refactor puts
  at risk. The skill keeps its ergonomics: `<bookmark mark='x'/>` in beat
  narration and a `beat()` context manager in `patterns_runtime.py` that reads
  `timing.json`, calls `add_sound`, exposes `time_until('x')` and
  `remaining()`, and pads the final wait. Fewer than 150 lines, MIT, ours.
- **Assembly**: ManimCE renders silent section videos with `--save_sections`;
  `assemble.py` concatenates with the concat demuxer, builds the narration
  track by placing beat WAVs at their section offsets, normalizes to -16 LUFS
  and -1.5 dBTP in two passes, muxes AAC at 192 kbps, and soft-muxes the SRT
  (M05 section 6). `add_sound` inside the scene is still called so the section
  MP4s have audio for the frame reviewer, but the final track is the external
  mix so loudness is uniform across sections.

## 8. Testing strategy

### 8.1 Scripts

- Unit tests in `scripts/selftest.py` over fixtures in `scripts/fixtures/`:
  storyboard schema accept and reject cases, `lint_scene.py` on a scene with
  each forbidden construct, `verify_sync.py` on a hand-made `timing.json` and
  section index with known drift, `assemble.py` on three 2 s synthetic clips
  and WAVs (ffmpeg `testsrc` and `sine`), `cite_check.py` (corpus repo) on a
  record with one broken citation.
- Integration test: a 20 s fixture storyboard with two sections renders at
  `-ql` with Piper or Kokoro cached voices, assembles, and passes
  `verify_sync.py` with drift under 0.25 s. Runs in the corpus repo's CI and
  by hand in the kit worktree (the kit has no Python gate by ADR-0002).

### 8.2 Framework

- **Pattern CI**: every `patterns/examples/<id>.py` renders at `-ql` with
  `--format png` and the frame is compared with a committed reference by
  perceptual hash; a diff above threshold fails. This is the translation
  fidelity test: it proves each CE idiom exists and behaves.
- **Framework-only generation test**: a subagent is given a topic, the
  framework files and the rubric, but not `SKILL.md`, and asked for a
  storyboard; `mv-critic` scores it. Target: median total at least 30 of 40
  across the five fixed topics (section 8.3), gate items at 2 for at least
  four of five. This isolates whether the framework teaches well before the
  orchestration is layered on.
- **Rule discrimination test**: for each principle, two storyboard snippets
  (one compliant, one violating) are graded by a critic with the rule text;
  a rule whose check does not separate them is rewritten (micro-test
  practice from writing-skills, M06 section 5.1).

### 8.3 Skill

Fixed test-prompt set, five topics, chosen to span the corpus domain and
beyond so the framework is not over-fitted:

1. "Explain what a softmax does and why temperature matters" (corpus domain).
2. "Why does gradient descent follow the negative gradient?" (corpus domain,
   chapter 2 overlap).
3. "Teach the dot product geometrically" (adjacent math).
4. "What is a hash table and why is lookup fast?" (non-math CS).
5. "How does compound interest grow?" (everyday quantitative).

Plus three pressure scenarios for the discipline rules (writing-skills form,
M06 section 5.1): render before the storyboard passes under time pressure,
skip sync verification because "it looked fine", translate a remembered
ManimGL snippet verbatim.

Procedure (M06 section 5.3): RED baseline runs without the skill, transcripts
saved under the gitignored `manim-teaching-video-workspace/`; eval cases
written in the skill-creator layout `evals/<case>/{prompt.md,case.yaml,graders/}`
before `SKILL.md`; GREEN with-skill and baseline runs in the same turn;
grading, aggregation and the static viewer; REFACTOR; description
optimization from a scratch project with `run_loop.py`.

"Pass" for the skill means, on all five topics in `draft` tier: an MP4 exists
with one video and one audio stream (ffprobe); durations agree within 0.25 s;
no `manimlib` import; section count equals the storyboard; `verify_sync.py`
max drift under 0.5 s; critic total at least 34 of 40 with all gates at 2;
and the with-skill median beats the baseline median on every objective grader.
For the pressure scenarios: the agent refuses the shortcut and cites the
skill's rule in every run of five.

## 9. Repo layout inside the kit and required kit changes

```text
skills/manim-teaching-video/
  SKILL.md
  references/framework/{principles,colors,timing,layout,arcs}.md
  references/patterns/INDEX.md  references/patterns/PT-01.md ... PT-44.md
  references/patterns/examples/PT-01.py ... PT-44.py
  references/rubric.md
  references/manimce/{translation,gotchas,config}.md
  references/analyses/INDEX.md  references/analyses/<lesson>.md  (eight files)
  scripts/{doctor,storyboard_check,narrate,lint_scene,render,check_frames,assemble,verify_sync,selftest,common}.py
  scripts/patterns_runtime.py   (beat() context manager and pattern helpers copied into generated projects)
  scripts/fixtures/
  assets/manim.cfg.{draft,standard,final}  assets/tex_template.tex
  evals/<case>/{prompt.md,case.yaml,graders/}
agents/mv-scriptwriter/agent.md  agents/mv-storyboarder/agent.md  agents/mv-critic/agent.md
agents/mv-scene-coder/agent.md   agents/mv-frame-reviewer/agent.md
docs/research/manim-teaching-video-design.md   (this proposal and the maps, condensed)
docs/adr/0008-skills-ship-scripts-and-references.md
docs/adr/0009-third-party-corpora-are-studied-not-vendored.md
```

Required kit changes, each minimal per `rules/minimal-changes.md` (M06
sections 2 and 7):

1. `scripts/install.sh`: change the `find` filter so every regular file under
   `skills/<id>/` except `SKILL.md`, `evals/`, `__pycache__` and `*.pyc` is
   shipped (today only `*.md` is copied, so `scripts/` and `.py` examples
   would be silently dropped). Tab-indented for `shfmt`.
2. `scripts/validate.sh`: exclude `evals` from the markdown reference scan,
   and extend `AGENT_REF` to `(?:cr|mv)-[a-z][a-z-]*` so `mv-*` references
   are validated.
3. `.github/workflows/validate.yml`: add `test -f` smoke lines for
   `skills/manim-teaching-video/skill.md`, one script and one reference file.
4. `README.md`: skills count, sub-agents table with the five `mv-*` agents,
   install note that skills may ship scripts.
5. `CHANGELOG.md`: `Unreleased` entry in the existing style.
6. `.gitignore`: `manim-teaching-video-workspace/`, `media/`, `out/`.
7. ADR-0008 and ADR-0009 in the kit's one-paragraph voice.
8. `.typos.toml`: no change expected; the skill's text avoids the corpus's
   misspelled identifiers (they stay in the corpus repository, which has its
   own allow-list).

## 10. Phasing and milestones

| Milestone | Deliverable | Proves | Effort (focused sessions) |
| --- | --- | --- | --- |
| M0 Environment | corpus repo skeleton, `run.py` with `fetch-*`, `scenes`, `figures`; install manim 0.22 and Kokoro in a venv; render one CE scene; synthesize one sentence with timestamps | the toolchain works outside this container | 1 |
| M1 Vertical slice | chapter 1 (`aircAruvnKk`) through the whole corpus pipeline: transcript, keyframes, alignment, 12 to 15 section records refuted and census-checked; ten patterns with rendering examples; rubric v0 | the analysis method and schema hold on the hardest 2017 file; the citation checker catches errors | 3 |
| M2 Skill RED and first GREEN | baseline runs on the five topics and three pressure scenarios; eval cases; `SKILL.md` v0 with the ten patterns; `narrate.py`, `render.py`, `assemble.py`, `verify_sync.py`; one draft MP4 end to end | the pipeline yields a synced MP4 and the TDD loop is live | 3 |
| M3 Corpus census | remaining seven primary videos analyzed, refuted, census-checked; human anchors confirmed; `technique_tags` histograms reconciled with the maps' counts | the framework rests on every content scene, not a sample | 5 |
| M4 Framework synthesis | all 24 principles with two-video evidence, 44 patterns rendering in CI, rubric v1, framework-only generation test at target | the framework teaches without the orchestrator | 3 |
| M5 Skill REFACTOR | with-skill runs beat baseline on every grader; pressure scenarios pass 5 of 5; description optimized; kit changes and ADRs; gates green; PR | the skill is bulletproof by the writing-skills definition and installable | 3 |
| M6 Secondary tier | 2026 code patterns (point clouds, procedural layouts) added to the library as optional patterns | the library tracks the author's newest idioms | 1 |

Total about 19 focused sessions. M1 and M2 can overlap once the schema is
frozen; M3 is the long pole and runs as background subagent waves.

## 11. Risks and mitigations

| Risk | Likelihood | Mitigation |
| --- | --- | --- |
| YouTube download or captions unavailable or against terms of service | medium | captions first, media second, delete media after keyframes; the bucket's 245 captioned figures already give a keyframe set keyed to article paragraphs (M07 section 2); the code is the primary corpus by decision, so analysis proceeds without video |
| Alignment accuracy too low for the 2024 videos spread over several files | medium | human anchors (3 to 6 per video), overlay tagging, figure bridge; records carry confidence so the synthesizer can discount weak links |
| Subagent analyses drift into paraphrase of memory instead of evidence | medium | `cite_check.py` rejects uncited claims; refuter pass; census compares tag histograms with grep counts from M01 and M02 |
| License leakage (quoted narration, copied scene code, frames) in committed records | low with checks | 13-word verbatim check, no code quotes beyond identifiers, media never under git, attribution note in `framework/principles.md` |
| ManimCE API skew between training data and 0.22 | high | pin `manim==0.22.0`; pattern CI renders every example; `translation.md` and `gotchas.md` are the first stop on any error; `doctor.py` prints the installed version |
| LaTeX absent on the user's machine | medium | `doctor.py`; Typst path for formulas; `Text` for labels; `DecimalNumber(mob_class=Text)` is unverified and must be tested in M0 |
| Kokoro on Python 3.13 or CPU speed | medium | install from GitHub or `kokoro-onnx`; Piper fallback; measure real-time factor in M0 and record it in `timing.md` |
| Render time at `final` tier | high | tiers; estimate from the `-ql` pass; per-`play` caching; ask before spending hours |
| Pi-creature pacing lost | certain | `PT-43 learner-objection-callout` as an original device; narration carries the reaction beats |
| Kit gates (markdownlint MD060 tables, typos on identifiers, lychee on blocked hosts) | medium | compact table style everywhere; corpus identifiers stay in the corpus repo; URLs only to GitHub and PyPI canonical pages; `sync_to_kit.py` runs the gates before copying |
| Scope creep into a general Manim toolkit | medium | section 12 |

## 12. Deliberately cut

- **Rendering 3b1b's own scenes** for keyframe comparison: ManimGL plus
  missing Dropbox assets and absolute paths make it infeasible (M02 section
  11, M07 section 3).
- **manim-voiceover as a dependency**: section 7.
- **Pi creatures, logo, end screens, banners**: brand assets whose SVGs are not
  public (M03 section 2); replaced by one original callout device.
- **OpenGL renderer and live preview**: the agent has no window; Cairo is the
  documented headless path (M04 renderers section).
- **A general ManimGL-to-ManimCE transpiler**: the skill never translates his
  code, so only the idioms the patterns need are mapped.
- **Real model calls (GPT-2, GloVe, OpenAI) at run time**: synthetic seeded
  values with a documented swap hook, following the 2026 file's own choice
  (M02 section 11.5).
- **OCR of keyframes** and **CLIP matching**: perceptual hashing against the
  bucket figures plus string literals is enough for alignment (M07 section 4);
  OCR's 50 to 60 percent reliability does not pay for its dependencies.
- **Per-language lint gates in the kit** (ruff, pytest in CI): reopens
  ADR-0002 for one skill; `selftest.py` and the corpus repo's CI cover it.
- **Multi-voice or multilingual narration**: Kokoro timestamps are
  English-only; one voice, English, in v1.
- **Interactive storyboard tooling or a GUI**: the YAML plus the critic loop
  is the interface.
- **Thumbnail generation and YouTube publishing**: outside "one run yields a
  finished MP4" and would touch a code host (ADR-0007).

## 13. Decisions needed from the user

1. Corpus repository placement: a separate MIT repository
   `manim-3b1b-corpus` (recommended, keeps CC-derived analysis and raw caches
   out of the kit) versus a gitignored directory inside the kit worktree.
2. Media policy: download the eight primary videos for transcription and
   keyframes (terms-of-service risk, M07 section 6) versus captions plus
   bucket figures only (lower fidelity on timing, no risk).
3. Human anchor time: about 30 minutes per video, eight videos, to confirm
   low-confidence alignment links; or accept automatic alignment with
   confidence weighting only.
4. Default narration provider: Kokoro `af_heart` as proposed, or Piper if
   PyTorch must be avoided on the target machine.
5. Default quality tier for an unqualified request: `standard` 1080p30 as
   proposed, or `draft`.
6. Agent naming: five new `mv-*` agents under `agents/` with the `AGENT_REF`
   regex extended, versus reusing the generic harness agent with inlined
   definitions and no new agents.
7. Two ADRs (0008 scripts and references, 0009 corpora studied not vendored)
   versus one combined ADR.
8. Pattern count target: 44 patterns in six groups as proposed, or a smaller
   core of about 25 with the rest deferred to M6.
9. Whether `final` tier (2160p30) is in scope for v1 or `standard` is the
   ceiling until render times are measured.
