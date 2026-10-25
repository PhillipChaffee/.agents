# Judgment: pragmatic shipping engineer

Lens: effort, dependency and maintenance risk (ManimCE versions, TTS services,
LaTeX, model downloads), CPU-only render and transcription time, CI gates, repo
size, licensing, and whether each milestone proves the right thing early.

Inputs read in full: the three architectures under `design/architectures/`
(corpus-fidelity 813 lines, repeatable-process 892, minimal-viable 751) and the
seven maps under `design/maps/`. Claims below are checked against the maps,
against the local clones (`ManimCommunity/manim` at the 0.22.0 tag,
`/home/user/.agents` at its current HEAD, the merge of pull request 17), or marked unverified. Nothing was
rendered or synthesized in this container (manim, LaTeX and Kokoro are not
installed), so every throughput number stays an estimate.

## Facts checked for this judgment

These are the checks that moved scores. Each row names where the evidence is.

| Claim or question | Finding | Evidence |
| --- | --- | --- |
| ManimCE 0.22.0 Python floor | `requires-python = ">=3.11"`; Kokoro PyPI wheel is `<3.13`, so the default voice installs from PyPI only on 3.11 or 3.12 | CE `pyproject.toml:23`; map 05 lines 231-234 |
| CE needs `audioop-lts` on 3.13 for `pydub` | yes, declared conditionally, so `add_sound` works on 3.13 | CE `pyproject.toml:25,40` |
| Section MP4s written by `--save_sections` carry audio | no: `combine_to_section_videos` concatenates partial movie files only; audio is mixed into the final movie | CE `manim/scene/scene_file_writer.py:966-985`; map 04 line 303 |
| Section index JSON fields | `name`, `type`, `video` plus ffprobe-style metadata per section | CE `manim/scene/section.py:83-105`; map 04 line 296 |
| Scene clock available to a `beat()` runtime | `Scene.time` returns `renderer.time`; the 0.22 `Manager` also exposes `time` | CE `manim/scene/scene.py:286-288`; `manim/manager.py:101-107` |
| `--disable_caching_warning` CLI flag | does not exist; `disable_caching_warning` is a `manim.cfg` key only | CE `manim/_config/default.cfg:134`, `manim/_config/utils.py:1293-1299`; CLI flags in `manim/cli/render/global_options.py:65,112` |
| `--dry_run`, `--save_sections`, `-r`, `--fps`, `--format` | all present | CE `manim/cli/render/global_options.py:112`; `render_options.py:153,199-207,260` |
| A custom TeX preamble is needed for the 3b1b packages | CE already ships `TexTemplateLibrary.threeb1b` with `dsfont`, `physics` and the rest; only the `\minus` macro is missing | CE `manim/utils/tex_templates.py:26-67`; plain `TexTemplate()` has three packages, `manim/utils/tex.py:7-9` |
| `max_inflight_encoders` | real key, default 1, "4 is a good value" | map 04 lines 312, 374 |
| Whisper time for 149 minutes on 4 CPUs | map 05 extrapolates "an hour or more" for `large-v3` per 25 minutes; map 07 says "hours" for the whole corpus | map 05 lines 533-537; map 07 line 474 |
| Kokoro CPU real-time factor | community figure 0.57 to 0.79, low confidence; 10 minutes of narration is 6 to 8 minutes of synthesis | map 05 lines 245-248 |
| Kokoro dependency weight | `torch`, `transformers`, `spacy`, `spacy-curated-transformers`, `espeakng-loader`; weights from `huggingface.co` | map 05 lines 224-236 |
| Piper fallback license | package GPL-3.0-or-later (fine as subprocess); voices "intended for personal use and text to speech research only" | map 05 lines 263-266 |
| Installer today | copies `SKILL.md` as lowercase `skill.md` and only `*.md` beside it | `scripts/install.sh:87,94` |
| Stamp manifest charset | `^[A-Za-z0-9._/-]+$` | `scripts/install.sh:116` |
| `AGENT_REF` prefixes | `cr-`, `researcher-*`, `research-*` only | `scripts/validate.sh:90-93` |
| jscpd scope | 5 percent threshold; ignores `**/*.md`; Python and JSON count | `.jscpd.json`; map 06 lines 429-438 |
| CI smoke test | five `test -f` lines in `validate.yml:22-26`, lowercase `skill.md` | `.github/workflows/validate.yml:22-26` |
| ADR numbering | 0001 to 0007 exist, so 0008 is free | `docs/adr/` |
| Kit size today | `skills/` 60 KB, `agents/` 172 KB, `.git` 1.5 MB | `du -sh` in the kit |
| Map numbers quoted by the designs (117, 105, 27; 148, 85, 139, 736; 245 figures; 518 objects and 271 MB; 149 minutes; 30 minutes per video for anchors; chapter 6 in `attention.py` plus `supplements.py:841-1338`) | all present in the maps as quoted | map 01 lines 480-517, 805-847; map 02 lines 414, 466-472, 552; map 07 lines 102, 292, 301, 414, 566 |

## Scores

Scale 1 to 10. One sentence each. Criteria: (1) output-quality fidelity,
(2) repeatability, (3) feasibility under the stated constraints, (4) corpus
leverage and evidence grounding, (5) fit with kit conventions and skill
authoring practice, (6) testability, (7) simplicity and YAGNI.

### Corpus-fidelity scores

| # | Score | Why |
| --- | --- | --- |
| 1 | 9 | Highest ceiling: 24 principles each with an apply rule and an observable check, 44 rendered patterns, a 20-item rubric with gates, and both 2017 and 2024 visual regimes covered. |
| 2 | 7 | Section renders, per-`play` caching, `verify_sync.py` and the fix loop are there, but there is no run-state record, so a usage-limit cutoff means re-deriving where the run was from the artifacts on disk. |
| 3 | 5 | About 19 focused sessions, hundreds of analyst, synthesizer, refuter and census subagent runs, roughly four hours of human anchor time, a multi-hour whisper pass, and a pattern CI that needs manim plus LaTeX somewhere the kit does not have them. |
| 4 | 10 | Every content scene gets a record, every citation is machine-checked, tag histograms are reconciled against grep counts, and two analysts cross-check two sections per video. |
| 5 | 7 | Kit voice, two ADRs, `mv-*` agents and the installer change are all right, but 44 example `.py` files plus fixtures plus reference images under `skills/` enlarge the jscpd, typos and install surface more than any other design. |
| 6 | 8 | Self-tests, pattern renders, a framework-only generation test and a rule discrimination test are a strong set; where the pattern CI runs is left open. |
| 7 | 3 | Three analyst roles plus two verifiers plus inter-analyst agreement, 44 patterns, a dual audio path (`add_sound` in the scene and an external mix), and a census before synthesis is far more machinery than the first good video needs. |

Total: 49 of 70.

### Repeatable-process scores

| # | Score | Why |
| --- | --- | --- |
| 1 | 7 | Rules carry apply, check, why and fails, the rubric maps to rule ids, and narration-first timing is correct, but 3D and the 2024 camera vocabulary are cut from v1, so transformer-style topics will look flatter than the corpus. |
| 2 | 10 | `state.json` with input hashes, one scene per process, narration cached by content hash, hard objective gates and a documented resume path make it the most repeatable of the three. |
| 3 | 6 | 19 to 24 session days with the first end-to-end MP4 only at M4, three math engines (`mathtex`, `typst`, `text_only`) that multiply pattern variants, and a whisper estimate that is optimistic against maps 05 and 07. |
| 4 | 8 | Eight videos analyzed with a schema validator, a refuter, cross-video vocabulary convergence and a coverage rule, on a captions-first path that avoids media download. |
| 5 | 8 | Closest to the kit's orchestrator voice and to map 06's exact recommendations, including `CONTEXT.md` vocabulary; committing eight schema-identical `analyses/*.json` into the kit is a jscpd exposure it does not list. |
| 6 | 9 | `selftest.py` runs without ManimCE, a `null` provider, `--one-beat` end to end, a conformance eval before the skill exists, and a pass rule that the baseline must fail on at least four of six prompts "otherwise the skill adds nothing measurable". |
| 7 | 4 | Seven gates, five agents, ten scripts plus a providers package, three math engines and text-only pattern variants are each justified in isolation and heavy in sum for a first release. |

Total: 52 of 70.

### Minimal-viable scores

| # | Score | Why |
| --- | --- | --- |
| 1 | 6 | The framework is seeded from maps 01 to 04 and two videos, ten helpers cover the 2017 look and one orbit, and 2024 visual nouns are absent at release; shipping idioms as importable code rather than prose is the one fidelity lever the others underuse. |
| 2 | 8 | One contract (`lesson.json`) with exactly one writer per field, resume by missing outputs, and hard gates in `verify.py`; it lacks hash-based invalidation, so a changed upstream stage does not force downstream reruns. |
| 3 | 9 | M0 is a hand-written two-beat spike on day one, M1 yields a verified MP4 with no model in the loop by about day four, nine to ten days to release, LaTeX is a hard requirement with a printed install line, and media download is opt-in. |
| 4 | 6 | Two videos with a ten-claim refuter and bucket figures as keyframes is honest but thin; the rest is deferred to a repeat-a-step loop, so the first framework leans on the maps more than on aligned transcripts. |
| 5 | 7 | Three single-expression kit changes, one ADR, no `AGENT_REF` change and inlined roles fit the kit; putting `tools/corpus-3b1b/` and its JSON data inside the kit repo contradicts map 06 section 6 and widens the hygiene surface. |
| 6 | 8 | Pytest per unit boundary, a framework test before the skill exists, three fixed topics plus pressure scenarios and script graders; only three topics and no off-domain topic until M4. |
| 7 | 9 | One contract, one package, ten helpers, twelve criteria, hard stop on LaTeX, no new agents, and every cut has a named way back. |

Total: 53 of 70.

## Corpus-fidelity assessment

### Corpus-fidelity strengths

- The analysis record schema (section 4.2) and `cite_check.py` (section 4.3)
  are the best-specified evidence contract of the three: a code citation must
  fall inside the cited class's AST span and contain an animation named in the
  beat; a transcript citation must overlap a word; a 13-word verbatim run is
  rejected. That is checkable in a few hundred lines of Python.
- The two-`Check` rule form (section 5.2), one predicate for the storyboard
  critic and one for `lint_scene.py`, is the right way to make a framework
  rule enforceable rather than aspirational.
- The load-order table (section 5.5) is a concrete answer to context budgets:
  under 6 k tokens for the script stage, under 15 k for one section of code.
- Separate MIT corpus repository with a single `sync_to_kit.py` that runs the
  kit's gates before copying (section 3.2 and 3.3) is the cleanest license
  boundary of the three.
- The deliberately-cut list (section 12) and the nine user decisions (section
  13) are complete and honest, including the 25-pattern alternative.

### Corpus-fidelity weaknesses

- Milestone order proves the wrong thing first. M0 installs tools, then M1
  spends three sessions on the chapter 1 corpus pipeline before M2 produces
  the first MP4. The unproven part of this project is CPU render time, Kokoro
  on the consumer's Python and sync across re-renders (maps 04 and 05), and
  that risk is not retired until roughly session five.
- Effort is the largest: about 19 sessions before the secondary tier, with
  M3 (seven more videos through code analyst, narration analyst, synthesizer,
  refuter and census critic) as "the long pole". Add eight times 30 minutes of
  human anchor time (map 07 line 566) that the effort table does not count.
- Pattern CI (section 8.2) renders 44 examples and compares each against a
  committed reference image by perceptual hash. The kit has no Python or manim
  in CI (ADR-0002, map 06 section 3.10), so either this runs only in the
  corpus repository while the patterns live in the kit, or binaries enter the
  kit. Both are unresolved in the text.
- 44 example `.py` files under `skills/` all start with the same
  `Scene`/`construct` boilerplate; jscpd counts Python at a 5 percent token
  threshold (`.jscpd.json`), and these files are installed into every consumer
  home.
- Dual audio path: `add_sound` inside the scene plus an external loudnorm mix
  (section 7). The stated reason, audio in section MP4s for the frame
  reviewer, is false (see errors) and the frame reviewer reads PNGs anyway.
- Whisper on the full 149 minutes with `large-v3-turbo` int8 on 4 CPUs is a
  multi-hour background job (map 05 lines 533-537; map 07 line 474), accepted
  rather than avoided; the captions-first path exists but media download is
  still the default in section 3.3.

### Corpus-fidelity errors and unverified claims

1. Section 7, "`add_sound` inside the scene is still called so the section
   MP4s have audio for the frame reviewer": wrong. `combine_to_section_videos`
   concatenates partial movie files with no audio
   (CE `manim/scene/scene_file_writer.py:966-985`); audio is mixed only into
   the final movie (map 04 line 303).
2. Section 7, Kokoro "PyPI on 3.10 to 3.12": ManimCE 0.22.0 requires Python
   3.11 or newer (CE `pyproject.toml:23`), so the shared window is 3.11 to
   3.12.
3. Section 8.2, pattern CI home and committed reference images: unresolved,
   see weaknesses.
4. Section 5.3, every example "renders at `-ql` in under 30 s": unverified; no
   render was timed anywhere in the design work.
5. Section 5.4, object budget "about 250 primitives": the maps give edge
   counts after thinning (map 01 section 2.2), not a frame-wide primitive
   budget; the number is a guess presented as a rubric constant.
6. Section 3.5, whisper "roughly real time or slower": consistent with maps 05
   and 07 but low confidence; the design's own M1 estimate (three sessions)
   depends on it.
7. Section 6.6, `final` tier "hours": unverified, correctly flagged by the
   design as a risk.
8. Sections 5.1 and 6.2, shipping `assets/tex_template.tex` and
   `manimce/config.md` with a custom preamble: CE already ships
   `TexTemplateLibrary.threeb1b` with `dsfont`, `physics`, `mathrsfs` and
   `xcolor` (CE `manim/utils/tex_templates.py:26-67`); only the `\minus`
   macro from map 03 section 1.3 needs `add_to_preamble`. Not an error, but
   work the design does not need to do.

### Corpus-fidelity ideas worth grafting

- `cite_check.py` rules (AST span containment, animation-name presence,
  transcript word overlap, 13-word verbatim guard) and the "records that fail
  go back to the synthesizer, never patched by hand" rule.
- The two-`Check` rule form, and `lint_scene.py` as the home for every
  statically decidable check (no `manimlib`, colors outside the contract,
  `self.play(mob.method, ...)`, missing `next_section`, missing seed).
- The load-order table in `SKILL.md` with token budgets per stage.
- `sync_to_kit.py` running the kit's markdownlint and typos before copying
  anything across the license boundary.
- The three pressure scenarios phrased as discipline rules with a "refuses and
  cites the rule in five of five runs" pass bar.
- `doctor.py` printing which quality tier is still possible given what is
  missing, rather than a bare fail.

## Repeatable-process assessment

### Repeatable-process strengths

- `state.json` keyed by input hashes with a documented "resume at the first
  stage whose inputs changed" rule (section 6.2) directly answers the brief's
  one-run-one-MP4 requirement and the usage-limit interruption that produced
  this very task.
- Narration-first with a static guard that a beat cannot run longer than its
  audio (section 7.4) is the right default; the audio length is the budget.
- One scene per `manim` process (section 6.6) so a crash loses one section's
  cache, and a hung process is killed on a ten-minute silent log.
- `selftest.py` runs without ManimCE (schema, `check.py`, `assemble.py`,
  `verify.py`, `null` provider) and grows `--patterns` and `--one-beat` when
  ManimCE is present (section 8.1). This is the only design whose script tests
  can run in the kit's current CI runner without manim.
- Pass definition for the skill includes "the baseline fails at least one
  objective grader on at least four of six prompts, otherwise the skill adds
  nothing measurable" (section 8.3 item 5). That is the writing-skills RED
  discipline turned into a number.
- Captions-first corpus with `DOWNLOAD_MEDIA=1` as an explicit opt-in and
  `make clean-media` after keyframes (section 3.2) is the best handling of the
  YouTube terms-of-service risk.
- G0 decides the math engine before any content exists (section 6.6), so a
  LaTeX-less machine never gets a storyboard full of `MathTex`.

### Repeatable-process weaknesses

- The first end-to-end MP4 arrives at M4 after M1 to M3 (corpus, eight
  analyses, framework and 24 patterns), roughly day ten to thirteen. M0
  measures render time on a hand-written scene, which is good, but the sync
  contract (`NarratedScene`, `verify.py`) is not exercised until M4.
- Three math engines with `text_only` variants of number-bearing patterns
  (sections 6.3 and 6.6) is a maintenance multiplier: every pattern that uses
  `DecimalNumber`, `Matrix` or `Brace.get_text` needs a `Text` twin, and
  `DecimalNumber(mob_class=Text)` is unverified (map 04 line 615). A hard
  stop with the TeX Live install line costs nothing to maintain.
- `check.py` "rejects a beat whose declared `run_time`s sum to more than the
  audio length minus 0.3 s" (section 7.4). Static summation of `run_time`
  keyword arguments is unreliable: defaults (1 s when omitted), expressions,
  `until()` results and `LaggedStart` composition all defeat it. The runtime
  overrun warning in the same section already does this job at render time.
- Eight `analyses/<slug>.json` records in the kit: jscpd counts JSON at 5
  percent (map 06 section 3.4) and schema-identical records repeat long key
  runs. The risk table lists fixtures but not these.
- Transcription estimate "one to two hours for the 149 primary minutes"
  (section 3.3) is optimistic against map 05's extrapolation (an hour or more
  for `large-v3` per 25 minutes) and map 07 line 474; the author marks it low
  confidence, but M1's two-day budget rests on it.
- Five new `agents/mv-*` entries require the `AGENT_REF` regex change and
  README table edits in the first release; minimal-viable shows the same
  roles work inlined.

### Repeatable-process errors and unverified claims

1. Section 3.3, whisper time: optimistic, see weaknesses; low confidence is
   stated.
2. Section 7.4, static `run_time` sum check: feasibility unverified and
   doubtful; the runtime warning is the reliable mechanism.
3. Section 5.3, a `tex_template` pattern that "adds `dsfont`, `mathrsfs`,
   `physics`, `xcolor`": CE's `TexTemplateLibrary.threeb1b` already has them
   (CE `manim/utils/tex_templates.py:26-67`); only `\minus` is missing.
4. Section 7.1, Piper as fallback "GPL used as a subprocess": the package
   point is right, but Piper voices are "intended for personal use and text to
   speech research only" (map 05 lines 265-266), which the design does not
   surface for a skill that produces publishable videos.
5. Section 6.7, tier budgets (draft 5 minutes, standard 40 minutes, uhd 3
   hours on 4 CPUs): correctly labelled calibration targets, unverified.
6. Section 9.1, `analyses/<slug>.json` committed to the kit: jscpd exposure
   not in the risk table.
7. Section 6.3 step 7, `frames.py` reads "a bounding-box log the runtime
   writes at the end of each beat": plausible via `self.mobjects` and
   `get_bounding_box`, untested in CE 0.22.

### Repeatable-process ideas worth grafting

- `state.json` with per-stage input hashes and the resume rule.
- One `manim` process per scene, background render with log tailing, kill on
  ten minutes of silence, one retry with `--disable_caching`.
- `selftest.py` that runs without ManimCE and adds `--patterns` and
  `--one-beat` when it is present.
- The `null` provider that writes silence and evenly spaced words, so the
  whole pipeline is testable with no model and no network.
- The baseline-must-fail clause in the skill pass definition.
- `DOWNLOAD_MEDIA=1` opt-in with the captions-plus-figures path as default.
- Regex matching of render exceptions to the map 04 error table so the retry
  prompt carries the fix text.
- `bookmarks` as word indices in the storyboard and `sync` naming the visual
  that must be on screen at that word, which gives the frame reviewer an
  exact frame to pull.

## Minimal-viable assessment

### Minimal-viable strengths

- M0 is the right first milestone for this project: a hand-written two-beat
  `NarratedScene`, rendered with `--save_sections`, narrated with Kokoro,
  muxed by hand, with render seconds per second and the Kokoro real-time
  factor measured on day one (section 10). Every later budget constant is a
  measurement, not a guess.
- M1 produces a verified MP4 from a hand-written `lesson.py` with no model in
  the loop (section 10), so the toolchain and the sync contract are proven
  before any subagent prompt exists.
- `lesson.json` with one writer per field (section 2.3) is a smaller contract
  than repeatable-process's storyboard plus narration plus render records,
  and it is enough for resume by missing outputs.
- Patterns are code, not prose: ten helpers in `scripts/mtv/patterns.py`
  (section 5.3) are imported by generated scenes, so the agent cannot recall a
  ManimGL idiom in their place. This is the cheapest fidelity mechanism of the
  three and the only one that also shrinks the scene coder's context.
- Audio is never added inside Manim (section 7.3): renders stay cacheable and
  a voice change re-renders nothing. The other two designs say the same but
  corpus-fidelity then also calls `add_sound`.
- Kit changes are three single expressions plus one ADR and no `AGENT_REF`
  change (section 9.2), with inlined roles the kit explicitly allows (map 06
  section 4.1).
- Every cut in section 12 names the way back, and most extensions are "repeat
  an M1 or M2 step", which is a credible claim given the per-unit script
  boundaries.
- LaTeX is a hard preflight requirement with the install line printed (section
  6.4). One engine, no `Text` twins to maintain.

### Minimal-viable weaknesses

- Corpus depth at release is two videos and the framework is seeded from the
  maps. Maps 01 to 04 are themselves evidence-backed, so this is less risky
  than it sounds, but the transcript-aligned "what he says when the visual
  changes" rules (R24 in section 5.2) rest on two alignments, one of them the
  multi-file chapter 6 that map 07 rates at about 60 percent.
- `tools/corpus-3b1b/` plus `data/<id>/alignment.json` inside the kit repo
  (section 3.3): not installed, but scanned by jscpd, typos, lychee and
  gitleaks, and it is a new top-level directory that map 06 section 6
  recommends keeping out of the kit. The design lists the separate repository
  as an alternative; it should be the default.
- `scripts/tests/` under `skills/manim-teaching-video/` is shipped to every
  consumer by the proposed `find` filter, which excludes only `SKILL.md`,
  `evals/`, `__pycache__` and `*.pyc` (section 9.2). Either exclude `tests/`
  or accept the extra files in the stamp.
- Resume is by missing outputs only (section 2.3). An edited beat narration
  does not invalidate its stale WAV unless `narrate.py` compares text hashes,
  which the text does not say.
- Nine to ten days is tight: M2 covers two corpus analyses, a refuter pass,
  five reference files and a framework test in three days; M3 covers RED,
  GREEN, REFACTOR, kit changes and all gates in three days, with each
  with-skill eval run rendering a draft video.
- Fix loop is capped at two passes and three test topics with no off-domain
  topic until M4, so generalization beyond the corpus domain is unmeasured at
  release.

### Minimal-viable errors and unverified claims

1. Section 6.2 step 6, `manim -ql --fps 15 --save_sections
   --disable_caching_warning`: `--disable_caching_warning` is not a CLI flag
   in 0.22.0, only a `manim.cfg` key (CE `manim/_config/default.cfg:134`;
   `manim/_config/utils.py:1293-1299`; the CLI has `--disable_caching` at
   `manim/cli/render/global_options.py:65`). `--fps 15` is redundant with
   `-ql` (map 04 line 342).
2. Section 7.4, "the useful core is about 400 lines": map 05 line 190 gives
   `voiceover_scene.py` at 238 lines plus `tracker.py` and parts of
   `base.py`; the figure is a reasonable estimate, not a count.
3. Section 6.2 step 8, `adelay` plus `amix`: ffmpeg's `amix` rescales inputs
   by default, which lowers the narration level before `loudnorm`; map 05
   line 664-665 offers plain WAV concatenation as the alternative. Unverified
   here (filter option not checked in this container).
4. Section 5.1, `look.py` ships a `TexTemplate` with `dsfont`, `mathrsfs`,
   `physics`, `xcolor`: CE's `TexTemplateLibrary.threeb1b` already has them
   (CE `manim/utils/tex_templates.py:26-67`); `look.py` reduces to selecting
   it and adding `\minus`.
5. Section 7.1, Kokoro real-time factor under 1.0: correctly marked low
   confidence and measured in M0.
6. Section 3.1, chapter 6 as a one-subagent analysis: `attention.py` is 4093
   lines (map 02 line 717) plus the `supplements.py` block; one analyst's
   context is a real constraint the design acknowledges only as the M4
   per-section extension.
7. Section 8.1, pytest: the kit has no Python gate (ADR-0002), so these tests
   run only by hand; the design says so.

### Minimal-viable ideas worth grafting

- M0 as a hand-written two-beat spike that measures render seconds per second
  and Kokoro real-time factor before any corpus work.
- M1 as "hand-written `lesson.py` to verified MP4 with no model in the loop".
- `lesson.json` with exactly one writer per field.
- Patterns as an importable helper module with docstrings citing the map and
  line, rather than prose examples the coder must transcribe.
- Hard LaTeX requirement at preflight with the install line.
- Inlined role prompts in `references/roles.md` until a second skill reuses
  them.
- The extension table in section 12 (cut, why not needed, how it comes back).

## Ranking

1. **Minimal-viable** (53). For this lens it proves the risky things first
   (toolchain on day one, no-model MP4 by day four), has the smallest
   dependency and gate surface, and names every extension. Its thinness on
   the corpus is a known, scheduled gap rather than an unknown.
2. **Repeatable-process** (52). The best run-time engineering of the three:
   state and resume, one process per scene, a null provider, tests that run
   without manim, and a pass rule that forces the baseline to fail. It loses
   on time to first MP4 and on the three-engine math fallback.
3. **Corpus-fidelity** (49). The strongest framework if finished, with the
   best evidence contract, but the longest path, the heaviest subagent bill,
   an unresolved CI home for 44 rendered patterns, and one factual error in
   the audio path.

Tie-break note: minimal-viable and repeatable-process are one point apart and
the right synthesis is minimal-viable's milestone order and contract with
repeatable-process's `state.json`, process isolation, null provider and
`selftest.py`, and corpus-fidelity's `cite_check.py` and two-`Check` rule form.

## What none of them handles

- **Default voice install weight.** Kokoro pulls `torch`, `transformers`,
  `spacy` and `spacy-curated-transformers` (map 05 lines 224-228), a
  multi-gigabyte CPU install plus model downloads from `huggingface.co`. No
  design states the install size or time, offers a pre-download step, or
  measures cold-start on a clean machine. `kokoro-onnx` is lighter but its
  token timestamps are unverified (map 05 line 253), and none plans the one
  experiment that would settle it.
- **Fallback voice licensing.** All three fall back to Piper. Piper voices are
  "intended for personal use and text to speech research only" (map 05 lines
  265-266). A kit that produces publishable videos needs either to drop Piper
  or to tell the user when a Piper voice was used.
- **A TeX template that already exists.** All three ship a custom preamble;
  CE's `TexTemplateLibrary.threeb1b` (CE `manim/utils/tex_templates.py:67`)
  already carries the 3b1b packages, leaving one `add_to_preamble` for
  `\minus`.
- **Pinning the Python version in the skill's `compatibility` line.** CE
  0.22.0 needs 3.11 or newer and Kokoro's wheel needs under 3.13; only
  minimal-viable and repeatable-process state 3.11 or 3.12, and none makes
  `preflight.py` fail fast on 3.13 with the GitHub install line before
  anything else is attempted.
- **Pinning ManimCE and its transitive deps.** All three pin `manim==0.22.0`
  in prose; none proposes a `requirements.txt` or lock file shipped with the
  skill, so the first consumer install after a 0.23 release will drift. The
  installer ships arbitrary files after the `find` change, so a lock file is
  one more file.
- **Measuring the whole-run wall clock.** Each design budgets render time;
  none budgets the full run (script, storyboard critic, narration, code
  waves, draft render, frame review, final render, assemble) or states what a
  five-minute video costs end to end on four CPUs. That number decides
  whether "one run yields a finished MP4" is minutes or an afternoon.
- **Where pattern renders run in CI.** The kit has no Python, manim or LaTeX
  in CI (ADR-0002, map 06 section 3.10). Corpus-fidelity renders 44 patterns,
  repeatable-process 24, minimal-viable runs pytest; all are "by hand in the
  implementation session". None proposes the cheap alternative: a scheduled
  job in the separate corpus repository that installs manim and renders the
  kit's `references/patterns/*.py` from a checkout.
- **Transcript cost avoidance.** All three mention captions-first, but none
  commits to "no whisper at all when manual captions exist and cue timing is
  good enough for section alignment", which would remove the multi-hour CPU
  step and the `huggingface.co` model download from the corpus phase.
