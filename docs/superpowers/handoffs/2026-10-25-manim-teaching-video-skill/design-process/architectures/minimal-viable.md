# Architecture: minimal viable, extensible

This is one of the candidate architectures for the `manim-teaching-video` skill in the `.agents`
kit. Its angle is the smallest system that turns one topic into one finished, narrated,
3Blue1Brown-grade MP4 in a fresh session, with every piece that is not needed for that first
good video cut and every place where depth can be added later named as an extension point.
Evidence is cited as `map NN` (the seven design maps under `scratchpad/design/maps/`), which in
turn carry `file:line` references into the local clones; anything not traceable to a map or a
clone is marked unverified.

## 1. Thesis

The design optimizes for **time to the first rubric-passing video**, then for **the cost of
adding depth afterwards**, in that order. Three facts from the maps make this the right trade.

1. The teaching framework is already most of the way extracted. Maps 01 and 02 reduce roughly
   33,000 lines of ManimGL to sixteen plus fourteen evidence-backed "moves that make it good",
   two color contracts, a layout grammar, timing distributions and a dozen composite idioms
   (map 01 sections 3 to 8; map 02 sections 2 to 8). Map 04 adds twelve original ManimCE idioms
   and a 24-row runtime-error table. A first framework can be written from these today; the
   transcript-aligned corpus refines it, it does not gate it.
2. The hard, unproven part is the toolchain, not the pedagogy: ManimCE 0.22.0 rendering with
   LaTeX on CPU, Kokoro synthesis with usable word timestamps, and sync that survives a
   re-render (map 04 "Quality flags", "LaTeX requirement"; map 05 sections 2 and 3). None of
   this was executed in the design container (manim, LaTeX and Kokoro are not installed). So the
   first milestone is a toolchain spike with a hand-written two-beat scene, before any corpus
   work, because a wrong assumption there invalidates everything downstream.
3. One contract makes everything else small. Every stage reads and writes a single
   `lesson.json` (sections, beats, narration, timing, pattern references, render paths). Stages
   are then independent scripts and subagent prompts that can be tested alone, replaced alone,
   and extended alone (section 2).

What this angle costs: the first framework is thinner than the corpus could support (two
transcript-aligned videos instead of eight at the first release), there are no 3D patterns
beyond one camera orbit, there is one voice, and no new `agents/` entries. Section 10 shows
how each gap is closed by repeating a step that already exists rather than by new design.

## 2. System overview

### 2.1 Components and data flow

```text
                 (build time, in the kit repo worktree)                (run time, in the consumer project)

 3b1b/videos clone ──┐                                                  topic + user answers
 YouTube captions ───┼─> tools/corpus-3b1b/ ──> corpus/<id>/*.json            │
 site bucket figures ┘   fetch | transcribe | align                     ┌──────▼──────┐
                                 │                                      │ 1 brief     │ SKILL.md step
                                 ▼                                      └──────┬──────┘
                    subagent per video: analysis record                 ┌──────▼──────┐
                    references/analyses/<lesson>.md ───┐                │ 2 script    │ subagent, reads framework.md
                                                       │                └──────┬──────┘
                    synthesis (parent + refuter):      │                ┌──────▼──────┐
                    references/framework.md  <─────────┤                │ 3 storyboard│ subagent, reads patterns.md
                    references/patterns.md  <──────────┤                │   + critic  │ writes lesson.json
                    references/rubric.md    <──────────┘                └──────┬──────┘
                    scripts/mtv/ (NarratedScene, look, patterns)        ┌──────▼──────┐
                                                                        │ 4 narrate   │ python scripts/narrate.py
                                                                        └──────┬──────┘  audio/*.wav + words
                                                                        ┌──────▼──────┐
                                                                        │ 5 scenes    │ subagent per section
                                                                        └──────┬──────┘  lesson.py
                                                                        ┌──────▼──────┐
                                                                        │ 6 render -ql│ python scripts/render.py
                                                                        │   frames    │ + frame critic (reads PNGs)
                                                                        └──────┬──────┘
                                                                        ┌──────▼──────┐
                                                                        │ 7 render    │ tier standard
                                                                        │ 8 assemble  │ python scripts/assemble.py
                                                                        │ 9 verify    │ python scripts/verify.py
                                                                        └──────┬──────┘
                                                                          out/<slug>.mp4 + .srt + report.md
```

### 2.2 Unit boundaries

Each unit has one input file set, one output file set, and can be run and tested without the
others. "Deps" lists only what the unit itself imports or shells out to.

| Unit | Boundary | Inputs | Outputs | Deps |
| --- | --- | --- | --- | --- |
| `tools/corpus-3b1b/fetch.py` | one video id | id, `corpus/manifest.json` | `corpus/<id>/info.json`, captions (`json3`/`vtt`), bucket figure jpgs | `yt-dlp`, `curl` (map 07 appendix B) |
| `tools/corpus-3b1b/transcribe.py` | one video | audio file, optional manual captions | `corpus/<id>/words.json` (word, start, end) | `faster-whisper` int8 (map 05 section 4); skipped when manual captions exist |
| `tools/corpus-3b1b/align.py` | one video | `words.json`, source file list, article headings | `corpus/<id>/alignment.json` (map 07 section 4 schema) | Python stdlib `ast`, no ML |
| analysis subagent | one video | `alignment.json`, source files (read-only), transcript (local) | `references/analyses/<lesson>.md` | harness subagent |
| synthesis (parent) | all records | analyses, maps 01 to 05 | `references/framework.md`, `patterns.md`, `rubric.md` | none |
| `scripts/mtv/` package | one lesson | `lesson.json` | `NarratedScene` base, `look` (colors, `TexTemplate`, fonts), `patterns` helpers | `manim==0.22.0` |
| `scripts/narrate.py` | one lesson | `lesson.json` narration text | `audio/<beat>.wav`, `audio/<beat>.words.json`, updated `lesson.json` durations | Kokoro (default), provider adapters |
| `scripts/render.py` | one lesson, one tier | `lesson.py`, `lesson.json`, `manim.cfg` | `media/videos/lesson/<q>/sections/*.mp4` + JSON index, `frames/<beat>-{mid,end}.png` | `manim`, `ffmpeg` |
| `scripts/assemble.py` | one lesson | section MP4s, section JSON, beat WAVs | `out/<slug>.mp4`, `out/<slug>.srt` | `ffmpeg` (concat, `adelay`, `amix`, `loudnorm`) |
| `scripts/verify.py` | one MP4 | `out/<slug>.mp4`, `lesson.json`, section JSON | `out/report.md` with pass or fail per hard check | `ffprobe` |
| `scripts/preflight.py` | the environment | nothing | pass or fail per tool with the fix to apply | none |

The unit tests in section 8 target exactly these boundaries.

### 2.3 The one contract: `lesson.json`

```json
{
  "schema": "mtv-lesson/1",
  "slug": "what-a-neuron-computes",
  "title": "What a neuron computes",
  "audience": "first-year undergraduate",
  "target_minutes": 5,
  "tier": "standard",
  "colors": {"weight_pos": "BLUE", "weight_neg": "RED", "bias": "MAROON_B", "cost": "RED",
             "emphasis": "PURE_YELLOW", "sigma": "PURE_YELLOW"},
  "sections": [
    {
      "id": "s01", "title": "A working thing first", "scene_class": "S01WorkingThing",
      "beats": [
        {
          "id": "s01-b01",
          "narration": "Here is a network that already reads handwritten digits.",
          "visual": "784-16-16-10 network scaled 0.75 at the bottom; digit image upper left",
          "patterns": ["network_mobject", "feed_forward_flash"],
          "moves": ["working-thing-first"],
          "audio": "audio/s01-b01.wav", "duration": 4.21,
          "words": "audio/s01-b01.words.json",
          "render": {"section_index": 0, "video": null, "frames": []}
        }
      ]
    }
  ],
  "checks": {"storyboard_rubric": null, "frame_rubric": null, "verify": null}
}
```

Every field above is written by exactly one stage: `sections[].beats[].narration` and
`visual` by the storyboard stage, `audio`, `duration`, `words` by `narrate.py`, `render` by
`render.py`, `checks` by the critics and `verify.py`. A stage never edits another stage's
fields, which is what makes a run resumable: rerun the stage whose outputs are missing.

## 3. Corpus pipeline

### 3.1 Scope for the first release

Two videos, chosen so the two visual regimes in the corpus are both represented and so that
alignment is easy: chapter 1 (`aircAruvnKk`, source `_2017/nn/part1.py`, one file, 2D, the
network drawing) and chapter 6 (`eMlx5fFNoYc`, source `_2024/transformers/attention.py` plus
the `supplements.py` block at lines 841 to 1338, 3D camera work, matrices and role colors)
(map 07 section 1 table; map 07 section 3 "Video to file and class mapping"). Map 07 rates
monotonic alignment at 80 to 90 percent for one-file videos, so chapter 1 needs few manual
anchors; chapter 6 is the test of the alignment script on a multi-file video.

The remaining six primary videos are the extension loop (section 10, M4): same scripts, same
record schema, one subagent per video.

### 3.2 Steps

| Step | Command | Input | Output | Idempotent by |
| --- | --- | --- | --- | --- |
| 1 Manifest | hand-written once | map 07 section 1 table | `corpus/manifest.json`: id, slug, title, source files, expected duration, caption status | file exists |
| 2 Fetch metadata and captions | `python tools/corpus-3b1b/fetch.py --id aircAruvnKk` | manifest | `corpus/aircAruvnKk/info.json`, `*.en.json3` or `*.en.vtt`, `description.txt` | skips when `info.json` exists; records `sha256` of each file in `corpus/aircAruvnKk/stamp.json` |
| 3 Fetch figures | same script, `--figures` | bucket prefix `lessons/2017/neural-networks/` | `corpus/aircAruvnKk/figures/*.jpg` (jpg only, png twins skipped) | per-object `ETag` from the XML listing (map 07 section 2) |
| 4 Transcribe | `python tools/corpus-3b1b/transcribe.py --id aircAruvnKk` | audio (downloaded only when no manual captions) | `words.json` | skips when `words.json` exists |
| 5 Align | `python tools/corpus-3b1b/align.py --id aircAruvnKk --source $CORPUS_SRC/_2017/nn/part1.py` | `words.json` or captions, source file, article `##` headings from the site clone | `alignment.json` (map 07 section 4 schema) with `confidence` and `signals` per link | deterministic; overwrites |
| 6 Anchor | human or agent edits `anchors.json` (3 to 6 `(t, class)` pairs) and reruns step 5 | low-confidence links | same, `verified_by` set | rerun |

The alignment algorithm is the one map 07 section 4 proposes: scene list by definition order
from `ast` (helper mobjects, stubs, thumbnails and end screens dropped, Pi-creature scenes
tagged `overlay`), candidate transcript sections at article headings and pauses longer than
1.5 s, scores from string-literal hits (`Text`, `Tex`, `TexText`, `says` arguments) plus
CamelCase-split class names, and a monotonic dynamic-programming alignment with a skip penalty.
No embeddings, no OCR, no render-and-compare in the first release.

### 3.3 Where data lives and what is committed

- Raw corpus (captions, audio, figures, `words.json`) lives under `$CORPUS_DIR` (default
  `$HOME/corpus/3b1b`), gitignored, never in the kit. License: `3b1b/videos` is CC BY-NC-SA 4.0
  and the site content is all rights reserved (map 07 section 6; map 06 section 6).
- Committed: `corpus/manifest.json` (ids, hashes, caption availability), `alignment.json` and
  `anchors.json` per video (time ranges, class names, file paths, line numbers, paraphrased
  summaries only), and the three tools. These go in the kit repo under
  `tools/corpus-3b1b/` with the data files under `tools/corpus-3b1b/data/`. This is a new
  top-level directory and is not installed by `install.sh` (which copies only `skills/`,
  `agents/`, `rules/` and `agents.kit.md`; map 06 section 2.1). Section 13 lists the
  alternative of a separate repository.
- Never committed: verbatim transcripts, frames, figures, media, or any of his scene code.

### 3.4 Running in a fresh session with network

```bash
pip install yt-dlp faster-whisper
export CORPUS_DIR=$HOME/corpus/3b1b CORPUS_SRC=$HOME/3b1b/videos
GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 https://github.com/3b1b/videos $CORPUS_SRC
python tools/corpus-3b1b/fetch.py --all --captions --figures
python tools/corpus-3b1b/transcribe.py --all --model distil-large-v3 --compute-type int8
python tools/corpus-3b1b/align.py --all
```

`fetch.py` runs `yt-dlp --skip-download --write-info-json --write-description --write-subs
--write-auto-subs --sub-langs "en.*" --sub-format "json3/vtt" --js-runtimes node` (flags from
the yt-dlp README as cited in map 05 section 4 and map 07 appendix B; the `yt-dlp-ejs`
requirement and Node runtime are from the same README). Whether the eight videos carry manual
captions is unverified (map 07 section 7 item 2); `--list-subs` decides whether step 4 downloads
audio at all. Media download is a YouTube terms-of-service risk the user must accept (section
13); the captions-only path has the same risk surface as reading the page.

## 4. Per-video analysis method

### 4.1 Who analyzes

One subagent per video, run in parallel for the two first-release videos, each with a
self-contained prompt (goal, the record schema below, the local paths to `alignment.json`, the
source file list and the raw transcript, the rule "cite `file:line` and `t=mm:ss` for every
claim, quote no scene code, paraphrase narration"). Per-section fan-out is not needed at two
videos; it becomes the extension when a 25-minute video exceeds one subagent's context
(section 10, M4). A second, cheaper subagent per record acts as refuter: it samples ten claims,
opens the cited lines and timestamps, and returns `CONFIRMED` or `REFUTED` per claim. A record
with more than one refuted claim goes back to the analyst with the refutations attached.

### 4.2 Analysis record schema

File: `skills/manim-teaching-video/references/analyses/<lesson-slug>.md`, one per video, with
this fixed outline (headings unique within the file for MD024):

```text
# <Lesson title> (<year>, <YouTube id>)
## Sources and coverage        source files with line ranges; transcript source; figure count
## Arc                          numbered sections: t-range, paraphrased narration summary,
                                scene classes (file:line), teaching move tags
## Visual nouns                 each recurring object: what it is, how built, where (file:line)
## Color contract               role -> color with first-introduction line and any drift
## Layout habits                where things live on screen, with counts and lines
## Timing                       run_time and wait distributions; longest holds and why
## Moves observed               each move: evidence (file:line, t=), why it works (one sentence)
## Narration-to-visual rules    what the narration says when a visual appears (from alignment)
## Anti-patterns                what he avoids or admits (hedges, "honest lie", "we'll get back")
## Open questions               unverified items, low-confidence alignment links
```

Each `## Moves observed` entry carries a stable id (`working-thing-first`, `numbers-before-
symbols`, `provenance-by-transform`, `dim-do-not-delete`, `count-the-parameters`) so that
`framework.md` rules can cite records by id and the storyboard's `moves[]` field can be
validated against the known set.

### 4.3 Evidence grounding and transcript-to-code alignment

- Every claim about code cites `file:line` in the `3b1b/videos` clone; every claim about
  narration cites `t=mm:ss` from `words.json`; every claim about the look cites a bucket figure
  object name or a frame timestamp. The refuter checks exactly these three citation kinds.
- Alignment is `alignment.json` from section 3; the analyst does not re-derive it. Where a link
  has `confidence < 0.6` the record marks the section `(alignment uncertain)` and the arc says
  what the uncertainty is.
- Keyframes are the secondary check (brief): in the first release the bucket figures (245
  captioned frames across the eight articles, map 07 section 2) stand in for extracted
  keyframes. Scene-change extraction with ffmpeg `select='gt(scene,0.3)'` (verified locally,
  map 07 section 3) is the M4 extension.

### 4.4 Quality check of the analyses

1. Refuter pass (section 4.1), ten sampled claims per record.
2. Schema lint: `python tools/corpus-3b1b/check_record.py references/analyses/<slug>.md`
   verifies the ten headings, that each move entry has a `file:line` and a `t=` citation, and
   that no line of the record matches a line of the source files (a cheap copied-code guard;
   exact-line match only).
3. The kit gates: markdownlint, typos, lychee run over `references/` because the files are
   shipped markdown (map 06 section 3).

## 5. Framework representation

### 5.1 Files

| File | Lines (target) | Role | Loaded by |
| --- | --- | --- | --- |
| `references/framework.md` | 250 to 350 | the rules: narrative, visual, timing, color, layout, honesty | script and storyboard subagents, critics |
| `references/patterns.md` | 300 to 400 | the pattern library index: one entry per helper in `scripts/mtv/patterns.py` and per idiom, with an original ManimCE example and its 3b1b evidence | scene-code subagents |
| `references/rubric.md` | 120 to 180 | twelve scored criteria plus the hard gates | critics, `verify.py` (hard gates only) |
| `references/pipeline.md` | 150 to 250 | the stage-by-stage contract (`lesson.json` fields, commands, error table from map 04) | the parent orchestrator |
| `references/analyses/*.md` | 200 to 400 each | per-video records (section 4) | synthesis at build time; at run time only when a critic asks "what did he do here" |
| `references/manimgl-to-manimce.md` | 150 | the translation table from map 04 trimmed to the names the corpus uses | scene-code subagents on demand |
| `scripts/mtv/look.py` | 80 | `TexTemplate` with `dsfont`, `mathrsfs`, `physics`, `xcolor` and the `\minus` macro (map 03 section 1.3); `Text.set_default(font=...)`; color constants incl. `PURE_YELLOW` for 3b1b yellow (map 04 colors row) | imported by every lesson |
| `scripts/mtv/narrated.py` | 150 | `NarratedScene` (section 7) | imported by every lesson |
| `scripts/mtv/patterns.py` | 400 to 600 | ten helpers (section 5.3) | imported by every lesson |

### 5.2 How rules are phrased

Each rule in `framework.md` has four parts so an agent can apply it and a critic can check it:

```text
### R07 Numbers before symbols
DO    Show the concrete value (a decimal in a neuron, a 2x3 matrix of numbers) in the beat
      before the symbol that names it; introduce the symbol by transforming a copy of the
      concrete thing into it.
CHECK In lesson.json, every beat whose `visual` introduces a symbol is preceded by a beat
      whose `visual` shows that quantity numerically. In frames, the symbol's first frame
      contains the concrete object it came from.
WHY   Activations are decimals inside circles ~1900 lines before the first weighted sum is
      written; vectors start as columns of decimals and collapse to a symbol only after.
       (analyses/neural-networks.md "Moves observed"; map 01 section 6.2; map 02 section 8.1)
SCOPE Every section that introduces notation. Exception: a recap section may show the symbol
      directly if the same symbol was introduced earlier in this lesson.
```

Rules are numbered `R01` to about `R40`, grouped as Narrative (hook, plan preview, one working
thing first, question before answer, honest hedging), Visual (one visual noun per concept, dim
not delete, provenance by transform, object budget, boxes name regions), Color (one hue per
role for the whole lesson, emphasis is `PURE_YELLOW`, cost is `RED`, inert structure `GREY_B`),
Layout (diagram low, text high, captions next to referent, `FRAME_WIDTH - 1` banners, nothing
outside the frame), Timing (narration first, 1 to 2 s plays, 1 s beat tail, long holds only
with motion or narration, montage under 0.5 s per item) and Honesty (say what is simplified,
seed randomness, prefer real numbers where free). Each `CHECK` is either a `lesson.json`
predicate (the storyboard critic applies it), a frame predicate (the frame critic applies it)
or a script predicate (`verify.py` applies it); the rule says which.

### 5.3 Pattern library

Ten helpers in `scripts/mtv/patterns.py`, each one function or class with an original
implementation, a docstring that names the 3b1b evidence by map and line, and one example
scene in `patterns.md`:

| Helper | What it does | 3b1b evidence (via maps) |
| --- | --- | --- |
| `LayeredNetwork(layer_sizes, max_shown=16, ...)` | circles, edges, `vdots` with brace for large layers, `edges_in`/`edges_out` per neuron, `activate(vector)` sets fills | map 01 section 2.2 (`NetworkMobject` config keys and structure) |
| `flash_along(edges, color=PURE_YELLOW, lag_ratio=0.5)` | copy, thicken, `ShowPassingFlash` sweep | map 01 section 5.4 "Signal flow"; map 04 row `ShowCreationThenDestruction` |
| `focus_and_dim(scene, focus, others, opacity=0.2)` | dim the rest, `Circumscribe` the focus, return a restore animation | map 02 section 8.4; map 04 idiom 1 |
| `numbers_to_symbol(scene, entries, symbol)` | collapse a column of decimals into a `MathTex` symbol while brackets squash | map 02 section 2.3 |
| `NumericColumn(values, ramp="data")` and `WeightGrid(values)` | decimal column or matrix colored by sign and magnitude (`BLUE_E..BLUE_B`, `RED_E..RED_B`) or grey-to-white | map 02 section 2.2 |
| `provenance(scene, source, target)` | `TransformFromCopy` with `path_arc`, source stays | map 01 section 5.3; map 02 section 5.2 item 2 |
| `count_parameters(scene, braces_and_ints)` | braces grow, integers count in, product transforms from factors | map 02 section 6.3 item 5 |
| `staggered(anim_cls, group, lag_ratio=0.1, **kw)` | `LaggedStartMap` with the corpus default lags (0.1 crowds, 0.5 sequential) | map 01 section 5.2; map 02 section 5.1 |
| `delayed(*anims, offsets)` | the `time_span` emulation with `Succession(Wait(t), anim)` | map 04 idiom 10 |
| `orbit_with_hud(scene, title, phi, theta, rate, seconds)` | `ThreeDScene` ambient rotation with a fixed-in-frame title | map 04 idiom 11 |

Visual nouns specific to the 2024 series (token tape, machine with dials, attention grid,
slab stack, context arcs, next-token bar chart; map 02 section 2) are not in the first
release. They are the natural M4 additions, one helper each, after the chapter 6 analysis
record is in hand.

### 5.4 Rubric

`rubric.md` scores twelve criteria 0, 1 or 2 and lists hard gates that are not scored:

| # | Criterion | Scored by | From |
| --- | --- | --- | --- |
| 1 | Opens with a concrete thing or question, not a definition | storyboard critic | R01, R03 |
| 2 | Previews where the lesson goes within the first minute | storyboard critic | R02 |
| 3 | Every symbol was first shown as numbers or a picture | storyboard + frame critic | R07 |
| 4 | One color per role, no hue changes | frame critic (legend in `lesson.json`) | R15 |
| 5 | Focus moves by dimming, not deleting; frame never clutters | frame critic | R10, R12 |
| 6 | Captions sit next to their referent | frame critic | R19 |
| 7 | Each beat's visual changes when the narration's subject changes | storyboard critic + `verify.py` (word timestamps vs section boundaries) | R24 |
| 8 | Pacing: 1 to 3 plays per narration sentence, no hold over 4 s without motion | `verify.py` from section JSON | R25, R26 |
| 9 | Says what is simplified or skipped | storyboard critic | R31 |
| 10 | Uses at least one count or real number to show scale | storyboard critic | R33 |
| 11 | Recaps by carrying the picture forward | storyboard critic | R05 |
| 12 | Text readable: no overflow, no overlap, font size at or above 24 at 1080p | frame critic + `verify.py` bounding boxes | R20, R21 |

Pass bar: total at least 19 of 24 and no criterion at 0. Hard gates (fail stops the run): one
MP4 with one video and one audio stream; audio and video durations within 0.5 s; every beat's
audio starts within 0.25 s of its section start; no `manimlib` import; every `lesson.json`
section has a rendered section video; LaTeX compiled (no `latex error converting to dvi` in
the log; map 04 error table).

The storyboard critic and the frame critic are subagents with inlined role prompts from
`references/roles.md` (section 6.1); the frame critic reads PNGs with the image-reading tool.

### 5.5 Context budget and progressive disclosure

`SKILL.md` stays an orchestrator under 300 lines and names each reference once. The parent
never loads `patterns.md` or the analyses; subagents load exactly one reference each
(script subagent: `framework.md`; storyboard subagent: `framework.md` plus the pattern table
of `patterns.md`; scene-code subagent: `patterns.md` plus the section of `lesson.json` it
implements; critics: `rubric.md` plus the artifact under review). `framework.md` opens with a
one-screen table of rule ids and titles so a subagent can skim and then read only the rules
its stage checks. Analyses are build-time inputs; at run time they are consulted only when a
critic wants a precedent, by grepping `references/analyses/` for a move id.

## 6. Skill design

### 6.1 SKILL.md outline

```text
---
compatibility: Python 3.11 or 3.12, manim 0.22.0, a TeX distribution with dvisvgm, ffmpeg,
  and a narration provider (default Kokoro, offline)
description: >-
  Produces a narrated teaching video in the 3Blue1Brown style from a topic using Manim
  Community Edition: script, storyboard, synthesized narration, synced animation, one MP4.
  Use when asked for an explainer video, a math or ML animation with voice-over, a
  "3b1b-style" or "Manim" video, or to turn notes or a lesson into a narrated animation.
enabled: true
id: manim-teaching-video
name: manim-teaching-video
---
# Manim Teaching Video (narration-first pipeline)
Framing paragraph; no-model-pins boilerplate (ADR-0001) in the kit's words.
## 0. Triage out loud: tier (draft | standard | final), target length, provider, output dir
## 1. Preflight: python scripts/preflight.py (hard stop with fixes)
## 2. Brief: ask the user only what section 6.5 lists; write lesson.json header
## 3. Script: one subagent writes narration per section with framework.md; parent checks R01-R05
## 4. Storyboard: one subagent fills beats (visual, patterns, moves); storyboard critic scores
## 5. Narrate: python scripts/narrate.py lesson.json  (durations and words into lesson.json)
## 6. Scenes: one subagent per section writes class S<nn> in lesson.py using mtv.*
## 7. Draft render and frame review: python scripts/render.py --tier draft; frame critic
## 8. Fix loop: at most two passes; each pass re-renders only failed sections
## 9. Final render, assemble, verify: scripts/render.py --tier <tier>; assemble.py; verify.py
## 10. Report (text template) and what to tell the user
## Roles (inlined prompt contents for script writer, storyboarder, scene coder, two critics)
## A valid run (checklist in the research skill's Tier 3 style)
## Guardrails / Scope boundaries / Communication style
```

`references/roles.md` holds the five role prompts (each: goal, inputs by path, the one
reference to read, output contract, "cite the rule id you applied"). They are inlined into
generic subagents because the kit allows that when a named type is unavailable (map 06
section 4.1) and because adding `agents/` entries needs an `AGENT_REF` regex change and README
edits (map 06 section 4.2). Promotion to `agents/mtv-*` is an extension (section 13).

### 6.2 Run-time process

1. Brief. From the topic and the user's answers, the parent writes the `lesson.json` header
   (`slug`, `title`, `audience`, `target_minutes`, `tier`, `colors` legend) and the first
   section titles (3 to 6 sections for a 4 to 8 minute video; the corpus has one spine scene
   per 2 to 4 minutes, map 01 section 1.4).
2. Script. One subagent writes `narration` for every beat (one to three sentences per beat,
   10 to 25 s of speech at 150 to 170 words per minute, map 07 section 5). Parent checks the
   narrative rules by reading, not by subagent: hook present, plan previewed, hedges present.
3. Storyboard. One subagent fills `visual`, `patterns[]` (names from `patterns.py`) and
   `moves[]` (ids from the analyses) per beat. The storyboard critic scores criteria 1, 2, 3,
   7, 9, 10, 11 and returns `checks.storyboard_rubric`. Below the bar, the storyboarder gets
   the critique and one retry.
4. Narrate. `python scripts/narrate.py lesson.json` synthesizes each beat to
   `audio/<beat>.wav` at 24 kHz and writes `duration` and `words` (section 7).
5. Scenes. One subagent per section writes `class S01WorkingThing(NarratedScene)` in a single
   `lesson.py` (parallel, 4 to 6 at a time per `rules/subagents.md`). Each beat is a block:

   ```python
   with self.beat("s01-b01") as b:
       net = LayeredNetwork([784, 16, 16, 10]).scale(0.75).to_edge(DOWN)
       self.play(FadeIn(net, lag_ratio=0.05), run_time=2)
       self.play(flash_along(net.edges), run_time=b.until("digits"))
   ```

   `beat()` opens `next_section(beat_id)`, adds the subcaption, and on exit pads with
   `self.wait(remaining)` so the section lasts at least the narration (section 7).
   The parent runs `python scripts/check_scenes.py lesson.py lesson.json` before any render:
   every section has a class, every beat id appears once, no `manimlib` import, no GL-only
   names (`set_backstroke`, `get_grid`, `replicate`, `fix_in_frame`, `reorient`,
   `ShowCreation`; map 04 error table), no `self.play(mob.method, ...)` form.
6. Draft render. `python scripts/render.py lesson.json --tier draft` runs
   `manim -ql --fps 15 --save_sections --disable_caching_warning lesson.py S01... S0n`
   with `manim.cfg` from `assets/`, then extracts per beat the last frame and one mid frame
   with `ffmpeg -ss` from the section videos, writing `frames/<beat>-end.png`,
   `frames/<beat>-mid.png` and updating `render` in `lesson.json`. The frame critic reads
   the PNGs (image reading) and scores criteria 3, 4, 5, 6, 12.
7. Fix loop. Failed beats go back to their section's scene coder with the critique and the
   frame paths; only those sections re-render. Two passes maximum; after that the run stops
   with a report rather than looping.
8. Final render. Same command at the chosen tier (section 6.4). `assemble.py` concatenates
   section videos in `lesson.json` order with the ffmpeg concat demuxer, builds the narration
   track by placing each beat WAV at its section's start offset (`adelay` + `amix`, section
   JSON durations as offsets), runs `loudnorm` two-pass to -16 LUFS, muxes AAC 192k, and
   writes the SRT from the subcaptions (map 05 section 6). `verify.py` applies the hard gates
   and writes `out/report.md`.
9. Report. Path to MP4 and SRT, rubric totals from both critics, hard-gate table, render
   time, what was simplified, and the two things the user is most likely to want changed.

### 6.3 Verification loops

- Static: `check_scenes.py` (above) and `python -m manim --dry_run lesson.py S01...`
  (`--dry_run` renders nothing but executes `construct`, catching LaTeX and API errors;
  map 03 section 3.5).
- Draft render plus frame review (step 6). Frame review is the only place a model looks at
  pixels; it is given at most two PNGs per beat and the beat's `visual` text, and answers
  per criterion with a one-line reason.
- Rubric self-review happens twice: on the storyboard (cheap, before any audio or code) and
  on draft frames (after code, before the expensive render). There is no third review on the
  final render; `verify.py` checks the final MP4 mechanically.
- Sync check in `verify.py`: for each beat, the section's start time (cumulative section
  durations from the JSON index) versus the beat audio's placement; drift over 0.25 s fails.
  Because `beat()` pads to the narration duration, drift can only come from an animation
  overrunning its beat, which `NarratedScene` already logs as a warning with the overrun.

### 6.4 Error handling, render budget and tiers

| Failure | Detection | Response |
| --- | --- | --- |
| Tool missing (manim, latex, dvisvgm, ffmpeg, Kokoro) | `preflight.py` | stop; print the install line per tool (map 04 "LaTeX requirement"; map 05 Kokoro install); never continue without LaTeX because `DecimalNumber`, `Matrix`, `Brace.get_text` all need it |
| `latex error converting to dvi` | render log | show the offending lines; scene coder fixes; if the package is missing, `look.py`'s template is the only place to add it |
| GL-only name or `play(mob.method)` | `check_scenes.py` | reject before render with the map 04 translation row |
| Section missing from JSON index | `render.py` compares to `lesson.json` | the beat had no play or wait; `beat()` always issues a `wait`, so this indicates an exception inside the beat; surface the traceback |
| Animation overruns narration | `NarratedScene` warning | allowed up to 1.0 s (narration pauses); beyond that the scene coder shortens `run_time` |
| Kokoro import or model download fails | `narrate.py` | fall back to `kokoro-onnx`, then Piper (map 05 section 2); never to edge-tts or gTTS; report the voice used |
| Premium provider network error | `narrate.py` | retry twice, then fall back to Kokoro and say so in the report |
| Render longer than budget | `render.py` timer | draft tier measures seconds per rendered second; the final tier estimate is `draft_time * (pixels_final / pixels_draft) * (fps_final / fps_draft)`; if over 45 minutes, ask the user to confirm or lower the tier |
| Usage limit or session cut | `lesson.json` stage fields | rerun the skill; the parent skips stages whose outputs exist |

Tiers: `draft` is 854x480 at 15 fps (`-ql`), `standard` is 1920x1080 at 30 fps (set via
`manim.cfg`, because `-qh` means 60 fps; map 04 "Quality flags"), `final` is 3840x2160 at
30 fps (3b1b's own output, map 03 section 1.1). Default is `standard`; 4K only on request.

### 6.5 What the skill asks the user

At most three questions, asked once at the brief and only when the topic does not answer
them: audience level (default: motivated adult non-specialist), target length (default
5 minutes, range 3 to 8), and narration provider when a premium key is present in the
environment (default: Kokoro offline). Everything else (colors, section count, tier) is
decided by the skill and reported. The run also stops to ask when the final render estimate
exceeds 45 minutes or when the fix loop is exhausted.

## 7. Narration and sync

### 7.1 Default and premium providers

Default: Kokoro-82M, voice `af_heart`, speed 1.0, 24 kHz, offline, Apache-2.0 weights from
`huggingface.co/hexgrad/Kokoro-82M`, with per-token `start_ts` and `end_ts` from
`KPipeline.join_timestamps` (map 05 section 2 "Kokoro"). Stated assumption: the consumer
environment runs Python 3.11 or 3.12 so the PyPI wheel installs; on 3.13 the package is
installed from the GitHub repository (map 05 notes the `<3.13` PyPI constraint and the 3.13
commit on `main`). Kokoro's real-time factor on four CPUs is unverified; map 05 quotes a
low-confidence community figure under 1.0, which for a five-minute script means minutes, not
hours. `preflight.py` measures it on a ten-word sentence and records the figure.

Premium: ElevenLabs through `convert_with_timestamps` (character-level `alignment` and
`normalized_alignment`), selected when `ELEVENLABS_API_KEY` is set and the user confirms
(map 05 section 2 "ElevenLabs"). The provider interface in `scripts/mtv/tts.py` is one
function, `synthesize(text, out_wav) -> list[Word]`, with two implementations in the first
release; OpenAI, Azure, Piper and `kokoro-onnx` are added by implementing that function.

### 7.2 Alignment approach

Timing comes from the synthesizer, never from transcription of the synthesized audio:
Kokoro tokens and ElevenLabs characters both give word start times by construction (map 05
section 3 comparison table). `narrate.py` writes `audio/<beat>.words.json` as
`[{"word": "digits", "start": 1.84, "end": 2.31}, ...]` and the beat's total `duration`.
No forced aligner is shipped in the first release; the hook for one is a provider that
returns `[]` for words, in which case `b.until(word)` falls back to proportional interpolation
over the beat text (the fallback manim-voiceover itself uses) and `verify.py` records that
the beat used interpolated timing.

### 7.3 `NarratedScene`

```python
class NarratedScene(Scene):
    lesson_json = "lesson.json"
    def beat(self, beat_id):          # context manager
        ...                           # next_section(beat_id); add_subcaption(narration, duration)
        yield Beat(duration, words)   # b.duration, b.until("word"), b.remaining()
        ...                           # wait(max(duration - elapsed, 1/fps)); warn if elapsed > duration + 1.0
```

`Beat.until(word)` returns the time from the current scene clock to that word's start, so a
play can be timed to land on a word. Audio is not added inside Manim: sections are rendered
silent, and `assemble.py` places each beat's WAV at the section's start. This keeps the
render cacheable and lets the voice be changed without re-rendering a frame.

### 7.4 manim-voiceover: not used, and why

Its `voiceover()` context manager and `<bookmark/>` ergonomics are the right design and are
reproduced in `beat()`; the dependency is not taken because its service pins are stale
(`elevenlabs<0.3`, `openai<2`), its bookmark timing is whisper interpolation requiring PyTorch
plus openai-whisper plus stable-ts, it needs `--disable_caching`, and it reaches into renderer
internals that 0.22.0's `Manager` refactor puts at risk (map 05 section 1). The useful core is
about 400 lines under MIT, so owning an equivalent is cheaper than adapting to it.

## 8. Testing strategy

### 8.1 Scripts

`skills/manim-teaching-video/scripts/tests/` with pytest, run by hand in the implementation
session (the kit has no Python gate, ADR-0002; map 06 section 3.10):

- `test_lesson_schema.py`: a fixture `lesson.json` validates; a stage writing another stage's
  field is rejected.
- `test_narrate.py`: a fake provider returning fixed words; `duration` and `words` land in
  the right beat; the fallback chain is exercised with monkeypatched import failures.
- `test_narrated_scene.py`: a two-beat scene rendered with `-ql --save_sections` on a
  two-sentence fixture; the JSON index has two sections whose durations are at least the beat
  durations; the overrun warning fires on a deliberately long play.
- `test_check_scenes.py`: fixtures with `manimlib`, `ShowCreation`, `play(mob.shift, UP)` are
  rejected with the right message.
- `test_assemble_verify.py`: three one-second silent section MP4s plus three WAVs produce one
  MP4 with two streams and `ffprobe` durations within 0.5 s; a shifted WAV fails the drift gate.
- `tools/corpus-3b1b/tests/test_align.py`: a synthetic source file with four classes and a
  synthetic `words.json` align monotonically; a string-literal hit raises confidence.

jscpd counts Python at a 5 percent threshold (map 06 section 3.4), so shared argparse and
ffprobe code lives once in `scripts/mtv/common.py`.

### 8.2 Framework

Does an agent given only `framework.md` and `patterns.md` produce rubric-passing work? Three
fixed topics (section 8.4), one storyboard subagent each with the two references, scored by
the storyboard critic. Pass: at least two of three storyboards reach the bar on first try and
the third after one retry. This runs before the skill exists (M2) and again whenever a rule
changes, because the framework is what the skill carries.

### 8.3 Skill

Following the writing-skills method and the skill-creator layout (map 06 section 5.3):

1. RED. The three topics run as subagents with no skill, in the implementation environment
   with manim installed. Transcripts are saved under `manim-teaching-video-workspace/`
   (gitignored). Expected failures to record verbatim: ManimGL idioms from training data, no
   narration or narration added as a last step, no sync, 60 fps renders, definitions first,
   one giant scene, no color discipline. Plus one pressure scenario per discipline rule
   ("render now, skip the storyboard check", "LaTeX is missing, just use Text everywhere",
   "ship it, the audio is only two seconds off").
2. Eval cases under `skills/manim-teaching-video/evals/<case>/` with `prompt.md`,
   `case.yaml`, `graders/`. Objective graders are scripts: MP4 exists; `ffprobe` reports one
   video and one audio stream; durations within 0.5 s; `grep -L manimlib`; section count in
   the JSON index equals `lesson.json` beats; frame rate 30 at the standard tier. One LLM
   grader applies `rubric.md` to the storyboard and the frame set with the numeric floor.
3. GREEN. `SKILL.md` plus references and scripts are written to the recorded failures, then
   with-skill and without-skill runs happen in the same turn per case, graded and aggregated
   with the skill-creator scripts, static viewer generated.
4. REFACTOR. Close loopholes found in the transcripts; any helper two runs wrote
   independently becomes a `patterns.py` function.

Pass for the skill: all three topics produce an MP4 that clears every hard gate; two of three
reach the rubric bar without a fix loop and the third within two passes; every pressure
scenario ends with the agent citing the rule it refused to break.

### 8.4 Fixed test-prompt set

| Id | Prompt | Why |
| --- | --- | --- |
| T1 | "Make a narrated video explaining what a single neuron in a neural network computes: weighted sum, bias, sigmoid." | in-corpus 2D; the framework's home ground; exercises `LayeredNetwork`, `numbers_to_symbol`, `provenance` |
| T2 | "Make a narrated video on why gradient descent steps in the direction of the negative gradient." | adjacent topic; exercises axes, `ValueTracker` numbers, a 3D orbit |
| T3 | "Make a 5-minute video explaining how softmax turns scores into probabilities, with temperature." | in-corpus 2024 topic without the 2024 helpers; tests whether rules transfer |

The set is fixed so that iterations are comparable; a fourth off-domain topic (for example
the central limit theorem) is added in M4 to test generalization.

## 9. Repo layout inside the kit and required kit changes

### 9.1 Layout

```text
skills/manim-teaching-video/
  SKILL.md
  references/
    framework.md  patterns.md  rubric.md  pipeline.md  roles.md  manimgl-to-manimce.md
    analyses/neural-networks.md  analyses/attention.md
  scripts/
    preflight.py  narrate.py  render.py  assemble.py  verify.py  check_scenes.py
    mtv/__init__.py  mtv/common.py  mtv/look.py  mtv/narrated.py  mtv/patterns.py  mtv/tts.py
    tests/...
  assets/manim.cfg  assets/lesson.example.json
  evals/<case>/prompt.md  case.yaml  graders/NN-*.md
tools/corpus-3b1b/
  fetch.py  transcribe.py  align.py  check_record.py  tests/
  data/manifest.json  data/<id>/alignment.json  data/<id>/anchors.json
docs/adr/0008-skills-may-ship-scripts-and-references.md
docs/research/manim-teaching-video/  (the seven maps and this architecture, as research record)
```

File names stay within `[A-Za-z0-9._/-]` so the installer's stamp filter manages them (map 06
section 2.3). No bare absolute paths, `~/` paths or `> /dev/null` anywhere under `skills/`
because `validate.sh` scans all skill markdown including fences (map 06 section 1.4).

### 9.2 Kit changes, each a single expression where possible

| File | Change | Why |
| --- | --- | --- |
| `scripts/install.sh` | the `find` filter becomes `find . -type f ! -name 'SKILL.md' ! -path './evals/*' ! -path '*/__pycache__/*' ! -name '*.pyc'` (tab-indented for `shfmt`) | today only `*.md` is shipped, so `scripts/` and `assets/manim.cfg` would be dropped (map 06 section 2.1 and 2.2) |
| `scripts/validate.sh` | `md_files` excludes paths with `evals` in `p.parts` | eval prompts need real paths (map 06 section 2.2) |
| `.github/workflows/validate.yml` | add `test -f` for `skills/manim-teaching-video/skill.md`, `scripts/narrate.py` and `references/framework.md` in the sandbox install | exercise the ship-everything behavior |
| `README.md` | skills count and table row; install note that skills may ship scripts | counts change |
| `CHANGELOG.md` | `Unreleased` entry in the existing style | kit convention |
| `.gitignore` | `manim-teaching-video-workspace/`, `media/`, `*-workspace/` | eval and render bulk |
| `docs/adr/0008-*.md` | "Skills may ship executable scripts and reference material", one paragraph, alternatives rejected (per-skill manifest; vendoring the corpus; Python gates) | map 06 section 7; ADR-0002 and ADR-0006 unchanged |

No change to `AGENT_REF` because no agents are added in the first release.

## 10. Phasing and milestones

Effort is in focused agent-session days in an environment with network, manim, TeX Live and
Kokoro installed; each milestone ends with a commit in the worktree
`$HOME/worktrees/.agents/<branch>` per `rules/git-worktrees.md`.

| M | Scope | Effort | Proves |
| --- | --- | --- | --- |
| M0 Spike | install `manim==0.22.0`, TeX Live packages from the CE install docs, Kokoro; hand-write a two-beat `NarratedScene`; render `-ql --save_sections`; synthesize two sentences; assemble and mux by hand; measure render seconds per second and Kokoro real-time factor | 1 day | the toolchain works on CPU; the timing contract (sections padded to narration) holds; the numbers for the render budget |
| M1 Runtime scripts | `scripts/mtv/` (`look`, `narrated`, `tts` with Kokoro and ElevenLabs, five `patterns` helpers), `preflight`, `narrate`, `render`, `assemble`, `verify`, `check_scenes`, `manim.cfg`, unit tests | 2 to 3 days | a `lesson.json` plus hand-written `lesson.py` yields a verified MP4 end to end with no model in the loop |
| M2 Corpus pilot and framework v0 | `tools/corpus-3b1b/` on chapters 1 and 6; two analysis records with refuter pass; `framework.md`, `patterns.md` (remaining helpers), `rubric.md`, `pipeline.md`, `roles.md` synthesized from the records and maps 01 to 05; framework test (section 8.2) | 3 days | two agents given the framework produce storyboards that pass the storyboard critic |
| M3 Skill TDD | RED baselines on T1 to T3 and the pressure scenarios; eval cases; `SKILL.md` GREEN; with-skill runs; REFACTOR; kit changes, ADR, CHANGELOG, README; all gates green | 3 days | the skill produces a hard-gate-clean, rubric-passing video for T1 to T3 in a fresh session, and beats the baseline |
| M4 Extension loop (after first release) | remaining six videos through the same three tools and the analyst plus refuter pair; per-section analysts for the 25-minute videos; 2024 visual-noun helpers; keyframe extraction as the secondary check; OpenAI and Azure providers; fourth test topic; `agents/mtv-*` promotion; description optimization with `run_loop.py` | 1 day per video, 1 day per helper group | each addition is a repeat of an M2 or M1 step, not new design |

The first release ships at the end of M3, about nine to ten days.

## 11. Risks and mitigations

| Risk | Evidence | Mitigation |
| --- | --- | --- |
| CPU render time makes the fix loop too slow | no CE render was timed; 60 fps presets double frames (map 04 "Quality flags") | M0 measures; 30 fps everywhere; draft tier at 15 fps 480p; per-section renders; caching left on for final renders |
| Kokoro will not install on the consumer's Python | PyPI `requires_python <3.13` versus GitHub `main` (map 05) | preflight detects and prints the GitHub install line; `kokoro-onnx` and Piper fallbacks; stated assumption of Python 3.11 or 3.12 |
| LaTeX missing or incomplete breaks numbers, matrices and braces | CE `DecimalNumber`, `Matrix`, `Brace.get_text` need LaTeX (map 04 "LaTeX requirement") | preflight hard-stops with the package list; `look.py` ships the richer `TexTemplate` so the 3b1b preamble packages are present |
| Agents write ManimGL idioms from training data | `Tex`/`TexText` naming swap, `ShowCreation`, `play(mob.method)` (map 04 translation table) | `check_scenes.py` rejects before render; `patterns.py` provides the idioms so they are imported, not recalled |
| Transcript-to-code alignment is noisy for multi-file videos | 60 percent estimated for 2024 videos (map 07 section 4) | start with one-file chapter 1; anchors file; records mark uncertain sections; alignment refines rules rather than gating them |
| License leakage into the kit | CC BY-NC-SA code, all-rights-reserved articles (map 07 section 6) | only paraphrase and `file:line`; `check_record.py` exact-line guard; raw corpus outside the repo; attribution note atop `framework.md` |
| Kit gates reject the content | MD024 file-wide unique headings, MD060 table style, `SLASH_REF` on absolute paths, typos on jargon (map 06 sections 1.4 and 3.1) | fixed heading outlines; compact table style; relative paths and `$VAR` forms; run markdownlint-cli2 and typos before every commit |
| Sync drift after a section is edited | overruns shift later audio | `beat()` pads to narration; `verify.py` drift gate at 0.25 s; audio placed by section JSON offsets, so a re-render moves audio with it |
| 3D in Cairo is slow and the camera conventions differ from GL | surfaces are many `VMobject` pieces; `reorient` angle convention unverified (map 04) | one orbit helper in the first release, 2.5D by default; 3D nouns deferred to M4 |
| The skill description does not trigger | kit style versus writing-skills style tension (map 06 section 5.1) | description names capability and trigger phrases without the workflow; `run_loop.py` optimization in M4 |

## 12. Deliberately cut

| Cut | Why it is not needed for the first good video | How it comes back |
| --- | --- | --- |
| manim-voiceover dependency | stale pins, interpolated timing, PyTorch for timing Kokoro already gives (map 05 section 1) | never as a dependency; its ergonomics live in `beat()` |
| Pi creatures, teacher-student cutaways, logo, end screens, banners | brand assets whose SVGs are not public (map 03 section 2); the reaction beat's pacing job is carried by narration | an original "learner question" callout pattern, if the rubric shows the hole |
| Forced alignment (torchaudio, stable-ts, whisperX) | both first-release providers return timestamps natively | one provider function returning `[]` plus an aligner in `tts.py` |
| Keyframe extraction from downloaded video | bucket figures are a captioned frame set already keyed to article paragraphs (map 07 section 2) | M4, with the verified ffmpeg `select` command |
| Eight-video corpus at release | two videos cover both visual regimes; the framework is seeded from the maps | M4, one subagent per video |
| 2024 visual nouns (token tape, dials, attention grid, slab stack, context arcs, bar chart) | T1 to T3 do not need them | one helper each after the chapter 6 record |
| OpenGL renderer and interactive embed | undocumented, needs a window; Cairo is the documented path (map 04 "Renderers") | not planned |
| 4K default | 4K at 30 fps is four times the pixels of 1080p; 3b1b's output but not required to pass the rubric | the `final` tier, on request |
| New `agents/` entries and the `AGENT_REF` change | five inlined role prompts suffice; adding agents touches the validator and README | M4 promotion when roles are reused by another skill |
| Real data (GPT-2, GloVe, MNIST weights) | deterministic seeded synthetic values tell the truth the narration tells (map 02 section 10 item 4 and section 11.5) | a `data` hook in `patterns.py` for a real tensor |
| Subtitle burn-in, music, sound effects, multiple voices, thumbnails | not part of "teaches like 3b1b"; the SRT is produced anyway | libass burn-in is one ffmpeg line (map 05 section 6) |
| Description optimization with `run_loop.py` | needs a scratch project and `claude -p`; triggering can be judged by the three test prompts first | M4 |
| Per-section analysts and judge panels over competing storyboards | one storyboard plus one critic plus one retry is enough for a five-minute video | M4 if rubric scores plateau |

## 13. Decisions needed from the user

1. Corpus tooling location: `tools/corpus-3b1b/` inside the kit repo (one new top-level
   directory, not installed) or a separate repository. The design assumes in-kit.
2. Narration default confirmed as Kokoro `af_heart` offline, and the environment assumption of
   Python 3.11 or 3.12 for the PyPI wheel (3.13 requires the GitHub install).
3. Default output tier `standard` at 1920x1080 and 30 fps, with 4K only on request.
4. Inline role prompts in `references/roles.md` for the first release rather than new
   `agents/mtv-*` entries (which would require the `AGENT_REF` regex and README changes).
5. One ADR (0008, scripts and reference material shippable) or two (adding 0009, corpora are
   studied not vendored).
6. LaTeX as a hard requirement at preflight (recommended, because numbers, matrices and brace
   labels need it) versus a Typst fallback mode that forbids `Tex` classes (unverified).
7. Acceptance of the YouTube terms-of-service risk for the pilot: captions-only fetch for
   transcripts (recommended for the first release) versus media download for keyframes.
8. First-release corpus scope of two videos (chapters 1 and 6) before the skill ships, with
   the other six as the M4 loop.
9. Skill id `manim-teaching-video` and the internal package name `mtv`.
10. The three fixed test topics in section 8.4.

## Unverified items

- No ManimCE, LaTeX or Kokoro code was executed in the design container; render throughput,
  Kokoro real-time factor and the GL-to-CE camera angle convention are measured or checked
  in M0.
- Whether the eight videos carry manual English captions, and whether their descriptions
  contain chapter timestamps (map 07 section 7).
- `DecimalNumber(mob_class=Text)` as a LaTeX-free fallback is plausible from the CE source but
  untested (map 04).
- The lychee behavior from a GitHub runner against the few external links this design adds.
- Canonical pages referenced: <https://github.com/3b1b/videos>,
  <https://github.com/ManimCommunity/manim>, <https://github.com/hexgrad/kokoro>,
  <https://github.com/ManimCommunity/manim-voiceover>, <https://pypi.org/project/manim/>,
  <https://pypi.org/project/kokoro/>, <https://pypi.org/project/yt-dlp/>,
  <https://pypi.org/project/faster-whisper/>.
