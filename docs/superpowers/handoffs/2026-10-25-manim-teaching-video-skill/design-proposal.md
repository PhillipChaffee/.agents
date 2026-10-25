# Design proposal: the manim-teaching-video skill

Status: PROPOSAL, awaiting owner approval (brainstorming step 5)

## Context and goal

The `.agents` kit needs a skill that turns a topic into one finished,
narrated, 3Blue1Brown-grade teaching video rendered with Manim Community
Edition (ManimCE): one run yields a script, synthesized narration, animation
synced to that narration, and one MP4 that both looks and teaches like the
reference videos. Decisions already fixed by the brief and not reopened here:
ManimCE is the target and 3b1b's ManimGL idioms are translated, never copied;
the primary corpus is his public Manim source aligned to transcripts per video
section, with video keyframes as a secondary check and our own tooling; the
skill bundles everything it needs; the narration provider is pluggable with a
stated default; `3b1b/videos` is CC BY-NC-SA 4.0, so the framework carries
derived principles and original ManimCE examples only; the kit's rules (git
worktrees, look-it-up, minimal changes, delegation) apply.

This proposal synthesizes seven research maps (cited as map NN), three
candidate architectures (cited by file name under `architectures/`) and
three judgments (cited by lens under `judgments/`). Claims that no map could
verify from this container are marked unverified.

## Approaches considered

### Approach A: corpus fidelity first

The skill is only as good as its framework and the framework only as good as
its evidence, so this design reads every content scene of the eight primary
videos into per-section records with `file:line`, transcript and keyframe
citations enforced by a citation checker, a refuter and a census, then
distills 24 principles, 44 patterns and a 20-item rubric
(`architectures/corpus-fidelity.md`, sections 4 and 5).

Trade-offs. Strongest framework form: rules with an `Apply` line and two
`Check` lines, one for the storyboard critic and one for a static lint
(section 5.2); the only design with a defense against analysts writing from
memory (citation checker, 13-word verbatim guard, tag histogram versus grep
counts, section 4.3 and 4.5). Costs: about 19 sessions, hundreds of subagent
dispatches, four hours of human anchor time, no run-time state record, the
first MP4 only after three sessions of corpus work, and 44 example scenes
whose render-CI home is unresolved. Two factual errors: the claim that
`add_sound` gives the frame reviewer audio in section MP4s (section MP4s carry
no audio, CE `scene_file_writer.py:966-985` per the shipping judgment), and
`query: YELLOW` in the color contract where CE needs `PURE_YELLOW` (map 04,
constants row). Judges scored it 50, 48 and 49 of 70; the animation judge
ranked it first for its method and said its scope should be cut.

### Approach B: repeatable process first

The run-time process is the product: a gated, resumable batch pipeline
(preflight, script, storyboard, narration, scene code, draft render and frame
review, final render, assemble and verify) in which every human check in
3b1b's interactive loop becomes a code or rubric check that runs before the
next expensive step (`architectures/repeatable-process.md`, sections 1 and 6).

Trade-offs. Best run-time engineering: `state.json` with input hashes and a
resume rule, one `manim` process per scene, bounded loops with named
escalations, a `selftest.py` that runs without ManimCE using a `null` TTS
provider, frames extracted at bookmark times, a runtime bounding-box log, and
a pass definition that requires the baseline to fail (sections 6.2, 6.5, 8.1,
8.3). Costs: 19 to 24 days with the first end-to-end MP4 at M4; it cuts all
3D and camera work from v1 although the camera is one of the 2024 series'
fourteen moves (map 02 section 8 move 5); it bans `wait()` inside a beat
while its own pacing rules demand play-wait-play-wait (animation judgment,
weaknesses); its static `run_time` sum check is undecidable for non-literal
values; and three math engines multiply pattern variants. Judges scored it
50, 52 and 52; the reliability judge ranked it first.

### Approach C: minimal viable, extensible

Optimize for time to the first rubric-passing video, then for the cost of
adding depth. The toolchain, not the pedagogy, is the unproven part, so M0 is
a hand-written two-beat spike before any corpus work; one `lesson.json`
contract is read and written by every stage; a small shipped `mtv` package
carries `NarratedScene`, the look and ten pattern helpers that generated
scenes import rather than recall; audio is muxed after render so a voice
change never re-renders a frame (`architectures/minimal-viable.md`, sections
1, 2.3, 5.3, 7.3).

Trade-offs. Fastest to a verified MP4 (nine to ten days), smallest kit diff
(three single-expression changes plus one ADR, no new agents), and the only
design that avoids `add_sound` inside cached scenes. Costs: two videos at
release with one analyst each, which the design itself says overflows on a
25-minute video; a sync gate that compares the JSON index against offsets
computed from the same index; a rubric item ("no hold over 4 s without
motion") that contradicts the corpus's deliberate 5 to 30 s holds (map 01
section 6.4; map 02 section 6.2); two rubric mechanisms whose named inputs
cannot compute them; and one wrong CLI flag (`--disable_caching_warning` is a
`manim.cfg` key, CE `default.cfg:134`). Judges scored it 51, 49 and 53; the
shipping judge ranked it first.

### Recommendation

Adopt a hybrid, named here **spike-first gated pipeline with an
evidence-grounded framework**: Approach C's spine and milestone order,
Approach B's run-time engineering, and Approach A's evidence discipline and
rule form. All three judgments end with a tie-break note that names this same
combination (animation judgment, ranking; reliability judgment, top ideas to
graft; shipping judgment, tie-break note), and the totals are within five
points, so the choice is about where each design is strong, not which wins.

| Taken from | What | Why |
| --- | --- | --- |
| C | M0 toolchain spike, then a hand-written lesson to a verified MP4 with no model in the loop, then corpus, then skill TDD | Nothing in the render, TTS or sync chain was executed in the design container; a wrong assumption there invalidates everything downstream |
| C | One `lesson.json` contract, single writer per field; `mtv` package with `NarratedScene`, `look.py` and imported pattern helpers; silent renders muxed by beat offset; inlined roles; three kit changes and one ADR | Smallest surface that still attacks the highest-likelihood failure (ManimGL idioms recalled from training data) |
| B | Input hashes and resume at the first changed stage (folded into `lesson.json`), bounded loops with escalation, "stop" semantics, one `manim` process per scene, `selftest.py` with a `null` provider and `--one-beat`, frames at mark times, bounding-box log, error-table rows injected into retry prompts, baseline-must-fail pass definition | Makes every gate checkable and every interruption resumable |
| A | Rule form with `Apply`, `Check (storyboard)`, `Check (code or frames)`; `cite_check.py` with the 13-word verbatim guard; tag histogram census against the maps' grep counts; rule discrimination micro-test; load-order table; six-group pattern taxonomy; lead/lag recorded per beat | Keeps rules out of platitude territory and analyses out of memory |

Seven items that no architecture handled are added from the judgments: rubric
calibration against paraphrased corpus storyboards, continuity across scene
boundaries, contact-sheet motion review, a signed lead/lag field, the
encode-time saturation filter, a between-beat tail, and a vocabulary that
separates the storyboard unit from ManimCE's "section". Each appears in the
design section that owns it.

Contradictions resolved: 3D stays in v1 as one orbit helper plus a
`MovingCameraScene` zoom (C's choice, not B's cut); `wait()` is allowed inside
a beat and the runtime pads against the absolute clock (B's ban dropped);
`add_sound` is never called inside scenes (A's dual path dropped); the
default `run_time` rule is "1 s confirmations, 2 s meaning-carrying
transforms" because both series support it (map 01 section 5.2; map 02
section 6.2); every GL `YELLOW` in a role contract becomes `PURE_YELLOW`;
CE's shipped `TexTemplateLibrary.threeb1b` is selected rather than a custom
preamble, with only the `\minus` macro added (CE `tex_templates.py:26-67` per
the shipping judgment; map 03 section 1.3). Approach C's circular drift gate
is not carried over: the sync gate compares a run log written by the scene
itself against the section index and the WAV durations (section 8), so the
gate can fail. Approach C's single `NarratedScene` is replaced by a mixin and
three concrete classes because CE's `MovingCameraScene` and `ThreeDScene` are
sibling subclasses of `Scene` (CE `moving_camera_scene.py:104`,
`three_d_scene.py:31`).

## Design

### 1. Architecture overview

Two halves share nothing but the synced framework files.

```text
BUILD TIME (once per corpus revision, separate repo)
  3b1b/videos clone ─┐
  YouTube captions  ─┼─► corpus tools ─► corpus/<id>/ (gitignored cache)
  site figures      ─┘        │
                              ▼
            section analysts + merger + refuter ─► analyses/<slug>/*.json
                              │   cite_check.py, census.py
                              ▼
            framework synthesis ─► framework.md, patterns.md + mtv/patterns.py,
                                   rubric.md, manimce.md
                              │   sync_to_kit.py (runs markdownlint, typos)
                              ▼
RUN TIME (every invocation, in the consumer project)
  topic ─► 0 triage ─► 1 preflight ─► 2 brief ─► 3 script ─► 4 storyboard + critic
        ─► 5 narrate ─► 6 scenes + check_scenes ─► 7 draft render + frames + critic
        ─► 8 fix loop ─► 9 final render ─► 10 assemble ─► 11 verify ─► report
                                     all stages read and write mtv-runs/<slug>/lesson.json
```

Vocabulary, fixed so that ManimCE's own "section" does not collide with ours
(reliability judgment, "what none of them handles"): a **lesson** is one
video; a **scene** is one storyboard unit rendered as one `Scene` subclass; a
**beat** is one narration paragraph of one to three sentences rendered as one
`self.next_section(beat_id)` call, so ManimCE's section index describes
beats; a **mark** is a named word inside a beat's narration that an animation
lands on; a **tier** is `draft`, `standard` or `final`; a **gate** is a check
that must pass before the next stage runs. The word "section" is reserved
for two things only: ManimCE's own `next_section` unit at run time, and a
transcript span (`section_id`) on the corpus side (section 5); it is never a
storyboard unit. Three principles follow from the
maps. Narration first: the beat's audio length is its duration budget, since
the agent has no editor; map 03 section 6 infers from the code that 3b1b
resolves timing in the edit, with the recording order unverified, and that
inference is adopted here as a design choice rather than a fact. Imported,
not recalled: idioms ship as functions in `mtv/patterns.py` and
a static lint rejects GL names before any render (map 04, translation
tables). Evidence or nothing: every framework rule cites analyses that cite
`file:line` and transcript time, and a script checks the citations.

### 2. Components

| Component | What it does | Used | Depends on |
| --- | --- | --- | --- |
| `scripts/preflight.py` | Checks Python 3.11 or 3.12, `manim` 0.22.x, `latex`, `dvisvgm`, `ffmpeg`, the provider (ten-word synthesis, real-time factor recorded), fonts, disk, CPUs | `python scripts/preflight.py --json`; hard stop with install lines | standard library |
| `scripts/narrate.py` | One WAV and `words.json` per beat; mark times and durations into `lesson.json`; cache keyed by provider, voice and the clean narration text only, so editing a mark never re-synthesizes | `python scripts/narrate.py lesson.json` | `mtv/tts.py` providers `kokoro`, `elevenlabs`, `null`, each with its own token matcher |
| `scripts/storyboard_check.py` | Static gate over the storyboard: every `lands` mark resolves to a word index in its beat, `scene_kind` is set per scene, the `Apply` predicates of the storyboard-checkable rules (section 6) hold, no `visual` names a raster image | after the storyboard stage, before the critic | `mtv/lesson.py` |
| `scripts/check_scenes.py` | Static gate: one class per scene, its base matches the scene's `scene_kind`, beat ids once in order, no `manimlib` or GL-only names, no `self.play(mob.method, ...)`, contract colors, no `ImageMobject` or file reads; then `--dry_run` | before any render | `ast`, ManimCE |
| `scripts/render.py` | One `manim` process per scene, `--jobs N` of them concurrently (default CPU count minus one), each with the tier's `manim.cfg`, `--save_sections` and `PYTHONPATH` set to the skill's `scripts/` directory; kill after ten silent minutes, retry once with `--disable_caching`; beat index, beat run log and the environment actually used into `lesson.json` | `python scripts/render.py lesson.json --tier draft` | ManimCE 0.22.0 |
| `scripts/frames.py` | Per beat: a frame per mark, the last frame, a six-frame contact sheet; reads the bounding-box log; boundary continuity check (section 9) | after a draft render | ffmpeg, Pillow |
| `scripts/assemble.py` | Concat demuxer, beat WAVs at index offsets, two-pass `loudnorm`, optional saturation, AAC mux, SRT | `python scripts/assemble.py lesson.json` | ffmpeg |
| `scripts/verify.py` | Hard gates: two streams; container within 0.5 s of the summed audio; per beat, the run log's entry and exit clock within 0.25 s of the section index, and the WAV duration not longer than the rendered beat; every beat's mark time inside its beat; no `manimlib`; all scenes indexed; LaTeX clean; writes `report.md`; a failing file is never delivered | last stage | ffprobe |
| `scripts/selftest.py` | Tests over generated fixtures for every script, including a synthetic storyboard for `storyboard_check.py`, synthetic clips for `frames.py` and a fake `manim` executable for `render.py`; `--patterns` and `--one-beat` with ManimCE | before every commit | none |
| `scripts/mtv/lesson.py` | Schema, single parser, stage hashes, resume, retry counters | imported by every script | Python |
| `scripts/mtv/narrated.py` | `NarratedMixin` with `beat()`, `until()`, `remaining()`, run log and bounding-box log; concrete `NarratedScene(Scene)`, `NarratedCameraScene(MovingCameraScene)`, `Narrated3DScene(ThreeDScene)` | imported by generated `lesson.py` | ManimCE |
| `scripts/mtv/look.py` | `threeb1b` template plus `\minus`, serif font list with the font actually found reported back, role colors (`PURE_YELLOW`) | imported by generated `lesson.py` | ManimCE |
| `scripts/mtv/patterns.py` | Sixteen original helpers (section 6) | imported by generated `lesson.py` | ManimCE |
| `references/*.md` | framework, patterns, rubric, pipeline, roles, ManimCE table, analyses | by the load-order table | none |
| corpus repo `tools/corpus/*.py` | fetch, transcribe, scenes, sections, anchors, `narration_stats`, `cite_check`, `census`, `sync_to_kit` | build time only | yt-dlp with `yt-dlp-ejs` and a JavaScript runtime (Node or Deno), faster-whisper, ffmpeg |

### 3. Data flow

`lesson.json` is the only contract. Every field has exactly one writer, and
the file carries a `stages` block with the sha256 of each stage's inputs and
the tool versions used, so a re-invocation resumes at the first stage whose
inputs changed (B's `state.json` folded into C's contract, as the reliability
judgment proposed).

```json
{
  "schema": "mtv-lesson/1",
  "slug": "what-a-neuron-computes",
  "title": "What a neuron computes",
  "audience": "motivated adult non-specialist",
  "target_minutes": 5,
  "tier": "standard",
  "provider": "kokoro",
  "colors": {"weight_pos": "BLUE", "weight_neg": "RED", "bias": "MAROON_B",
             "cost": "RED", "emphasis": "PURE_YELLOW"},
  "scenes": [
    {"id": "s01", "title": "A working thing first", "scene_class": "S01WorkingThing",
     "scene_kind": "flat",
     "opening_state": "black", "closing_state": "network scaled 0.75 at bottom, digit grid upper left",
     "beats": [
       {"id": "s01-b01",
        "narration": "Here is a network that already reads handwritten digits.",
        "marks": {"reveal": 7},
        "visual": "784-16-16-10 network fades in at the bottom; a seeded 28 by 28 pixel grid drawn as squares upper left",
        "patterns": ["LayeredNetwork", "WeightGrid", "flash_along"],
        "moves": ["working-thing-first"],
        "introduces": ["network"], "shows_value_of": [], "symbol_introduced": [],
        "lands": [{"mark": "reveal", "visual": "pixel grid", "lead_s": 0.2}],
        "tail_s": 0.4,
        "audio": "audio/s01-b01.wav", "duration_s": 4.21, "words": "audio/s01-b01.words.json",
        "marks_s": {"reveal": 2.87},
        "render": {"index": 0, "video": null, "duration_s": null, "frames": [],
                   "log": {"enter_s": null, "exit_s": null, "overrun_s": null}}}
     ]}
  ],
  "env": {"pythonpath": null, "font": null, "manim": null, "ffmpeg": null},
  "attempts": {"storyboard_rounds": 0, "fix_passes": 0, "render_retries": {}, "dispatches": 0},
  "checks": {"storyboard": null, "frames": null, "verify": null},
  "stages": {"storyboard": {"inputs_sha256": "...", "done": "2026-11-02T10:00:00Z"}}
}
```

Writers: the brief writes the header; the script stage writes `narration`
as clean prose with no tags; the storyboard stage writes `marks` (mark name
to zero-based word index in the clean text), `scene_kind` (`flat`, `camera`
or `3d`), `visual`, `patterns`, `moves`, `introduces`, `shows_value_of`,
`symbol_introduced`, `lands`, `opening_state` and `closing_state`;
`narrate.py` writes `audio`, `duration_s`, `words`, `marks_s`; `render.py`
writes `render` (including the beat run log that `NarratedMixin` emits) and
`env`; the parent increments `attempts`; the critics and `verify.py` write
`checks`. Marks therefore belong to the storyboard stage, which is the stage
that knows what will land on them, and `storyboard_check.py` rejects a
`lands` entry whose mark has no `marks` index or whose index is outside the
beat's word count. The generated `lesson.py` reads only `audio`,
`duration_s`, `marks_s`, `tail_s` and `narration` (the last for
`add_subcaption`) through the narrated base class. The storyboard fields
`introduces`, `shows_value_of` and `symbol_introduced` come from Approach B
so that "numbers before symbols" is a static predicate before any audio or
code exists; `lands` is the signed lead/lag field the animation judgment
asked for, with a default lead of 0.2 s (show, then name).

### 4. Corpus pipeline

The tooling lives in a separate MIT repository, `manim-3b1b-corpus`, with a
gitignored cache: the kit's gates scan every text file, the installer ships
everything under `skills/<id>/`, and transcripts and figures are third-party
material (map 06 sections 2.3, 3 and
6; map 07 section 6). Only the framework, pattern index and rubric cross
into the kit, through `sync_to_kit.py`, which runs the kit's lint gates
first; whether the paraphrased analyses cross too is decision 8.

| Step | Tool | Output | Notes |
| --- | --- | --- | --- |
| `inventory` | Python over the sparse site clone | `videos.json`: slug, title, YouTube id, date, source files, both chapter numberings | map 07 section 1 |
| `fetch-captions` | `yt-dlp --skip-download --write-info-json --write-subs --write-auto-subs --sub-langs "en.*" --sub-format "json3/vtt" --js-runtimes node` | captions, `info.json` | map 05 section 4; needs `yt-dlp-ejs` plus Node or Deno in the corpus requirements; manual captions unverified |
| `fetch-figures` | `curl` over the public bucket listing, jpg only | `figures/*.jpg`, `figures.json` keyed to paragraphs | 245 captioned frames (map 07 section 2) |
| `fetch-media` | `yt-dlp -f "bv*[height<=1080]+bestaudio"` | mp4 for keyframes | opt-in `DOWNLOAD_MEDIA=1`; deleted after keyframes; terms risk (map 07 section 6) |
| `transcribe` | faster-whisper `large-v3-turbo` int8, word timestamps, VAD, domain prompt | `words.json` | only without manual captions; a multi-hour CPU job (map 05 section 4, low confidence) |
| `scenes` | Python `ast` | `scenes.json`: class, span, bases, `kind`, beat comments, string literals, and per-class counts of every idiom in the map 04 frequency list (`play`, `wait`, `ReplacementTransform`, `LaggedStartMap`, `TransformFromCopy`, `reorient`, and the rest) | map 01 appendix A; these counts, not the maps, are what `census.py` reads |
| `sections` | reader-made in M2: a reader lists `(t_start, t_end, class list)` per transcript section, assisted by a `grep` of string literals against the captions | `sections.json` with a per-section confidence set by the reader | about 30 minutes per video (map 07 section 4); the monotonic dynamic program and the figure bridge move to M5 |
| `anchors` | reader adds three to six `(time, class)` pairs where a section lists more than one spine class | `anchors.json` | folded into `sections` for the two-video release |
| `narration_stats` | Python over captions and `sections.json` | per section: words, sentences, mean sentence length, questions, second-person pronouns, hedge phrases from a fixed list, time of the first formula as a fraction of runtime | facts, not text; feeds the voice rules (section 6) |
| `analyze` | subagents (section 5) | `analyses/<slug>/<section>.json` | parent writes files |
| `cite_check`, `census` | Python | pass or fail per record; `census.md` | section 5 |
| `sync-kit` | Python | copies into the kit worktree | gates first |

Release scope is two videos: chapter 1 (`aircAruvnKk`, `_2017/nn/part1.py`,
one file, 2D) and chapter 6 (`eMlx5fFNoYc`, `attention.py` plus
`embedding.py` lines 2232 to 2566 and `supplements.py` lines 841 to 1338, 3D
camera and role colors): both visual regimes, one easy and one multi-file
alignment. Map 07 section 3 marks the chapter-to-file mapping as inferred
from class names and definition order, and map 02 section 1.1 assigns the
three `embedding.py` scenes to chapter 6; the census is told exactly these
ranges so that scenes outside them are neither missed nor flagged. The
other six videos and the 2026 code are the extension loop, the same steps
repeated; the citation checker and census apply from the first video.

### 5. Analysis record schema

One JSON record per aligned transcript section, rendered to
`references/analyses/<slug>.md` by one script.

```json
{
  "video_id": "aircAruvnKk", "lesson": "neural-networks", "section_id": "s09",
  "t_start": 712.0, "t_end": 798.5, "title": "Weights as a pixel grid",
  "narration_summary": "paraphrase, 40 to 120 words, no 13-word verbatim run",
  "question_planted": "what are these connections actually doing?",
  "admitted_uncertainty": null,
  "scenes": [{"class": "IntroduceWeights", "file": "_2017/nn/part1.py",
              "line": 2237, "end_line": null, "kind": "spine"}],
  "beats": [{"beat_id": "b03", "t_start": 741.0, "t_end": 760.0,
             "narration_gist": "the 784 weights laid out as a 28 by 28 grid",
             "visual": "parameter list morphs into a pixel grid beside the digit",
             "lead_lag_s": -0.4,
             "code_evidence": [{"file": "_2017/nn/part1.py", "lines": "2497-2541"}],
             "animations": ["ReplacementTransform", "LaggedStartMap"],
             "timing": {"run_time": [2, 3], "waits": [1, 1, 2]},
             "figures": ["lessons/2017/neural-networks/weights-grid.jpg"]}],
  "moves": ["formula"],
  "technique_tags": ["numbers-before-symbols", "provenance-transform", "zoom-to-one-unit"],
  "colors": {"positive_weight": "GREEN", "negative_weight": "RED", "emphasis": "PURE_YELLOW"},
  "layout": "network scaled 0.8 at bottom; grid upper left; formula top strip",
  "why_it_works": ["one sentence per beat id"],
  "manimce_notes": ["ShowCreationThenDestruction -> ShowPassingFlash(copy, time_width=1.0)"],
  "narration_stats": {"words": 212, "sentences": 11, "mean_sentence_words": 19.3,
                      "questions": 2, "second_person": 5, "hedges": 1},
  "confidence": 0.85, "verified_by": ["refuter", "anchor"]
}
```

Controlled vocabularies are fixed before analysis: `moves` are `hook`,
`concrete`, `abstraction`, `formula`, `recap`, `aside`, `meta`, `outro` (map
01 section 1); `kind` is `spine`, `support`, `overlay`, `ambient`,
`thumbnail`, `end_screen`, `stub`, `utility`, which extends the five-value
list map 03 section 4.3 proposes (`main`, `overlay`, `ambient`, `thumbnail`,
`end_screen`) by splitting `main` into `spine` and `support` and adding two
housekeeping values; `technique_tags` are Approach A's 24 tags plus
`motion-with-a-reason`, `transitions-reuse-geometry` and `recurring-cast`
(animation judgment). `lead_lag_s` is negative when the visual lands before
the word. `section_id` names a transcript span, the corpus-side meaning of
"section" fixed in section 1. Class names are stored in `scenes[].class` for
`cite_check.py` but the renderer that writes `references/analyses/<slug>.md`
emits only `file:line` citations in prose, never the class identifier, so a
misspelled upstream class name can never trip the kit's `typos` gate (map 06
section 3.3; the critique's probe showed identifiers containing a dictionary
misspelling do fail).

Roles per video, in waves of four to six: a **section analyst** per aligned
section receives the transcript slice, the full source of every aligned
class (whole, so straddling spine scenes are not sliced),
one-line summaries of the neighboring sections, the figure captions in range
and the schema; a **video merger** writes the arc, color contract and recap
devices; a **refuter** tries to disprove three random claims per record from
the cited lines and timestamps. A record passes the refuter only with zero
disproved claims; one disproved claim returns the record to its analyst,
never patched by hand, and a video whose records need more than two refuter
rounds in total is flagged in `census.md` for the owner.

`cite_check.py` rejects a record when a code citation falls outside the
cited class's AST span or names no animation listed in the beat, a transcript
citation overlaps no word, a figure path does not exist, a 13-word run of the
summary appears verbatim in the transcript, or a tag is outside the
vocabulary. `census.py` checks that every `spine` and `support` class in the
release ranges has a record, every transcript minute belongs to one section,
and the per-video tag histogram is consistent with the per-class idiom counts
emitted by the `scenes` step: for each idiom-to-tag pair in a fixed table
(for example `ReplacementTransform` to `provenance-transform`,
`LaggedStartMap` to `staggered-reveal`, `reorient` to `camera-move`), the
number of records carrying the tag must be at least 30 percent of the number
of analyzed classes that use the idiom, otherwise the video fails the census
and its analysts are re-dispatched with the gap named. The maps' grep counts
(map 01 section 9; map 02 section 5.1) are a sanity check on the `scenes`
step, not the census input, because map 02 counts lines summed over ten
files and gives per-file counts only for four idioms (map 02 section 9.1).

### 6. Framework representation

`references/framework.md` holds about 30 rules, `R01` to `R30`, in seven
groups (narrative, voice, visual, color, layout, timing, honesty), each with
the same fields (Approach A's form plus B's `Fails` and C's `Scope`):

```text
R07 numbers-before-symbols
Statement: show a quantity as a concrete number before its symbol; the symbol
  arrives by transforming a copy of the number.
Why: decimals sit in neurons long before the first weighted sum (analyses
  neural-networks s04, s09; attention s03).
Apply: a beat with symbol_introduced [x] follows a beat with shows_value_of [x].
Check (storyboard): storyboard_check.py evaluates the Apply predicate.
Check (frames): the introducing beat's mark frame still shows the source.
Scope: scenes introducing notation; a recap may show a known symbol.
Fails: a first beat that writes a = sigma(Wx + b).
```

Timing rules follow the measured distributions: `run_time` 1 s confirmations,
2 s meaning-carrying transforms, 3 to 5 s multi-part reveals, 8 to 12 s
orbits; `wait` 1 s after most plays, 2 s closing a step; long holds only
where narration, ambient motion or an orbit carries the moment; `lag_ratio` 0.1 crowds, 0.5 sequential reveals (map 01 sections 5.2 and 6.4; map
02 sections 5.1 and 6.2). The color contract is the later 2017 convention
plus the 2024 roles, GL `YELLOW` becoming `PURE_YELLOW` (map 01 section 3; map 02 section 3.1; map 04 constants row).

Voice rules. Paraphrase does not carry voice, so the voice group is derived
from the `narration_stats` facts (section 4), not from the paraphrases:
three to five rules with numeric `Apply` predicates that
`storyboard_check.py` evaluates on the clean `narration` text, for example
"a beat is 1 to 3 sentences and at most 60 words", "at least one question
per two minutes of script", "second person or first person plural, never
third person about the learner", "the first formula appears after at least
one concrete beat and no later than the measured corpus fraction plus 20
percent", and "at least one beat per lesson carries an admitted
uncertainty or a stated simplification". The thresholds are placeholders
until M2 computes the corpus values; the rule form and the check are fixed
now so that the scriptwriter is checked, not only the storyboarder.

Asset policy (v1). Visuals are vector only: every noun helper draws from
numbers, and the data behind a visual is seeded synthetic data generated in
`lesson.py` (the precedent is the 2026 `transformer_render.py`, which draws
procedural point clouds from synthetic values, map 02 section 10 item 8). No
raster assets, no `ImageMobject`, no dataset download, no network access at
render time; `check_scenes.py` rejects `ImageMobject` and file reads, and
the storyboard critic rejects a `visual` that names an image or a real
dataset. Real data (an MNIST digit, GloVe vectors) is an M5 extension behind
an explicit asset manifest. Fonts: `look.py` tries, in order, CMU Serif,
Latin Modern Roman, TeX Gyre Termes, DejaVu Serif, then Pango's default
serif, and reports the font it found; `render.py` records it in
`lesson.json` under `env.font`, `preflight.py` warns when the first two are
absent, and the frame critic is told which font to expect. CMU Serif is
3b1b's text font (map 03 section 1.1) but is not a default Linux font (map
03 section 7, availability unverified), so the fallback list is the design,
not a hope.

`references/patterns.md` indexes `scripts/mtv/patterns.py`: sixteen
original helpers in six groups, nouns (`LayeredNetwork`,
`NumericColumn`, `WeightGrid`), provenance (`provenance`,
`numbers_to_symbol`, `save_and_restore_layout`), emphasis (`flash_along`,
`focus_and_dim`, `nudge_and_return`), numbers (`count_parameters`,
`live_decimal`), camera (`zoom_to`, `orbit_with_hud`), narration
(`staggered`, `delayed` for `time_span`, `question_caption`). The last is
the original device that replaces the Pi-creature reaction beat: a caption
in the learner's words with an arrow to the object in question, held until
the narration answers it, so the rubric item "question before answer" has a
helper and a storyboard move to point at (Approach A's `PT-42` and `PT-43`
idea, `architectures/corpus-fidelity.md:396`). `zoom_to` requires
`NarratedCameraScene` and `orbit_with_hud` requires `Narrated3DScene`; a
scene cannot both zoom in 2D and orbit in 3D, and `manimce.md` says so.
Docstrings cite map and line; `selftest.py --patterns` renders one example
per helper, so sixteen is also the test budget. The 2024 nouns are one
helper each in the extension loop (map 02 section 13).

`references/manimce.md` also records two TeX facts the implementer will
otherwise trip over: `TexTemplateLibrary.default` and `threeb1b` are the
same preamble (CE `tex_templates.py:64-67`), but `TexTemplate()` with no
arguments, which is what an empty `tex_template` key in `manim.cfg` yields
(CE `default.cfg:144`), is the three-package preamble (CE `tex.py:21-23,50`);
and `threeb1b` loads `calligra`, `tipa`, `wasysym`, `dsfont`, `physics` and
`mathrsfs` (CE `tex_templates.py:33-42`), which on Debian-family systems
means `texlive-fonts-extra` and `texlive-science` on top of the base
packages, a multi-gigabyte install that `preflight.py` names in its stop
message (map 03 section 1.3 for the package list 3b1b's README gives).

`references/rubric.md` scores 16 items 0 to 2, each with an anchor per score
and its rule ids: teaching (hook before definition,
destination previewed, value before symbol, one idea per scene, question
before answer, honesty beat, picture carried into the recap), voice (beat
length, person and question cadence as the voice rules define them), visual
(role colors, dim not delete, captions beside referents, object budget,
legible at 480p, scene boundaries continuous or deliberately cleared),
motion (every move has a reason, nothing teleports, staggers and eased
travel where the corpus uses them; scored from the six-frame contact sheet,
never from one still), sync (the named visual on screen at each mark frame).
Pass: at least 25 of 32, no zero. Hard gates are `verify.py`'s scripted
checks (section 2). Calibration: paraphrased storyboards of two real
sections must score at least 27 of 32, or the rubric is wrong, not the
corpus (animation judgment).

### 7. Skill structure and run-time process

`SKILL.md` is a kit-voice orchestrator of about 1,500 words: frontmatter with
`compatibility`, `description` (capability plus trigger phrases, no workflow
summary), `enabled`, `id` and `name` in sorted order (map 06 section 1.2);
the no-model-pins paragraph; a triage line said out loud; numbered steps;
roster; load-order table; "a valid run" checklist; guardrails.

```text
0. Triage out loud: tier (draft | standard | final), length, provider, output dir mtv-runs/<slug>/.
1. Preflight: python scripts/preflight.py --json; hard stop with install lines.
2. Brief: at most three questions (audience, length, premium provider if a key is present).
3. Script: one scriptwriter reads framework.md and writes clean narration; python scripts/storyboard_check.py --script checks the word budget and the voice rules; one retry.
4. Storyboard: one storyboarder writes marks, scene_kind and the visual fields; python scripts/storyboard_check.py rejects unresolved marks and failed Apply predicates; one storyboard critic (MANDATORY); two rounds, then ask.
5. Narrate: python scripts/narrate.py lesson.json.
6. Scenes: one scene coder per scene in waves of four; python scripts/check_scenes.py lesson.py lesson.json.
7. Draft render and frame review: render.py --tier draft --jobs N; frames.py; one frame critic per scene.
8. Fix loop: failed beats return to their coder; at most two passes; only failed scenes re-render.
9. Final render in the background, estimate printed first.
10. Assemble and verify; never deliver a file that failed verify.
11. Report: path, duration, tier, provider, voice and model, font used, rubric totals, hard-gate table, render time, how to resume.
```

The five roles (scriptwriter, storyboarder, storyboard critic, scene coder,
frame critic) are inlined prompts in `references/roles.md`, each with goal,
inputs by path, the one reference to read, the output contract and "cite the
rule id you applied"; the kit allows inlining into the generic agent when a
named type is unavailable (map 06 section 4.1), which avoids the `AGENT_REF`
and README changes for v1. The load-order table keeps context small: the
parent never loads the pattern index or the analyses; the scriptwriter reads
`framework.md`; the storyboarder adds the pattern index; a scene coder reads
only its scene of `lesson.json`, the docstrings of the patterns it names, and
`manimce.md`; critics read `rubric.md` and the artifact under review. The
parent holds the header and the gate results only. The hand-off trigger is
observable, not felt: the parent increments `attempts.dispatches` on every
subagent dispatch, and when the count reaches 48 (a pre-M0 default; a
five-minute lesson of six scenes needs about 20 in the happy path) it stops
with a resumable `lesson.json` and tells the user to rerun, which resets
the counter but not the stage hashes.
Subagent returns are validated by the parent's scripts; a non-conforming
return is re-dispatched once with the validation error, then the run stops.

### 8. Narration and sync

Default provider: Kokoro-82M, voice `af_heart`, speed 1.0, 24 kHz, offline,
Apache-2.0 weights from Hugging Face, per-token `start_ts` and `end_ts` from
`KPipeline.join_timestamps` (map 05 section 2). Premium: ElevenLabs
`convert_with_timestamps`, character-level alignment, with `previous_text`
and `next_text` passed for prosody across beats, key from
`ELEVENLABS_API_KEY` only. A `null` provider writes silence and evenly spaced
words for tests. Piper is not a silent fallback because its voices are
"intended for personal use and text to speech research only" (map 05
section 2); it is an explicit opt-in that the report names. The provider
protocol is one function, `synthesize(text, out_wav) -> list[Word]`; a
provider returning `[]` triggers proportional interpolation with a warning in
the report, and forced alignment is an extension. manim-voiceover is not a
dependency (stale `elevenlabs<0.3` and `openai<2` pins, whisper-interpolated
bookmarks, `--disable_caching` requirement, renderer internals across the
0.22 `Manager` refactor; map 05 section 1), but its `voiceover()` and
`<bookmark/>` ergonomics are kept.

Marks are not inline tags. The scriptwriter's `narration` is clean prose,
and the storyboarder writes `marks` as a map from mark name to the
zero-based index of the word the animation lands on (section 3); the
storyboarder may also ask for a wording change through the critic, which
sends the beat back to the scriptwriter rather than editing `narration`
itself. `narrate.py` synthesizes the clean text, then aligns script words to
provider tokens with a per-provider matcher in `mtv/tts.py`: the script side
is normalized (lower case, punctuation stripped, digits expanded with
`num2words`), and the provider side is normalized the same way or left as
is depending on what that provider's tokens contain, because Kokoro attaches
timestamps to misaki tokens whose text for a numeral such as "784" is
unverified (map 05 section 2; an M0 measurement), while ElevenLabs returns
both `alignment` and `normalized_alignment`. A matcher that fails for a beat
falls back to proportional interpolation and says so in `report.md`. The
mark time is the aligned token's start. This is the normalization step the
reliability judgment found missing.

`NarratedMixin.beat(beat_id)` is a context manager available on
`NarratedScene`, `NarratedCameraScene` and `Narrated3DScene` (CE has no
single class with both a movable 2D frame and a 3D camera, CE
`moving_camera_scene.py:104`, `three_d_scene.py:31`): it calls
`next_section(beat_id)` and `add_subcaption`, yields `b` with `b.duration`,
`b.until(mark, lead=0.2)` (seconds from the scene clock to the mark minus the
lead, clamped to one frame so CE never sees `run_time <= 0`, CE
`scene.py:1141-1168`) and `b.remaining()`; `wait()` is allowed inside the
beat for the corpus rhythm; on exit it pads with
`wait(max(target_end - self.time, 1/fps))`, where `target_end` is the
cumulative audio plus `tail_s` from the scene start, so quantization error
never accumulates (`Scene.time` is the renderer clock, CE
`scene.py:286-288`, advanced by whole frames, CE `cairo_renderer.py:210`);
it logs every mobject's bounding box and any overrun. It also appends one
run-log line per beat, `(beat_id, time at entry, time at exit, audio
duration, overrun)`, to a file beside the render that `render.py` copies into
`render.log`. That log is the sync gate's independent witness: `verify.py`
compares it to the section index (entry and exit within 0.25 s of the
index's cumulative durations) and to the WAV durations (a WAV longer than
its rendered beat fails), so the gate measures what can actually drift
instead of comparing the index against offsets derived from the same index,
the circularity the critique found in Approach C and the earlier draft.
Scenes render silent. `assemble.py` places each beat WAV at the beat's start
offset from the index, so a re-render moves the audio with it and a voice
change re-renders nothing; `tail_s` (0.4 s, 1.0 s on scene-closing beats) is
the breath between beats. `render.py` runs up to `--jobs N` scene processes
at once (default CPU count minus one; Cairo is single-threaded per scene and
CE's own `max_inflight_encoders` key defaults to 1, CE `default.cfg:118`),
and M0 measures sequential against concurrent throughput. The narration
track is normalized to -16 LUFS and
-1.5 dBTP in two passes, and the video pass applies `eq=saturation=1.5` by
default because 3b1b's encoder does (map 03 section 1.1); `--saturation 1.0`
disables it.

### 9. Error handling

| Failure | Detection | Response |
| --- | --- | --- |
| Tool missing (Python version, manim, latex, dvisvgm, ffmpeg, provider) | `preflight.py` | stop; print the install line per tool; on Python 3.13 print the Kokoro GitHub install line |
| Malformed subagent return | the parent's schema check (`storyboard_check.py`, `check_scenes.py`) | re-dispatch once with the error text; then stop |
| GL-only name, `play(mob.method)`, color outside the contract | `check_scenes.py` | reject before render with the `manimce.md` translation row |
| Render exception | `render.py` regex over the traceback against the 24-row error table (map 04) | the owning coder retries with the row's fix text; three attempts per scene, then the parent swaps the scene's patterns for simpler ones once, then stops |
| Hung render | no log line for ten minutes | kill, retry once with `--disable_caching` |
| `latex error converting to dvi` | render log | show the offending lines; coder fixes; a missing package is added only in `look.py` |
| Beat missing from the index | `render.py` compares to `lesson.json` | `beat()` always waits, so this is an exception inside the beat; surface the traceback |
| Animation overruns its audio | `NarratedScene` log | allowed up to 1.0 s; beyond that the coder shortens `run_time` or splits the beat |
| Mark does not resolve to a word | `storyboard_check.py` (index missing or out of range) | storyboarder fixes `marks`; if the wording must change, the critic returns the beat to the scriptwriter; counts as a storyboard round |
| Provider tokens cannot be aligned to a mark | `narrate.py` matcher | proportional interpolation for that beat, named in `report.md`; never a stop |
| Clipped mobject or illegible text | bounding-box log; frame critic | coder re-lays out; re-render that scene only |
| Jump cut at a scene boundary | `frames.py` continuity check: the previous scene's last frame and this scene's first frame, both downscaled to 64 by 36 grayscale, differ by a mean absolute pixel difference above 0.15 (0 to 1 scale, pre-M1 default) while `opening_state` is not `black` | coder rebuilds the previous `closing_state` before the first beat; the threshold is calibrated on M1's two-scene lesson |
| Final render over budget | estimate from the draft pass scaled by pixels and fps | ask before spending more than 45 minutes; suggest a lower tier |
| Provider network failure | `narrate.py` | retry three times with backoff; fall back to Kokoro and say so |
| Interruption or usage limit | `stages` hashes in `lesson.json` | rerun the skill; it resumes at the first changed stage |

`opening_state` is a small enumeration the checker can parse: `black` (the
scene starts from an empty frame, so no continuity check), `continue` (the
scene must rebuild the previous `closing_state` before its first beat and the
continuity check runs), or `cut` (a deliberate hard cut the storyboard critic
has approved, recorded so the check is skipped on purpose). `closing_state`
stays free text for the coder; only `opening_state` is machine-read.

Every bounded loop is counted in `lesson.json` under `attempts`, and the
values below are the pre-M0 defaults that M0 and M3 may tighten but not
loosen without a note in `report.md`:

| Loop | Bound | Counter | After the bound |
| --- | --- | --- | --- |
| Script word budget or voice rule | 1 retry | `attempts.script_retries` | ask the user |
| Storyboard check plus critic | 2 rounds | `attempts.storyboard_rounds` | ask the user |
| Malformed subagent return | 1 re-dispatch per call | `attempts.redispatches` | stop |
| Render exception per scene | 3 attempts, then 1 pattern simplification | `attempts.render_retries[scene]` | stop |
| Hung render per scene | 1 retry with `--disable_caching` | `attempts.render_retries[scene]` | stop |
| Frame-review fix loop | 2 passes | `attempts.fix_passes` | deliver with the failing rubric items listed, or stop if a hard gate fails |
| Provider network failure | 3 retries with backoff | `attempts.provider_retries` | fall back to Kokoro |
| Parent hand-off | 48 dispatches | `attempts.dispatches` | stop with a resumable `lesson.json` |
| Sync gate | 0.25 s per beat, 0.5 s per container | not a loop | the value is the pre-M0 default; M0 may tighten it to the measured frame quantization but never loosen it |

"Stop" always means: write `report.md` with the failing gate, keep every
artifact, and say how to resume. The skill never installs TeX Live, never
reads keys from files, and never commits.

### 10. Testing

Scripts. `python scripts/selftest.py` runs without ManimCE: schema accept and
reject fixtures, `storyboard_check.py` against a synthetic storyboard with
one unresolved mark and one failed `Apply` predicate, `check_scenes.py`
against a fixture containing every banned GL name and a `scene_kind`
mismatch, `narrate.py` with the `null` provider, `render.py` against a fake
`manim` executable that writes a section index and a run log, `frames.py`
over two synthetic clips that do and do not jump, `assemble.py` and
`verify.py` over synthetic clips and a tone WAV generated by ffmpeg, and a
run log shifted by 0.5 s that must fail the sync gate. With ManimCE present
it adds `--patterns` (every helper's example renders at `-ql`) and
`--one-beat` (a one-scene, one-beat lesson renders, assembles and verifies
in under two minutes). The kit has no Python gate (ADR-0002), so the
implementation session runs it before every commit and records the output
in the PR. Shared code lives in `mtv/common.py`, and eval `case.yaml` files
and JSON fixtures are rendered from one template by `selftest.py --fixtures`
rather than committed as near-duplicates, so jscpd's 5 percent threshold
over a small denominator is not tripped (map 06 section 3.4).

Framework. Three tests run before the skill exists: the rule discrimination
micro-test (one compliant and one violating storyboard snippet per rule,
graded by a critic holding only the rule text; a rule that does not separate
them is rewritten), the rubric calibration against two paraphrased corpus
storyboards (section 6), and a framework-only storyboard test on the fixed
prompts scored by the storyboard critic.

Skill, following the writing-skills method and the skill-creator layout (map
06 section 5.3). Fixed prompts: T1 "what a single neuron computes" (corpus,
2D), T2 "why gradient descent follows the negative gradient" (adjacent, one
orbit), T3 "how softmax turns scores into probabilities, with temperature"
(2024 topic without 2024 helpers), T4 "why binary search is fast" (off
domain, few formulas). Three pressure scenarios: render before the storyboard
passes under time pressure, "LaTeX is missing, just use Text and do not
mention it", "the audio is two seconds off, ship it". RED runs without the
skill into the gitignored `manim-teaching-video-workspace/`; eval cases are
written first under `evals/<case>/{prompt.md,case.yaml,graders/}` with
objective graders (MP4 exists; ffprobe shows two streams; durations within
0.5 s; no `manimlib`; beat count equals the index; `report.md` present) plus
one LLM grader applying `rubric.md`; GREEN runs with and without the skill in
the same turn. Every eval markdown file (`prompt.md`, each grader file)
opens with an H1 and every fence names a language, because
`.markdownlint-cli2.jsonc` has no ignores and `evals/**/*.md` is linted (map
06 section 3.1).

Eval budget. The inner loop, used for every GREEN and REFACTOR iteration,
runs storyboard, `check_scenes.py` and `--dry_run` only, so it costs
subagent time but no render; one full-tier run (render at `draft`) per
prompt closes each iteration, with the four prompts run concurrently. The
three-runs-per-prompt rule applies once, at release, again concurrently:
twelve with-skill and twelve baseline runs. M0 produces the wall clock of
one full-tier run on four CPUs, and M3's day budget is derived from it as
(iterations times four plus 24) runs; if one run exceeds 20 minutes the
release-time count drops to two runs per prompt and the proposal says so in
the PR. Pass: all four prompts clear every objective grader on every
release run; the rubric passes on at least three prompts; the baseline fails
at least one objective grader on at least three of four prompts, otherwise
the skill adds nothing measurable; every pressure scenario ends with the
agent citing the rule it refused to break.

### 11. Repo layout and kit changes

```text
skills/manim-teaching-video/
  SKILL.md
  references/framework.md  patterns.md  rubric.md  pipeline.md  roles.md  manimce.md
  references/analyses/neural-networks.md  analyses/attention.md   (option B of decision 8 only)
  scripts/preflight.py  narrate.py  storyboard_check.py  check_scenes.py  render.py
  scripts/frames.py  assemble.py  verify.py  selftest.py
  scripts/requirements.txt  requirements-kokoro.txt
  scripts/mtv/__init__.py  common.py  lesson.py  look.py  narrated.py  patterns.py  tts.py
  assets/manim.cfg.draft  manim.cfg.standard  manim.cfg.final  lesson.example.json
  evals/<case>/prompt.md  case.yaml  graders/NN-*.md
docs/research/manim-teaching-video/  (the seven maps, three architectures, three judgments, this proposal)
docs/adr/0008-skills-may-ship-scripts-and-references.md
manim-3b1b-corpus/   (separate MIT repository; see section 4)
```

Kit changes, each a single expression where possible (map 06 sections 2.2
and 7): `scripts/install.sh` ships every regular file under `skills/<id>/`
except `SKILL.md`, `evals/`, `__pycache__` and `*.pyc` (today only `*.md`
ships, so `scripts/` would be silently dropped); `scripts/validate.sh`
excludes `evals` from the markdown reference scan; `validate.yml` adds
`test -f` smoke lines for the installed `skill.md`, `scripts/mtv/narrated.py`
and one reference; `README.md` skills count and install note; `CHANGELOG.md`
`Unreleased` entry; `.gitignore` adds the anchored patterns
`/manim-teaching-video-workspace/`, `/mtv-runs/` and `/media/`; ADR-0008 in
the kit's one-paragraph voice. The run directory is `mtv-runs/<slug>/`, not
`mtv/<slug>/`, and the patterns are anchored, because an unanchored `mtv/`
matches at any depth and would ignore the shipped
`skills/manim-teaching-video/scripts/mtv/` package itself (the critique
verified this with `git check-ignore` in a scratch repository). The import
path is explicit: `render.py` runs `manim` with `PYTHONPATH` set to the
skill's `scripts/` directory, records that path in `lesson.json` under
`env.pythonpath`, and the generated `lesson.py` carries no `sys.path` edit;
`selftest.py --one-beat` imports `mtv` the same way. No `AGENT_REF` change
because no agents are added. Requirements are split: `requirements.txt`
pins `manim==0.22.0`, `soundfile`, `elevenlabs`, `num2words`, `Pillow`;
`requirements-kokoro.txt` pins `kokoro==0.9.4` for Python 3.11 and 3.12 (its
PyPI metadata is `requires_python <3.13,>=3.10`), and `preflight.py` prints
the install line that matches the interpreter it finds, the GitHub line on
3.13, so an ElevenLabs-only user never installs torch and a 3.13 user never
sees `pip` fail before the preflight message. All skill markdown avoids bare
absolute paths, `~/` paths and `> /dev/null` because `validate.sh` scans
fences too (map 06 section 1.4); tables use the compact style for MD060.

Research hygiene. The seven maps, three architectures, three judgments and
this proposal go under `docs/research/`, where the hygiene job runs `typos`,
markdownlint and lychee over them (map 06 section 3) and ADR-0006 forbids
relaxing the configs. The critique ran the kit's `typos` config over the
design directory and found seven errors, all verbatim misspelled upstream
identifiers in maps 01 and 02, and maps 01 and 07 use the `|---|---|`
separator style that MD060 flags under the CI-pinned markdownlint 0.41.1;
this revision ran the cached `markdownlint-cli2` 0.23.2 with the kit's
config over the design directory and confirmed it: 86 MD060 errors in map
01, 72 in map 07, none in this proposal or the other twelve files.
Before the PR, the implementation session rewrites each misspelled
identifier as a `file:line` reference, converts every separator row to
`| --- |`, and runs `markdownlint-cli2` 0.23.2, `typos` and lychee in the
worktree; the PR records their output. The same rule binds
`references/analyses/*.md` through the renderer rule in section 5.

### 12. Phasing and milestones

| M | Scope | Effort | Proves |
| --- | --- | --- | --- |
| M0 spike | `uv venv --python 3.12` (the implementation container defaults to Python 3.13 but ships 3.11 and 3.12 and `uv`, per the critique's inventory); install ManimCE 0.22.0, TeX Live with `texlive-fonts-extra` and `texlive-science`, Kokoro; hand-write a two-beat scene on each of the three narrated base classes; render `-ql --save_sections`; synthesize two sentences; mux by hand; measure render seconds per second at each tier with `--jobs 1` and `--jobs 3`, the wall clock of one full draft-tier run, Kokoro real-time factor and the token text it returns for numerals, install size and time, `wait()` frame quantization, and whether `apt-get` reaches a Debian mirror; confirm that silent renders cache cleanly (`DecimalNumber` needing LaTeX is already settled: its digits are `MathTex` by default, CE `numbers.py:87`) | 1 day | every budget constant is a measurement |
| M1 runtime | `mtv/` package, the nine scripts, `manim.cfg` tiers, `selftest.py`; a hand-written two-scene `lesson.json` plus `lesson.py` yields a verified MP4 with no model in the loop; the continuity threshold is calibrated on its one scene boundary and the sync gate is shown to fail on a shifted run log | 2 to 3 days | the contract and the sync hold end to end |
| M2 corpus pilot and framework v0 | corpus repo; chapters 1 and 6 through fetch, reader-made sections, `narration_stats`, per-section analysts, refuter (zero disproved claims per record), `cite_check` (every record passes), census (every spine and support class covered, tag ratio at least 30 percent); `framework.md` including the voice group, `patterns.md` with all sixteen helpers, `rubric.md`, `pipeline.md`, `roles.md`, `manimce.md`; rule discrimination test (every rule separates its pair); rubric calibration (27 of 32 on two paraphrased sections); framework-only storyboard test (storyboards for T1 to T4 written from `framework.md` alone score at least 25 of 32 with the storyboard critic) | 3 to 4 days | the framework teaches without the orchestrator and rests on checked evidence |
| M3 skill TDD | RED baselines on T1 to T4 and the pressure scenarios; eval cases; `SKILL.md` GREEN; with-skill runs on the inner loop plus one full-tier run per prompt per iteration; REFACTOR; release runs (three per prompt, concurrent) with the day budget derived from M0's per-run wall clock | 3 to 4 days, revised after M0 | the skill measurably beats the baseline |
| M4 kit integration | installer, validator and workflow changes, ADR-0008, README, CHANGELOG, all hygiene gates in the worktree, PR | 1 day | the kit ships the skill intact to a sandbox home |
| M5 extension loop | remaining six videos one at a time; 2024 noun helpers; keyframe extraction; forced alignment and more providers; a fifth prompt; description optimization with `run_loop.py`; promotion of roles to `agents/` when a second skill reuses them | repeat of M2 or M1 steps | each addition is a repeat, not new design |

First release at the end of M4, about ten to thirteen focused agent-days.
Work happens in a worktree at `$HOME/worktrees/.agents/<branch>` per the
kit's rule.

## Assumptions

1. The default narration provider is Kokoro-82M, voice `af_heart`, speed
   1.0, 24 kHz, installed from PyPI on Python 3.11 or 3.12 (the PyPI wheel
   declares `<3.13`; ManimCE 0.22.0 requires 3.11 or newer), from GitHub on
   3.13.
2. The default video length is 5 minutes, accepted range 3 to 8, with the
   skill asking when a topic implies more than 10; the word budget is 150
   words per minute.
3. The default tier is `standard` (1920x1080 at 30 fps); `draft` is 854x480
   at 15 fps; `final` is 3840x2160 at 30 fps and only on request.
4. ManimCE is pinned at 0.22.0 with the Cairo renderer; the consumer runs
   Python 3.11 or 3.12. M0 runs on 3.12 in the implementation container,
   which closes this assumption for that environment only, not for
   consumers.
5. A LaTeX distribution with `dvisvgm` is required; `look.py` selects CE's
   shipped `TexTemplateLibrary.threeb1b` and adds only the `\minus` macro.
   On Debian-family systems the template's packages mean
   `texlive-fonts-extra` and `texlive-science` in addition to the base
   packages, a multi-gigabyte install the preflight message names; the
   exact size is measured in M0.
6. ffmpeg 6 or newer is on the PATH for assembly, even though ManimCE itself
   encodes through PyAV.
7. Narration is English only, one voice per lesson.
8. The encode pass applies `eq=saturation=1.5` by default to match 3b1b's
   file-writer setting.
9. The beat tail is 0.4 s, 1.0 s for scene-closing beats; the default mark
   lead is 0.2 s.
10. The rubric pass bar is 25 of 32 with no zero (16 items including voice
    and motion); hard gates are unscored.
11. The corpus at release is chapters 1 and 6, captions-first, with no media
    download by default.
12. Render budgets, Kokoro speed and whole-run wall clock are measured in M0;
    the design target of a five-minute `standard` video in under one hour on
    four CPUs is unverified until then.
13. Subagents run on whatever the harness configures (ADR-0001); no model is
    named anywhere in the skill.
14. The run directory is `mtv-runs/<slug>/` in the consumer project; the
    skill never commits.
15. Visuals are vector only and drawn from seeded synthetic data; no raster
    assets, dataset downloads or network access at render time in v1.
16. Text uses the first available of CMU Serif, Latin Modern Roman, TeX Gyre
    Termes, DejaVu Serif, then Pango's default serif; the font found is
    recorded per run.
17. The parent hands off at 48 subagent dispatches; the continuity
    threshold is a 0.15 mean absolute difference on 64 by 36 grayscale
    frames; both are pre-measurement defaults that M0 and M1 may tighten.

## Decisions needed from the owner

1. Corpus tooling location: a separate MIT repository `manim-3b1b-corpus`
   (recommended, keeps third-party material and the hygiene surface out of
   the kit) versus a `tools/` directory inside the kit repo.
2. Media policy: captions plus bucket figures only at release (recommended)
   versus `DOWNLOAD_MEDIA=1` downloads of the eight videos for keyframes,
   accepting the YouTube terms-of-service risk.
3. Agents: five inlined role prompts in `references/roles.md` (recommended,
   no `AGENT_REF` or README change) versus five new `agents/mv-*` entries.
4. Math engine: LaTeX as a hard preflight requirement (recommended; one
   engine, no `Text` twins of number-bearing patterns) versus a Typst or
   text-only fallback mode.
5. Corpus depth at release: two videos with per-section analysts and the
   other six as the extension loop (recommended) versus all eight before the
   skill ships.
6. Whether `final` (2160p30) is in scope for v1 at all, or `standard` is the
   ceiling until render times are measured.
7. Whether to reopen ADR-0002 and add a Python test step to CI for the
   bundled scripts, or keep `selftest.py` manual (recommended).
8. License granularity of the analyses. The section 5 records hold, per
   aligned section of a CC BY-NC-SA 4.0 video, a 40-to-120-word paraphrase
   of the narration and a per-beat gist and staging description; for a
   19-minute video that is closer to an abridgment than to "principles",
   and the 13-word guard prevents copying, not abridgment. Map 06 section 6
   and map 07 section 6 allow principles, original code, citations and
   short attributed quotes in the MIT kit. Options: (A) the analyses stay
   in the corpus repository under CC BY-NC-SA and the kit ships only
   `framework.md`, `patterns.md` and `rubric.md`, whose rules cite video
   id, timestamp, file and line (recommended until counsel or the owner
   says otherwise; the load-order table already keeps the analyses out of
   every run-time context); or (B) the analyses ship in
   `references/analyses/` with an ADR-0009 stating why factual
   descriptions of staging are not an adaptation. Under either option the
   attribution note goes atop every shipped reference derived from the
   corpus, not `framework.md` alone.
9. Description style. The writing-skills method the brief names says a
   skill description is triggers only; map 06 section 5.1 resolves this
   toward the kit's own style (capability plus trigger phrases, no workflow
   summary, as in the kit's `research` skill). The proposal follows the
   kit style; the owner should confirm this conscious deviation.

## Risks and mitigations

| Risk | Likelihood | Mitigation |
| --- | --- | --- |
| Agents write ManimGL idioms from training data | high | helpers imported from `mtv/patterns.py`; `check_scenes.py` bans GL names and `play(mob.method)`; `manimce.md` error table drives retries; `--dry_run` before frames |
| CPU render time makes the fix loop too slow | medium | M0 measures; 30 fps at `standard` and `final`; `draft` at 480p15; one scene per process, `--jobs` of them concurrently; caching kept valid by silent renders; estimate printed before the final tier |
| Eval wall clock makes M3 overrun | medium | inner loop without renders; one full-tier run per prompt per iteration; three per prompt only at release, concurrently; the day budget is recomputed from M0's measured run |
| Kokoro install weight or Python constraint | medium | preflight fails fast on 3.13 with the GitHub line; `narrate.py --warmup` pre-downloads; install size recorded in M0; ElevenLabs as the alternative |
| LaTeX absent on the consumer machine | medium | hard stop with the TeX Live package list; `threeb1b` template already in CE |
| LLM critic inconsistency | medium | objective hard gates independent of the critic; anchors per score; rubric calibration against corpus storyboards; three runs per eval case |
| Frame review misses motion defects | medium | contact sheets per beat; bounding boxes by code; motion items never scored from one still |
| Alignment noisy on the multi-file chapter 6 | medium | anchors; per-link confidence carried into records; alignment refines rules, it does not gate them |
| License leakage into the kit | medium until decision 8 is taken | paraphrase only; 13-word verbatim guard; media and transcripts never under git; attribution note atop every shipped reference; analyses stay in the corpus repository under option A |
| Kit gates reject bundled content (MD024, MD060, `SLASH_REF`, jscpd, typos) | medium | fixed heading outlines; compact tables; relative paths; one `common.py`; corpus identifiers stay in the corpus repo; gates run locally before every commit |
| Scene-boundary jump cuts | medium | `opening_state` and `closing_state` fields; perceptual distance check in `frames.py`; rubric item |
| Scope creep into a general Manim toolkit | medium | the extension table in section 12 names how each cut returns; nothing else is added before the first release |

## Open questions

1. Kokoro's CPU real-time factor and `kokoro-onnx` token timestamps are
   unmeasured (map 05 section 2); M0 measures the first.
2. ManimCE render throughput on four CPUs, sequential and with `--jobs 3`,
   is unverified; no render ran in the design container (map 04). The
   `wait()` quantization half of this question is answered from source: the
   clock advances by whole frames (CE `cairo_renderer.py:210`) and
   `beat()` pads against that clock, so error cannot accumulate; M0 only
   confirms it.
3. Whether the eight videos carry manual English captions and whether their
   descriptions contain chapter timestamps (map 07 section 7).
4. Exact video durations (third-party, minute-rounded) and the 2026 pair's
   durations (unknown).
5. Whether `DecimalNumber(mob_class=Text)` works without LaTeX (map 04,
   unverified); moot if decision 4 keeps LaTeX required. That
   `DecimalNumber` needs LaTeX by default is settled (CE `numbers.py:87`).
   The new unknown is the text Kokoro's tokens carry for numerals, which
   decides the matcher's normalization (section 8); M0 measures it.
6. Whether GL `reorient(theta, phi)` conventions match CE
   `set_camera_orientation(phi, theta)` beyond degrees to radians (map 04).
7. Why manim-voiceover requires `--disable_caching` (map 05 section 1); the
   silent-render path sidesteps it, and M0 confirms clean caching.
8. lychee's behavior from a GitHub runner against the few external links this
   work adds, and the GitHub rate-limit threshold (map 06 section 3.2).
9. The YouTube terms wording and whether the channel applies a Creative
   Commons license to uploads (map 07 section 6, third-party only).
10. The Hugging Face CDN host names to allow-list for Kokoro weights (map 05
    section 7).
11. Whole-run wall clock for a five-minute video on four CPUs; no design
    budgeted it and M0 produces the first number, from which M3's eval
    budget is derived.
12. Whether `apt-get` reaches a Debian mirror from the implementation
    container for TeX Live; M0 assumes it and reports if not.
13. ElevenLabs and OpenAI output-usage terms for generated audio by tier
    (vendor pages blocked, map 05 section 9); the report names provider,
    voice and model so the user can check their own rights.
14. The corpus values for the voice rules (words per beat, questions per
    minute, hedge rate, first-formula fraction); the rule form is fixed and
    M2 fills the thresholds.

Canonical pages referenced: <https://github.com/3b1b/videos>,
<https://github.com/ManimCommunity/manim>, <https://github.com/hexgrad/kokoro>,
<https://pypi.org/project/manim/>, <https://pypi.org/project/kokoro/>.

## Revision notes

Changes made in response to `critique.md`, one line each, keyed by its gap
ids; facts added here were re-checked against the ManimCE 0.22.0 clone and
the maps before being written.

1. G01: marks moved out of the narration text into a storyboard-owned
   `marks` field (name to word index); `narrate.py` caches on the clean text;
   `storyboard_check.py` rejects unresolved `lands` marks (sections 2, 3, 7,
   8, 9).
2. G02: `NarratedMixin.beat()` writes a per-beat run log that `verify.py`
   compares to the section index and the WAV durations; the circular gate is
   named and removed (recommendation, sections 2, 3, 8, 10).
3. G03: one `NarratedMixin` plus `NarratedScene`, `NarratedCameraScene` and
   `Narrated3DScene`; `scene_kind` field checked against the class bases;
   `manimce.md` note on zoom versus orbit (recommendation, sections 2, 3, 6,
   8, 12).
4. G04: run directory renamed `mtv-runs/<slug>/`, `.gitignore` patterns
   anchored, `PYTHONPATH` set by `render.py` and recorded under `env`, smoke
   test asserts `scripts/mtv/narrated.py` (sections 1, 3, 7, 11, assumption
   14).
5. G05: v1 asset policy (vector only, seeded synthetic data, no raster or
   downloads, checked by `check_scenes.py` and the critic) and a named serif
   font fallback list recorded per run (sections 2, 3, 6, assumptions 15 and
   16).
6. G06: eval budget defined (inner loop without renders, one full-tier run
   per prompt per iteration, three per prompt once at release, concurrent,
   day budget derived from M0's measured run) and a risk row added (sections
   10, 12, risks).
7. G07: research hygiene paragraph: misspelled upstream identifiers become
   `file:line` references, MD060 separators converted, CI-pinned tools run
   before the PR; analyses renderer never emits class identifiers in prose
   (sections 5, 11).
8. G08: license granularity of the analyses raised as decision 8 with
   options A and B; attribution note on every shipped reference; risk
   raised to medium pending the decision; layout and section 4 qualified
   (sections 4, 11, decisions, risks).
9. G09: numeric M2 criteria: refuter zero disproved claims per record,
   census tag ratio at least 30 percent of per-class idiom counts emitted by
   the `scenes` step, framework-only storyboard test at the rubric floor
   (sections 4, 5, 12).
10. G10: `narration_stats` corpus step, a voice rule group with numeric
    `Apply` predicates evaluated on the script, a voice rubric item, and open
    question 14 for the corpus thresholds (sections 4, 5, 6, 7).
11. G11: chapter 6 release scope now includes `embedding.py` lines 2232 to
    2566 (section 4).
12. G12: `storyboard_check.py` added to the components table, "nine
    scripts" in M1, and self-test fixtures for `storyboard_check.py`,
    `frames.py` and `render.py` (sections 2, 10, 12).
13. G13 and G28: helper count fixed at sixteen with `question_caption`
    added as the learner-objection device (sections 2, 6).
14. G14: "30 fps everywhere" corrected to `standard` and `final` (risks).
15. G15: requirements split into `requirements.txt` and
    `requirements-kokoro.txt`; `preflight.py` chooses the install line by
    interpreter (section 11).
16. G16: `narration` added to the fields the generated `lesson.py` reads
    (section 3).
17. G17: all retry bounds, counters and the sync tolerance consolidated in
    one table with pre-M0 defaults; the parent hand-off trigger is a
    dispatch count (sections 3, 7, 9, assumption 17).
18. G18: a motion rubric item added with the contact sheet as its input;
    rubric is 16 items, pass 25 of 32, calibration 27 of 32 (section 6,
    assumption 10, M2).
19. G19: `kind` vocabulary described as an extension of map 03's list,
    "timing resolved in the edit" marked as map 03's inference adopted by
    choice, chapter-6 file mapping marked inferred (sections 1, 4, 5).
20. G20: `manimce.md` records the `TexTemplate()` versus library default
    difference and the `threeb1b` package cost; assumption 5 costs the TeX
    Live packages (section 6, assumption 5).
21. G21: the alignment dynamic program and figure bridge deferred to M5; M2
    uses reader-made sections (section 4).
22. G22: `render.py --jobs N`, default CPU count minus one, measured in M0
    (sections 2, 7, 8, 12).
23. G23: every eval markdown file opens with an H1 and fences name a
    language (section 10).
24. G24: eval `case.yaml` and JSON fixtures rendered from a template by
    `selftest.py --fixtures` (section 10).
25. G25: `report.md` lists provider, voice, model and font; open question 13
    added for vendor terms (section 7, open questions).
26. G26: per-provider token matcher in `mtv/tts.py` with interpolation
    fallback; Kokoro numeral token text is an M0 measurement (section 8, open
    question 5).
27. G27: description style listed as decision 9 (decisions).
28. G29: continuity metric, threshold and `opening_state` enumeration
    defined; calibrated on M1's two-scene lesson (section 9, assumption 17,
    M1).
29. G30: `yt-dlp-ejs` plus a JavaScript runtime added to the corpus
    requirements (sections 2, 4).
30. G31: the two meanings of "section" fixed in the vocabulary paragraph and
    the schema (sections 1, 5).
31. G32: M0 names `uv venv --python 3.12` and the interpreter inventory;
    assumption 4 notes what this does and does not close (section 12,
    assumption 4).
32. Critique claims 5 and 7: open question 2 updated with the
    frame-quantization answer, and M0's `DecimalNumber` check replaced by the
    settled citation (section 12, open questions); open question 12 added
    for `apt-get` reachability.
33. Critique unverified item 1 closed: the CI-pinned markdownlint-cli2
    0.23.2 was run here and MD060 does fail maps 01 and 07 (86 and 72
    errors); this proposal reports 0 markdownlint and 0 typos errors under
    the kit's configs after revision (section 11).
